# -*- coding: utf-8 -*-
"""
Google Maps'ten gercek kullanici yorumlarini cekip
Groq ile detayli, zengin icerik uretir.

Kullanim:
  python scripts/scrape_reviews.py --batch 100
"""

import json
import re
import sys
import time
import asyncio
import argparse
from playwright.async_api import async_playwright
from groq import Groq

GROQ_API_KEYS = [
    "os.environ.get("GROQ_API_KEY_1", "")",
    "os.environ.get("GROQ_API_KEY_2", "")",
]
_key_index = 0

def get_client():
    return Groq(api_key=GROQ_API_KEYS[_key_index % len(GROQ_API_KEYS)])


async def scrape_reviews(page, restaurant: dict) -> list[str]:
    name = restaurant["name"]
    lat = restaurant.get("lat")
    lng = restaurant.get("lng")

    query = f"{name} istanbul"
    if lat and lng:
        url = f"https://www.google.com/maps/search/{query}/@{lat},{lng},17z"
    else:
        url = f"https://www.google.com/maps/search/{query}"

    reviews = []

    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=10000)
        await page.wait_for_timeout(1500)

        # Yorumlar sekmesine tikla
        review_tab_selectors = [
            'button[aria-label*="Yorum"]',
            'button[aria-label*="Review"]',
            '[data-tab-index="1"]',
            'button[jsaction*="reviews"]',
        ]
        for sel in review_tab_selectors:
            btn = await page.query_selector(sel)
            if btn:
                await btn.click()
                await page.wait_for_timeout(2000)
                break

        # "Daha fazla" butonuna tikla - yorumlari ac
        more_btns = await page.query_selector_all('button[aria-label*="daha fazla"], button[aria-label*="more"], .w8nwRe')
        for btn in more_btns[:10]:
            try:
                await btn.click()
                await page.wait_for_timeout(300)
            except:
                pass

        # Scroll yaparak daha fazla icerik yukle
        for _ in range(3):
            await page.keyboard.press("End")
            await page.wait_for_timeout(800)

        # Tum span ve div'leri tara - yorum benzeri uzun metinler
        full_text = await page.inner_text("body")
        lines = full_text.splitlines()

        # Skip listesi
        skip_words = [
            "google", "harita", "yol tarifi", "kaydet", "web sitesi",
            "telefon", "saat", "adres", "paylaş", "fotoğraf", "yıldız",
            "puan ver", "yorum yaz", "daha fazla göster", "daha az göster",
            "öneri", "popüler saatler", "ziyaret", "hizmet türleri"
        ]

        for line in lines:
            line = line.strip()
            if (
                40 < len(line) < 600
                and not any(skip in line.lower() for skip in skip_words)
                and re.search(r"[a-zA-ZğüşöçİĞÜŞÖÇ]{4,}", line)
                and not re.match(r"^\d", line)  # Sayi ile baslamasin
                and line not in reviews
            ):
                reviews.append(line)
            if len(reviews) >= 12:
                break

    except Exception as e:
        name_safe = name.encode("ascii", "replace").decode()
        print(f"  [SCRAPE ERROR] {name_safe}: {str(e)[:50]}")

    return reviews[:10]


def generate_rich_content(client: Groq, r: dict, reviews: list[str]) -> dict:
    neighborhood = r.get("neighborhood") or "İstanbul"
    cuisine = r.get("cuisine") or "Türk mutfağı"
    rating = r.get("avg_rating") or 0
    reviews_count = r.get("review_count") or 0
    tags = r.get("tags") or []
    price = r.get("price_range", 2)
    features = [k for k, v in (r.get("features") or {}).items() if v]

    price_label = {1: "bütçe dostu", 2: "orta fiyat", 3: "üst segment", 4: "fine dining"}.get(price, "orta fiyat")

    reviews_text = ""
    if reviews:
        reviews_text = "\n".join([f"- {r[:200]}" for r in reviews[:8]])
    else:
        reviews_text = "Yorum verisi mevcut değil."

    special_tags = [t for t in tags if t in [
        "romantik", "manzarali", "boğaz manzarası", "teras", "aile dostu",
        "iş yemeği", "gastronomi", "şef restoranı", "tarihi mekan",
        "kahvaltı", "gece", "geç saate kadar açık", "vegan"
    ]]

    prompt = f"""Sen deneyimli bir İstanbul gastronomi yazarısın. Aşağıdaki restoran için gerçek müşteri yorumlarına dayanarak detaylı, özgün ve bilgilendirici Türkçe içerik yaz.

RESTORAN:
Ad: {r['name']}
Konum: {neighborhood}, İstanbul
Mutfak: {cuisine}
Puan: {rating}/5 ({reviews_count} değerlendirme)
Fiyat: {price_label}
Özellikler: {', '.join(features) or 'standart'}
Kategoriler: {', '.join(special_tags) or 'genel'}

GERÇEK MÜŞTERİ YORUMLARI:
{reviews_text}

GÖREVLER:

1. LLM_SUMMARY (3-4 cümle):
- Restoranın atmosferini, öne çıkan yemeklerini ve deneyimini anlat
- Yorumlardaki somut detayları kullan
- Kime uygun olduğunu belirt (çiftler, aileler, iş yemeği...)
- Kalıp cümle KULLANMA

2. SENTIMENT (2-3 cümle):
- Yorumların genel havasını yansıt
- En çok övülen ve eleştirilen noktaları belirt
- Yüzdelik tahmin ekle ("Ziyaretçilerin büyük çoğunluğu...")

3. HIGHLIGHTS (virgülle ayrılmış 3-5 madde):
- Restoranın en önemli özellikleri
- Somut örnekler (özel yemekler, manzara detayı, özel atmosfer)

ÖRNEKLER — tam bu tarzda yaz:

KÖTÜ (yazma): "X mahallesinde bulunan bir restoran olup misafirlerine keyifli bir atmosfer sunmaktadır."
İYİ (yaz): "Boğaz'ın tam karşısında, ahşap dekorasyonuyla sıcak bir balıkçı ambiyansı sunan Karaköy Lokantası, taze levrek ve kalkan balığıyla öne çıkıyor. Hafta sonu öğle saatlerinde dolup taşan mekân, özellikle deniz ürünleri tutkunları için vazgeçilmez bir adres."

KÖTÜ (yazma): "Ziyaretçiler genel olarak memnuniyetlerini dile getiriyor."
İYİ (yaz): "Ziyaretçilerin %90'ı özellikle levrek tava ve servis hızını övüyor; tek şikayet konusu hafta sonu yoğunluğunda yer bulmak."

SADECE şu formatı kullan, başka hiçbir şey yazma:
LLM_SUMMARY: ...
SENTIMENT: ...
HIGHLIGHTS: ..."""

    try:
        global _key_index
        resp = None
        for attempt in range(len(GROQ_API_KEYS) * 3):
            try:
                c = get_client()
                resp = c.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=500,
                    temperature=0.85,
                )
                break
            except Exception as e:
                if "429" in str(e):
                    _key_index += 1
                    next_key = _key_index % len(GROQ_API_KEYS)
                    print(f"  [RATE LIMIT] Key degistiriliyor -> key{next_key + 1}, 5s bekleniyor...", flush=True)
                    time.sleep(5)
                else:
                    raise
        if resp is None:
            return {}
        text = resp.choices[0].message.content.strip()

        result = {"llm_summary": "", "sentiment_summary": "", "highlights": []}
        for line in text.splitlines():
            if line.startswith("LLM_SUMMARY:"):
                result["llm_summary"] = line.replace("LLM_SUMMARY:", "").strip()
            elif line.startswith("SENTIMENT:"):
                result["sentiment_summary"] = line.replace("SENTIMENT:", "").strip()
            elif line.startswith("HIGHLIGHTS:"):
                hl = line.replace("HIGHLIGHTS:", "").strip()
                result["highlights"] = [h.strip() for h in hl.split(",") if h.strip()]

        return result

    except Exception as e:
        print(f"  [GROQ ERROR] {str(e)[:60]}")
        return {}


async def run(input_path: str, output_path: str, batch_size: int):
    with open(input_path, encoding="utf-8") as f:
        restaurants = json.load(f)

    client = get_client()

    # Puana gore sirala - en iyi restoranlardan baslayalim
    top = sorted(
        [r for r in restaurants if (r.get("avg_rating") or 0) > 0],
        key=lambda r: (-(r.get("avg_rating") or 0), -(r.get("review_count") or 0))
    )[:batch_size]

    print(f"[INFO] {len(top)} restoran icin yorum + detayli ozet uretiliyor...")

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

        done_count = sum(1 for r in restaurants if r.get("has_reviews"))
        print(f"[BASLANGIC] Zaten tamamlanan: {done_count}, devam ediliyor...", flush=True)

        for i, r in enumerate(top):
            name_safe = r["name"].encode("ascii", "replace").decode()
            print(f"[{i+1}/{len(top)}] {name_safe} ({r.get('avg_rating')}/5)", flush=True)
            sys.stdout.flush()

            # Yorumlari cek (max 20s timeout)
            try:
                reviews = await asyncio.wait_for(scrape_reviews(page, r), timeout=20)
            except asyncio.TimeoutError:
                print(f"  [TIMEOUT] Sayfa dondu, yeni sayfa aciliyor...", flush=True)
                try:
                    await page.close()
                except:
                    pass
                page = await context.new_page()
                await page.add_init_script(
                    "Object.defineProperty(navigator, 'webdriver', { get: () => undefined });"
                )
                reviews = []
            print(f"  {len(reviews)} yorum bulundu", flush=True)

            # Groq ile zengin icerik uret
            content = generate_rich_content(client, r, reviews)

            if content.get("llm_summary"):
                for orig in restaurants:
                    if orig["id"] == r["id"]:
                        orig["llm_summary"] = content["llm_summary"]
                        orig["sentiment_summary"] = content.get("sentiment_summary", "")
                        if content.get("highlights"):
                            orig["highlights"] = content["highlights"]
                        orig["confidence_score"] = 0.97
                        orig["has_reviews"] = len(reviews) > 0
                        break

                llm_safe = content["llm_summary"][:70].encode("ascii", "replace").decode()
                print(f"  OK: {llm_safe}...", flush=True)
            else:
                print(f"  ATLANDI", flush=True)

            # Her 10 restoranı tamamlayınca kaydet
            if (i + 1) % 10 == 0:
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(restaurants, f, ensure_ascii=False, indent=2)
                done_count = sum(1 for r in restaurants if r.get("has_reviews"))
                print(f">>> KAYIT: {i+1}/{len(top)} islendi | Toplam yorum bazli: {done_count}/453", flush=True)

            await asyncio.sleep(4)  # Groq rate limit icin daha uzun bekle

        await browser.close()

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(restaurants, f, ensure_ascii=False, indent=2)

    has_reviews = sum(1 for r in restaurants if r.get("has_reviews"))
    print(f"\n[OK] {has_reviews} restoran gercek yorum bazli icerige sahip -> {output_path}")
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
