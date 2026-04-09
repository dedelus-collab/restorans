# -*- coding: utf-8 -*-
"""
Yemeksepeti'nden restoran menülerini çeker.
Restoran adı + mahalle ile arama yapıp menü öğelerini alır.

Kullanim: python scripts/scrape_yemeksepeti.py
"""

import json
import re
import asyncio
from playwright.async_api import async_playwright

YEMEKSEPETI_BASE = "https://www.yemeksepeti.com/istanbul"

NOISE = {
    "sepete ekle", "favorilere ekle", "paylaş", "filtrele", "sırala",
    "kategori", "indirim", "kampanya", "ücretsiz", "teslimat", "min",
    "adet", "porsiyon", "ekstra", "seçenekler", "kişi", "kcal",
    "add to cart", "favorites", "share", "filter", "sort",
}


def clean_item(text: str) -> str:
    # Fiyat ve parantez içini temizle
    text = re.sub(r'\d+[.,]\d*\s*(TL|₺)?', '', text)
    text = re.sub(r'\(.*?\)', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def looks_like_food(text: str) -> bool:
    if len(text) < 3 or len(text) > 60:
        return False
    lower = text.lower()
    if any(n in lower for n in NOISE):
        return False
    # Sadece sayı/sembol ise atla
    if re.match(r'^[\d\s₺TL.,+-]+$', text):
        return False
    return True


async def search_restaurant(page, name: str, neighborhood: str) -> str | None:
    """Yemeksepeti'nde restoran arar, URL'yi döner."""
    # Ana sayfadan arama yap
    try:
        await page.goto("https://www.yemeksepeti.com/tr-TR/istanbul", wait_until="domcontentloaded", timeout=12000)
        await page.wait_for_timeout(2000)

        # Arama kutusunu bul
        search_box = await page.query_selector('input[type="search"], input[placeholder*="ara"], input[name="q"]')
        if search_box:
            await search_box.fill(name)
            await page.wait_for_timeout(1500)
            # Sonuçlar otomatik geliyorsa al
            links = await page.query_selector_all('a[href*="restaurant"], a[href*="restoran"]')
            for link in links:
                href = await link.get_attribute("href") or ""
                if href and len(href) > 10:
                    return "https://www.yemeksepeti.com" + href if href.startswith("/") else href

        # Alternatif: doğrudan arama URL'si
        query = name.replace(" ", "+")
        for search_url in [
            f"https://www.yemeksepeti.com/tr-TR/istanbul/ara?searchTerm={query}",
            f"https://www.yemeksepeti.com/istanbul/search?q={query}",
            f"https://www.yemeksepeti.com/tr-TR/search?q={query}&city=istanbul",
        ]:
            try:
                await page.goto(search_url, wait_until="domcontentloaded", timeout=10000)
                await page.wait_for_timeout(1500)
                links = await page.query_selector_all("a")
                for link in links:
                    href = await link.get_attribute("href") or ""
                    link_text = (await link.inner_text()).strip().lower()
                    name_lower = name.lower()[:10]
                    if href and (name_lower in link_text or name_lower in href.lower()):
                        if href.startswith("/"):
                            href = "https://www.yemeksepeti.com" + href
                        return href
            except:
                continue
    except:
        pass
    return None


async def scrape_menu(page, restaurant_url: str) -> list:
    """Restoran sayfasından menü öğelerini çeker."""
    try:
        await page.goto(restaurant_url, wait_until="domcontentloaded", timeout=12000)
        await page.wait_for_timeout(2500)

        items = []
        seen = set()

        # Menü öğesi selektörleri
        selectors = [
            '[data-testid*="product-name"]',
            '[class*="product-name"]',
            '[class*="menu-item-name"]',
            '[class*="item-name"]',
            'h3[class*="name"]',
            'h4[class*="name"]',
            'span[class*="name"]',
            'p[class*="name"]',
        ]

        for sel in selectors:
            els = await page.query_selector_all(sel)
            for el in els:
                text = (await el.inner_text()).strip()
                cleaned = clean_item(text)
                if cleaned and cleaned not in seen and looks_like_food(cleaned):
                    items.append(cleaned)
                    seen.add(cleaned)
            if len(items) >= 5:
                break

        # Fallback: sayfa metninden kısa satırlar
        if len(items) < 3:
            full = await page.inner_text("body")
            for line in full.splitlines():
                line = clean_item(line.strip())
                if line and line not in seen and looks_like_food(line) and 3 < len(line) < 50:
                    items.append(line)
                    seen.add(line)
                    if len(items) >= 12:
                        break

        return items[:12]
    except:
        return []


async def run():
    input_path = "data/processed/istanbul.json"

    with open(input_path, encoding="utf-8") as f:
        restaurants = json.load(f)

    total = len(restaurants)
    found = 0
    print(f"[INFO] {total} restoran icin Yemeksepeti menu taranacak...", flush=True)

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

        for i, r in enumerate(restaurants):
            # Zaten gerçek menüsü varsa atla
            if r.get("menu_source") == "yemeksepeti" or len(r.get("menu_items") or []) >= 5:
                continue

            name_safe = r["name"].encode("ascii", "replace").decode()
            neighborhood = (r.get("neighborhood") or "").encode("ascii", "replace").decode()
            print(f"[{i+1}/{total}] {name_safe}", flush=True)

            items = []
            try:
                # 1. Restoran URL'sini bul
                rest_url = await asyncio.wait_for(
                    search_restaurant(page, r["name"], r.get("neighborhood") or ""),
                    timeout=15
                )

                if rest_url:
                    print(f"  Bulundu: {rest_url[:60]}", flush=True)
                    # 2. Menüyü çek
                    items = await asyncio.wait_for(
                        scrape_menu(page, rest_url),
                        timeout=18
                    )
                else:
                    print(f"  Yemeksepeti'nde bulunamadi", flush=True)

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

            except Exception as e:
                print(f"  [HATA] {str(e)[:50]}", flush=True)

            if items and len(items) >= 3:
                for orig in restaurants:
                    if orig["id"] == r["id"]:
                        orig["menu_items"] = items
                        orig["menu_source"] = "yemeksepeti"
                        break
                found += 1
                print(f"  OK: {len(items)} item | {items[:3]}", flush=True)
            else:
                print(f"  Menu bulunamadi ({len(items)} item)", flush=True)

            if (i + 1) % 15 == 0:
                with open(input_path, "w", encoding="utf-8") as f:
                    json.dump(restaurants, f, ensure_ascii=False, indent=2)
                print(f">>> KAYIT: {i+1}/{total} | Bulunan: {found}", flush=True)

            await asyncio.sleep(2)

        await browser.close()

    with open(input_path, "w", encoding="utf-8") as f:
        json.dump(restaurants, f, ensure_ascii=False, indent=2)

    print(f"\n[OK] {found}/{total} restoran icin Yemeksepeti menusu bulundu", flush=True)
    print("[SONRAKI] python scripts/json_to_ts.py", flush=True)


if __name__ == "__main__":
    asyncio.run(run())
