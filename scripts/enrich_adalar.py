# -*- coding: utf-8 -*-
"""Adalar restoranlarına Groq ile FAQ ve sentimentSummary ekler."""
import json, os, re, sys, time
sys.stdout.reconfigure(encoding="utf-8")

# .env.local'den GROQ_API_KEY oku
env_path = os.path.join(os.path.dirname(__file__), "..", ".env.local")
if os.path.exists(env_path):
    with open(env_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("GROQ_API_KEY="):
                os.environ["GROQ_API_KEY"] = line.split("=", 1)[1].strip()

from groq import Groq
client = Groq(api_key=os.environ["GROQ_API_KEY"])

NEW_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "new_restaurants.json")

with open(NEW_FILE, encoding="utf-8") as f:
    data = json.load(f)

# Sadece Adalar restoranlarını enrichle
targets = [r for r in data if r.get("district") == "Adalar" and not r.get("faq")]
print(f"Enrichlenecek Adalar restoranı: {len(targets)}")

def enrich_restaurant(r: dict) -> dict:
    name = r["name"]
    neighborhood = r.get("neighborhood", "Büyükada Mahallesi")
    # Mahalle → ada adı
    ada_map = {
        "Büyükada Mahallesi": "Büyükada (Prinkipo)",
        "Heybeliada Mahallesi": "Heybeliada (Halki)",
        "Burgazada Mahallesi": "Burgazada (Antigone)",
        "Kınalıada Mahallesi": "Kınalıada (Proti)",
    }
    ada = ada_map.get(neighborhood, "Büyükada")
    cuisine = r.get("cuisine", "Turkish")
    highlights = r.get("highlights", [])
    summary = r.get("llmSummary", "")

    prompt = f"""You are writing content for a restaurant directory website.

Restaurant: {name}
Island: {ada}, Princes Islands (Adalar), Istanbul
Cuisine: {cuisine}
Existing summary: {summary}
Highlights: {', '.join(highlights)}

Generate realistic, helpful content in JSON format with these fields:

1. "faq": Array of 6 question-answer objects. Cover: price range, how to get there (ferry from Kabataş/Bostancı), reservation policy, popular dishes, atmosphere, family-friendly/couples.
   Questions must be practical traveler questions. Answers should be 1-2 sentences, specific to an island restaurant.

2. "sentimentSummary": 2 sentences describing what guests typically say. Focus on island atmosphere, food quality, value.

3. "highlights": Array of 4 short English phrases (features/selling points). Keep existing ones if good, improve or add.

4. "priceRange": One of "$", "$$", "$$$", "$$$$" based on typical island restaurant pricing (most are $$-$$$).

Return ONLY valid JSON, no extra text."""

    try:
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
            temperature=0.2,
            response_format={"type": "json_object"},
        )
        result = json.loads(resp.choices[0].message.content)
        return result
    except Exception as e:
        print(f"  Hata ({name}): {e}")
        return {}

updated = 0
for i, r in enumerate(data):
    if r.get("district") != "Adalar" or r.get("faq"):
        continue

    print(f"[{updated+1}/{len(targets)}] {r['name']} ({r.get('neighborhood','?')})...")
    enriched = enrich_restaurant(r)

    if enriched.get("faq"):
        r["faq"] = enriched["faq"]
    if enriched.get("sentimentSummary"):
        r["sentimentSummary"] = enriched["sentimentSummary"]
    if enriched.get("highlights"):
        r["highlights"] = enriched["highlights"]
    if enriched.get("priceRange"):
        r["priceRange"] = enriched["priceRange"]

    updated += 1
    time.sleep(1.0)

with open(NEW_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n[OK] {updated} restoran güncellendi.")

# Kontrol
sample = next((r for r in data if r.get("district") == "Adalar" and r.get("faq")), None)
if sample:
    print(f"\nÖrnek ({sample['name']}):")
    print(f"  sentimentSummary: {sample.get('sentimentSummary','—')[:80]}...")
    print(f"  faq[0]: {sample['faq'][0]}")
    print(f"  highlights: {sample.get('highlights')}")
