# -*- coding: utf-8 -*-
"""
Yemeksepeti'nden insan gibi davranarak menü çeker.
- playwright-stealth ile bot tespitini engeller
- Mouse hareketi, scroll, rastgele gecikmeler
- Cloudflare bypass için doğal navigasyon
"""

import json
import re
import asyncio
import random
import time
from urllib.parse import quote
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

INPUT  = "data/processed/istanbul.json"
SAVE_EVERY = 5

# --- İnsan benzeri yardımcı fonksiyonlar ---

async def human_sleep(page, min_ms=800, max_ms=2500):
    await page.wait_for_timeout(random.randint(min_ms, max_ms))

async def human_scroll(page, steps=3):
    for _ in range(steps):
        delta = random.randint(200, 600)
        await page.mouse.wheel(0, delta)
        await page.wait_for_timeout(random.randint(300, 700))

async def human_move(page):
    """Rastgele birkaç mouse hareketi yap."""
    vp = page.viewport_size or {"width": 1280, "height": 800}
    for _ in range(random.randint(2, 5)):
        x = random.randint(100, vp["width"] - 100)
        y = random.randint(100, vp["height"] - 100)
        await page.mouse.move(x, y)
        await page.wait_for_timeout(random.randint(80, 200))

async def is_cloudflare(page) -> bool:
    try:
        title = (await page.title()).lower()
        if any(k in title for k in ["cloudflare", "just a moment", "attention required"]):
            return True
        body = (await page.inner_text("body"))[:300].lower()
        if any(k in body for k in ["cloudflare", "ray id", "checking your browser"]):
            return True
    except:
        pass
    return False

async def wait_for_cloudflare(page, timeout=20):
    """Cloudflare challenge geçene kadar bekle."""
    for _ in range(timeout):
        if not await is_cloudflare(page):
            return True
        await page.wait_for_timeout(1000)
    return False

# --- Menü çekme ---

async def get_menu_from_restaurant_page(page) -> list:
    """Açık olan restoran sayfasından menü itemlarını çek."""
    items = []
    seen = set()

    await human_sleep(page, 1500, 3000)
    await human_scroll(page, steps=4)
    await human_move(page)

    # Yemeksepeti menü item selectorları
    selectors = [
        "[data-testid='menu-item-name']",
        "[class*='MenuItemName']",
        "[class*='menu-item-name']",
        "[class*='itemName']",
        "[class*='item-name']",
        "[class*='product-name']",
        "[class*='ProductName']",
        "h3[class*='name']",
        "h4[class*='name']",
        # Genel fallback
        "[class*='MenuItem'] h3",
        "[class*='MenuItem'] h4",
        "[class*='menuItem'] span",
        "[class*='food'] h3",
        "[class*='food'] h4",
    ]

    for sel in selectors:
        try:
            els = await page.query_selector_all(sel)
            for el in els[:20]:
                text = (await el.inner_text()).strip()
                if text and 2 < len(text) < 80 and text not in seen:
                    items.append(text)
                    seen.add(text)
        except:
            continue
        if len(items) >= 10:
            break

    # Fallback: tüm h3/h4 - kategori ve öğe karışımı
    if len(items) < 3:
        for sel in ["h3", "h4"]:
            try:
                els = await page.query_selector_all(sel)
                for el in els[:30]:
                    text = (await el.inner_text()).strip()
                    if text and 2 < len(text) < 60 and text not in seen:
                        # Navigasyon değil mi?
                        if not any(nav in text.lower() for nav in [
                            "anasayfa", "iletişim", "hakkında", "sepet",
                            "giriş", "kayıt", "profil", "kampanya",
                            "restaurant", "restoran", "kargo", "teslimat"
                        ]):
                            items.append(text)
                            seen.add(text)
            except:
                continue

    return items[:12]


async def search_restaurant_on_ys(page, name: str, district: str = "") -> bool:
    """
    Yemeksepeti'nde restoranı ara ve sayfasına git.
    True döner = sayfa açıldı.
    """
    # Arama URL'i
    query = f"{name} {district}".strip()
    search_url = f"https://www.yemeksepeti.com/search?term={quote(query)}&city=istanbul"

    try:
        await page.goto(search_url, wait_until="domcontentloaded", timeout=18000)
    except:
        return False

    if await is_cloudflare(page):
        if not await wait_for_cloudflare(page, timeout=25):
            return False

    await human_sleep(page, 1200, 2500)
    await human_move(page)

    # İlk restoran sonucunu bul
    result_selectors = [
        "[data-testid='restaurant-card']",
        "[class*='RestaurantCard']",
        "[class*='restaurant-card']",
        "a[href*='/istanbul/']",
        "a[href*='/menu']",
    ]

    for sel in result_selectors:
        try:
            els = await page.query_selector_all(sel)
            for el in els[:3]:
                # İsim uyumu kontrolü
                el_text = (await el.inner_text()).lower()
                name_lower = name.lower()
                # İlk kelime eşleşiyor mu?
                first_word = name_lower.split()[0]
                if first_word in el_text or name_lower[:8] in el_text:
                    href = await el.get_attribute("href")
                    if href:
                        if not href.startswith("http"):
                            href = "https://www.yemeksepeti.com" + href
                        # Mouse ile tıkla (insan gibi)
                        box = await el.bounding_box()
                        if box:
                            await page.mouse.move(
                                box["x"] + box["width"] / 2 + random.randint(-5, 5),
                                box["y"] + box["height"] / 2 + random.randint(-5, 5)
                            )
                            await page.wait_for_timeout(random.randint(200, 500))
                            await page.mouse.click(
                                box["x"] + box["width"] / 2,
                                box["y"] + box["height"] / 2
                            )
                        else:
                            await page.goto(href, wait_until="domcontentloaded", timeout=15000)
                        return True
        except:
            continue

    return False


async def run():
    with open(INPUT, encoding="utf-8") as f:
        restaurants = json.load(f)

    # Menüsü olmayan restoranları hedefle
    targets = [r for r in restaurants if not r.get("menu_items")]
    print(f"[INFO] {len(targets)} restoran hedefleniyor...", flush=True)

    found = 0
    errors = 0

    async with async_playwright() as p:
        # Gerçek tarayıcı gibi görün
        browser = await p.chromium.launch(
            headless=False,  # headless=False Cloudflare'i daha iyi geçer
            args=[
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars",
                "--window-size=1280,800",
            ],
        )

        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            locale="tr-TR",
            timezone_id="Europe/Istanbul",
            geolocation={"latitude": 41.0082, "longitude": 28.9784},
            permissions=["geolocation"],
            java_script_enabled=True,
            accept_downloads=False,
            extra_http_headers={
                "Accept-Language": "tr-TR,tr;q=0.9,en;q=0.8",
                "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
            },
        )

        page = await context.new_page()
        await Stealth().apply_stealth_async(page)

        # Önce ana sayfaya git - çerez ve session kur
        print("[INFO] Ana sayfaya gidiliyor...", flush=True)
        try:
            await page.goto("https://www.yemeksepeti.com/istanbul", wait_until="domcontentloaded", timeout=20000)
        except:
            await page.goto("https://www.yemeksepeti.com", wait_until="domcontentloaded", timeout=20000)

        if await is_cloudflare(page):
            print("[WARN] Cloudflare engeli - 30sn bekleniyor...", flush=True)
            solved = await wait_for_cloudflare(page, timeout=30)
            if not solved:
                print("[HATA] Cloudflare geçilemedi, çıkılıyor.", flush=True)
                await browser.close()
                return

        await human_sleep(page, 2000, 4000)
        await human_scroll(page, steps=3)
        await human_sleep(page, 1000, 2000)

        print("[INFO] Tarama başlıyor...", flush=True)

        for i, r in enumerate(targets[:100]):  # İlk 100 ile başla
            name_safe = r["name"].encode("ascii", "replace").decode()
            district = r.get("district", "")
            print(f"[{i+1}] {name_safe} | {district}", flush=True)

            try:
                ok = await asyncio.wait_for(
                    search_restaurant_on_ys(page, r["name"], district),
                    timeout=30
                )

                if not ok:
                    print(f"  Bulunamadi", flush=True)
                    errors += 1
                    if errors >= 5:
                        print("[WARN] Cok fazla hata - Cloudflare engeli olabilir, duraklatiliyor", flush=True)
                        await human_sleep(page, 10000, 20000)
                        errors = 0
                    continue

                if await is_cloudflare(page):
                    print(f"  Cloudflare engeli!", flush=True)
                    await wait_for_cloudflare(page, timeout=25)
                    continue

                items = await get_menu_from_restaurant_page(page)

                if items and len(items) >= 2:
                    for orig in restaurants:
                        if orig["id"] == r["id"]:
                            orig["menu_items"] = items
                            orig["menu_source"] = "yemeksepeti"
                            break
                    found += 1
                    print(f"  OK: {len(items)} item -> {[x.encode('ascii','replace').decode() for x in items[:3]]}", flush=True)
                    errors = 0
                else:
                    print(f"  Sayfa acildi ama menu bulunamadi", flush=True)

            except asyncio.TimeoutError:
                print(f"  TIMEOUT", flush=True)
                try:
                    await page.close()
                    page = await context.new_page()
                    await Stealth().apply_stealth_async(page)
                    await page.goto("https://www.yemeksepeti.com/istanbul", wait_until="domcontentloaded", timeout=15000)
                    await human_sleep(page, 2000, 4000)
                except:
                    pass
            except Exception as e:
                print(f"  HATA: {str(e)[:80]}", flush=True)

            # Kaydet
            if (i + 1) % SAVE_EVERY == 0:
                with open(INPUT, "w", encoding="utf-8") as f:
                    json.dump(restaurants, f, ensure_ascii=False, indent=2)
                total_menu = sum(1 for r2 in restaurants if r2.get("menu_items"))
                print(f">>> KAYIT: {i+1}/{len(targets)} | Yeni: {found} | Toplam menulu: {total_menu}", flush=True)

            # İnsan gibi bekleme - rastgele aralık
            await human_sleep(page, 2000, 5000)

        await browser.close()

    with open(INPUT, "w", encoding="utf-8") as f:
        json.dump(restaurants, f, ensure_ascii=False, indent=2)

    total_menu = sum(1 for r2 in restaurants if r2.get("menu_items"))
    print(f"\n[SONUÇ] {found} yeni menü bulundu | Toplam menulu: {total_menu}/453", flush=True)


if __name__ == "__main__":
    asyncio.run(run())
