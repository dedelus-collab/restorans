# -*- coding: utf-8 -*-
"""
FAQ sorularini cesitlendirir.
366 restoranin tamaminda olan "Neden bu restorana gideyim?" gibi
generic sorulari restorana ozgu sorularla replace eder.

Yontem:
- Her restoran icin name, cuisine, nearby, popularDishes, tags gonder
- Groq'tan 3-4 OZGUN soru uret (genel sorular degil)
- Mevcut FAQ'a ekle, duplicate kontrolu yap
- Generic soruları cıkar
"""
import json
import time
import re
from groq import Groq

INPUT = "data/processed/istanbul.json"
SAVE_EVERY = 25

GROQ_API_KEYS = [
    "os.environ.get("GROQ_API_KEY_1", "")",
    "os.environ.get("GROQ_API_KEY_2", "")",
]
_key_index = 0

# Bu sorular generic — kaldırılacak veya replace edilecek
GENERIC_QUESTIONS = {
    "neden bu restorana gideyim",
    "neden bu restorana gitmeliyim",
    "bu restorani neden tercih etmeliyim",
}

def get_client():
    return Groq(api_key=GROQ_API_KEYS[_key_index % len(GROQ_API_KEYS)])


def build_unique_prompt(r: dict, existing_questions: list[str]) -> str:
    name = r.get("name", "")
    cuisine = r.get("cuisine") or "Türk mutfağı"
    neighborhood = r.get("neighborhood", "")
    tags = r.get("tags") or []
    sf = r.get("special_features") or {}
    nearby = r.get("nearby") or {}
    dishes = sf.get("popularDishes") or []
    transit = nearby.get("transit") or []
    landmarks = nearby.get("landmarks") or []
    price = r.get("price_range", 2)
    features = r.get("features") or {}

    transit_str = ", ".join(f"{t['name']} ({t['walk_min']}dk)" for t in transit[:2])
    landmark_str = ", ".join(f"{l['name']}" for l in landmarks[:2])
    dishes_str = ", ".join(dishes[:4])
    price_label = {1: "ekonomik", 2: "orta", 3: "üst segment", 4: "fine dining"}.get(price, "orta")
    existing_str = " | ".join(existing_questions[:8])

    prompt = f"""Restoran: {name} ({cuisine}, {neighborhood}, {price_label})
Populer yemekler: {dishes_str or "bilinmiyor"}
Yakin transit: {transit_str or "yok"}
Yakin landmark: {landmark_str or "yok"}
Etiketler: {", ".join(tags[:5])}
Teras: {features.get("terrace") or features.get("teras")}, Rezervasyon: {features.get("reservation") or features.get("rezervasyon")}

Mevcut sorular (bunlari TEKRARLAMA): {existing_str}

Bu restorana OZGU, spesifik 3 soru-cevap uret.
- Mevcut sorularda olmayan konular sec
- Restoranin adini, mutfagini, konumunu, populer yemeklerini, yakin yerleri kullan
- "Neden gitmeliyim" gibi generic sorular YAZMA
- Sorular kisa, cevaplar 1-2 cumle

SADECE JSON array don:
[{{"q": "...", "a": "..."}}, ...]"""
    return prompt


def generate_unique_questions(r: dict, existing_questions: list[str]) -> list:
    global _key_index
    prompt = build_unique_prompt(r, existing_questions)

    for attempt in range(len(GROQ_API_KEYS) * 3):
        try:
            c = get_client()
            resp = c.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,
                temperature=0.5,
            )
            text = resp.choices[0].message.content.strip()
            start = text.find("[")
            end = text.rfind("]") + 1
            if start >= 0 and end > start:
                data = json.loads(text[start:end])
                return [{"question": x["q"], "answer": x["a"]}
                        for x in data if x.get("q") and x.get("a")]
            return []
        except Exception as e:
            err = str(e)
            if "429" in err or "rate" in err.lower():
                _key_index += 1
                print(f"  [RATE] rotate, 8s...", flush=True)
                time.sleep(8)
            else:
                print(f"  [ERR] {err[:60]}", flush=True)
                return []
    return []


def main():
    with open(INPUT, encoding="utf-8") as f:
        restaurants = json.load(f)

    total = len(restaurants)
    enriched = 0

    for i, r in enumerate(restaurants):
        name_safe = r["name"].encode("ascii", "replace").decode()
        faq = r.get("faq") or []

        existing_questions = [q["question"].lower().strip() for q in faq]

        # Generic soruları bul ve kaldır
        filtered_faq = [
            q for q in faq
            if not any(
                re.search(g, q["question"].lower())
                for g in GENERIC_QUESTIONS
            )
        ]
        removed = len(faq) - len(filtered_faq)

        # Yeni ozgun sorular uret
        new_qs = generate_unique_questions(r, existing_questions)

        # Duplicate kontrolu
        final_new = []
        for nq in new_qs:
            nq_lower = nq["question"].lower().strip()
            is_dup = any(
                nq_lower in eq or eq in nq_lower
                for eq in existing_questions
            )
            if not is_dup:
                final_new.append(nq)
                existing_questions.append(nq_lower)

        r["faq"] = filtered_faq + final_new
        if removed or final_new:
            enriched += 1

        safe_new = [q["question"].encode("ascii","replace").decode()[:40] for q in final_new]
        print(f"[{i+1}/{total}] {name_safe} | -{removed} generic +{len(final_new)} ozgun | {safe_new}", flush=True)

        if (i + 1) % SAVE_EVERY == 0:
            with open(INPUT, "w", encoding="utf-8") as f:
                json.dump(restaurants, f, ensure_ascii=False, indent=2)
            print(f">>> KAYIT {i+1}/{total}", flush=True)

        time.sleep(1.5)

    with open(INPUT, "w", encoding="utf-8") as f:
        json.dump(restaurants, f, ensure_ascii=False, indent=2)

    print(f"\n[OK] {enriched}/{total} restoran FAQ guncellendi", flush=True)
    print("[SONRAKI] python scripts/json_to_ts.py", flush=True)


if __name__ == "__main__":
    main()
