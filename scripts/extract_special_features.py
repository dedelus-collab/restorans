# -*- coding: utf-8 -*-
"""
Mevcut restoran verisinden specialFeatures alanlarini cikarir.

Kural tabanli (tum restoranlar):
  - contextualRatings: tags'ten
  - dietaryOptions: tags + features'ten
  - noiseLevel: tags'ten
  - avgMealCost: priceRange'ten

Groq tabanli (has_reviews olan restoranlar):
  - signatureDishes: llm_summary + highlights'ten
  - criticalMinus: sentiment_summary'den
  - standoutPlus: sentiment_summary'den

Kullanim:
  python scripts/extract_special_features.py
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

def next_client():
    global _key_index
    _key_index += 1
    return Groq(api_key=GROQ_API_KEYS[_key_index % len(GROQ_API_KEYS)])

PRICE_COST_MAP = {1: 150, 2: 350, 3: 700, 4: 1400}


def rule_based_features(r: dict) -> dict:
    tags = [t.lower() for t in (r.get("tags") or [])]
    features = r.get("features") or {}
    price_range = r.get("price_range", 2)

    result = {}

    # contextualRatings
    ratings = {}
    if any(t in tags for t in ["is yemegi", "i\u015f yeme\u011fi", "business"]):
        ratings["businessLunch"] = 4
    if any(t in tags for t in ["romantik", "romantic", "\u00e7ift", "sevgililer"]):
        ratings["romanticDate"] = 5 if price_range >= 3 else 4
    if any(t in tags for t in ["aile dostu", "aile", "family"]):
        ratings["familyDining"] = 4
    if any(t in tags for t in ["b\u00fcy\u00fck grup", "grup", "group"]):
        ratings["groupDining"] = 4
    if any(t in tags for t in ["laptop", "co-working", "sakin"]):
        ratings["soloVisit"] = 4

    # Default businessLunch for mid/high price restaurants
    if price_range >= 2 and "businessLunch" not in ratings:
        ratings["businessLunch"] = 3

    if ratings:
        result["contextualRatings"] = ratings

    # dietaryOptions
    dietary = []
    if features.get("vegan") or any(t in tags for t in ["vegan"]):
        dietary.append("Vegan")
    if any(t in tags for t in ["vejet", "vejeteryan", "vegetarian"]):
        dietary.append("Vejetaryen")
    if any(t in tags for t in ["helal", "halal"]):
        dietary.append("Helal")
    if any(t in tags for t in ["gl\u00fcten", "gluten", "sa\u011fl\u0131kl\u0131", "diyetik"]):
        dietary.append("Gl\u00fcten \u0130\u00e7ermez")
    if dietary:
        result["dietaryOptions"] = dietary

    # noiseLevel
    if any(t in tags for t in ["canl\u0131 m\u00fczik", "live music", "parti", "gece kul\u00fcb\u00fc", "bar"]):
        result["noiseLevel"] = "y\u00fcksek"
    elif any(t in tags for t in ["romantik", "sakin", "huzurlu", "sessiz"]):
        result["noiseLevel"] = "d\u00fc\u015f\u00fck"
    else:
        result["noiseLevel"] = "orta"

    # avgMealCost
    result["avgMealCost"] = PRICE_COST_MAP.get(price_range, 350)

    # laptopFriendly
    if features.get("laptopFriendly") or features.get("wifi") or any(t in tags for t in ["laptop", "wifi"]):
        result["laptopFriendly"] = True

    return result


def groq_extract(client: Groq, r: dict) -> dict:
    llm_summary = r.get("llm_summary", "")
    sentiment = r.get("sentiment_summary", "")
    highlights = r.get("highlights") or []
    cuisine = r.get("cuisine", "")

    highlights_text = ", ".join(highlights[:5]) if highlights else ""

    prompt = f"""Asagidaki restoran bilgilerine bakarak JSON formatinda cevap ver.

Restoran: {r['name']}
Mutfak: {cuisine}
LLM Ozeti: {llm_summary}
Duygu Analizi: {sentiment}
One Cikanlar: {highlights_text}

Asagidaki alanlari cikar ve SADECE JSON olarak don (baska hicbir sey yazma):
{{
  "signatureDishes": ["yemek1", "yemek2"],
  "standoutPlus": "en iyi tek ozellik - somut, max 15 kelime",
  "criticalMinus": "en buyuk eksik - somut, max 15 kelime"
}}

Kurallar:
- signatureDishes: 2-4 somut yemek adi (yoksa bos liste)
- standoutPlus: somut ozellik ("Lezzetli yemekler" degil, "Taze levrek tava ve sicak servis" gibi)
- criticalMinus: somut sorun ("Bekleme suresi uzun" veya "Hafta sonu rezervasyon zor" gibi)"""

    for attempt in range(3):
        try:
            resp = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.3,
            )
            text = resp.choices[0].message.content.strip()
            # JSON parcala
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(text[start:end])
        except Exception as e:
            if "429" in str(e):
                client = next_client()
                print(f"  [RATE LIMIT] Key degistiriliyor...", flush=True)
                time.sleep(2)
            else:
                print(f"  [GROQ ERROR] {str(e)[:60]}", flush=True)
                break
    return {}


def main():
    input_path = "data/processed/istanbul.json"
    output_path = "data/processed/istanbul.json"

    with open(input_path, encoding="utf-8") as f:
        restaurants = json.load(f)

    client = Groq(api_key=GROQ_API_KEYS[0])

    reviewed = [r for r in restaurants if r.get("has_reviews")]
    total = len(restaurants)

    print(f"[INFO] {total} restoran isleniyor ({len(reviewed)} yorumlu)...", flush=True)

    # Adim 1: Kural tabanli - tum restoranlar
    print("[ADIM 1] Kural tabanli ozellikler dolduruluyor...", flush=True)
    for r in restaurants:
        sf = rule_based_features(r)
        existing = r.get("special_features") or {}
        # Mevcut alanlari koruyarak birle
        for k, v in sf.items():
            if k not in existing:
                existing[k] = v
        r["special_features"] = existing

    print(f"  Kural tabanli tamamlandi: {total} restoran", flush=True)

    # Adim 2: Groq - yorumlu restoranlar
    print(f"[ADIM 2] Groq ile {len(reviewed)} yorumlu restoran zenginlestiriliyor...", flush=True)
    for i, r in enumerate(reviewed):
        name_safe = r["name"].encode("ascii", "replace").decode()
        print(f"[{i+1}/{len(reviewed)}] {name_safe}", flush=True)

        result = groq_extract(client, r)
        if result:
            sf = r.get("special_features") or {}
            if result.get("signatureDishes"):
                sf["signatureDishes"] = result["signatureDishes"]
            if result.get("standoutPlus"):
                sf["standoutPlus"] = result["standoutPlus"]
            if result.get("criticalMinus"):
                sf["criticalMinus"] = result["criticalMinus"]
            r["special_features"] = sf
            print(f"  OK: {result.get('standoutPlus', '')[:50].encode('ascii', 'replace').decode()}", flush=True)

        if (i + 1) % 10 == 0:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(restaurants, f, ensure_ascii=False, indent=2)
            print(f">>> KAYIT: {i+1}/{len(reviewed)}", flush=True)

        time.sleep(1)

    # Son kayit
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(restaurants, f, ensure_ascii=False, indent=2)

    enriched = sum(1 for r in restaurants if r.get("special_features"))
    print(f"\n[OK] {enriched}/{total} restoran special_features ile zenginlestirildi", flush=True)
    print("[SONRAKI] python scripts/json_to_ts.py", flush=True)


if __name__ == "__main__":
    main()
