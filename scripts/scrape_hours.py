# -*- coding: utf-8 -*-
"""
Google Maps'ten calisma saatlerini ceker.
Saatler acilir menude oldugu icin ayri script gerekiyor.

Kullanim:
  python scripts/scrape_hours.py --batch 453
"""

import json
import re
import asyncio
import argparse
from playwright.async_api import async_playwright

DAYS_TR = ["Pazartesi", "Sali", "Carsamba", "Persembe", "Cuma", "Cumartesi", "Pazar"]
DAYS_EN = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


async def get_hours(page, restaurant: dict) -> str:
    name = restaurant["name"]
    lat = restaurant.get("lat")
    lng = restaurant.get("lng")

    query = f"{name} istanbul"
    if lat and lng:
        url = f"https://www.google.com/maps/search/{query}/@{lat},{lng},17z"
    else:
        url = f"https://www.google.com/maps/search/{query}"

    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=15000)
        await page.wait_for_timeout(2000)

        # Saat butonuna tikla (acilir panel)
        hour_selectors = [
            'button[data-item-id="oh"]',
            '[aria-label*="saat"]',
            '[aria-label*:"hour"]',
            'div[jsaction*="openhours"]',
        ]
        for sel in hour_selectors:
            btn = await page.query_selector(sel)
            if btn:
                await btn.click()
                await page.wait_for_timeout(1000)
                break

        full_text = await page.inner_text("body")

        # Saat pattern: "09:00 - 22:00" veya "09.00–22.00"
        patterns = [
            r"\d{2}:\d{2}\s*[–\-]\s*\d{2}:\d{2}",
            r"\d{2}\.\d{2}\s*[–\-]\s*\d{2}\.\d{2}",
            r"\d{1,2}:\d{2}\s*(AM|PM)\s*[–\-]\s*\d{1,2}:\d{2}\s*(AM|PM)",
        ]
        for pat in patterns:
            m = re.search(pat, full_text)
            if m:
                hours = m.group(0).strip()
                # Normalize
                hours = hours.replace(".", ":").replace("–", "-")
                return f"Mo-Su {hours}"

        # 7/24 kontrol
        if "7/24" in full_text or "24 saat" in full_text.lower():
            return "Mo-Su 00:00-24:00"

    except Exception as e:
        name_safe = name.encode("ascii", "replace").decode()
        print(f"  [ERROR] {name_safe}: {str(e)[:60]}")

    return ""


async def run(input_path: str, output_path: str, batch_size: int):
    with open(input_path, encoding="utf-8") as f:
        restaurants = json.load(f)

    to_scrape = [r for r in restaurants if not r.get("opening_hours")][:batch_size]
    print(f"[INFO] {len(to_scrape)} restoran saat eksik, isleniyor...")

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

        for i, r in enumerate(to_scrape):
            name_safe = r["name"].encode("ascii", "replace").decode()
            print(f"[{i+1}/{len(to_scrape)}] {name_safe}")

            hours = await get_hours(page, r)

            for orig in restaurants:
                if orig["id"] == r["id"]:
                    if hours:
                        orig["opening_hours"] = hours
                        print(f"  -> {hours}")
                    else:
                        print(f"  -> bulunamadi")
                    break

            await asyncio.sleep(2)

        await browser.close()

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(restaurants, f, ensure_ascii=False, indent=2)

    has_hours = sum(1 for r in restaurants if r.get("opening_hours"))
    print(f"\n[OK] Saat dolu: {has_hours}/{len(restaurants)} -> {output_path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/processed/istanbul.json")
    parser.add_argument("--output", default="data/processed/istanbul.json")
    parser.add_argument("--batch", type=int, default=453)
    args = parser.parse_args()
    asyncio.run(run(args.input, args.output, args.batch))


if __name__ == "__main__":
    main()
