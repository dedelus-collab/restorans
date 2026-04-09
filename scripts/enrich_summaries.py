# -*- coding: utf-8 -*-
"""
Mevcut veriyi kullanarak Groq ile kaliteli llm_summary uretir.
Playwright yok - sadece mevcut data + Groq. Cok daha hizli ve stabil.

Kullanim:
  python scripts/enrich_summaries.py
"""

import json
import time
import sys
from groq import Groq

GROQ_API_KEYS = [
    "os.environ.get("GROQ_API_KEY_1", "")",
    "os.environ.get("GROQ_API_KEY_2", "")",
]
_key_index = 0

def get_client():
    return Groq(api_key=GROQ_API_KEYS[_key_index % len(GROQ_API_KEYS)])


def generate_summary(r: dict) -> dict:
    global _key_index

    name = r.get("name", "")
    neighborhood = r.get("neighborhood", "Istanbul")
    cuisine = r.get("cuisine") or "Turk mutfagi"
    rating = r.get("avg_rating") or 0
    review_count = r.get("review_count") or 0
    tags = r.get("tags") or []
    price = r.get("price_range", 2)
    features = [k for k, v in (r.get("features") or {}).items() if v]
    existing_summary = r.get("llm_summary", "")
    existing_sentiment = r.get("sentiment_summary", "")

    price_label = {1: "butce dostu", 2: "orta fiyat", 3: "ust segment", 4: "fine dining"}.get(price, "orta fiyat")

    special_tags = [t for t in tags if any(k in t.lower() for k in [
        "romantik", "manzara", "bogaz", "teras", "aile", "is yemegi",
        "gastronomi", "tarihi", "kahvalti", "vegan", "deniz", "canli muzik"
    ])]

    prompt = f"""Istanbul gastronomi yazari olarak asagidaki restoran icin Turkce 4 cumlelik ozet yaz.

{name} | {neighborhood} | {cuisine} | {rating}/5 ({review_count} yorum) | {price_label}
Ozellikler: {', '.join(features) or 'standart'} | Kategoriler: {', '.join((special_tags or tags)[:4])}
Mevcut: {existing_summary}

Kuralllar:
- "X mahallesinde bulunan bir restoran" yazma, dogrudan restorani anlat
- Somut detay ver: hangi yemekler, nasil atmosfer, kime uygun
- Sadece 4 cumle yaz, baska hicbir sey ekleme"""

    resp = None
    for attempt in range(len(GROQ_API_KEYS) * 3):
        try:
            c = get_client()
            resp = c.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,
                temperature=0.7,
            )
            break
        except Exception as e:
            if "429" in str(e):
                _key_index += 1
                print(f"  [RATE LIMIT] key{(_key_index % len(GROQ_API_KEYS)) + 1}, 10s...", flush=True)
                time.sleep(10)
            else:
                print(f"  [ERROR] {str(e)[:60]}", flush=True)
                return {}

    if resp is None:
        return {}

    text = resp.choices[0].message.content.strip()
    if not text:
        return {}
    # Tum metni llm_summary olarak kullan
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    summary = " ".join(lines[:4])  # ilk 4 cumle
    return {"llm_summary": summary}


def main():
    input_path = "data/processed/istanbul.json"

    with open(input_path, encoding="utf-8") as f:
        restaurants = json.load(f)

    # has_reviews olmayanlari isle (zaten gercek yorumlu olanlar dokunma)
    todo = [r for r in restaurants if not r.get("has_reviews")]
    total = len(todo)
    print(f"[INFO] {total} restoran icin ozet uretiliyor...", flush=True)

    for i, r in enumerate(todo):
        name_safe = r["name"].encode("ascii", "replace").decode()
        print(f"[{i+1}/{total}] {name_safe}", flush=True)

        result = generate_summary(r)
        if result.get("llm_summary"):
            for orig in restaurants:
                if orig["id"] == r["id"]:
                    orig["llm_summary"] = result["llm_summary"]
                    if result.get("sentiment_summary"):
                        orig["sentiment_summary"] = result["sentiment_summary"]
                    if result.get("highlights"):
                        orig["highlights"] = result["highlights"]
                    orig["has_reviews"] = True
                    break
            print(f"  OK: {result['llm_summary'][:60].encode('ascii','replace').decode()}", flush=True)
        else:
            print(f"  ATLANDI", flush=True)

        if (i + 1) % 20 == 0:
            with open(input_path, "w", encoding="utf-8") as f:
                json.dump(restaurants, f, ensure_ascii=False, indent=2)
            done = sum(1 for r in restaurants if r.get("has_reviews"))
            print(f">>> KAYIT: {i+1}/{total} | Toplam: {done}/453", flush=True)

        time.sleep(2)

    with open(input_path, "w", encoding="utf-8") as f:
        json.dump(restaurants, f, ensure_ascii=False, indent=2)

    done = sum(1 for r in restaurants if r.get("has_reviews"))
    print(f"\n[OK] {done}/453 restoran tamamlandi", flush=True)
    print("[SONRAKI] python scripts/json_to_ts.py", flush=True)


if __name__ == "__main__":
    main()
