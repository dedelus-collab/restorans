# -*- coding: utf-8 -*-
"""
new_restaurants.json'daki restoranların gerçek puan ve yorum sayısını
Google Maps'ten Playwright ile çeker.
"""
import json, re, asyncio, sys
sys.stdout.reconfigure(encoding="utf-8")

NEW_FILE = "data/new_restaurants.json"

async def scrape_place(page, r: dict) -> dict:
    name = r["name"]
    lat  = r.get("lat")
    lng  = r.get("lng")

    query = f"{name} istanbul"
    if lat and lng:
        url = f"https://www.google.com/maps/search/{query}/@{lat},{lng},17z"
    else:
        url = f"https://www.google.com/maps/search/{query}"

    result = {"avgRating": None, "reviewCount": None}

    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=18000)
        await page.wait_for_timeout(3000)

        full_text = await page.inner_text("body")

        # --- PUAN ---
        spans = await page.query_selector_all("span")
        for span in spans[:200]:
            try:
                t = (await span.inner_text()).strip().replace(",", ".")
                val = float(t)
                if 1.0 <= val <= 5.0 and "." in t:
                    result["avgRating"] = round(val, 1)
                    break
            except:
                pass

        # --- YORUM SAYISI ---
        m = re.search(r"\(([0-9][0-9.,\s]{0,8})\)", full_text)
        if m:
            num = re.sub(r"[^0-9]", "", m.group(1))
            try:
                cnt = int(num)
                if 1 <= cnt <= 100000:
                    result["reviewCount"] = cnt
            except:
                pass

    except Exception as e:
        print(f"  HATA ({name}): {str(e)[:60]}")

    return result


async def run():
    with open(NEW_FILE, encoding="utf-8") as f:
        data = json.load(f)

    targets = [r for r in data if r.get("avgRating") is None or r.get("reviewCount") in (None, 0)]
    print(f"Taranacak: {len(targets)} restoran\n")

    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"],
        )
        ctx = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36",
            locale="tr-TR",
        )
        page = await ctx.new_page()
        await page.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', { get: () => undefined });"
        )

        for i, r in enumerate(targets):
            print(f"[{i+1}/{len(targets)}] {r['name']}... ", end="", flush=True)
            scraped = await scrape_place(page, r)

            # JSON'daki ilgili kaydı güncelle
            for rec in data:
                if rec["slug"] == r["slug"]:
                    if scraped["avgRating"] is not None:
                        rec["avgRating"] = scraped["avgRating"]
                    if scraped["reviewCount"] is not None:
                        rec["reviewCount"] = scraped["reviewCount"]
                    break

            rating_str = str(scraped["avgRating"]) if scraped["avgRating"] else "?"
            review_str = str(scraped["reviewCount"]) if scraped["reviewCount"] else "?"
            print(f"puan={rating_str}  yorumlar={review_str}")

            await asyncio.sleep(2.5)

        await browser.close()

    with open(NEW_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    found = sum(1 for r in data if r.get("avgRating") is not None and r.get("district") == "Adalar")
    print(f"\n[OK] {NEW_FILE} güncellendi. Adalar puanı olan: {found}/12")


asyncio.run(run())
