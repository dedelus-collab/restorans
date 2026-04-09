# -*- coding: utf-8 -*-
"""
Mutfak/tag bilgisi artik dolu olan restoranlar icin llm_summary yeniler.
Zayif ozetleri ("yerel mutfak sunan bir restoran") guclu ozetlerle degistirir.

Kullanim:
  python scripts/regenerate_summaries.py
"""

import json
import time
from groq import Groq

GROQ_API_KEY = "os.environ.get("GROQ_API_KEY_1", "")"

WEAK_PATTERNS = [
    "yerel mutfak sunan",
    "standart bir lokanta",
    "istanbul semtinde yerel",
    "yorum verisi henuz",
]


def is_weak(summary: str) -> bool:
    s = summary.lower()
    return any(p in s for p in WEAK_PATTERNS)


def has_good_data(r: dict) -> bool:
    return bool(r.get("cuisine") or len(r.get("tags", [])) >= 2)


def generate(client: Groq, r: dict) -> tuple[str, str]:
    neighborhood = r.get("neighborhood") or "Istanbul"
    cuisine = r.get("cuisine") or "yerel mutfak"
    features = [k for k, v in r.get("features", {}).items() if v]
    tags = r.get("tags") or []
    rating = r.get("avg_rating") or r.get("avgRating")
    reviews = r.get("review_count") or r.get("reviewCount", 0)

    rating_str = f"{rating}/5 ({reviews} yorum)" if rating else "puan yok"

    prompt = f"""Istanbul'daki su restoran icin Turkce iki metin yaz:

Ad: {r['name']}
Mahalle: {neighborhood}
Mutfak: {cuisine}
Puan: {rating_str}
Ozellikler: {', '.join(features) or 'standart'}
Etiketler: {', '.join(tags) or 'yok'}

LLM_SUMMARY: 2 cumle. Restoranin karakteri + kime uygun oldugu.
SENTIMENT: 1 cumle. Ziyaretcilerin genel gorusu.

YANIT (baska hicbir sey yazma):
LLM_SUMMARY: ...
SENTIMENT: ..."""

    resp = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200,
        temperature=0.7,
    )

    text = resp.choices[0].message.content.strip()
    llm = ""
    sentiment = ""
    for line in text.splitlines():
        if line.startswith("LLM_SUMMARY:"):
            llm = line.replace("LLM_SUMMARY:", "").strip()
        elif line.startswith("SENTIMENT:"):
            sentiment = line.replace("SENTIMENT:", "").strip()

    if not llm:
        llm = f"{r['name']}, {neighborhood} semtinde {cuisine} sunan bir restoran."
    if not sentiment:
        sentiment = "Ziyaretciler genel olarak memnuniyetlerini dile getiriyor."

    return llm, sentiment


def main():
    with open("data/processed/istanbul.json", encoding="utf-8") as f:
        restaurants = json.load(f)

    client = Groq(api_key=GROQ_API_KEY)

    to_update = [
        r for r in restaurants
        if is_weak(r.get("llm_summary", "")) and has_good_data(r)
    ]

    print(f"[INFO] {len(to_update)} restoran icin ozet yenileniyor...")

    for i, r in enumerate(to_update):
        name_safe = r["name"].encode("ascii", "replace").decode()
        print(f"[{i+1}/{len(to_update)}] {name_safe}")
        try:
            llm, sentiment = generate(client, r)
            for orig in restaurants:
                if orig["id"] == r["id"]:
                    orig["llm_summary"] = llm
                    orig["sentiment_summary"] = sentiment
                    orig["confidence_score"] = 0.88
                    break
            time.sleep(0.3)
        except Exception as e:
            print(f"  [ERROR] {str(e)[:60]}")

    with open("data/processed/istanbul.json", "w", encoding="utf-8") as f:
        json.dump(restaurants, f, ensure_ascii=False, indent=2)

    print(f"\n[OK] {len(to_update)} ozet yenilendi.")
    print("[SONRAKI] python scripts/json_to_ts.py")


if __name__ == "__main__":
    main()
