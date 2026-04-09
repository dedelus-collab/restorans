# -*- coding: utf-8 -*-
"""
Restoranlar icin FAQ + dataFreshness alanlari uretir.
Kullanim: python scripts/enrich_faq.py
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


def generate_faq(r: dict) -> list:
    global _key_index

    name = r.get("name", "")
    cuisine = r.get("cuisine") or "Türk mutfağı"
    price = r.get("price_range", 2)
    tags = r.get("tags") or []
    features = r.get("features") or {}
    sf = r.get("special_features") or {}
    opening_hours = r.get("opening_hours", "")
    llm_summary = r.get("llm_summary", "")[:150]

    has_wifi = features.get("wifi")
    has_reservation = features.get("reservation") or features.get("rezervasyon")
    has_parking = features.get("parking")
    has_terrace = features.get("terrace") or features.get("teras")
    has_vegan = features.get("vegan") or sf.get("dietaryOptions")
    price_label = {1: "çok uygun", 2: "orta", 3: "üst segment", 4: "fine dining"}.get(price, "orta")
    noise = sf.get("noiseLevel", "orta")
    is_late = any(t in " ".join(tags).lower() for t in ["gece", "geç saate"])

    prompt = f"""Restoran: {name} | {cuisine} | {price_label} fiyat
WiFi: {has_wifi} | Rezervasyon: {has_reservation} | Otopark: {has_parking}
Teras: {has_terrace} | Vegan: {has_vegan} | Gurultu: {noise}
Gec acik: {is_late} | Saatler: {opening_hours}
Ozet: {llm_summary}
Etiketler: {', '.join(tags[:5])}

Bu restoran icin kullanicilarin sik sordugu 5 soruyu ve kisa Turkce cevaplarini yaz.
Gercekci ol — bilmiyorsan "Bilgi mevcut degil" de.

SADECE su JSON formatini don:
[
  {{"q": "Kredi karti geciyor mu?", "a": "Evet, kart kabul ediliyor."}},
  {{"q": "Rezervasyon gerekli mi?", "a": "..."}},
  {{"q": "Cocuk sandalyesi var mi?", "a": "..."}},
  {{"q": "Vejetaryen secenekler var mi?", "a": "..."}},
  {{"q": "Disaridan icecek getirilebilir mi?", "a": "..."}}
]"""

    resp = None
    for attempt in range(len(GROQ_API_KEYS) * 3):
        try:
            c = get_client()
            resp = c.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,
                temperature=0.3,
            )
            break
        except Exception as e:
            if "429" in str(e):
                _key_index += 1
                print(f"  [RATE LIMIT] key{(_key_index % len(GROQ_API_KEYS)) + 1}, 10s...", flush=True)
                time.sleep(10)
            else:
                print(f"  [ERROR] {str(e)[:60]}", flush=True)
                return []

    if resp is None:
        return []

    text = resp.choices[0].message.content.strip()
    try:
        start = text.find("[")
        end = text.rfind("]") + 1
        if start >= 0 and end > start:
            data = json.loads(text[start:end])
            return [{"question": item["q"], "answer": item["a"]} for item in data if item.get("q") and item.get("a")]
    except Exception as e:
        print(f"  [PARSE ERROR] {str(e)[:40]}", flush=True)
    return []


def build_freshness(r: dict) -> dict:
    last_updated = r.get("last_updated", "2026-04-06")
    has_reviews = r.get("has_reviews", False)
    confidence = r.get("confidence_score", 0.8)

    if confidence >= 0.95 and has_reviews:
        freshness = "Yüksek"
        source = "Google Maps yorumları + doğrulanmış veri"
    elif confidence >= 0.85:
        freshness = "Orta"
        source = "OpenStreetMap + otomatik zenginleştirme"
    else:
        freshness = "Tahmini"
        source = "OpenStreetMap verisi"

    return {
        "lastVerified": last_updated,
        "source": source,
        "confidence": freshness,
    }


def main():
    input_path = "data/processed/istanbul.json"

    with open(input_path, encoding="utf-8") as f:
        restaurants = json.load(f)

    total = len(restaurants)
    print(f"[INFO] {total} restoran icin FAQ uretiliyor...", flush=True)

    for i, r in enumerate(restaurants):
        name_safe = r["name"].encode("ascii", "replace").decode()
        print(f"[{i+1}/{total}] {name_safe}", flush=True)

        # dataFreshness kural tabanli - hep ekle
        r["data_freshness"] = build_freshness(r)

        # FAQ Groq ile
        faq = generate_faq(r)
        if faq:
            r["faq"] = faq
            print(f"  OK: {len(faq)} soru", flush=True)
        else:
            print(f"  ATLANDI", flush=True)

        if (i + 1) % 20 == 0:
            with open(input_path, "w", encoding="utf-8") as f:
                json.dump(restaurants, f, ensure_ascii=False, indent=2)
            done = sum(1 for r in restaurants if r.get("faq"))
            print(f">>> KAYIT: {i+1}/{total} | FAQ olan: {done}/{total}", flush=True)

        time.sleep(2)

    with open(input_path, "w", encoding="utf-8") as f:
        json.dump(restaurants, f, ensure_ascii=False, indent=2)

    done = sum(1 for r in restaurants if r.get("faq"))
    print(f"\n[OK] {done}/{total} restoran FAQ ile tamamlandi", flush=True)
    print("[SONRAKI] python scripts/json_to_ts.py", flush=True)


if __name__ == "__main__":
    main()
