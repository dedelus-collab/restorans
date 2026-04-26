# -*- coding: utf-8 -*-
"""
Besiktas ilcesindeki kebap restoranlarini OSM'den ceker,
new_restaurants.json'a ekler, Google Maps'ten rating ceker.
"""

import json, os, re, sys, time, unicodedata, uuid, asyncio
sys.stdout.reconfigure(encoding="utf-8")

import requests

ROOT     = os.path.join(os.path.dirname(__file__), "..")
EXISTING = os.path.join(ROOT, "data", "processed", "istanbul.json")
NEW_FILE = os.path.join(ROOT, "data", "new_restaurants.json")
HOOD_MAP = os.path.join(ROOT, "data", "neighborhood_to_district.json")

OVERPASS   = "https://overpass-api.de/api/interpreter"
NOMINATIM  = "https://nominatim.openstreetmap.org/reverse"
HEADERS    = {"User-Agent": "Restoralla/1.0 add_besiktas_kebap"}
GROQ_KEY   = os.environ.get("GROQ_API_KEY", "")

DISTRICT = "Beşiktaş"
BBOX     = "41.020,28.940,41.095,29.060"

TR = str.maketrans("ş\xe7ğ\xfc\xf6ıŞ\xc7Ğ\xdc\xd6İ\xe2\xee\xfb\xc2\xce\xdb", "scguoiSCGUOIaiuAIU")

def slugify(t):
    t = t.translate(TR).lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")

def clean_name(name):
    cleaned = "".join(c for c in name if unicodedata.category(c)[0] in ("L","N","Z","P"))
    cleaned = cleaned.strip()
    if cleaned == cleaned.lower():
        cleaned = cleaned.title()
    return cleaned

# Beşiktaş admin boundary via area query
QUERY = """
[out:json][timeout:90];
area["name"="Beşiktaş"]["admin_level"="6"]->.besiktas;
(
  node["amenity"="restaurant"](area.besiktas);
  way["amenity"="restaurant"](area.besiktas);
  node["amenity"="fast_food"](area.besiktas);
  way["amenity"="fast_food"](area.besiktas);
);
out center tags;
"""

print(f"Overpass API ({DISTRICT} kebap)...")
resp = requests.post(OVERPASS, data={"data": QUERY}, headers=HEADERS, timeout=90)
resp.raise_for_status()
elements = resp.json().get("elements", [])
print(f"OSM: {len(elements)} eleman")

with open(EXISTING, encoding="utf-8") as f:
    existing = json.load(f)
with open(NEW_FILE, encoding="utf-8") as f:
    new_rest = json.load(f)
with open(HOOD_MAP, encoding="utf-8") as f:
    hood_map = json.load(f)

all_slugs  = {r["slug"] for r in existing} | {r["slug"] for r in new_rest}
all_coords = {(round(r["lat"],4), round(r["lng"],4)) for r in existing if r.get("lat")}
all_coords |= {(round(r["lat"],4), round(r["lng"],4)) for r in new_rest if r.get("lat")}

SKIP = ["sosyal tesis","ibb ","okul","hastane","kafeterya","kantin","yurt","kres","spor ","bufe","kultur merkezi"]

KEBAP_CUISINE = {"kebab","kebap","turkish","kofte","kofteci","lahmacun","tantuni","doner","iskender","pide","ocakbasi","ocakbaşı"}
KEBAP_NAME_KEYWORDS = ["kebap","kebab","iskender","doner","döner","köfte","kofte","kofteci","adana","urfa","lahmacun","tantuni","ocakbaşı","ocakbasi","pide","cag","çağ","aspava"]

def is_kebap(tags, name):
    cuisine = tags.get("cuisine","").lower()
    if any(k in cuisine for k in KEBAP_CUISINE):
        return True
    name_lower = name.lower()
    return any(k in name_lower for k in KEBAP_NAME_KEYWORDS)

candidates = []
seen = set()

for el in elements:
    tags = el.get("tags", {})
    name = tags.get("name") or tags.get("name:tr") or tags.get("name:en")
    if not name: continue
    if any(kw in name.lower() for kw in SKIP): continue
    if not is_kebap(tags, name): continue

    if el["type"] == "node":
        lat, lng = el.get("lat"), el.get("lon")
    else:
        c = el.get("center", {})
        lat, lng = c.get("lat"), c.get("lon")
    if not lat or not lng: continue

    name = clean_name(name)
    slug = slugify(name)
    coord = (round(lat,4), round(lng,4))

    if slug in all_slugs or coord in all_coords or slug in seen:
        continue
    seen.add(slug)

    candidates.append({
        "name": name, "slug": slug, "lat": lat, "lng": lng,
        "osm_cuisine": tags.get("cuisine","").split(";")[0].strip(),
        "phone": tags.get("phone") or tags.get("contact:phone"),
        "website": tags.get("website") or tags.get("contact:website"),
        "address": tags.get("addr:street",""),
    })

print(f"Yeni aday: {len(candidates)}")
if not candidates:
    print("Yeni restoran bulunamadi.")
    sys.exit(0)

USE_GROQ = False
if GROQ_KEY:
    from groq import Groq
    groq_client = Groq(api_key=GROQ_KEY)
    USE_GROQ = True

def enrich(name, neighborhood, cuisine, lat, lng):
    return {
        "llm_summary": f"{name} is a kebap restaurant in {neighborhood}, {DISTRICT}, Istanbul.",
        "sentiment_summary": f"A local kebap spot in {DISTRICT}.",
        "tags": ["Kebap", DISTRICT, "Turkish Cuisine"],
        "faq": [
            {"question": f"What does {name} serve?", "answer": "Kebap and Turkish grilled dishes."},
            {"question": f"Where is {name}?", "answer": f"In {neighborhood}, {DISTRICT}, Istanbul."},
            {"question": "Do they take reservations?", "answer": "Contact the restaurant directly."},
        ],
    }

added_items = []

for c in candidates:
    print(f"\n-> {c['name']}")

    neighborhood = ""
    try:
        r = requests.get(NOMINATIM, params={
            "lat": c["lat"], "lon": c["lng"],
            "format": "json", "zoom": 16, "addressdetails": 1,
        }, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            addr = r.json().get("address", {})
            neighborhood = (addr.get("neighbourhood") or addr.get("suburb")
                           or addr.get("quarter") or addr.get("city_district") or "")
        print(f"  Mahalle: {neighborhood}")
    except Exception as e:
        print(f"  Nominatim error: {e}")
    time.sleep(1.1)

    district = hood_map.get(neighborhood, "")
    if neighborhood and district and district != DISTRICT:
        print(f"  Skip: {neighborhood} -> {district}")
        continue
    if not district:
        lat_ok = 41.020 <= c["lat"] <= 41.095
        lng_ok = 28.940 <= c["lng"] <= 29.060
        if not (lat_ok and lng_ok):
            print(f"  Skip: coord out of bbox")
            continue

    if neighborhood and neighborhood not in hood_map:
        hood_map[neighborhood] = DISTRICT
        print(f"  Map: {neighborhood} -> {DISTRICT}")

    enriched = enrich(c["name"], neighborhood or DISTRICT, c["osm_cuisine"] or "kebap", c["lat"], c["lng"])

    entry = {
        "id": uuid.uuid4().hex[:8],
        "slug": c["slug"],
        "name": c["name"],
        "city": "İstanbul",
        "citySlug": "istanbul",
        "neighborhood": neighborhood or DISTRICT,
        "cuisine": "Kebap",
        "cuisineSlug": "kebap",
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
        "features": {"terrace": False, "parking": False, "wifi": False,
                     "reservation": False, "romantic": False, "seaView": False,
                     "liveMusic": False, "vegan": False},
        "tags": enriched["tags"],
        "sentimentSummary": enriched["sentiment_summary"],
        "llmSummary": enriched["llm_summary"],
        "faq": enriched["faq"],
        "lastUpdated": "2026-04-26",
        "verifiedData": False,
        "confidenceScore": 0.5,
        "specialFeatures": {},
        "highlights": [f"Kebap in {neighborhood or DISTRICT}", f"{DISTRICT} district"],
    }

    new_rest.append(entry)
    added_items.append(entry)
    all_slugs.add(c["slug"])
    all_coords.add((round(c["lat"],4), round(c["lng"],4)))
    print(f"  Added ok")

with open(HOOD_MAP, "w", encoding="utf-8") as f:
    json.dump(hood_map, f, ensure_ascii=False, indent=2)
with open(NEW_FILE, "w", encoding="utf-8") as f:
    json.dump(new_rest, f, ensure_ascii=False, indent=2)

print(f"\n{len(added_items)} yeni {DISTRICT} kebap added.")

if not added_items:
    sys.exit(0)

print("\nGoogle Maps ratings...")

async def scrape_place(page, r):
    name = r["name"]
    lat, lng = r.get("lat"), r.get("lng")
    url = f"https://www.google.com/maps/search/{name} besiktas istanbul/@{lat},{lng},17z"
    result = {"avgRating": None, "reviewCount": None}
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=18000)
        await page.wait_for_timeout(3500)
        full_text = await page.inner_text("body")
        for span in (await page.query_selector_all("span"))[:200]:
            try:
                t = (await span.inner_text()).strip().replace(",",".")
                val = float(t)
                if 1.0 <= val <= 5.0 and "." in t:
                    result["avgRating"] = round(val,1)
                    break
            except: pass
        m = re.search(r"\(([0-9][0-9.,\s]{0,8})\)", full_text)
        if m:
            num = re.sub(r"[^0-9]","",m.group(1))
            try:
                cnt = int(num)
                if 1 <= cnt <= 200000:
                    result["reviewCount"] = cnt
            except: pass
    except Exception as e:
        print(f"  Error ({name}): {str(e)[:60]}")
    return result

async def run():
    targets = [r for r in added_items if r.get("avgRating") is None]
    print(f"Scraping: {len(targets)}")
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox","--disable-blink-features=AutomationControlled"])
        ctx = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36",
            locale="tr-TR",
        )
        page = await ctx.new_page()
        await page.add_init_script("Object.defineProperty(navigator,'webdriver',{get:()=>undefined});")
        for i, r in enumerate(targets, 1):
            res = await scrape_place(page, r)
            r["avgRating"] = res["avgRating"]
            r["reviewCount"] = res["reviewCount"]
            print(f"  [{i}/{len(targets)}] {r['name']}: {res['avgRating']} ({res['reviewCount']})")
            await asyncio.sleep(2)
        await browser.close()

    slug_map = {r["slug"]: r for r in added_items}
    for entry in new_rest:
        if entry["slug"] in slug_map:
            u = slug_map[entry["slug"]]
            entry["avgRating"] = u["avgRating"]
            entry["reviewCount"] = u["reviewCount"]
    with open(NEW_FILE, "w", encoding="utf-8") as f:
        json.dump(new_rest, f, ensure_ascii=False, indent=2)
    print("Ratings saved.")

asyncio.run(run())
