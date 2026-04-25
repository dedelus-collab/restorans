# -*- coding: utf-8 -*-
"""
Adalar ilçesindeki (Büyükada, Heybeliada, Burgazada, Kınalıada) restoranları
OpenStreetMap'ten çeker ve data/new_restaurants.json'a ekler.
"""
import json, os, re, sys, time, unicodedata
import requests

sys.stdout.reconfigure(encoding="utf-8")

ROOT     = os.path.join(os.path.dirname(__file__), "..")
EXISTING = os.path.join(ROOT, "data", "processed", "istanbul.json")
NEW_FILE = os.path.join(ROOT, "data", "new_restaurants.json")
HOOD_MAP = os.path.join(ROOT, "data", "neighborhood_to_district.json")

# .env.local'den GROQ_API_KEY oku
env_path = os.path.join(ROOT, ".env.local")
if os.path.exists(env_path):
    with open(env_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("GROQ_API_KEY="):
                os.environ["GROQ_API_KEY"] = line.split("=", 1)[1].strip()

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
OVERPASS     = "https://overpass-api.de/api/interpreter"
NOMINATIM    = "https://nominatim.openstreetmap.org/reverse"
HEADERS      = {"User-Agent": "Restoralla/1.0 sync_adalar"}

TR = str.maketrans("şçğüöıŞÇĞÜÖİâîûÂÎÛ", "scguoiSCGUOIaiuAIU")

def slugify(text: str) -> str:
    t = text.translate(TR).lower()
    t = re.sub(r"[^a-z0-9]+", "-", t).strip("-")
    return t

# Ada sınırları (bounding box yerine ada adıyla sorgula)
# Adalar ilçesi relation ID: 5553170
OVERPASS_QUERY = """
[out:json][timeout:60];
(
  area["name"="Adalar"]["admin_level"="7"]->.adalar;
  node["amenity"="restaurant"](area.adalar);
  way["amenity"="restaurant"](area.adalar);
  node["amenity"="cafe"](area.adalar);
);
out center tags;
"""

# Alternatif: koordinat bazlı sorgu (daha güvenilir)
OVERPASS_QUERY_BBOX = """
[out:json][timeout:60];
(
  node["amenity"="restaurant"](40.840,28.910,41.140,29.150);
  way["amenity"="restaurant"](40.840,28.910,41.140,29.150);
  node["amenity"="cafe"]["name"](40.840,28.910,41.140,29.150);
);
out center tags;
"""

# Ada koordinat aralıkları (sadece adaları kapsar, Kadıköy kıyısı değil)
ISLAND_BOUNDS = [
    # Büyükada
    (40.862, 29.052, 40.881, 29.088),
    # Heybeliada
    (40.879, 29.085, 40.896, 29.112),
    # Burgazada
    (40.870, 29.055, 40.882, 29.073),
    # Kınalıada
    (40.905, 28.990, 40.918, 29.007),
]

def is_on_island(lat: float, lng: float) -> bool:
    for (lat_min, lng_min, lat_max, lng_max) in ISLAND_BOUNDS:
        if lat_min <= lat <= lat_max and lng_min <= lng <= lng_max:
            return True
    return False

SKIP_KEYWORDS = [
    "sosyal tesis", "ibb ", "okul", "hastane", "kafeterya", "kantin",
    "belediye", "büfe",
]

def clean_name(name: str) -> str:
    cleaned = "".join(c for c in name if unicodedata.category(c)[0] in ("L", "N", "Z", "P"))
    cleaned = cleaned.strip()
    if cleaned == cleaned.lower():
        cleaned = cleaned.title()
    return cleaned

# Veri yükle
with open(EXISTING, encoding="utf-8") as f:
    existing = json.load(f)
with open(NEW_FILE, encoding="utf-8") as f:
    new_restaurants = json.load(f)
with open(HOOD_MAP, encoding="utf-8") as f:
    hood_district = json.load(f)

all_slugs = {r["slug"] for r in existing} | {r["slug"] for r in new_restaurants}
existing_coords = {(round(r["lat"], 4), round(r["lng"], 4)) for r in existing}

print(f"Mevcut: {len(existing)} + {len(new_restaurants)} yeni = {len(all_slugs)} toplam")

# Overpass sorgusu — her ada için ayrı bbox
print("Overpass API sorgulanıyor (ada bbox'ları)...")
elements = []
for (lat_min, lng_min, lat_max, lng_max) in ISLAND_BOUNDS:
    q = f"""
[out:json][timeout:30];
(
  node["amenity"="restaurant"]({lat_min},{lng_min},{lat_max},{lng_max});
  way["amenity"="restaurant"]({lat_min},{lng_min},{lat_max},{lng_max});
  node["amenity"="cafe"]["name"]({lat_min},{lng_min},{lat_max},{lng_max});
);
out center tags;
"""
    try:
        r = requests.post(OVERPASS, data={"data": q}, headers=HEADERS, timeout=45)
        r.raise_for_status()
        batch = r.json().get("elements", [])
        print(f"  bbox ({lat_min},{lng_min}) → {len(batch)} sonuç")
        elements.extend(batch)
        time.sleep(1.5)
    except Exception as e:
        print(f"  Overpass hatası: {e}")

print(f"Toplam OSM sonucu: {len(elements)}")

# Ada mahalle adlarına göre neighborhood belirle
def get_neighborhood(lat: float, lng: float) -> str:
    """Koordinata göre ada mahallesi döndür."""
    # Büyükada
    if 40.862 <= lat <= 40.881 and 29.052 <= lng <= 29.088:
        return "Büyükada Mahallesi"
    # Heybeliada
    if 40.879 <= lat <= 40.896 and 29.085 <= lng <= 29.112:
        return "Heybeliada Mahallesi"
    # Burgazada
    if 40.870 <= lat <= 40.882 and 29.055 <= lng <= 29.073:
        return "Burgazada Mahallesi"
    # Kınalıada
    if 40.905 <= lat <= 40.918 and 28.990 <= lng <= 29.007:
        return "Kınalıada Mahallesi"
    return "Büyükada Mahallesi"

# Aday restoranları filtrele
candidates = []
seen_ids = set()
for el in elements:
    eid = el.get("id")
    if eid in seen_ids:
        continue
    seen_ids.add(eid)

    tags = el.get("tags", {})
    name = tags.get("name") or tags.get("name:tr") or tags.get("name:en")
    if not name:
        continue

    name_lower = name.lower()
    if any(kw in name_lower for kw in SKIP_KEYWORDS):
        continue

    lat = el.get("lat") or (el.get("center", {}) or {}).get("lat")
    lng = el.get("lon") or (el.get("center", {}) or {}).get("lon")
    if not lat or not lng:
        continue

    lat, lng = float(lat), float(lng)

    name = clean_name(name)
    slug = slugify(name)
    if slug in all_slugs:
        continue
    if (round(lat, 4), round(lng, 4)) in existing_coords:
        continue

    neighborhood = get_neighborhood(lat, lng)
    district = hood_district.get(neighborhood, "Adalar")

    candidates.append({
        "slug": slug,
        "name": name,
        "tags": tags,
        "lat": lat,
        "lng": lng,
        "neighborhood": neighborhood,
        "district": district,
    })

print(f"\nYeni aday: {len(candidates)}")
for c in candidates:
    print(f"  {c['name']} ({c['neighborhood']}) lat={c['lat']:.4f}")

if not candidates:
    print("Eklenecek yeni restoran yok.")
    sys.exit(0)

# Groq ile zenginleştir
def enrich(c: dict) -> dict:
    if not GROQ_API_KEY:
        return {}
    from groq import Groq
    client = Groq(api_key=GROQ_API_KEY)
    tags = c["tags"]
    cuisine = tags.get("cuisine", "")
    prompt = f"""Restaurant: {c['name']}
Location: {c['neighborhood']}, Adalar (Princes Islands), Istanbul
Cuisine: {cuisine or 'unknown'}
OSM tags: {json.dumps({k: v for k, v in tags.items() if k in ['cuisine','opening_hours','phone','website','outdoor_seating','addr:street']}, ensure_ascii=False)}

Write a concise English summary (2-3 sentences) for this restaurant on the Princes Islands of Istanbul.
Then provide 3 highlight bullet points (short English phrases).
Return JSON: {{"summary": "...", "highlights": ["...", "...", "..."]}}"""
    try:
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
            temperature=0.2,
            response_format={"type": "json_object"},
        )
        return json.loads(resp.choices[0].message.content)
    except Exception as e:
        print(f"  Groq hatası: {e}")
        return {}

from datetime import date

added = []
for i, c in enumerate(candidates):
    print(f"[{i+1}/{len(candidates)}] {c['name']} zenginleştiriliyor...")
    enriched = enrich(c)
    tags = c["tags"]
    cuisine_raw = tags.get("cuisine", "")
    cuisine_name = cuisine_raw.capitalize() if cuisine_raw else "Restaurant"
    phone = tags.get("phone") or tags.get("contact:phone") or ""
    website = tags.get("website") or tags.get("contact:website") or ""

    entry = {
        "slug": c["slug"],
        "name": c["name"],
        "city": "Istanbul",
        "citySlug": "istanbul",
        "neighborhood": c["neighborhood"],
        "district": c["district"],
        "cuisine": cuisine_name,
        "cuisineSlug": None,
        "lat": c["lat"],
        "lng": c["lng"],
        "avgRating": None,
        "reviewCount": 0,
        "priceRange": "$$",
        "phone": phone,
        "website": website,
        "llmSummary": enriched.get("summary", f"{c['name']} is a restaurant on the Princes Islands (Adalar), Istanbul."),
        "highlights": enriched.get("highlights", ["Located on the Princes Islands", "Car-free island atmosphere", "Traditional Turkish dining"]),
        "tags": ["adalar", "princes-islands", "island-dining"],
        "lastUpdated": str(date.today()),
        "source": "osm-adalar-sync",
    }
    added.append(entry)
    all_slugs.add(c["slug"])
    time.sleep(1.2)

new_restaurants.extend(added)
with open(NEW_FILE, "w", encoding="utf-8") as f:
    json.dump(new_restaurants, f, ensure_ascii=False, indent=2)

print(f"\n[OK] {len(added)} Adalar restoranı eklendi → data/new_restaurants.json")
print(f"Toplam new_restaurants.json: {len(new_restaurants)}")
