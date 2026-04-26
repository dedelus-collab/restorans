# -*- coding: utf-8 -*-
"""
Tüm Istanbul ilçeleri için OSM'den restoran çeker, Google Maps rating ekler.
Zaten yeterli restoranı olan ilçeleri (SKIP_THRESHOLD) atlar.
"""

import json, os, re, sys, time, unicodedata, uuid, asyncio
sys.stdout.reconfigure(encoding="utf-8")
import requests

ROOT     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXISTING = os.path.join(ROOT, "data", "processed", "istanbul.json")
NEW_FILE = os.path.join(ROOT, "data", "new_restaurants.json")
HOOD_MAP = os.path.join(ROOT, "data", "neighborhood_to_district.json")

OVERPASS  = "https://overpass-api.de/api/interpreter"
NOMINATIM = "https://nominatim.openstreetmap.org/reverse"
HEADERS   = {"User-Agent": "Restoralla/1.0 add_all_districts"}

# Bu sayının üzerinde zaten iyi coverage var, atla
SKIP_THRESHOLD = 50
SKIP_RATINGS = os.environ.get("SKIP_RATINGS", "0") == "1"

# İşlenecek ilçeler (OSM'deki tam Türkçe adları)
DISTRICTS = [
    "Şişli",
    "Ümraniye",
    "Büyükçekmece",
    "Sarıyer",
    "Adalar",
    "Esenyurt",
    "Beykoz",
    "Çekmeköy",
    "Maltepe",
    "Bakırköy",
    "Üsküdar",
    "Ataşehir",
    "Bahçelievler",
    "Avcılar",
    "Güngören",
    "Kağıthane",
    "Kartal",
    "Zeytinburnu",
    "Beylikdüzü",
    "Pendik",
    "Bayrampaşa",
    "Eyüpsultan",
    "Sultangazi",
    "Gaziosmanpaşa",
    "Arnavutköy",
    # Zaten iyi coverage olanlar (threshold geçerse atlanır)
    "Fatih",
    "Beyoğlu",
    "Kadıköy",
    "Beşiktaş",
]

TR = str.maketrans(
    "şçğüöıŞÇĞÜÖİâîûÂÎÛ",
    "scguoisCGUOIaiuAIU"
)

def slugify(t):
    t = t.translate(TR).lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")

def clean_name(name):
    cleaned = "".join(c for c in name if unicodedata.category(c)[0] in ("L","N","Z","P"))
    cleaned = cleaned.strip()
    if cleaned == cleaned.lower():
        cleaned = cleaned.title()
    return cleaned

SKIP_KEYWORDS = [
    "sosyal tesis","ibb ","okul","hastane","kafeterya","kantin",
    "yurt","kreş","kres","spor ","büfe","bufe","kültür merkezi","kultur merkezi",
]

CUISINE_MAP = {
    "kebab": "Kebap", "kebap": "Kebap", "turkish": "Turkish",
    "seafood": "Seafood", "fish": "Seafood", "balik": "Seafood",
    "pizza": "Pizza", "italian": "Pizza & Italian",
    "sushi": "Sushi", "japanese": "Sushi & Japanese",
    "burger": "Burger & Steak", "steak": "Burger & Steak",
    "breakfast": "Breakfast", "kahvalti": "Breakfast",
    "vegan": "Vegan", "vegetarian": "Vegan & Vegetarian",
    "meyhane": "Meyhane",
    "chinese": "Chinese", "indian": "Indian", "georgian": "Georgian",
    "fast_food": "Fast Food", "sandwich": "Sandwich",
}

def normalize_cuisine(osm_cuisine):
    raw = osm_cuisine.lower().split(";")[0].strip()
    for k, v in CUISINE_MAP.items():
        if k in raw:
            return v
    return "Restaurant" if raw else "Restaurant"

def make_tags(cuisine, district):
    base = [district, "Istanbul"]
    if cuisine not in ("Restaurant",):
        base.insert(0, cuisine)
    return base

def make_summary(name, neighborhood, district, cuisine):
    loc = neighborhood if neighborhood and neighborhood != district else district
    return f"{name} is a {cuisine.lower()} restaurant located in {loc}, {district}, Istanbul."

def overpass_query(district_name):
    return f"""
[out:json][timeout:120];
area["name"="{district_name}"]["admin_level"="6"]->.district;
(
  node["amenity"="restaurant"](area.district);
  way["amenity"="restaurant"](area.district);
  node["amenity"="fast_food"](area.district);
  way["amenity"="fast_food"](area.district);
  node["amenity"="cafe"]["cuisine"](area.district);
  way["amenity"="cafe"]["cuisine"](area.district);
);
out center tags;
"""

def load_data():
    with open(EXISTING, encoding="utf-8") as f:
        existing = json.load(f)
    try:
        with open(NEW_FILE, encoding="utf-8") as f:
            new_rest = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        new_rest = []
    with open(HOOD_MAP, encoding="utf-8") as f:
        hood_map = json.load(f)
    return existing, new_rest, hood_map

def count_district(all_r, hood_map, district_name):
    count = 0
    for r in all_r:
        d = hood_map.get(r.get("neighborhood", ""), "")
        if d == district_name:
            count += 1
    return count

def fetch_osm(district_name):
    query = overpass_query(district_name)
    print(f"  Overpass query for {district_name}...")
    resp = requests.post(OVERPASS, data={"data": query}, headers=HEADERS, timeout=120)
    resp.raise_for_status()
    return resp.json().get("elements", [])

def get_neighborhood(lat, lng):
    try:
        r = requests.get(NOMINATIM, params={
            "lat": lat, "lon": lng,
            "format": "json", "zoom": 16, "addressdetails": 1,
        }, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            addr = r.json().get("address", {})
            return (addr.get("neighbourhood") or addr.get("suburb")
                    or addr.get("quarter") or addr.get("city_district") or "")
    except Exception as e:
        print(f"    Nominatim error: {e}")
    return ""

async def scrape_ratings(items):
    from playwright.async_api import async_playwright
    print(f"\n  Scraping {len(items)} ratings...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"]
        )
        ctx = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36",
            locale="tr-TR",
        )
        page = await ctx.new_page()
        await page.add_init_script("Object.defineProperty(navigator,'webdriver',{get:()=>undefined});")

        for i, r in enumerate(items, 1):
            name = r["name"]
            lat, lng = r.get("lat"), r.get("lng")
            url = f"https://www.google.com/maps/search/{name} istanbul/@{lat},{lng},17z"
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=18000)
                await page.wait_for_timeout(3500)
                full_text = await page.inner_text("body")

                rating = None
                for span in (await page.query_selector_all("span"))[:200]:
                    try:
                        t = (await span.inner_text()).strip().replace(",", ".")
                        val = float(t)
                        if 1.0 <= val <= 5.0 and "." in t:
                            rating = round(val, 1)
                            break
                    except:
                        pass

                review_count = None
                m = re.search(r"\(([0-9][0-9.,\s]{0,8})\)", full_text)
                if m:
                    num = re.sub(r"[^0-9]", "", m.group(1))
                    try:
                        cnt = int(num)
                        if 1 <= cnt <= 200000:
                            review_count = cnt
                    except:
                        pass

                r["avgRating"] = rating
                r["reviewCount"] = review_count
                print(f"    [{i}/{len(items)}] {name}: {rating} ({review_count})")
            except Exception as e:
                print(f"    [{i}/{len(items)}] {name}: ERROR {str(e)[:50]}")
                r["avgRating"] = None
                r["reviewCount"] = None

            await asyncio.sleep(2)

        await browser.close()

def process_district(district_name, existing, new_rest, hood_map):
    all_r = existing + new_rest
    current_count = count_district(all_r, hood_map, district_name)

    if current_count >= SKIP_THRESHOLD:
        print(f"\n[SKIP] {district_name}: {current_count} restaurants (>= {SKIP_THRESHOLD})")
        return 0

    print(f"\n{'='*50}")
    print(f"[{district_name}] current: {current_count} restaurants")

    try:
        elements = fetch_osm(district_name)
    except Exception as e:
        print(f"  OSM error: {e}")
        return 0

    print(f"  OSM returned {len(elements)} elements")

    all_slugs  = {r["slug"] for r in all_r}
    all_coords = {(round(r["lat"], 4), round(r["lng"], 4)) for r in all_r if r.get("lat")}

    candidates = []
    seen_slugs = set()

    for el in elements:
        tags = el.get("tags", {})
        name = tags.get("name") or tags.get("name:tr") or tags.get("name:en")
        if not name:
            continue
        if any(kw in name.lower() for kw in SKIP_KEYWORDS):
            continue

        if el["type"] == "node":
            lat, lng = el.get("lat"), el.get("lon")
        else:
            c = el.get("center", {})
            lat, lng = c.get("lat"), c.get("lon")
        if not lat or not lng:
            continue

        name = clean_name(name)
        slug = slugify(name)
        coord = (round(lat, 4), round(lng, 4))

        if slug in all_slugs or coord in all_coords or slug in seen_slugs:
            continue
        seen_slugs.add(slug)

        candidates.append({
            "name": name, "slug": slug, "lat": lat, "lng": lng,
            "osm_cuisine": tags.get("cuisine", "").split(";")[0].strip(),
            "phone": tags.get("phone") or tags.get("contact:phone"),
            "website": tags.get("website") or tags.get("contact:website"),
            "address": tags.get("addr:street", ""),
        })

    print(f"  New candidates: {len(candidates)}")
    if not candidates:
        return 0

    added_items = []

    for c in candidates:
        neighborhood = get_neighborhood(c["lat"], c["lng"])
        time.sleep(1.1)

        district_from_map = hood_map.get(neighborhood, "")

        # If Nominatim says it belongs to a different known district, skip
        if neighborhood and district_from_map and district_from_map != district_name:
            continue

        # Add unknown neighborhoods to the map
        if neighborhood and not district_from_map:
            hood_map[neighborhood] = district_name

        cuisine = normalize_cuisine(c["osm_cuisine"])
        tags_list = make_tags(cuisine, district_name)
        summary = make_summary(c["name"], neighborhood or district_name, district_name, cuisine)

        entry = {
            "id": uuid.uuid4().hex[:8],
            "slug": c["slug"],
            "name": c["name"],
            "city": "İstanbul",
            "citySlug": "istanbul",
            "neighborhood": neighborhood or district_name,
            "cuisine": cuisine,
            "cuisineSlug": slugify(cuisine),
            "priceRange": 2,
            "avgRating": None,
            "reviewCount": None,
            "address": c["address"],
            "lat": c["lat"],
            "lng": c["lng"],
            "phone": c["phone"],
            "website": c["website"],
            "openingHours": None,
            "hoursEstimated": True,
            "features": {
                "terrace": False, "parking": False, "wifi": False,
                "reservation": False, "romantic": False, "seaView": False,
                "liveMusic": False, "vegan": False,
            },
            "tags": tags_list,
            "sentimentSummary": f"A local restaurant in {district_name}.",
            "llmSummary": summary,
            "faq": [
                {"question": f"What does {c['name']} serve?", "answer": f"{cuisine} dishes."},
                {"question": f"Where is {c['name']} located?", "answer": f"In {neighborhood or district_name}, {district_name}, Istanbul."},
                {"question": "Do they take reservations?", "answer": "Contact the restaurant directly."},
            ],
            "lastUpdated": "2026-04-26",
            "verifiedData": False,
            "confidenceScore": 0.5,
            "specialFeatures": {},
            "highlights": [f"{cuisine} in {neighborhood or district_name}", f"{district_name} district"],
        }

        new_rest.append(entry)
        added_items.append(entry)
        all_slugs.add(c["slug"])
        all_coords.add((round(c["lat"], 4), round(c["lng"], 4)))

    print(f"  Added {len(added_items)} restaurants")

    # Save intermediate (before ratings)
    with open(HOOD_MAP, "w", encoding="utf-8") as f:
        json.dump(hood_map, f, ensure_ascii=False, indent=2)
    with open(NEW_FILE, "w", encoding="utf-8") as f:
        json.dump(new_rest, f, ensure_ascii=False, indent=2)

    # Scrape ratings
    if added_items and not SKIP_RATINGS:
        asyncio.run(scrape_ratings(added_items))
    elif added_items and SKIP_RATINGS:
        print(f"  SKIP_RATINGS=1, skipping Google Maps scraping")

        # Save with ratings
        slug_map = {r["slug"]: r for r in added_items}
        for entry in new_rest:
            if entry["slug"] in slug_map:
                u = slug_map[entry["slug"]]
                entry["avgRating"] = u["avgRating"]
                entry["reviewCount"] = u["reviewCount"]
        with open(NEW_FILE, "w", encoding="utf-8") as f:
            json.dump(new_rest, f, ensure_ascii=False, indent=2)

    return len(added_items)

def main():
    print("Loading data...")
    existing, new_rest, hood_map = load_data()
    print(f"Existing: {len(existing)}, New: {len(new_rest)}, Total: {len(existing)+len(new_rest)}")

    total_added = 0
    for district in DISTRICTS:
        n = process_district(district, existing, new_rest, hood_map)
        total_added += n
        # Reload new_rest to pick up changes from previous district
        try:
            with open(NEW_FILE, encoding="utf-8") as f:
                new_rest = json.load(f)
        except:
            pass

    print(f"\n{'='*50}")
    print(f"DONE. Total added: {total_added}")
    print(f"New total: {len(existing) + len(new_rest)}")

if __name__ == "__main__":
    main()
