# -*- coding: utf-8 -*-
"""
Google Maps'ten puan, mutfak, saat ve tag ceker.

Kullanim:
  python scripts/scrape_ratings.py --batch 453
  python scripts/scrape_ratings.py --mode missing  (sadece eksik alanlari doldur)
"""

import json
import re
import asyncio
import argparse
from playwright.async_api import async_playwright

CUISINE_KEYWORDS = [
    "turk", "italian", "pizza", "burger", "kebab", "balik", "fish", "seafood",
    "sushi", "chinese", "mexican", "indian", "greek", "french", "american",
    "vegetarian", "vegan", "cafe", "kahvalti", "breakfast", "steakhouse",
    "meze", "meyhane", "lokanta", "fastfood", "sandvic", "donerci", "pide",
    "lahmacun", "tantuni", "cig kofte", "iskender", "ocakbasi",
]

TAG_MAP = {
    "romantik": ["romantik", "romantic", "candle", "intimate"],
    "manzarali": ["manzara", "view", "bogazici", "bosphorus", "deniz", "sea"],
    "teras": ["teras", "terrace", "outdoor", "bahce", "garden"],
    "aile": ["aile", "family", "cocuk", "child"],
    "canli muzik": ["canli muzik", "live music", "muzik", "music"],
    "vegan": ["vegan", "vegetarian", "vejetaryen"],
    "wifi": ["wifi", "wi-fi", "internet"],
    "rezervasyon": ["rezervasyon", "reservation"],
}


async def scrape_place(page, restaurant: dict) -> dict:
    name = restaurant["name"]
    lat = restaurant.get("lat")
    lng = restaurant.get("lng")

    query = f"{name} istanbul"
    if lat and lng:
        url = f"https://www.google.com/maps/search/{query}/@{lat},{lng},17z"
    else:
        url = f"https://www.google.com/maps/search/{query}"

    result = {
        "rating": restaurant.get("avg_rating"),
        "review_count": restaurant.get("review_count", 0),
        "cuisine": restaurant.get("cuisine", ""),
        "opening_hours": restaurant.get("opening_hours", ""),
        "tags": restaurant.get("tags", []),
        "phone": restaurant.get("phone", ""),
        "website": restaurant.get("website", ""),
    }

    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=15000)
        await page.wait_for_timeout(2500)

        full_text = await page.inner_text("body")
        full_lower = full_text.lower()

        # --- PUAN ---
        if not result["rating"] or result["rating"] == 0:
            spans = await page.query_selector_all("span")
            for span in spans[:150]:
                try:
                    t = (await span.inner_text()).strip().replace(",", ".")
                    val = float(t)
                    if 1.0 <= val <= 5.0:
                        result["rating"] = round(val, 1)
                        break
                except:
                    pass

        # --- YORUM SAYISI ---
        if not result["review_count"]:
            m = re.search(r"\(([0-9][0-9.,\s]{0,8})\)", full_text)
            if m:
                num = re.sub(r"[^0-9]", "", m.group(1))
                try:
                    result["review_count"] = int(num)
                except:
                    pass

        # --- MUTFAK ---
        if not result["cuisine"]:
            for kw in CUISINE_KEYWORDS:
                if kw in full_lower:
                    result["cuisine"] = kw.title()
                    break

        # --- CALISMA SAATLERI ---
        if not result["opening_hours"]:
            patterns = [
                r"\d{2}:\d{2}\s*[–-]\s*\d{2}:\d{2}",
                r"\d{1,2}:\d{2}\s*(AM|PM)\s*[–-]\s*\d{1,2}:\d{2}\s*(AM|PM)",
            ]
            for pat in patterns:
                m = re.search(pat, full_text)
                if m:
                    result["opening_hours"] = m.group(0).strip()
                    break

        # --- TELEFON ---
        if not result["phone"]:
            m = re.search(r"(\+90[\s\-]?\d{3}[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2})", full_text)
            if m:
                result["phone"] = m.group(1)

        # --- TAGS ---
        existing_tags = set(result["tags"])
        for tag, keywords in TAG_MAP.items():
            if any(kw in full_lower for kw in keywords):
                existing_tags.add(tag)
        result["tags"] = list(existing_tags)

    except Exception as e:
        name_safe = name.encode("ascii", "replace").decode()
        print(f"  [ERROR] {name_safe}: {str(e)[:60]}")

    return result


async def run(input_path: str, output_path: str, batch_size: int, mode: str):
    with open(input_path, encoding="utf-8") as f:
        restaurants = json.load(f)

    if mode == "missing":
        to_scrape = [
            r for r in restaurants
            if not r.get("avg_rating") or not r.get("cuisine") or not r.get("opening_hours")
        ]
    else:
        to_scrape = restaurants

    to_scrape = to_scrape[:batch_size]
    print(f"[INFO] {len(to_scrape)} restoran islenecek...")

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

            result = await scrape_place(page, r)

            for orig in restaurants:
                if orig["id"] == r["id"]:
                    if result["rating"]:
                        orig["avg_rating"] = result["rating"]
                    if result["review_count"]:
                        orig["review_count"] = result["review_count"]
                    if result["cuisine"]:
                        orig["cuisine"] = result["cuisine"]
                    if result["opening_hours"]:
                        orig["opening_hours"] = result["opening_hours"]
                    if result["phone"]:
                        orig["phone"] = result["phone"]
                    if result["tags"]:
                        orig["tags"] = result["tags"]
                    break

            rating_str = str(result["rating"]) if result["rating"] else "-"
            cuisine_str = result["cuisine"] or "-"
            hours_str = result["opening_hours"][:20] if result["opening_hours"] else "-"
            print(f"  puan:{rating_str} mutfak:{cuisine_str} saat:{hours_str}")

            await asyncio.sleep(2)

        await browser.close()

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(restaurants, f, ensure_ascii=False, indent=2)

    print(f"\n[SONUC]")
    print(f"  Puan   : {sum(1 for r in restaurants if r.get('avg_rating'))}/{len(restaurants)}")
    print(f"  Mutfak : {sum(1 for r in restaurants if r.get('cuisine'))}/{len(restaurants)}")
    print(f"  Saat   : {sum(1 for r in restaurants if r.get('opening_hours'))}/{len(restaurants)}")
    print(f"  Tag    : {sum(1 for r in restaurants if r.get('tags'))}/{len(restaurants)}")
    print(f"\n[OK] -> {output_path}")
    print("[SONRAKI] python scripts/json_to_ts.py")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/processed/istanbul.json")
    parser.add_argument("--output", default="data/processed/istanbul.json")
    parser.add_argument("--batch", type=int, default=50)
    parser.add_argument("--mode", default="missing", choices=["missing", "all"])
    args = parser.parse_args()
    asyncio.run(run(args.input, args.output, args.batch, args.mode))


if __name__ == "__main__":
    main()
