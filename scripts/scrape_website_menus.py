# -*- coding: utf-8 -*-
"""
Sadece website linki olan restoranlardan gercek menu ceker.
Playwright ile sayfayi tarar, yemek gibi gorunen satirlari alir.

Kullanim: python scripts/scrape_website_menus.py
"""

import json
import re
import asyncio
from playwright.async_api import async_playwright

# Google Maps UI gürültüsü ve genel web kelimeleri
NOISE_WORDS = {
    "kaydedildi", "paylaş", "yol tarifi", "ara", "gönder", "fotoğraflar",
    "yorumlar", "hakkında", "menü", "indir", "uygulamayı", "açık", "kapalı",
    "web sitesi", "telefon", "adres", "harita", "navigasyon", "kapat",
    "tamam", "iptal", "geri", "ileri", "yükle", "paylaşım", "favoriler",
    "son öğeler", "results", "saved", "share", "directions", "photos",
    "reviews", "about", "overview", "updated", "website", "call", "hours",
    "home", "contact", "gallery", "about us", "reservation", "book",
    "facebook", "instagram", "twitter", "copyright", "all rights",
    "çerez", "gizlilik", "kullanım koşulları", "anasayfa", "iletişim",
    "hakkımızda", "galeri", "rezervasyon", "bize ulaşın",
}

# Yemek içeriği olduğuna dair ipuçları
FOOD_HINTS = [
    "kebap", "köfte", "pilav", "çorba", "salata", "börek", "pide", "lahmacun",
    "pizza", "pasta", "burger", "sandviç", "döner", "ızgara", "tava", "güveç",
    "meze", "balık", "tavuk", "et", "sebze", "tatlı", "baklava", "künefe",
    "kahvaltı", "omlet", "menemen", "simit", "poğaça", "sushi", "ramen",
    "steak", "soup", "salad", "rice", "chicken", "beef", "fish", "dessert",
    "cake", "coffee", "tea", "juice", "smoothie", "cocktail",
]


def looks_like_food(text: str) -> bool:
    """Bu satır bir yemek ismi gibi görünüyor mu?"""
    lower = text.lower()

    # Noise ise atla
    if any(n in lower for n in NOISE_WORDS):
        return False

    # Sayı/fiyat içeriyorsa (menü fiyatı olabilir ama isim değil) - temizle
    text = re.sub(r'\d+[\s.,]*(?:TL|₺|lira|\$|€)?', '', text).strip()
    if len(text) < 3:
        return False

    # Yemek ipucu varsa kesinlikle al
    if any(h in lower for h in FOOD_HINTS):
        return True

    # Büyük harf başlayan, 3-40 karakter arası, özel karakter yok
    if re.match(r'^[A-ZÇĞİÖŞÜa-zçğışöüA-Z][a-zçğışöüA-Z\s\-\'&]{2,39}$', text):
        return True

    return False


async def scrape_menu_from_website(page, url: str, restaurant_name: str) -> list:
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=12000)
        await page.wait_for_timeout(2000)

        # Menü sayfası linki ara
        links = await page.query_selector_all("a")
        menu_url = None
        for link in links:
            href = await link.get_attribute("href") or ""
            text = (await link.inner_text()).strip().lower()
            if any(k in text for k in ["menü", "menu", "yemek listesi", "yiyecek"]):
                if href and "mailto" not in href and "tel:" not in href:
                    if not href.startswith("http"):
                        from urllib.parse import urljoin
                        href = urljoin(url, href)
                    menu_url = href
                    break

        if menu_url and menu_url != url:
            try:
                await page.goto(menu_url, wait_until="domcontentloaded", timeout=10000)
                await page.wait_for_timeout(1500)
            except:
                pass

        # Sayfadaki tüm kısa metin bloklarını topla
        elements = await page.query_selector_all("h1, h2, h3, h4, li, td, .item, .dish, .food, .product-title, .menu-item")
        items = []
        seen = set()

        for el in elements:
            try:
                text = (await el.inner_text()).strip()
                # Çok satırlı ise satırlara böl
                for line in text.splitlines():
                    line = line.strip()
                    if line and line not in seen and looks_like_food(line):
                        items.append(line)
                        seen.add(line)
            except:
                continue

        # Fallback: tüm metin paragrafları
        if len(items) < 3:
            full_text = await page.inner_text("body")
            for line in full_text.splitlines():
                line = line.strip()
                if line and line not in seen and looks_like_food(line) and 4 < len(line) < 45:
                    items.append(line)
                    seen.add(line)

        return items[:12]

    except Exception as e:
        return []


async def run():
    input_path = "data/processed/istanbul.json"

    with open(input_path, encoding="utf-8") as f:
        restaurants = json.load(f)

    with_website = [r for r in restaurants if r.get("website")]
    print(f"[INFO] {len(with_website)} restoranin websitesi var, menu taranacak...", flush=True)

    found = 0

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"],
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0",
            locale="tr-TR",
        )
        page = await context.new_page()

        for i, r in enumerate(with_website):
            name_safe = r["name"].encode("ascii", "replace").decode()
            print(f"[{i+1}/{len(with_website)}] {name_safe} | {r['website'][:50]}", flush=True)

            try:
                items = await asyncio.wait_for(
                    scrape_menu_from_website(page, r["website"], r["name"]),
                    timeout=20
                )
            except asyncio.TimeoutError:
                print(f"  [TIMEOUT] Atlanıyor...", flush=True)
                try:
                    await page.close()
                    page = await context.new_page()
                except:
                    pass
                items = []
            except Exception as e:
                print(f"  [HATA] {str(e)[:50]}", flush=True)
                items = []

            if items and len(items) >= 3:
                for orig in restaurants:
                    if orig["id"] == r["id"]:
                        orig["menu_items"] = items
                        orig["menu_source"] = "website"
                        break
                found += 1
                print(f"  OK: {len(items)} item -> {items[:3]}", flush=True)
            else:
                print(f"  Bulunamadi ({len(items)} item)", flush=True)

            if (i + 1) % 10 == 0:
                with open(input_path, "w", encoding="utf-8") as f:
                    json.dump(restaurants, f, ensure_ascii=False, indent=2)
                print(f">>> KAYIT: {i+1}/{len(with_website)} | Bulunan: {found}", flush=True)

            await asyncio.sleep(1.5)

        await browser.close()

    with open(input_path, "w", encoding="utf-8") as f:
        json.dump(restaurants, f, ensure_ascii=False, indent=2)

    print(f"\n[OK] {found}/{len(with_website)} websiteden gercek menu bulundu", flush=True)
    print("[SONRAKI] python scripts/json_to_ts.py", flush=True)


if __name__ == "__main__":
    asyncio.run(run())
