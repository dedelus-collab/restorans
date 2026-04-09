# -*- coding: utf-8 -*-
"""
Her restoran icin "likely signature/popular dishes" listesi uretir.
Kaynak: name, cuisine, neighborhood, llm_summary, tags, nearby landmarks.
Etiketleme: "popularDishes" (tahmini/ogrenimsel, gercek menu degil).

Kullanim: python scripts/enrich_popular_dishes.py
"""

import json
import time
from groq import Groq

INPUT = "data/processed/istanbul.json"
SAVE_EVERY = 20

GROQ_API_KEYS = [
    "os.environ.get("GROQ_API_KEY_1", "")",
    "os.environ.get("GROQ_API_KEY_2", "")",
]
_key_index = 0


def get_client():
    return Groq(api_key=GROQ_API_KEYS[_key_index % len(GROQ_API_KEYS)])


def generate_dishes(r: dict) -> list:
    global _key_index

    name = r.get("name", "")
    cuisine = r.get("cuisine") or "Turk mutfagi"
    neighborhood = r.get("neighborhood", "")
    tags = r.get("tags") or []
    llm_summary = (r.get("llm_summary") or "")[:200]
    price = r.get("price_range", 2)
    price_label = {1: "ekonomik", 2: "orta", 3: "ust segment", 4: "fine dining"}.get(price, "orta")

    prompt = f"""Restoran: {name}
Mutfak: {cuisine}
Mahalle: {neighborhood}
Fiyat: {price_label}
Etiketler: {', '.join(tags[:5])}
Aciklama: {llm_summary}

Bu restoran icin 4-6 adet populer/imza yemek tahminini Turkce olarak ver.
- Restoranin mutfagina ve genel bilinirligine uygun olsun
- Her yemek 2-5 kelime, acilirse kisa parantez aciklamasi
- Tahmini olduklarinin farkinda ol, gercekci ol

SADECE JSON array don:
["yemek1", "yemek2", "yemek3", "yemek4"]"""

    for attempt in range(len(GROQ_API_KEYS) * 3):
        try:
            c = get_client()
            resp = c.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=250,
                temperature=0.4,
            )
            text = resp.choices[0].message.content.strip()
            start = text.find("[")
            end = text.rfind("]") + 1
            if start >= 0 and end > start:
                data = json.loads(text[start:end])
                cleaned = [str(x).strip() for x in data if x and isinstance(x, str)]
                return cleaned[:6]
            return []
        except Exception as e:
            err = str(e)
            if "429" in err or "rate" in err.lower():
                _key_index += 1
                print(f"  [RATE LIMIT] key rotate, 8s...", flush=True)
                time.sleep(8)
            else:
                print(f"  [ERR] {err[:60]}", flush=True)
                return []
    return []


def main():
    with open(INPUT, encoding="utf-8") as f:
        restaurants = json.load(f)

    total = len(restaurants)
    targets = [r for r in restaurants if not (r.get("special_features", {}) or {}).get("popularDishes")]
    print(f"[INFO] {len(targets)}/{total} restorana populer yemek eklenecek", flush=True)

    done = 0
    for i, r in enumerate(restaurants):
        sf = r.get("special_features") or {}
        if sf.get("popularDishes"):
            continue

        name_safe = r["name"].encode("ascii", "replace").decode()
        print(f"[{i+1}/{total}] {name_safe}", flush=True, end="")

        dishes = generate_dishes(r)
        if dishes:
            sf["popularDishes"] = dishes
            r["special_features"] = sf
            done += 1
            safe = " | ".join(d.encode("ascii", "replace").decode() for d in dishes[:3])
            print(f" -> OK ({len(dishes)}): {safe}", flush=True)
        else:
            print(f" -> bos", flush=True)

        if (i + 1) % SAVE_EVERY == 0:
            with open(INPUT, "w", encoding="utf-8") as f:
                json.dump(restaurants, f, ensure_ascii=False, indent=2)
            total_done = sum(
                1 for x in restaurants if (x.get("special_features") or {}).get("popularDishes")
            )
            print(f">>> KAYIT {i+1}/{total} | Yeni: {done} | Toplam: {total_done}/{total}", flush=True)

        time.sleep(1.5)

    with open(INPUT, "w", encoding="utf-8") as f:
        json.dump(restaurants, f, ensure_ascii=False, indent=2)

    total_done = sum(
        1 for x in restaurants if (x.get("special_features") or {}).get("popularDishes")
    )
    print(f"\n[OK] +{done} yeni | Toplam: {total_done}/{total}", flush=True)


if __name__ == "__main__":
    main()
