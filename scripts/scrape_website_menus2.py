# -*- coding: utf-8 -*-
"""
Restoran websitelerinden gerçek menü itemlarını çeker.
Menü sayfasını bulur, yapısal elementleri önce dener, fallback ile kısa satırlar alır.

Kullanim: python scripts/scrape_website_menus2.py
"""

import json
import re
import asyncio
from urllib.parse import urljoin, urlparse
from playwright.async_api import async_playwright

# Kesinlikle menü öğesi olmayan gürültü kelimeleri
NOISE = {
    # Navigasyon / UI
    "anasayfa", "home", "hakkımızda", "hakkimizda", "about", "iletişim", "iletisim",
    "contact", "galeri", "gallery", "fotoğraflar", "photos", "rezervasyon",
    "reservation", "book", "booking", "kariyer", "career", "blog", "haberler", "news",
    "gizlilik", "privacy", "kullanım koşulları", "terms", "cookie", "çerez",
    "facebook", "instagram", "twitter", "youtube", "whatsapp",
    "copyright", "all rights reserved", "© 20",
    # Şirket/kurumsal
    "kurumsal", "corporate", "hakkında", "sertifika", "belgeler",
    "misyonumuz", "vizyonumuz", "tarihçe", "history",
    # Teknik / CDN engel
    "javascript", "jquery", "loading", "error", "404", "cloudflare",
    "attention required", "browser", "ray id", "performance", "security",
    "just a moment", "checking your", "ddos",
    # Ödeme/sipariş UI
    "sepete ekle", "add to cart", "sipariş ver", "order now",
    "adet", "porsiyon", "seçenekler", "options",
    # Çok genel
    "bize ulaşın", "bizimle iletişime geçin", "scroll", "back to top",
    "next", "previous", "read more", "devamını oku",
    "paylaş", "share", "favoriler", "favorites",
    # Sosyal
    "takip et", "follow us", "abone ol", "subscribe",
    # Spam/casino
    "giriş", "casino", "bahis", "jojobet", "casibom", "betturkey",
}

# Güçlü yemek sinyalleri - bunlar varsa kesin al
FOOD_STRONG = [
    "kebap", "köfte", "pilav", "çorba", "salata", "börek", "pide", "lahmacun",
    "pizza", "pasta", "burger", "sandviç", "döner", "ızgara", "tava", "güveç",
    "meze", "balık", "tavuk", "et", "tatlı", "baklava", "künefe", "kadayıf",
    "kahvaltı", "omlet", "menemen", "simit", "poğaça", "sushi", "ramen",
    "steak", "schnitzel", "risotto", "hummus", "falafel", "shawarma",
    "mantı", "gözleme", "kumpir", "waffle", "krep", "cheesecake",
    "tiramisu", "cheesesteak", "teriyaki", "tempura", "katsu",
    "soup", "salad", "rice", "chicken", "beef", "fish", "lamb",
    "dessert", "cake", "bread", "wrap", "taco", "burrito",
    "latte", "cappuccino", "espresso", "smoothie", "milkshake",
    "şarap", "bira", "kokteyl", "wine", "beer", "cocktail",
    "izgara", "kavurma", "haşlama", "buğulama", "fırın",
]

def is_noise(text: str) -> bool:
    lower = text.lower()
    return any(n in lower for n in NOISE)

def has_food_signal(text: str) -> bool:
    lower = text.lower()
    return any(f in lower for f in FOOD_STRONG)

def clean_price(text: str) -> str:
    """Fiyat bilgisini temizle, ismi bırak."""
    text = re.sub(r'\d+[\s.,]*(?:TL|₺|lira|\$|€|USD|EUR)', '', text, flags=re.IGNORECASE)
    text = re.sub(r'^\d+[\s.,]+', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def score_line(text: str) -> int:
    """Satırın menü öğesi olma skorunu döner (0 = geç, yüksek = al)."""
    if not text or len(text) < 3:
        return 0
    if is_noise(text):
        return 0
    # Sadece sayı/sembol
    if re.match(r'^[\d\s₺TL.,\-+%()/*]+$', text):
        return 0
    # URL veya email
    if 'http' in text or '@' in text or 'www.' in text:
        return 0
    # Çok uzun (paragraf)
    if len(text) > 80:
        return 0

    clean = clean_price(text)
    if len(clean) < 3:
        return 0

    score = 1
    if has_food_signal(clean):
        score += 3
    if 4 <= len(clean) <= 40:
        score += 1
    if re.match(r'^[A-ZÇĞİÖŞÜ]', clean):
        score += 1  # Büyük harfle başlıyor
    return score


async def find_menu_url(page, base_url: str) -> str | None:
    """Ana sayfada menü linkini ara."""
    try:
        links = await page.query_selector_all("a")
        candidates = []
        for link in links:
            href = (await link.get_attribute("href") or "").strip()
            text = (await link.inner_text()).strip().lower()
            if not href or 'mailto:' in href or 'tel:' in href:
                continue
            if any(k in text for k in ["menü", "menu", "yemek listesi", "yiyecekler", "food", "carte", "dishes"]):
                if not href.startswith("http"):
                    href = urljoin(base_url, href)
                candidates.append(href)
            elif any(k in href.lower() for k in ["/menu", "/menu", "/yemek", "/food", "/dishes"]):
                if not href.startswith("http"):
                    href = urljoin(base_url, href)
                candidates.append(href)
        # base_url'den farklı olanı seç
        for c in candidates:
            if c.rstrip('/') != base_url.rstrip('/'):
                return c
    except:
        pass
    return None


async def extract_items_from_page(page) -> list:
    """Sayfadan yemek isimlerini çıkar."""
    items = []
    seen = set()

    # 1. Yapısal elementler - menü itemı olma ihtimali yüksek
    structural_selectors = [
        # Özel menü sınıfları
        "[class*='menu-item']", "[class*='menuitem']",
        "[class*='menu_item']", "[class*='dish']",
        "[class*='food-item']", "[class*='product-name']",
        "[class*='item-name']", "[class*='item-title']",
        # Tablolar (menü tabloları)
        "td:first-child", "th",
        # Listeler
        "ul li", "ol li",
        # Başlıklar
        "h3", "h4", "h5",
    ]

    for sel in structural_selectors:
        try:
            els = await page.query_selector_all(sel)
            for el in els:
                raw = (await el.inner_text()).strip()
                # Çok satırlıysa ilk satırı al
                first_line = raw.splitlines()[0].strip() if raw else ""
                cleaned = clean_price(first_line)
                if cleaned and cleaned not in seen and score_line(cleaned) >= 2:
                    items.append(cleaned)
                    seen.add(cleaned)
        except:
            continue
        if len(items) >= 15:
            break

    # 2. Fallback: tam sayfa metni satır satır
    if len(items) < 4:
        try:
            full = await page.inner_text("body")
            for line in full.splitlines():
                line = line.strip()
                if not line or line in seen:
                    continue
                cleaned = clean_price(line)
                if cleaned not in seen and score_line(cleaned) >= 3:  # Daha katı eşik
                    items.append(cleaned)
                    seen.add(cleaned)
                    if len(items) >= 15:
                        break
        except:
            pass

    return items[:12]


async def is_blocked_page(page) -> bool:
    """Cloudflare veya erişim engeli var mı?"""
    try:
        title = (await page.title()).lower()
        if any(k in title for k in ["cloudflare", "attention required", "just a moment", "access denied", "403", "404", "error"]):
            return True
        url = page.url.lower()
        if "cloudflare" in url or "captcha" in url:
            return True
        # Sayfa metninde cloudflare işaretleri
        try:
            body_text = (await page.inner_text("body"))[:500].lower()
            if any(k in body_text for k in ["cloudflare", "ray id", "checking your browser", "ddos protection", "visitor of this website", "owner of this website"]):
                return True
        except:
            pass
    except:
        pass
    return False


async def scrape_restaurant(page, r: dict) -> list:
    url = r.get("website", "").strip()
    if not url:
        return []

    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=12000)
        await page.wait_for_timeout(1500)
    except:
        return []

    if await is_blocked_page(page):
        return []

    # Menü sayfasına geç
    menu_url = await find_menu_url(page, url)
    if menu_url and menu_url != url:
        try:
            await page.goto(menu_url, wait_until="domcontentloaded", timeout=10000)
            await page.wait_for_timeout(1500)
            if await is_blocked_page(page):
                await page.goto(url, wait_until="domcontentloaded", timeout=8000)
                await page.wait_for_timeout(1000)
        except:
            pass

    items = await extract_items_from_page(page)

    # Yemek sinyali olan itemları tercih et, ama tüm skorlu itemları da koru
    food_items = [item for item in items if has_food_signal(item)]

    # Az item geldiyse ana sayfayı da dene
    if len(food_items) < 3 and menu_url:
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=10000)
            await page.wait_for_timeout(1000)
            items2 = await extract_items_from_page(page)
            food_items2 = [item for item in items2 if has_food_signal(item)]
            if len(food_items2) > len(food_items):
                food_items = food_items2
        except:
            pass

    # Gerçek yemek sinyali olanları önce koy, yetmezse diğerlerini ekle
    if len(food_items) >= 3:
        return food_items[:12]

    # Fallback: yemek sinyali olmasa bile scored itemlar (en az 5 farklı item varsa)
    all_scored = [item for item in items if score_line(item) >= 2]
    if len(all_scored) >= 5 and len(food_items) >= 1:
        return (food_items + [x for x in all_scored if x not in food_items])[:12]

    return []


async def run():
    input_path = "data/processed/istanbul.json"

    with open(input_path, encoding="utf-8") as f:
        restaurants = json.load(f)

    with_website = [r for r in restaurants if r.get("website")]
    print(f"[INFO] {len(with_website)} restoran websitesi taranacak...", flush=True)

    found = 0

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"],
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
            locale="tr-TR",
        )
        page = await context.new_page()
        await page.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', { get: () => undefined });"
        )

        for i, r in enumerate(with_website):
            name_safe = r["name"].encode("ascii", "replace").decode()
            print(f"[{i+1}/{len(with_website)}] {name_safe} | {r['website'][:50]}", flush=True)

            try:
                items = await asyncio.wait_for(
                    scrape_restaurant(page, r),
                    timeout=22
                )
            except asyncio.TimeoutError:
                print(f"  [TIMEOUT]", flush=True)
                try:
                    await page.close()
                    page = await context.new_page()
                    await page.add_init_script(
                        "Object.defineProperty(navigator, 'webdriver', { get: () => undefined });"
                    )
                except:
                    pass
                items = []
            except Exception as e:
                print(f"  [HATA] {str(e)[:60]}", flush=True)
                items = []

            if items and len(items) >= 3:
                for orig in restaurants:
                    if orig["id"] == r["id"]:
                        orig["menu_items"] = items
                        orig["menu_source"] = "website"
                        break
                found += 1
                print(f"  OK: {len(items)} item -> {[x.encode('ascii','replace').decode() for x in items[:3]]}", flush=True)
            else:
                print(f"  Bulunamadi ({len(items)} item)" + (f": {[x.encode('ascii','replace').decode() for x in items]}" if items else ""), flush=True)

            if (i + 1) % 10 == 0:
                with open(input_path, "w", encoding="utf-8") as f:
                    json.dump(restaurants, f, ensure_ascii=False, indent=2)
                print(f">>> KAYIT: {i+1}/{len(with_website)} | Bulunan: {found}", flush=True)

            await asyncio.sleep(1.5)

        await browser.close()

    with open(input_path, "w", encoding="utf-8") as f:
        json.dump(restaurants, f, ensure_ascii=False, indent=2)

    print(f"\n[OK] {found}/{len(with_website)} websiteden gercek menu bulundu", flush=True)
    print(f"[SONRAKI] python scripts/json_to_ts.py", flush=True)


if __name__ == "__main__":
    asyncio.run(run())
