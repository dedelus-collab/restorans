# -*- coding: utf-8 -*-
"""
Restoranlar icin senaryo bazli ozetler uretir.
Kullanim: python scripts/enrich_scenarios.py
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


def generate_scenarios(r: dict) -> dict:
    global _key_index

    name = r.get("name", "")
    neighborhood = r.get("neighborhood", "")
    cuisine = r.get("cuisine") or "Turk mutfagi"
    rating = r.get("avg_rating") or 0
    price = r.get("price_range", 2)
    tags = r.get("tags") or []
    features = r.get("features") or {}
    llm_summary = r.get("llm_summary", "")
    sf = r.get("special_features") or {}
    opening_hours = r.get("opening_hours", "")

    price_label = {1: "cok uygun (kisi basi ~150TL)", 2: "orta (kisi basi ~350TL)",
                   3: "ust segment (kisi basi ~700TL)", 4: "fine dining (kisi basi ~1400TL)"}.get(price, "orta")

    has_terrace = features.get("terrace") or features.get("teras")
    has_reservation = features.get("reservation") or features.get("rezervasyon")
    has_vegan = features.get("vegan") or "vegan" in " ".join(tags).lower()
    is_late = any(t in " ".join(tags).lower() for t in ["gece", "gec saate", "gec saate kadar"])
    dietary = sf.get("dietaryOptions") or []
    noise = sf.get("noiseLevel", "orta")
    cr = sf.get("contextualRatings") or {}

    prompt = f"""Restoran bilgileri:
Ad: {name} | Konum: {neighborhood} | Mutfak: {cuisine}
Puan: {rating}/5 | Fiyat: {price_label}
Teras: {has_terrace} | Rezervasyon: {has_reservation} | Vegan: {has_vegan}
Gec acik: {is_late} | Gurultu: {noise} | Diyet: {', '.join(dietary) or 'yok'}
Calisma saatleri: {opening_hours}
Ozet: {llm_summary[:150]}
Etiketler: {', '.join(tags[:6])}

Asagidaki senaryolar icin BU RESTORANA OZEL kisa Turkce aciklama yaz (max 15 kelime).
Uygun degilse "null" yaz.

SADECE su JSON formatini don, baska hicbir sey yazma:
{{
  "birthday": "...",
  "budget": "...",
  "vegetarian": "...",
  "quickLunch": "...",
  "tourist": "...",
  "romantic": "...",
  "family": "...",
  "lateNight": "..."
}}"""

    resp = None
    for attempt in range(len(GROQ_API_KEYS) * 3):
        try:
            c = get_client()
            resp = c.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.4,
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
    try:
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            data = json.loads(text[start:end])
            # null string olanları temizle
            return {k: v for k, v in data.items() if v and isinstance(v, str) and v.lower() != "null" and len(v) > 3}
    except Exception as e:
        print(f"  [PARSE ERROR] {str(e)[:40]}", flush=True)
    return {}


def main():
    input_path = "data/processed/istanbul.json"

    with open(input_path, encoding="utf-8") as f:
        restaurants = json.load(f)

    total = len(restaurants)
    print(f"[INFO] {total} restoran icin senaryo ozetleri uretiliyor...", flush=True)

    for i, r in enumerate(restaurants):
        name_safe = r["name"].encode("ascii", "replace").decode()
        print(f"[{i+1}/{total}] {name_safe}", flush=True)

        result = generate_scenarios(r)
        if result:
            r["scenario_summary"] = result
            keys = list(result.keys())
            print(f"  OK: {keys}", flush=True)
        else:
            print(f"  ATLANDI", flush=True)

        if (i + 1) % 20 == 0:
            with open(input_path, "w", encoding="utf-8") as f:
                json.dump(restaurants, f, ensure_ascii=False, indent=2)
            done = sum(1 for r in restaurants if r.get("scenario_summary"))
            print(f">>> KAYIT: {i+1}/{total} | Senaryo olan: {done}/{total}", flush=True)

        time.sleep(2)

    with open(input_path, "w", encoding="utf-8") as f:
        json.dump(restaurants, f, ensure_ascii=False, indent=2)

    done = sum(1 for r in restaurants if r.get("scenario_summary"))
    print(f"\n[OK] {done}/{total} restoran senaryo ozeti ile tamamlandi", flush=True)
    print("[SONRAKI] python scripts/json_to_ts.py", flush=True)


if __name__ == "__main__":
    main()
