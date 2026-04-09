# -*- coding: utf-8 -*-
"""
Menü öğeleri ve fiyat detayı ekler.
Kullanim: python scripts/enrich_menu_price.py
"""

import json
import time
from groq import Groq

GROQ_API_KEYS = [
    "os.environ.get("GROQ_API_KEY_1", "")",
    "os.environ.get("GROQ_API_KEY_2", "")",
]
_key_index = 0

def get_client():
    return Groq(api_key=GROQ_API_KEYS[_key_index % len(GROQ_API_KEYS)])

PRICE_RANGES = {
    1: {"starter": "40-80", "main": "80-150", "dessert": "30-60",  "drink": "20-50"},
    2: {"starter": "80-150", "main": "200-400", "dessert": "60-120", "drink": "50-100"},
    3: {"starter": "150-300", "main": "400-800", "dessert": "120-200", "drink": "100-200"},
    4: {"starter": "300-600", "main": "800-2000", "dessert": "200-400", "drink": "200-500"},
}

def build_price_detail(r: dict) -> dict:
    pr = r.get("price_range", 2)
    p = PRICE_RANGES.get(pr, PRICE_RANGES[2])
    return {
        "starterRange": f"{p['starter']} TL",
        "mainCourseRange": f"{p['main']} TL",
        "dessertRange": f"{p['dessert']} TL",
        "drinkRange": f"{p['drink']} TL",
        "avgPerPerson": f"{r.get('special_features', {}).get('avgMealCost', 350)} TL",
    }

def generate_menu(r: dict) -> list:
    global _key_index

    cuisine = r.get("cuisine") or "Türk mutfağı"
    name = r.get("name", "")
    tags = r.get("tags") or []
    sf = r.get("special_features") or {}
    existing = sf.get("signatureDishes") or []

    prompt = f"""Restoran: {name} | Mutfak: {cuisine}
Etiketler: {', '.join(tags[:5])}
Bilinen yemekler: {', '.join(existing)}

Bu restoranda tipik olarak bulunabilecek 6-8 menü öğesi listele.
Türkçe isimler kullan. Sadece JSON array döndür:
["yemek1", "yemek2", "yemek3", "yemek4", "yemek5", "yemek6"]"""

    resp = None
    for attempt in range(len(GROQ_API_KEYS) * 3):
        try:
            c = get_client()
            resp = c.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.4,
            )
            break
        except Exception as e:
            if "429" in str(e):
                _key_index += 1
                print(f"  [RATE LIMIT] key{(_key_index % len(GROQ_API_KEYS))+1}, 10s...", flush=True)
                time.sleep(10)
            else:
                return []

    if resp is None:
        return []

    text = resp.choices[0].message.content.strip()
    try:
        start = text.find("[")
        end = text.rfind("]") + 1
        if start >= 0 and end > start:
            items = json.loads(text[start:end])
            return [i for i in items if isinstance(i, str) and len(i) > 1][:8]
    except:
        pass
    return []


def main():
    input_path = "data/processed/istanbul.json"

    with open(input_path, encoding="utf-8") as f:
        restaurants = json.load(f)

    total = len(restaurants)
    print(f"[INFO] {total} restoran icin menu + fiyat detayi uretiliyor...", flush=True)

    for i, r in enumerate(restaurants):
        name_safe = r["name"].encode("ascii", "replace").decode()
        print(f"[{i+1}/{total}] {name_safe}", flush=True)

        # Fiyat detayı - kural tabanlı, hep ekle
        r["price_detail"] = build_price_detail(r)

        if (i + 1) % 20 == 0:
            with open(input_path, "w", encoding="utf-8") as f:
                json.dump(restaurants, f, ensure_ascii=False, indent=2)
            done = sum(1 for r in restaurants if r.get("menu_items"))
            print(f">>> KAYIT: {i+1}/{total} | Menu olan: {done}/{total}", flush=True)

        time.sleep(0.1)

    with open(input_path, "w", encoding="utf-8") as f:
        json.dump(restaurants, f, ensure_ascii=False, indent=2)

    done = sum(1 for r in restaurants if r.get("menu_items"))
    print(f"\n[OK] {done}/{total} restoran menu ile tamamlandi", flush=True)


if __name__ == "__main__":
    main()
