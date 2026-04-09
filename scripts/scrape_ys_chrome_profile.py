# -*- coding: utf-8 -*-
"""
Gerçek Chrome profili kullanarak Yemeksepeti'nden menü çeker.
Kullanıcının mevcut oturumu ve cookie'leri kullanılır.

KULLANIM:
  1. Chrome'u KAPAT (Playwright aynı profili kullanamaz)
  2. python scripts/scrape_ys_chrome_profile.py
  3. Açılan tarayıcıda ilk sayfayı manuel geç (varsa challenge)
  4. Sonrasını otomatik yapar
"""

import json, re, asyncio, random
from urllib.parse import quote
from playwright.async_api import async_playwright

INPUT = "data/processed/istanbul.json"
CHROME_PROFILE = r"C:\Users\dedelus\AppData\Local\Google\Chrome\User Data"
SAVE_EVERY = 5

FOOD_WORDS = [
    "kebap","köfte","pilav","çorba","salata","börek","omlet","meze","pide",
    "tatlı","pasta","pizza","burger","sandviç","döner","ızgara","tava","güveç",
    "balık","tavuk","et","lahmacun","sushi","ramen","waffle","krep",
    "soup","salad","chicken","beef","fish","dessert","appetizer",
    "kahvaltı","serpme","menemen","gözleme","mantı",
]


def has_food(text: str) -> bool:
    t = text.lower()
    return any(f in t for f in FOOD_WORDS)


async def human_sleep(page, a=800, b=2000):
    await page.wait_for_timeout(random.randint(a, b))


async def human_scroll(page, n=3):
    for _ in range(n):
        await page.mouse.wheel(0, random.randint(200, 500))
        await page.wait_for_timeout(random.randint(200, 500))


async def get_menu(page) -> list:
    await human_sleep(page, 1500, 3000)
    await human_scroll(page, 4)

    items = []
    seen = set()

    selectors = [
        "[data-testid='menu-item-name']",
        "[class*='MenuItemName']",
        "[class*='menu-item-name']",
        "[class*='itemName']",
        "[class*='item-name']",
        "[class*='ProductName']",
        "[class*='MenuItem'] h3",
        "[class*='MenuItem'] h4",
        "[class*='menuItem'] span",
        "h3", "h4",
    ]

    for sel in selectors:
        try:
            els = await page.query_selector_all(sel)
            for el in els[:30]:
                raw = (await el.inner_text()).strip().splitlines()[0]
                if raw and 2 < len(raw) < 70 and raw not in seen:
                    items.append(raw)
                    seen.add(raw)
        except:
            continue
        if len(items) >= 15:
            break

    # Sadece yemek sinyali olanları döndür
    food_items = [x for x in items if has_food(x)]
    return food_items[:12]


async def find_and_open_restaurant(page, name: str, district: str) -> bool:
    query = f"{name} {district}".strip()
    url = f"https://www.yemeksepeti.com/search?term={quote(query)}"

    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=15000)
    except Exception as e:
        return False

    await human_sleep(page, 1500, 3000)

    # Sonuç kartlarını bul
    card_selectors = [
        "a[href*='/istanbul/']",
        "[class*='RestaurantCard'] a",
        "[class*='restaurant-card'] a",
        "[data-testid='restaurant-card'] a",
    ]

    name_words = set(name.lower().split())

    for sel in card_selectors:
        try:
            els = await page.query_selector_all(sel)
            for el in els[:5]:
                text = (await el.inner_text()).lower()
                href = await el.get_attribute("href") or ""
                # En az 1 isim kelimesi eşleşiyor mu?
                first_word = list(name_words)[0] if name_words else ""
                if (first_word and first_word in text) or (first_word and first_word in href.lower()):
                    if not href.startswith("http"):
                        href = "https://www.yemeksepeti.com" + href
                    await page.goto(href, wait_until="domcontentloaded", timeout=15000)
                    return True
        except:
            continue

    return False


async def run():
    with open(INPUT, encoding="utf-8") as f:
        restaurants = json.load(f)

    targets = [r for r in restaurants if not r.get("menu_items")]
    print(f"[INFO] {len(targets)} restoran hedefleniyor", flush=True)

    found = 0

    async with async_playwright() as p:
        # Kalıcı profil - cookie'leri saklar, challenge sonrası tekrar challenge yok
        context = await p.chromium.launch_persistent_context(
            user_data_dir="./tmp_ys_profile",
            headless=False,
            args=[
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars",
                "--window-size=1366,768",
                "--start-maximized",
            ],
            viewport={"width": 1366, "height": 768},
            locale="tr-TR",
            timezone_id="Europe/Istanbul",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        )

        page = await context.new_page()

        # Manuel geçiş için ilk sayfaya git
        print("[INFO] Yemeksepeti açılıyor... (challenge varsa manuel çöz)", flush=True)
        await page.goto("https://www.yemeksepeti.com/istanbul", wait_until="domcontentloaded", timeout=20000)
        print("[INFO] 8 saniye bekleniyor - gerekirse tarayıcıda challenge çöz...", flush=True)
        await page.wait_for_timeout(8000)

        title = await page.title()
        print(f"[INFO] Sayfa: {title[:60]}", flush=True)

        if "denied" in title.lower() or "challenge" in title.lower():
            print("[UYARI] Erişim engeli! Tarayıcıda manuel olarak geç, 30sn bekleniyor...", flush=True)
            await page.wait_for_timeout(30000)

        print("[INFO] Tarama başlıyor...", flush=True)

        for i, r in enumerate(targets[:150]):
            name_safe = r["name"].encode("ascii", "replace").decode()
            print(f"[{i+1}/{len(targets)}] {name_safe}", flush=True)

            try:
                ok = await asyncio.wait_for(
                    find_and_open_restaurant(page, r["name"], r.get("district", "")),
                    timeout=25
                )

                if not ok:
                    print(f"  Bulunamadi", flush=True)
                    continue

                items = await asyncio.wait_for(get_menu(page), timeout=15)

                if items and len(items) >= 2:
                    for orig in restaurants:
                        if orig["id"] == r["id"]:
                            orig["menu_items"] = items
                            orig["menu_source"] = "yemeksepeti"
                            break
                    found += 1
                    print(f"  OK: {len(items)} item -> {[x.encode('ascii','replace').decode() for x in items[:3]]}", flush=True)
                else:
                    print(f"  Menü bulunamadı", flush=True)

            except asyncio.TimeoutError:
                print(f"  TIMEOUT", flush=True)
            except Exception as e:
                print(f"  HATA: {str(e)[:80]}", flush=True)

            if (i + 1) % SAVE_EVERY == 0:
                with open(INPUT, "w", encoding="utf-8") as f:
                    json.dump(restaurants, f, ensure_ascii=False, indent=2)
                total = sum(1 for r2 in restaurants if r2.get("menu_items"))
                print(f">>> KAYIT | Yeni: {found} | Toplam: {total}/453", flush=True)

            await human_sleep(page, 2500, 5000)

        await context.close()

    with open(INPUT, "w", encoding="utf-8") as f:
        json.dump(restaurants, f, ensure_ascii=False, indent=2)

    total = sum(1 for r2 in restaurants if r2.get("menu_items"))
    print(f"\n[SONUÇ] {found} yeni menü | Toplam: {total}/453", flush=True)


if __name__ == "__main__":
    asyncio.run(run())
