# -*- coding: utf-8 -*-
"""Adalar restoranlarına Groq ile tahmini puan ve yorum sayısı ekler."""
import json, os, sys, time
sys.stdout.reconfigure(encoding="utf-8")

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

targets = [r for r in data if r.get("district") == "Adalar" and r.get("avgRating") is None]
print(f"Puan eklenecek: {len(targets)}")

def estimate_rating(r: dict) -> dict:
    ada_map = {
        "Büyükada Mahallesi": "Büyükada",
        "Heybeliada Mahallesi": "Heybeliada",
        "Burgazada Mahallesi": "Burgazada",
        "Kınalıada Mahallesi": "Kınalıada",
    }
    ada = ada_map.get(r.get("neighborhood", ""), "Büyükada")
    prompt = f"""Restaurant: {r['name']}
Island: {ada}, Princes Islands, Istanbul
Cuisine: {r.get('cuisine', 'Turkish')}
Highlights: {', '.join(r.get('highlights', []))}
Summary: {r.get('llmSummary', '')}

Based on this restaurant's profile, estimate realistic Google Maps-style ratings.
Island restaurants in Istanbul's Princes Islands typically rate between 3.8-4.8.
Return JSON with exactly these fields:
- "avgRating": number between 3.5 and 4.9 (one decimal, e.g. 4.3)
- "reviewCount": integer between 80 and 800 (realistic for an island restaurant)

Return ONLY the JSON object."""

    try:
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=60,
            temperature=0.3,
            response_format={"type": "json_object"},
        )
        return json.loads(resp.choices[0].message.content)
    except Exception as e:
        print(f"  Hata: {e}")
        return {"avgRating": 4.1, "reviewCount": 120}

updated = 0
for r in data:
    if r.get("district") != "Adalar" or r.get("avgRating") is not None:
        continue

    print(f"  {r['name']}...", end=" ", flush=True)
    result = estimate_rating(r)

    avg = result.get("avgRating")
    cnt = result.get("reviewCount")

    # Sınır kontrolü
    if isinstance(avg, (int, float)) and 3.0 <= avg <= 5.0:
        r["avgRating"] = round(float(avg), 1)
    else:
        r["avgRating"] = 4.1

    if isinstance(cnt, int) and 10 <= cnt <= 2000:
        r["reviewCount"] = cnt
    else:
        r["reviewCount"] = 120

    print(f"→ {r['avgRating']}/5 ({r['reviewCount']} reviews)")
    updated += 1
    time.sleep(0.5)

with open(NEW_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n[OK] {updated} restoran güncellendi.")
