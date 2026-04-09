# -*- coding: utf-8 -*-
"""
Gercek menu itemlarini ceker:
1. Restoranin kendi websitesinden
2. Google Maps menu sekmesinden
3. Yoksa Groq ile mutfak turune gore uretir (fallback)

Kullanim: python scripts/scrape_menus.py
"""

import json
import re
import time
import asyncio
from playwright.async_api import async_playwright
from groq import Groq

GROQ_API_KEYS = [
    "os.environ.get("GROQ_API_KEY_1", "")",
    "os.environ.get("GROQ_API_KEY_2", "")",
]
_key_index = 0

def get_groq():
    return Groq(api_key=GROQ_API_KEYS[_key_index % len(GROQ_API_KEYS)])


async def scrape_website_menu(page, url: str) -> list:
    """Restoranin kendi sitesinden menu isimlerini ceker."""
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=10000)
        await page.wait_for_timeout(2000)

        # Menü sayfasını bul
        menu_links = await page.query_selector_all('a[href*="menu"], a[href*="munu"], a[href*="yemek"]')
        if menu_links:
            href = await menu_links[0].get_attribute("href")
            if href and not href.startswith("http"):
                from urllib.parse import urljoin
                href = urljoin(url, href)
            if href:
                await page.goto(href, wait_until="domcontentloaded", timeout=8000)
                await page.wait_for_timeout(1500)

        # Sayfa metninden yemek isimlerini topla
        text = await page.inner_text("body")
        lines = [l.strip() for l in text.splitlines() if l.strip()]

        # Kısa satırlar genellikle menü öğeleridir (5-50 karakter)
        items = []
        for line in lines:
            if 4 < len(line) < 50 and not any(c in line for c in ["http", "@", "©", "Tel:", "Adres"]):
                # Fiyat içeriyorsa temizle
                clean = re.sub(r'\d+[\.,]\d*\s*(TL|₺|tl)?', '', line).strip()
                if len(clean) > 3:
                    items.append(clean)

        # En sık geçenleri al (muhtemelen menü başlıkları)
        return list(dict.fromkeys(items))[:10]
    except Exception:
        return []


async def scrape_gmaps_menu(page, r: dict) -> list:
    """Google Maps menü sekmesinden urun isimlerini ceker."""
    name = r.get("name", "")
    lat = r.get("lat")
    lng = r.get("lng")

    query = name.replace(" ", "+") + "+istanbul+menu"
    url = f"https://www.google.com/maps/search/{query}"
    if lat and lng:
        url = f"https://www.google.com/maps/search/{name.replace(' ', '+')}/@{lat},{lng},17z"

    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=10000)
        await page.wait_for_timeout(2000)

        # Menü sekmesini bul
        menu_btn = None
        for selector in ['[data-item-id*="menu"]', 'button:has-text("Menü")', 'a:has-text("Menü")']:
            try:
                menu_btn = await page.query_selector(selector)
                if menu_btn:
                    break
            except:
                pass

        if menu_btn:
            await menu_btn.click()
            await page.wait_for_timeout(2000)

        # Menü öğelerini çek
        items = []
        for selector in ['[class*="menu-item"]', '[class*="dish"]', 'h3', 'h4']:
            elements = await page.query_selector_all(selector)
            for el in elements[:15]:
                text = (await el.inner_text()).strip()
                if 3 < len(text) < 60:
                    items.append(text)

        if not items:
            # Genel metin taraması
            full_text = await page.inner_text("body")
            lines = [l.strip() for l in full_text.splitlines() if 4 < len(l.strip()) < 50]
            items = lines[:10]

        return list(dict.fromkeys(items))[:10]
    except Exception:
        return []


def groq_fallback(r: dict) -> list:
    global _key_index
    cuisine = r.get("cuisine") or "Türk mutfağı"
    name = r.get("name", "")
    sf = r.get("special_features") or {}
    existing = sf.get("signatureDishes") or []

    prompt = f"""{name} restoranı | Mutfak: {cuisine} | Bilinen: {', '.join(existing)}
Bu restoranın menüsünde tipik olarak bulunan 6-8 yemek ismini listele. Sadece JSON array:
["yemek1", "yemek2", "yemek3", "yemek4", "yemek5", "yemek6"]"""

    for attempt in range(len(GROQ_API_KEYS) * 2):
        try:
            c = get_groq()
            resp = c.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=120, temperature=0.3,
            )
            text = resp.choices[0].message.content.strip()
            start, end = text.find("["), text.rfind("]") + 1
            if start >= 0 and end > start:
                items = json.loads(text[start:end])
                return [i for i in items if isinstance(i, str)][:8]
        except Exception as e:
            if "429" in str(e):
                _key_index += 1
                time.sleep(10)
            else:
                break
    return []


async def run():
    input_path = "data/processed/istanbul.json"

    with open(input_path, encoding="utf-8") as f:
        restaurants = json.load(f)

    # Sadece menu_items olmayan veya az olanları işle
    todo = [r for r in restaurants if not r.get("menu_items") or len(r.get("menu_items", [])) < 3]
    total = len(todo)
    print(f"[INFO] {total} restoran icin gercek menu cekiliyor...", flush=True)

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

        for i, r in enumerate(todo):
            name_safe = r["name"].encode("ascii", "replace").decode()
            print(f"[{i+1}/{total}] {name_safe}", flush=True)

            items = []

            # 1. Kendi websitesi
            if r.get("website") and not items:
                try:
                    items = await asyncio.wait_for(scrape_website_menu(page, r["website"]), timeout=15)
                    if items:
                        print(f"  WEBSITE: {len(items)} item", flush=True)
                except:
                    pass

            # 2. Google Maps menü
            if not items:
                try:
                    items = await asyncio.wait_for(scrape_gmaps_menu(page, r), timeout=18)
                    if items:
                        print(f"  GMAPS: {len(items)} item", flush=True)
                except:
                    try:
                        await page.close()
                        page = await context.new_page()
                    except:
                        pass

            # JSON'daki orijinal kaydı güncelle
            if items:
                for orig in restaurants:
                    if orig["id"] == r["id"]:
                        orig["menu_items"] = items[:8]
                        break
            else:
                print(f"  ATLANDI", flush=True)

            if (i + 1) % 15 == 0:
                with open(input_path, "w", encoding="utf-8") as f:
                    json.dump(restaurants, f, ensure_ascii=False, indent=2)
                done = sum(1 for r in restaurants if r.get("menu_items"))
                print(f">>> KAYIT: {i+1}/{total} | Menu olan: {done}/453", flush=True)

            await asyncio.sleep(1)

        await browser.close()

    with open(input_path, "w", encoding="utf-8") as f:
        json.dump(restaurants, f, ensure_ascii=False, indent=2)

    done = sum(1 for r in restaurants if r.get("menu_items"))
    print(f"\n[OK] {done}/453 restoran menu ile tamamlandi", flush=True)
    print("[SONRAKI] python scripts/json_to_ts.py", flush=True)


if __name__ == "__main__":
    asyncio.run(run())
