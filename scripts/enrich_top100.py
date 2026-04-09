# -*- coding: utf-8 -*-
"""
Top 100 restorani llama-3.3-70b ile yeniden ozetler.
Website varsa icerigi de ceker.

Kullanim:
  python scripts/enrich_top100.py
"""

import json
import time
import asyncio
import re
from groq import Groq
from playwright.async_api import async_playwright

GROQ_API_KEY = "os.environ.get("GROQ_API_KEY_1", "")"

NEIGHBORHOOD_CONTEXT = {
    "besiktas": "Beşiktaş'ın canlı kıyı şeridinde",
    "kadikoy": "Kadıköy'ün eklektik ve bohemien atmosferinde",
    "beyoglu": "Beyoğlu'nun kozmopolit kalbinde, İstiklal yakınlarında",
    "sariyer": "Boğaz'ın Avrupa yakasında, Sarıyer'in sakin kıyılarında",
    "uskudar": "Üsküdar'ın köklü ve tarihi semtinde",
    "fatih": "Tarihi Yarımada'nın kalbinde, Fatih'te",
    "sisli": "Şişli'nin modern iş ve alışveriş merkezinde",
    "bakirkoy": "Bakırköy'ün sahil kenarında",
    "adalar": "İstanbul'un otomobilsiz cennetinde, Prens Adaları'nda",
    "eminonu": "Tarihi Eminönü'nde, Boğaz'ın ağzında",
    "karakoy": "Karaköy'ün restore edilmiş tarihi yapıları arasında",
    "galata": "Galata Kulesi'nin gölgesinde",
    "nisantasi": "Nişantaşı'nın şık butik caddelerinde",
    "bebek": "Boğaz'ın en prestijli semti Bebek'te",
    "ortakoy": "Ortaköy'ün ikonik camii ve köprü manzarasında",
    "arnavutkoy": "Arnavutköy'ün ahşap yalıları arasında",
    "yenikoy": "Boğaz kıyısında, Yeniköy'ün sakin atmosferinde",
    "tarabya": "Boğaz'ın en güzel koyu Tarabya'da",
    "rumelihisari": "Rumelihisarı'nın tarihi surları dibinde",
    "cihangir": "Cihangir'in sanatçı ve yaratıcı ruhunda",
    "balat": "Balat'ın renkli tarihi sokaklarında",
    "fener": "Fener'in Bizans mirası mahallelerinde",
}


async def scrape_website(page, url: str) -> str:
    """Restoranin websitesinden aciklama metni ceker."""
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=12000)
        await page.wait_for_timeout(1500)

        # Meta description
        meta = await page.query_selector('meta[name="description"]')
        if meta:
            content = await meta.get_attribute("content")
            if content and len(content) > 50:
                return content[:400]

        # og:description
        og = await page.query_selector('meta[property="og:description"]')
        if og:
            content = await og.get_attribute("content")
            if content and len(content) > 50:
                return content[:400]

        # Ilk anlamli paragraf
        paras = await page.query_selector_all("p")
        for p in paras[:10]:
            text = (await p.inner_text()).strip()
            if len(text) > 80:
                return text[:400]

    except Exception:
        pass
    return ""


async def scrape_google_about(page, restaurant: dict) -> str:
    """Google Maps Hakkinda bolumunden aciklama ceker."""
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

        full_text = await page.inner_text("body")

        # Anlamli ve uzun satirlari bul
        for line in full_text.splitlines():
            line = line.strip()
            if (
                len(line) > 60
                and not any(skip in line.lower() for skip in [
                    "google", "harita", "yol tarifi", "kaydet", "paylaş",
                    "yakın", "fotoğraf", "web sitesi", "ara ", "telefon"
                ])
                and re.search(r"[a-zA-ZğüşöçİĞÜŞÖÇ]{5,}", line)
            ):
                return line[:400]
    except Exception:
        pass
    return ""


def build_prompt(r: dict, web_content: str, google_about: str) -> str:
    neighborhood = (r.get("neighborhood") or "").lower()
    location_ctx = ""
    for key, val in NEIGHBORHOOD_CONTEXT.items():
        if key in neighborhood:
            location_ctx = val
            break
    if not location_ctx:
        location_ctx = f"{r.get('neighborhood') or 'İstanbul'}'da"

    cuisine = r.get("cuisine") or "Türk mutfağı"
    rating = r.get("avg_rating") or 0
    reviews = r.get("review_count") or 0
    tags = r.get("tags") or []
    price = r.get("price_range", 2)
    hours = r.get("opening_hours") or ""
    features = [k for k, v in (r.get("features") or {}).items() if v]

    price_label = {1: "bütçe dostu", 2: "orta bütçeye uygun", 3: "üst segment", 4: "fine dining/lüks"}.get(price, "orta bütçeye uygun")

    extra_ctx = []
    if web_content:
        extra_ctx.append(f"Restoranın kendi tanımı: {web_content[:250]}")
    if google_about:
        extra_ctx.append(f"Google'daki açıklama: {google_about[:200]}")
    if "romantik" in tags:
        extra_ctx.append("Romantik atmosfer, çiftler için ideal")
    if "manzarali" in tags or "seaView" in features:
        extra_ctx.append("Deniz/Boğaz manzaralı")
    if "teras" in features or "terrace" in features:
        extra_ctx.append("Açık hava terası mevcut")
    if hours:
        extra_ctx.append(f"Çalışma saatleri: {hours}")
    if rating >= 4.5:
        extra_ctx.append(f"Yüksek beğeni: {rating}/5 ({reviews} değerlendirme)")

    return f"""Sen bir Türk gastronomi yazarısın. Aşağıdaki İstanbul restoranı için özgün, akıcı ve bilgilendirici Türkçe içerik yaz.

RESTORAN BİLGİLERİ:
Ad: {r['name']}
Konum: {location_ctx}
Mutfak: {cuisine}
Fiyat: {price_label}
Ek bilgiler: {' | '.join(extra_ctx) if extra_ctx else 'Standart restoran'}

KURALLAR:
- "X mahallesinde bulunan bir restoran" gibi kalıp KULLANMA
- Restoranı sanki orada yemek yemiş biri anlatıyor gibi yaz
- Somut detaylar ver: atmosfer, özel yemekler, kime uygun
- Doğal ve akıcı Türkçe kullan

LLM_SUMMARY: 2 cümle (max 55 kelime). Restoranın ruhunu yansıt.
SENTIMENT: 1 cümle (max 20 kelime). Misafirlerin en çok neyi övdüğü.

SADECE şu formatı kullan:
LLM_SUMMARY: ...
SENTIMENT: ..."""


def parse_response(text: str) -> tuple[str, str]:
    llm = ""
    sentiment = ""
    for line in text.strip().splitlines():
        if line.startswith("LLM_SUMMARY:"):
            llm = line.replace("LLM_SUMMARY:", "").strip()
        elif line.startswith("SENTIMENT:"):
            sentiment = line.replace("SENTIMENT:", "").strip()
    return llm, sentiment


async def run():
    with open("data/processed/istanbul.json", encoding="utf-8") as f:
        restaurants = json.load(f)

    client = Groq(api_key=GROQ_API_KEY)

    # Top 100: puana gore sirala
    top100 = sorted(
        [r for r in restaurants if (r.get("avg_rating") or 0) > 0],
        key=lambda r: (-(r.get("avg_rating") or 0), -(r.get("review_count") or 0))
    )[:100]

    print(f"[INFO] Top {len(top100)} restoran yeniden yaziliyor (llama-3.3-70b)...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
            locale="tr-TR",
        )
        page = await context.new_page()
        await page.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', { get: () => undefined });"
        )

        for i, r in enumerate(top100):
            name_safe = r["name"].encode("ascii", "replace").decode()
            print(f"[{i+1}/100] {name_safe} ({r.get('avg_rating')}/5)")

            # Web icerigi cek
            web_content = ""
            if r.get("website"):
                web_content = await scrape_website(page, r["website"])

            # Google Maps hakkinda
            google_about = await scrape_google_about(page, r)

            # 70b ile ozet uret
            try:
                prompt = build_prompt(r, web_content, google_about)
                resp = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=250,
                    temperature=0.85,
                )
                llm, sentiment = parse_response(resp.choices[0].message.content)

                if llm:
                    for orig in restaurants:
                        if orig["id"] == r["id"]:
                            orig["llm_summary"] = llm
                            orig["sentiment_summary"] = sentiment
                            orig["confidence_score"] = 0.95
                            break
                    llm_safe = llm[:70].encode("ascii", "replace").decode()
                    print(f"  -> {llm_safe}...")
                else:
                    print(f"  -> parse hatasi")

                time.sleep(0.4)
            except Exception as e:
                print(f"  [ERROR] {str(e)[:60]}")

            await asyncio.sleep(1.5)

        await browser.close()

    with open("data/processed/istanbul.json", "w", encoding="utf-8") as f:
        json.dump(restaurants, f, ensure_ascii=False, indent=2)

    print(f"\n[OK] Top 100 yeniden yazildi -> data/processed/istanbul.json")
    print("[SONRAKI] python scripts/json_to_ts.py")


if __name__ == "__main__":
    asyncio.run(run())
