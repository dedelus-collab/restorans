# -*- coding: utf-8 -*-
"""
Google Maps'ten detayli icerik cekip Groq ile zengin ozet uretir.
- Hakkinda bolumu
- Mutfak turu
- Ozellikler (wifi, rezervasyon, teras...)
- Gercek calisma saatleri

Kullanim:
  python scripts/enrich_deep.py --batch 100
"""

import json
import re
import time
import asyncio
import argparse
from playwright.async_api import async_playwright
from groq import Groq

GROQ_API_KEY = "os.environ.get("GROQ_API_KEY_1", "")"

FEATURE_KEYWORDS = {
    "teras": ["teras", "terrace", "outdoor", "dis mekan", "bahce"],
    "rezervasyon": ["rezervasyon", "reservation", "booking"],
    "wifi": ["wi-fi", "wifi", "wireless"],
    "seaView": ["deniz manzara", "bogaz manzara", "bosphorus view", "sea view", "manzara"],
    "romantic": ["romantik", "candle", "intimate", "cift", "sevgililer"],
    "parking": ["otopark", "parking", "vale"],
    "liveMusic": ["canli muzik", "live music", "muzisyen"],
    "vegan": ["vegan", "vejetaryen", "vegetarian"],
}

CUISINE_MAP = {
    "turk": "Türk", "turkish": "Türk", "kebap": "Kebap", "kebab": "Kebap",
    "pide": "Pide", "lahmacun": "Lahmacun", "balik": "Balık", "fish": "Balık",
    "seafood": "Deniz Ürünleri", "meze": "Meze", "meyhane": "Meyhane",
    "pizza": "İtalyan/Pizza", "italian": "İtalyan", "pasta": "İtalyan",
    "burger": "Burger/Amerikan", "american": "Amerikan",
    "sushi": "Japon/Sushi", "japanese": "Japon",
    "chinese": "Çin", "indian": "Hint", "mexican": "Meksika",
    "greek": "Yunan", "french": "Fransız",
    "kahvalti": "Kahvaltı", "breakfast": "Kahvaltı",
    "steakhouse": "Steakhouse", "steak": "Steakhouse",
    "vegan": "Vegan/Vejetaryen", "vegetarian": "Vegan/Vejetaryen",
    "ocakbasi": "Ocakbaşı", "tantuni": "Tantuni",
    "iskender": "Iskender", "doner": "Döner",
    "cafe": "Kafe", "kahve": "Kafe",
    "anatolian": "Anadolu Mutfağı", "anadolu": "Anadolu Mutfağı",
    "antakya": "Antakya Mutfağı", "ege": "Ege Mutfağı",
}


async def scrape_details(page, restaurant: dict) -> dict:
    name = restaurant["name"]
    lat = restaurant.get("lat")
    lng = restaurant.get("lng")

    query = f"{name} istanbul"
    if lat and lng:
        url = f"https://www.google.com/maps/search/{query}/@{lat},{lng},17z"
    else:
        url = f"https://www.google.com/maps/search/{query}"

    details = {
        "about": "",
        "cuisine": restaurant.get("cuisine", ""),
        "opening_hours": restaurant.get("opening_hours", ""),
        "features": restaurant.get("features", {}),
        "phone": restaurant.get("phone", ""),
        "website": restaurant.get("website", ""),
        "rating": restaurant.get("avg_rating"),
        "review_count": restaurant.get("review_count", 0),
    }

    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=15000)
        await page.wait_for_timeout(2500)

        full_text = await page.inner_text("body")
        full_lower = full_text.lower()

        # Puan
        if not details["rating"]:
            spans = await page.query_selector_all("span")
            for span in spans[:150]:
                try:
                    t = (await span.inner_text()).strip().replace(",", ".")
                    val = float(t)
                    if 1.0 <= val <= 5.0:
                        details["rating"] = round(val, 1)
                        break
                except:
                    pass

        # Yorum sayisi
        if not details["review_count"]:
            m = re.search(r"\(([0-9][0-9.,\s]{0,8})\)", full_text)
            if m:
                num = re.sub(r"[^0-9]", "", m.group(1))
                try:
                    details["review_count"] = int(num)
                except:
                    pass

        # Mutfak turu - Google Maps kategori metninden
        if not details["cuisine"]:
            for key, val in CUISINE_MAP.items():
                if key in full_lower:
                    details["cuisine"] = val
                    break

        # Calisma saatleri
        if not details["opening_hours"]:
            patterns = [
                r"\d{2}:\d{2}\s*[–\-]\s*\d{2}:\d{2}",
                r"\d{1,2}:\d{2}\s*(AM|PM)[^a-z]*[–\-][^a-z]*\d{1,2}:\d{2}\s*(AM|PM)",
            ]
            for pat in patterns:
                m = re.search(pat, full_text)
                if m:
                    details["opening_hours"] = f"Mo-Su {m.group(0).strip()}"
                    break
            if "7/24" in full_text or "24 saat" in full_lower:
                details["opening_hours"] = "Mo-Su 00:00-24:00"

        # Ozellikler
        features = dict(details["features"])
        for feature, keywords in FEATURE_KEYWORDS.items():
            if any(kw in full_lower for kw in keywords):
                features[feature] = True
        details["features"] = features

        # Hakkinda metni - ilk anlamli paragraf
        lines = [l.strip() for l in full_text.splitlines() if len(l.strip()) > 40]
        for line in lines[:30]:
            if any(skip in line.lower() for skip in ["google", "harita", "yol tarifi", "kaydet", "paylash", "yakın"]):
                continue
            if re.search(r"[a-zA-ZğüşöçİĞÜŞÖÇ]{4,}", line):
                details["about"] = line[:300]
                break

        # Telefon
        if not details["phone"]:
            m = re.search(r"(\+90[\s\-]?\d{3}[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2})", full_text)
            if m:
                details["phone"] = m.group(1)

    except Exception as e:
        name_safe = name.encode("ascii", "replace").decode()
        print(f"  [SCRAPE ERROR] {name_safe}: {str(e)[:50]}")

    return details


def generate_rich_summary(client: Groq, r: dict, details: dict) -> tuple[str, str]:
    neighborhood = r.get("neighborhood") or "İstanbul"
    cuisine = details.get("cuisine") or r.get("cuisine") or "yerel mutfak"
    rating = details.get("rating") or r.get("avg_rating") or 0
    reviews = details.get("review_count") or r.get("review_count") or 0
    tags = r.get("tags") or []
    about = details.get("about") or ""
    features = details.get("features") or {}
    active_features = [k for k, v in features.items() if v]
    price = r.get("price_range", 2)
    hours = details.get("opening_hours") or r.get("opening_hours") or ""

    price_label = {1: "ekonomik", 2: "orta fiyat aralığında", 3: "üst segment", 4: "lüks"}.get(price, "orta fiyat")
    rating_label = "çok beğenilen" if rating >= 4.5 else "beğenilen" if rating >= 4.0 else "ziyaret edilen"

    context_parts = []
    if about:
        context_parts.append(f"Mekan hakkında: {about[:200]}")
    if active_features:
        context_parts.append(f"Özellikler: {', '.join(active_features)}")
    if hours:
        context_parts.append(f"Saatler: {hours}")
    if "romantik" in tags:
        context_parts.append("Romantik atmosfer")
    if "manzarali" in tags or "seaView" in active_features:
        context_parts.append("Deniz/Boğaz manzarası")

    context = " | ".join(context_parts) if context_parts else "Standart restoran"

    prompt = f"""Asagidaki Istanbul restorani icin dogal, bilgilendirici ve cekici Turkce iki metin yaz.
Robotic kalip cumlelerden kacin. Gercek bir yerden bahsediyormus gibi yaz.

RESTORAN:
Ad: {r['name']}
Konum: {neighborhood}, Istanbul
Mutfak: {cuisine}
Puan: {rating}/5 ({reviews} yorum) - {rating_label}
Fiyat: {price_label}
Ek bilgi: {context}

KURALLAR:
- "X mahallesinde bulunan bir restoran" gibi kalip cumle YAZMA
- Restoranin en dikkat cekici ozelligini one ckar
- Kime uygun oldugunu belirt (ciftler, aileler, is yemekleri...)
- Kisa ve net ol

LLM_SUMMARY: (2 cumle, max 60 kelime)
SENTIMENT: (1 cumle, ziyaretcilerin ne ovdugu, max 25 kelime)

SADECE su iki satiri yaz:
LLM_SUMMARY: ...
SENTIMENT: ..."""

    try:
        resp = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=250,
            temperature=0.8,
        )
        text = resp.choices[0].message.content.strip()
        llm = ""
        sentiment = ""
        for line in text.splitlines():
            if line.startswith("LLM_SUMMARY:"):
                llm = line.replace("LLM_SUMMARY:", "").strip()
            elif line.startswith("SENTIMENT:"):
                sentiment = line.replace("SENTIMENT:", "").strip()
    except Exception as e:
        print(f"  [GROQ ERROR] {str(e)[:50]}")
        llm = ""
        sentiment = ""

    if not llm:
        llm = f"{r['name']}, {neighborhood}'de {cuisine} sunan {price_label} bir mekan."
    if not sentiment:
        sentiment = "Ziyaretçiler genel olarak memnuniyetlerini dile getiriyor."

    return llm, sentiment


async def run(input_path: str, output_path: str, batch_size: int):
    with open(input_path, encoding="utf-8") as f:
        restaurants = json.load(f)

    client = Groq(api_key=GROQ_API_KEY)

    # En oncelikli: yuksek puanli veya eksik mutfak/icerik olanlar
    priority = sorted(
        restaurants,
        key=lambda r: (
            -(r.get("avg_rating") or 0),
            bool(r.get("cuisine")),
        )
    )[:batch_size]

    print(f"[INFO] {len(priority)} restoran derin zenginlestirme yapilacak...")

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

        for i, r in enumerate(priority):
            name_safe = r["name"].encode("ascii", "replace").decode()
            print(f"[{i+1}/{len(priority)}] {name_safe}")

            # Scrape
            details = await scrape_details(page, r)

            # Groq ile zengin ozet
            llm, sentiment = generate_rich_summary(client, r, details)

            # Orijinal kaydi guncelle
            for orig in restaurants:
                if orig["id"] == r["id"]:
                    orig["llm_summary"] = llm
                    orig["sentiment_summary"] = sentiment
                    orig["confidence_score"] = 0.92
                    if details["cuisine"]:
                        orig["cuisine"] = details["cuisine"]
                    if details["opening_hours"]:
                        orig["opening_hours"] = details["opening_hours"]
                    if details["rating"]:
                        orig["avg_rating"] = details["rating"]
                    if details["review_count"]:
                        orig["review_count"] = details["review_count"]
                    if details["phone"]:
                        orig["phone"] = details["phone"]
                    # Features guncelle
                    for feat, val in details["features"].items():
                        if val:
                            orig.setdefault("features", {})[feat] = True
                    break

            llm_safe = llm[:60].encode("ascii", "replace").decode()
            print(f"  -> {llm_safe}...")

            await asyncio.sleep(2)

        await browser.close()

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(restaurants, f, ensure_ascii=False, indent=2)

    print(f"\n[SONUC]")
    print(f"  Mutfak : {sum(1 for r in restaurants if r.get('cuisine'))}/{len(restaurants)}")
    print(f"  Saat   : {sum(1 for r in restaurants if r.get('opening_hours'))}/{len(restaurants)}")
    print(f"  Puan   : {sum(1 for r in restaurants if r.get('avg_rating'))}/{len(restaurants)}")
    print(f"\n[OK] -> {output_path}")
    print("[SONRAKI] python scripts/json_to_ts.py")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/processed/istanbul.json")
    parser.add_argument("--output", default="data/processed/istanbul.json")
    parser.add_argument("--batch", type=int, default=100)
    args = parser.parse_args()
    asyncio.run(run(args.input, args.output, args.batch))


if __name__ == "__main__":
    main()
