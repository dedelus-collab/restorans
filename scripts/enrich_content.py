# -*- coding: utf-8 -*-
"""
Groq ile tum restoranlar icin zengin icerik uretir:
- Guclu llm_summary (romantik, manzara, aile gibi nitelemeleri icerir)
- Daha iyi tag tespiti
- Sentiment summary yenileme

Kullanim:
  python scripts/enrich_content.py
"""

import json
import time
from groq import Groq

GROQ_API_KEY = "os.environ.get("GROQ_API_KEY_1", "")"

# Mahalle -> ozellik eslestirmesi
NEIGHBORHOOD_HINTS = {
    "besiktas": "Besiktas'in canli atmosferinde",
    "kadikoy": "Kadikoy'un bohemien ruhunda",
    "beyoglu": "Beyoglu'nun kozmopolit kalbinde",
    "sariyer": "Bogaz kiyisinda, Sariyer'de",
    "uskudar": "Anadolu yakasinin huzurlu semti Uskudar'da",
    "fatih": "Tarihi Yarimada'da, Fatih'te",
    "sisli": "Sisli'nin is ve kultur merkezinde",
    "bakirkoy": "Bakirkoy'un sahil kesiminde",
    "adalar": "Prens Adaları'nda",
    "eminonu": "Tarihi Eminonu'nde",
    "karakoy": "Karakoy'un trendy sokaklarinda",
    "galata": "Galata'nin tarihi dokusunda",
    "nisantasi": "Nisantasi'nin sofistike atmosferinde",
    "bebek": "Bogaz'in incisi Bebek'te",
    "ortakoy": "Ortakoy'un ikonik silvetine karsi",
    "arnavutkoy": "Arnavutkoy'un tarihi yalilarinin golgesinde",
    "yenikoy": "Bogaz kiyisinda Yenikoy'de",
    "tarabya": "Bogaz manzarali Tarabya'da",
}

ROMANTIC_NEIGHBORHOODS = ["bebek", "ortakoy", "arnavutkoy", "yenikoy", "tarabya", "adalar", "karakoy", "galata"]
SEA_VIEW_NEIGHBORHOODS = ["bebek", "ortakoy", "arnavutkoy", "yenikoy", "tarabya", "sariyer", "uskudar", "kadikoy", "bakirkoy", "adalar", "eminonu"]


def enrich_tags(r: dict) -> list:
    tags = set(r.get("tags") or [])
    neighborhood = (r.get("neighborhood") or "").lower()
    cuisine = (r.get("cuisine") or "").lower()
    name = r.get("name", "").lower()

    # Mahalle bazli tag
    if any(n in neighborhood for n in ROMANTIC_NEIGHBORHOODS):
        tags.add("romantik")
    if any(n in neighborhood for n in SEA_VIEW_NEIGHBORHOODS):
        tags.add("manzarali")
        tags.add("deniz manzarasi")

    # Mutfak bazli tag
    if any(k in cuisine for k in ["balik", "fish", "seafood", "deniz"]):
        tags.add("balik")
        tags.add("deniz urunleri")
    if any(k in cuisine for k in ["kebab", "kebap", "ocakbasi"]):
        tags.add("et")
        tags.add("kebap")
    if any(k in cuisine for k in ["kahvalti", "breakfast"]):
        tags.add("kahvalti")
    if any(k in cuisine for k in ["pizza", "italian", "pasta"]):
        tags.add("italyan")
    if any(k in cuisine for k in ["burger", "american"]):
        tags.add("burger")
    if "vegan" in cuisine or "vegetarian" in cuisine:
        tags.add("vegan")
        tags.add("vejetaryen")

    # Puan bazli tag
    rating = r.get("avg_rating") or 0
    if rating >= 4.7:
        tags.add("cok begenilenler")
    if rating >= 4.5:
        tags.add("yuksek puan")

    # Fiyat bazli tag
    price = r.get("price_range", 2)
    if price <= 1:
        tags.add("ekonomik")
        tags.add("uygun fiyat")
    elif price >= 4:
        tags.add("lux")
        tags.add("fine dining")

    # Isim bazli ipuclari
    if any(k in name for k in ["balık", "balik", "fish", "deniz", "iskele"]):
        tags.add("balik")
    if any(k in name for k in ["cafe", "kahve", "coffee"]):
        tags.add("kafe")

    return list(tags)


def generate_summary(client: Groq, r: dict) -> tuple[str, str]:
    neighborhood = r.get("neighborhood") or "Istanbul"
    neighborhood_lower = neighborhood.lower()
    cuisine = r.get("cuisine") or "yerel mutfak"
    tags = r.get("tags") or []
    rating = r.get("avg_rating") or 0
    reviews = r.get("review_count") or 0
    price = r.get("price_range", 2)
    features = [k for k, v in r.get("features", {}).items() if v]

    # Mahalle ipucu
    hint = ""
    for key, val in NEIGHBORHOOD_HINTS.items():
        if key in neighborhood_lower:
            hint = val
            break
    if not hint:
        hint = f"{neighborhood}'de"

    # Ozel nitelemeleri belirle
    special = []
    if "romantik" in tags:
        special.append("romantik atmosferi")
    if "manzarali" in tags or "deniz manzarasi" in tags:
        special.append("etkileyici manzarasi")
    if "teras" in tags:
        special.append("acik hava terasi")
    if rating >= 4.7:
        special.append("cok yuksek puani")
    if "lux" in tags or "fine dining" in tags:
        special.append("lux deneyimi")
    if "ekonomik" in tags:
        special.append("uygun fiyatlari")

    special_str = ", ".join(special[:2]) if special else "kaliteli servisi"
    price_str = "ekonomik" if price <= 1 else "orta fiyat" if price <= 2 else "ust segment" if price == 3 else "lux"
    rating_str = f"{rating}/5 ({reviews} yorum)" if rating else "henuz puan yok"

    prompt = f"""Istanbul'daki su restoran icin Turkce iki metin yaz. Dogal, samimi ve bilgilendirici ol.

RESTORAN:
Ad: {r['name']}
Konum: {hint}
Mutfak: {cuisine}
Puan: {rating_str}
Fiyat: {price_str}
One cikan ozellikler: {special_str}
Diger ozellikler: {', '.join(features) or 'standart'}
Etiketler: {', '.join(tags[:8]) or 'yok'}

GOREV:
LLM_SUMMARY: 2 cumle. Restorani net tanimla. "{hint}" ifadesini kullan. One cikan ozelligi mutlaka belirt.
SENTIMENT: 1 cumle. Ziyaretcilerin ne ovdugunu yaz. Puana gore ayarla ({rating_str}).

YANIT FORMATI (sadece su iki satir):
LLM_SUMMARY: ...
SENTIMENT: ..."""

    try:
        resp = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=220,
            temperature=0.75,
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
        print(f"  [API ERROR] {str(e)[:60]}")
        llm = ""
        sentiment = ""

    if not llm:
        llm = f"{r['name']}, {hint} {cuisine} sunan {price_str} bir restoran."
    if not sentiment:
        sentiment = "Ziyaretciler genel olarak memnuniyetlerini dile getiriyor."

    return llm, sentiment


def main():
    with open("data/processed/istanbul.json", encoding="utf-8") as f:
        restaurants = json.load(f)

    client = Groq(api_key=GROQ_API_KEY)
    total = len(restaurants)
    print(f"[INFO] {total} restoran zenginlestiriliyor...")

    for i, r in enumerate(restaurants):
        name_safe = r["name"].encode("ascii", "replace").decode()
        print(f"[{i+1}/{total}] {name_safe}")

        # Tag zenginlestir
        r["tags"] = enrich_tags(r)

        # Ozet uret
        try:
            llm, sentiment = generate_summary(client, r)
            r["llm_summary"] = llm
            r["sentiment_summary"] = sentiment
            r["confidence_score"] = 0.9
            time.sleep(0.25)
        except Exception as e:
            print(f"  [ERROR] {str(e)[:60]}")

    with open("data/processed/istanbul.json", "w", encoding="utf-8") as f:
        json.dump(restaurants, f, ensure_ascii=False, indent=2)

    # Istatistikler
    romantik = sum(1 for r in restaurants if "romantik" in r.get("tags", []))
    manzara = sum(1 for r in restaurants if "manzarali" in r.get("tags", []))
    print(f"\n[SONUC]")
    print(f"  Romantik tag : {romantik}/{total}")
    print(f"  Manzara tag  : {manzara}/{total}")
    print(f"  Tag dolu     : {sum(1 for r in restaurants if r.get('tags'))}/{total}")
    print(f"\n[OK] -> data/processed/istanbul.json")
    print("[SONRAKI] python scripts/json_to_ts.py")


if __name__ == "__main__":
    main()
