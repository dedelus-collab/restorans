# -*- coding: utf-8 -*-
"""
Her restoran icin restoran ozelinde 10-12 sorudan olusan zengin FAQ uretir.
Nearby (transit/landmark) + popularDishes + features + cuisine kullanir.

Kullanim: python scripts/enrich_faq2.py
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


def build_prompt(r: dict) -> str:
    name = r.get("name", "")
    cuisine = r.get("cuisine") or "Turk mutfagi"
    neighborhood = r.get("neighborhood", "")
    tags = r.get("tags") or []
    features = r.get("features") or {}
    sf = r.get("special_features") or {}
    nearby = r.get("nearby") or {}
    opening = r.get("opening_hours") or ""
    price = r.get("price_range", 2)
    price_label = {1: "ekonomik (kisi basi ~150-250TL)", 2: "orta (kisi basi ~300-600TL)", 3: "ust segment (kisi basi ~700-1500TL)", 4: "fine dining (kisi basi 1500TL+)"}.get(price, "orta")

    popular = sf.get("popularDishes") or []
    transit = nearby.get("transit") or []
    landmarks = nearby.get("landmarks") or []

    transit_str = " | ".join(f"{t['name']} ({t['type']}, {t['walk_min']}dk)" for t in transit[:3])
    landmark_str = " | ".join(f"{l['name']} ({l['walk_min']}dk)" for l in landmarks[:3])
    popular_str = ", ".join(popular[:5])

    has_wifi = features.get("wifi")
    has_reservation = features.get("reservation") or features.get("rezervasyon")
    has_parking = features.get("parking")
    has_terrace = features.get("terrace") or features.get("teras")
    has_vegan = features.get("vegan")
    has_sea_view = features.get("seaView")
    has_romantic = features.get("romantic")

    prompt = f"""Restoran: {name}
Mutfak: {cuisine}
Mahalle: {neighborhood}
Fiyat: {price_label}
Acilis saatleri: {opening or "bilinmiyor"}
Etiketler: {', '.join(tags[:6])}
WiFi:{has_wifi} | Rezervasyon:{has_reservation} | Otopark:{has_parking} | Teras:{has_terrace} | Vegan:{has_vegan} | Deniz manzarasi:{has_sea_view} | Romantik:{has_romantic}
Populer yemekler: {popular_str or "bilinmiyor"}
Yakin transit: {transit_str or "yok"}
Yakin landmark: {landmark_str or "yok"}

Bu restorana ozgu 10-12 adet Turkce soru-cevap yaz.
Sorular cesitli ve spesifik olsun:
- Fiyat/odeme bilgileri
- Ulasim (transit bilgisi varsa kullan)
- Rezervasyon
- Populer yemekler (varsa yemek isimlerini kullan)
- Konum avantajlari (landmark varsa bahset)
- Diyet/alerji secenekleri
- Ortam/atmosfer
- Cocuklar/aileler icin uygunluk
- Ozel gunler/organizasyon
- En az 1 "neden bu restorana gideyim" sorusu

SADECE JSON array don, baska hicbir sey ekleme:
[
  {{"q": "soru metni", "a": "cevap metni"}},
  ...
]"""
    return prompt


def generate_faq(r: dict) -> list:
    global _key_index
    prompt = build_prompt(r)

    for attempt in range(len(GROQ_API_KEYS) * 3):
        try:
            c = get_client()
            resp = c.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                temperature=0.3,
            )
            text = resp.choices[0].message.content.strip()
            start = text.find("[")
            end = text.rfind("]") + 1
            if start >= 0 and end > start:
                data = json.loads(text[start:end])
                items = [
                    {"question": item["q"], "answer": item["a"]}
                    for item in data
                    if item.get("q") and item.get("a")
                ]
                return items[:12]
            return []
        except Exception as e:
            err = str(e)
            if "429" in err or "rate" in err.lower():
                _key_index += 1
                print(f"  [RATE] key rotate, 8s...", flush=True)
                time.sleep(8)
            else:
                print(f"  [ERR] {err[:60]}", flush=True)
                return []
    return []


def main():
    with open(INPUT, encoding="utf-8") as f:
        restaurants = json.load(f)

    total = len(restaurants)
    # Tum restoranlari yeniden isle (eski 5 soruluk FAQ'lari uc: daha iyi yapacagiz)
    print(f"[INFO] {total} restoran icin zengin FAQ uretiliyor (10-12 soru)...", flush=True)

    done = 0
    for i, r in enumerate(restaurants):
        name_safe = r["name"].encode("ascii", "replace").decode()
        print(f"[{i+1}/{total}] {name_safe}", flush=True, end="")

        faq = generate_faq(r)
        if faq:
            r["faq"] = faq
            done += 1
            print(f" -> {len(faq)} soru", flush=True)
        else:
            print(f" -> bos", flush=True)

        if (i + 1) % SAVE_EVERY == 0:
            with open(INPUT, "w", encoding="utf-8") as f:
                json.dump(restaurants, f, ensure_ascii=False, indent=2)
            print(f">>> KAYIT {i+1}/{total} | Yeni: {done}", flush=True)

        time.sleep(1.8)

    with open(INPUT, "w", encoding="utf-8") as f:
        json.dump(restaurants, f, ensure_ascii=False, indent=2)

    print(f"\n[OK] {done}/{total} restoran zengin FAQ aldi", flush=True)
    print("[SONRAKI] python scripts/json_to_ts.py", flush=True)


if __name__ == "__main__":
    main()
