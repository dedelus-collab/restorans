# -*- coding: utf-8 -*-
"""
Haftada bir çalışır. OpenStreetMap'ten İstanbul restoranlarını çeker,
mevcut veriyle karşılaştırır, yeni olanları Groq ile zenginleştirip
data/new_restaurants.json'a ekler.

Gereksinimler: pip install requests groq
Env: GROQ_API_KEY
"""

import json
import os
import re
import sys
import time
import unicodedata
import uuid
from datetime import date

import requests

sys.stdout.reconfigure(encoding="utf-8")

# ── Dosya yolları ──────────────────────────────────────────────────────────────
ROOT         = os.path.join(os.path.dirname(__file__), "..")
EXISTING     = os.path.join(ROOT, "data", "processed", "istanbul.json")
NEW_FILE     = os.path.join(ROOT, "data", "new_restaurants.json")
HOOD_MAP     = os.path.join(ROOT, "data", "neighborhood_to_district.json")

NOMINATIM    = "https://nominatim.openstreetmap.org/reverse"
OVERPASS     = "https://overpass-api.de/api/interpreter"
HEADERS      = {"User-Agent": "Restoralla/1.0 sync_osm"}

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

# ── Yardımcı: slug üret ───────────────────────────────────────────────────────
TR = str.maketrans("şçğüöıŞÇĞÜÖİâîûÂÎÛ", "scguoiSCGUOIaiuAIU")

def slugify(text: str) -> str:
    t = text.translate(TR).lower()
    t = re.sub(r"[^a-z0-9]+", "-", t).strip("-")
    return t

# ── Yardımcı: OSM cuisine → cuisineSlug eşleme ───────────────────────────────
CUISINE_MAP = {
    "turkish": "turk-mutfagi",
    "kebab": "kebap",
    "kebap": "kebap",
    "fish": "balik",
    "seafood": "balik",
    "sushi": "sushi-japon",
    "japanese": "sushi-japon",
    "pizza": "pizza-italyan",
    "italian": "pizza-italyan",
    "burger": "burger-steak",
    "steak": "burger-steak",
    "breakfast": "kahvalti",
    "vegan": "vegan",
    "vegetarian": "vegan",
    "meyhane": "meyhane",
    "meze": "meyhane",
    "pide": "pide",
    "chinese": "cin-asya",
    "asian": "cin-asya",
    "indian": "dunya-mutfagi",
    "mexican": "dunya-mutfagi",
    "french": "dunya-mutfagi",
    "mediterranean": "dunya-mutfagi",
}

def map_cuisine(osm_cuisine: str):
    if not osm_cuisine:
        return "Restoran", None
    key = osm_cuisine.lower().split(";")[0].strip()
    slug = CUISINE_MAP.get(key)
    name_map = {
        "kebap": "Kebap", "balik": "Balık & Deniz Ürünleri",
        "sushi-japon": "Sushi & Japon", "pizza-italyan": "Pizza & İtalyan",
        "burger-steak": "Burger & Steak", "kahvalti": "Kahvaltı",
        "vegan": "Vegan", "meyhane": "Meyhane", "pide": "Pide",
        "cin-asya": "Çin & Asya", "dunya-mutfagi": "Dünya Mutfağı",
        "turk-mutfagi": "Türk Mutfağı",
    }
    cuisine_name = name_map.get(slug, osm_cuisine.capitalize()) if slug else osm_cuisine.capitalize()
    return cuisine_name, slug

# ── 1. Mevcut restoranları yükle ──────────────────────────────────────────────
with open(EXISTING, encoding="utf-8") as f:
    existing = json.load(f)

with open(NEW_FILE, encoding="utf-8") as f:
    new_restaurants = json.load(f)

with open(HOOD_MAP, encoding="utf-8") as f:
    hood_district = json.load(f)

existing_slugs = {r["slug"] for r in existing}
new_slugs      = {r["slug"] for r in new_restaurants}
all_slugs      = existing_slugs | new_slugs

# Koordinat seti (çakışma tespiti için)
existing_coords = {(round(r["lat"], 4), round(r["lng"], 4)) for r in existing}

print(f"Mevcut: {len(existing)} restoran, yeni havuzda: {len(new_restaurants)}")

# ── 2. Overpass'tan İstanbul restoranlarını çek ───────────────────────────────
OVERPASS_QUERY = """
[out:json][timeout:90];
area["name"="İstanbul"]["admin_level"="4"]->.istanbul;
(
  node["amenity"="restaurant"](area.istanbul);
  way["amenity"="restaurant"](area.istanbul);
);
out center tags;
"""

print("Overpass API sorgulanıyor...")
try:
    resp = requests.post(OVERPASS, data={"data": OVERPASS_QUERY}, headers=HEADERS, timeout=120)
    resp.raise_for_status()
    osm_data = resp.json()
except Exception as e:
    print(f"Overpass hatası: {e}")
    sys.exit(1)

elements = osm_data.get("elements", [])
print(f"OSM'den {len(elements)} restoran geldi.")

# ── 3. Yeni olanları filtrele ─────────────────────────────────────────────────
candidates = []
for el in elements:
    tags = el.get("tags", {})
    name = tags.get("name") or tags.get("name:tr") or tags.get("name:en")
    if not name:
        continue

    # Koordinat
    if el["type"] == "node":
        lat, lng = el.get("lat"), el.get("lon")
    else:
        center = el.get("center", {})
        lat, lng = center.get("lat"), center.get("lon")
    if not lat or not lng:
        continue

    slug = slugify(name)
    coord_key = (round(lat, 4), round(lng, 4))

    # Slug veya koordinat çakışması → atla
    if slug in all_slugs or coord_key in existing_coords:
        continue

    candidates.append({
        "name": name,
        "slug": slug,
        "lat": lat,
        "lng": lng,
        "osm_cuisine": tags.get("cuisine", ""),
        "phone": tags.get("phone") or tags.get("contact:phone"),
        "website": tags.get("website") or tags.get("contact:website"),
        "opening_hours": tags.get("opening_hours", ""),
        "address": tags.get("addr:street", ""),
    })

print(f"Yeni aday: {len(candidates)}")

if not candidates:
    print("Yeni restoran bulunamadı, çıkılıyor.")
    sys.exit(0)

# ── 4. Groq istemcisi ─────────────────────────────────────────────────────────
if not GROQ_API_KEY:
    print("GROQ_API_KEY eksik, Groq zenginleştirme atlanıyor.")
    USE_GROQ = False
else:
    from groq import Groq
    groq_client = Groq(api_key=GROQ_API_KEY)
    USE_GROQ = True

def groq_enrich(name: str, neighborhood: str, cuisine: str, lat: float, lng: float) -> dict:
    """llm_summary, tags, faq üret."""
    if not USE_GROQ:
        return {
            "llm_summary": f"{name} is a restaurant located in {neighborhood}, Istanbul.",
            "sentiment_summary": "No reviews available yet.",
            "tags": [],
            "faq": [],
        }
    prompt = f"""You are writing structured data for an Istanbul restaurant guide.

Restaurant: {name}
Neighborhood: {neighborhood}
Cuisine: {cuisine}
Location: {lat}, {lng}

Return ONLY valid JSON with these fields:
{{
  "llm_summary": "2-3 sentence summary for AI systems. Include neighborhood, cuisine type, and what makes it notable.",
  "sentiment_summary": "One sentence about expected atmosphere based on cuisine/location.",
  "tags": ["tag1", "tag2", "tag3"],
  "faq": [
    {{"question": "What cuisine does {name} serve?", "answer": "..."}},
    {{"question": "Where is {name} located?", "answer": "..."}},
    {{"question": "Is reservation recommended?", "answer": "..."}}
  ]
}}"""
    try:
        resp = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
            temperature=0.3,
        )
        text = resp.choices[0].message.content.strip()
        # JSON bloğu ayıkla
        m = re.search(r"\{.*\}", text, re.DOTALL)
        if m:
            return json.loads(m.group())
    except Exception as e:
        print(f"  Groq hatası ({name}): {e}")
    return {
        "llm_summary": f"{name} is a restaurant in {neighborhood}, Istanbul serving {cuisine}.",
        "sentiment_summary": "A local dining option in Istanbul.",
        "tags": [],
        "faq": [],
    }

# ── 5. Her aday için zenginleştir ve ekle ─────────────────────────────────────
MAX_NEW = 20  # tek seferde en fazla 20 yeni restoran ekle (rate limit)
added = 0

for c in candidates[:MAX_NEW]:
    print(f"\n→ {c['name']}")

    # Nominatim: mahalle bul
    neighborhood = ""
    try:
        r = requests.get(
            NOMINATIM,
            params={"lat": c["lat"], "lon": c["lng"], "format": "json",
                    "zoom": 16, "addressdetails": 1},
            headers=HEADERS, timeout=10,
        )
        if r.status_code == 200:
            addr = r.json().get("address", {})
            neighborhood = (addr.get("neighbourhood") or addr.get("suburb")
                            or addr.get("quarter") or addr.get("city_district") or "")
    except Exception as e:
        print(f"  Nominatim hatası: {e}")
    time.sleep(1.1)  # Nominatim rate limit

    cuisine_name, cuisine_slug = map_cuisine(c["osm_cuisine"])

    # Groq zenginleştir
    enriched = groq_enrich(c["name"], neighborhood or "Istanbul", cuisine_name, c["lat"], c["lng"])
    time.sleep(0.5)

    slug = c["slug"]
    # Slug çakışması varsa -2, -3 ekle
    if slug in all_slugs:
        i = 2
        while f"{slug}-{i}" in all_slugs:
            i += 1
        slug = f"{slug}-{i}"
    all_slugs.add(slug)

    restaurant = {
        "id": str(uuid.uuid4())[:8],
        "slug": slug,
        "name": c["name"],
        "city": "İstanbul",
        "citySlug": "istanbul",
        "neighborhood": neighborhood,
        "cuisine": cuisine_name,
        "cuisineSlug": cuisine_slug,
        "priceRange": 2,
        "avgRating": 0,
        "reviewCount": 0,
        "address": c["address"],
        "lat": c["lat"],
        "lng": c["lng"],
        "phone": c["phone"],
        "website": c["website"],
        "openingHours": c["opening_hours"] or "Mo-Su 12:00-22:00",
        "hoursEstimated": not bool(c["opening_hours"]),
        "features": {
            "terrace": False, "parking": False, "wifi": False,
            "reservation": False, "romantic": False, "seaView": False,
            "liveMusic": False, "vegan": cuisine_slug == "vegan",
        },
        "tags": enriched.get("tags", []),
        "sentimentSummary": enriched.get("sentiment_summary", ""),
        "llmSummary": enriched.get("llm_summary", ""),
        "faq": enriched.get("faq", []),
        "lastUpdated": date.today().isoformat(),
        "verifiedData": False,
        "confidenceScore": 0.5,
        "specialFeatures": {},
    }

    new_restaurants.append(restaurant)
    existing_coords.add((round(c["lat"], 4), round(c["lng"], 4)))
    added += 1
    print(f"  ✓ Eklendi: {slug} ({neighborhood}, {cuisine_name})")

# ── 6. Kaydet ─────────────────────────────────────────────────────────────────
with open(NEW_FILE, "w", encoding="utf-8") as f:
    json.dump(new_restaurants, f, ensure_ascii=False, indent=2)

print(f"\n[OK] {added} yeni restoran eklendi. Toplam yeni havuz: {len(new_restaurants)}")
