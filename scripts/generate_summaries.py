# -*- coding: utf-8 -*-
"""
Groq API ile otomatik llm_summary uretimi (UCRETSIZ).
scrape_osm.py ile toplanan ham veriyi zenginlestirir.

Kurulum:
  pip install groq

Kullanim:
  python scripts/generate_summaries.py --input data/raw/istanbul.json
"""

import json
import os
import time
import argparse
from pathlib import Path
from groq import Groq

GROQ_API_KEY = "os.environ.get("GROQ_API_KEY_1", "")"


def get_client() -> Groq:
    return Groq(api_key=GROQ_API_KEY)


def generate_summaries(client: Groq, restaurant: dict) -> tuple[str, str]:
    neighborhood = restaurant.get("neighborhood") or "Istanbul"
    cuisine = restaurant.get("cuisine") or "yerel mutfak"
    features = [k for k, v in restaurant.get("features", {}).items() if v]
    tags = restaurant.get("tags") or []

    prompt = f"""Asagidaki Istanbul restorani icin iki ayri Turkce metin yaz.

RESTORAN BILGILERI:
Ad: {restaurant['name']}
Mahalle: {neighborhood}
Mutfak: {cuisine}
Fiyat: {'TL' * restaurant.get('price_range', 2)}
Ozellikler: {', '.join(features) or 'standart'}
Etiketler: {', '.join(tags) or 'yok'}

GOREV 1 - llm_summary:
2 kisa cumlelik ozet. Restoranin karakterini ve kime uygun oldugunu belirt.

GOREV 2 - sentiment_summary:
1 cumlelik yorum ozeti. "Ziyaretciler genellikle [X]'i ovuyor, [Y] one cikiyor." formatinda.

YANIT FORMATI (baska hicbir sey yazma):
LLM_SUMMARY: [buraya yaz]
SENTIMENT: [buraya yaz]"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200,
        temperature=0.7,
    )

    text = response.choices[0].message.content.strip()
    llm_summary = ""
    sentiment = ""

    for line in text.splitlines():
        if line.startswith("LLM_SUMMARY:"):
            llm_summary = line.replace("LLM_SUMMARY:", "").strip()
        elif line.startswith("SENTIMENT:"):
            sentiment = line.replace("SENTIMENT:", "").strip()

    if not llm_summary:
        llm_summary = f"{restaurant['name']}, {neighborhood} semtinde {cuisine} sunan bir restoran."
    if not sentiment:
        sentiment = "Ziyaretciler genel olarak memnuniyetlerini dile getiriyor."

    return llm_summary, sentiment


def process_file(input_path: str, output_path: str | None = None):
    client = get_client()

    with open(input_path, "r", encoding="utf-8") as f:
        restaurants = json.load(f)

    total = len(restaurants)
    skipped = sum(1 for r in restaurants if r.get("llm_summary"))
    print(f"[INFO] {total} restoran | {skipped} atlanacak | {total - skipped} islenecek")

    for i, r in enumerate(restaurants):
        if r.get("llm_summary"):
            continue

        try:
            print(f"[{i+1}/{total}] {r['name']}")
            for attempt in range(3):
                try:
                    r["llm_summary"], r["sentiment_summary"] = generate_summaries(client, r)
                    r["confidence_score"] = 0.82
                    break
                except Exception as e:
                    if "429" in str(e) and attempt < 2:
                        wait = 30 * (attempt + 1)
                        print(f"  [RATE LIMIT] {wait}s bekleniyor...")
                        time.sleep(wait)
                    else:
                        raise
            time.sleep(4)  # Gemini free tier: 15 req/dk = 4sn aralik
        except Exception as e:
            print(f"  [ERROR] {e}")
            neighborhood = r.get("neighborhood") or "Istanbul"
            cuisine = r.get("cuisine") or "yerel"
            r["llm_summary"] = f"{r['name']}, {neighborhood} semtinde {cuisine} sunan bir restoran."
            r["sentiment_summary"] = "Yorum verisi henuz mevcut degil."

    out_path = output_path or input_path.replace("\\raw\\", "\\processed\\").replace("/raw/", "/processed/")
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(restaurants, f, ensure_ascii=False, indent=2)

    print(f"\n[OK] {total} restoran -> {out_path}")
    print("[SONRAKI] python scripts/json_to_ts.py")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="data/raw/istanbul.json")
    parser.add_argument("--output", help="Cikis yolu (varsayilan: data/processed/...)")
    args = parser.parse_args()
    process_file(args.input, args.output)


if __name__ == "__main__":
    main()
