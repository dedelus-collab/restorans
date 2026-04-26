# -*- coding: utf-8 -*-
"""
Kadıköy ilçesindeki kebap restoranlarını OSM'den çeker,
Groq ile zenginleştirir, new_restaurants.json'a ekler.
Sonra Playwright ile Google Maps'ten gerçek rating çeker.
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
HEADERS    = {"User-Agent": "Restoralla/1.0 add_kadikoy_kebap"}
GROQ_KEY   = os.environ.get("GROQ_API_KEY", "")

TR = str.maketrans("şçğüöıŞÇĞÜÖİâîûÂÎÛ", "scguoiSCGUOIaiuAIU")

def slugify(t):
    t = t.translate(TR).lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")

def clean_name(name):
    cleaned = "".join(c for c in name if unicodedata.category(c)[0] in ("L","N","Z","P"))
    cleaned = cleaned.strip()
    if cleaned == cleaned.lower():
        cleaned = cleaned.title()
    return cleaned

# Kadıköy ilçesi gerçek sınırları (Ataşehir hariç, Marmara kıyısından Ataşehir sınırına kadar)
KADIKOY_BBOX = "40.950,28.980,41.015,29.075"

QUERY = f"""
[out:json][timeout:60];
(
  node["amenity"="restaurant"]["cuisine"~"kebab|kebap|turkish|köfte|kofteci|lahmacun|tantuni|döner|doner|iskender",i]({KADIKOY_BBOX});
  way["amenity"="restaurant"]["cuisine"~"kebab|kebap|turkish|köfte|kofteci|lahmacun|tantuni|döner|doner|iskender",i]({KADIKOY_BBOX});
  node["amenity"="restaurant"]["name"~"kebap|kebab|iskender|döner|doner|köfte|kofteci|adana|urfa|lahmacun",i]({KADIKOY_BBOX});
  way["amenity"="restaurant"]["name"~"kebap|kebab|iskender|döner|doner|köfte|kofteci|adana|urfa|lahmacun",i]({KADIKOY_BBOX});
  node["amenity"="fast_food"]["cuisine"~"kebab|kebap|turkish",i]({KADIKOY_BBOX});
  way["amenity"="fast_food"]["cuisine"~"kebab|kebap|turkish",i]({KADIKOY_BBOX});
);
out center tags;
"""

print("Overpass API sorgulanıyor (Kadıköy kebap)...")
resp = requests.post(OVERPASS, data={"data": QUERY}, headers=HEADERS, timeout=90)
resp.raise_for_status()
elements = resp.json().get("elements", [])
print(f"OSM'den {len(elements)} eleman geldi.")

with open(EXISTING, encoding="utf-8") as f:
    existing = json.load(f)
with open(NEW_FILE, encoding="utf-8") as f:
    new_rest = json.load(f)
with open(HOOD_MAP, encoding="utf-8") as f:
    hood_map = json.load(f)

all_slugs   = {r["slug"] for r in existing} | {r["slug"] for r in new_rest}
all_coords  = {(round(r["lat"],4), round(r["lng"],4)) for r in existing if r.get("lat")}
all_coords |= {(round(r["lat"],4), round(r["lng"],4)) for r in new_rest if r.get("lat")}

SKIP = ["sosyal tesis","ibb ","okul","hastane","kafeterya","kantin","yurt","kreş","spor ","büfe","kültür merkezi"]

candidates = []
seen_this_run = set()

for el in elements:
    tags = el.get("tags", {})
    name = tags.get("name") or tags.get("name:tr") or tags.get("name:en")
    if not name: continue
    if any(kw in name.lower() for kw in SKIP): continue

    if el["type"] == "node":
        lat, lng = el.get("lat"), el.get("lon")
    else:
        c = el.get("center", {})
        lat, lng = c.get("lat"), c.get("lon")
    if not lat or not lng: continue

    name = clean_name(name)
    slug = slugify(name)
    coord = (round(lat,4), round(lng,4))

    if slug in all_slugs or coord in all_coords or slug in seen_this_run:
        continue
    seen_this_run.add(slug)

    candidates.append({
        "name": name, "slug": slug, "lat": lat, "lng": lng,
        "osm_cuisine": tags.get("cuisine","").split(";")[0].strip(),
        "phone": tags.get("phone") or tags.get("contact:phone"),
        "website": tags.get("website") or tags.get("contact:website"),
        "address": tags.get("addr:street",""),
    })

print(f"Yeni aday: {len(candidates)}")

if not candidates:
    print("Yeni kebap restoranı bulunamadı.")
    sys.exit(0)

# Groq
if GROQ_KEY:
    from groq import Groq
    groq = Groq(api_key=GROQ_KEY)
    USE_GROQ = True
else:
    USE_GROQ = False
    print("GROQ_API_KEY eksik, basit verilerle devam ediliyor.")

def groq_enrich(name, neighborhood, cuisine, lat, lng):
    if not USE_GROQ:
        return {
            "llm_summary": f"{name} is a kebap restaurant in {neighborhood}, Kadıköy, Istanbul.",
            "sentiment_summary": "A local kebap spot in Kadıköy.",
            "tags": ["Kebap", "Kadıköy", "Turkish Cuisine"],
            "faq": [
                {"question": f"What does {name} serve?", "answer": "Kebap and Turkish grilled dishes."},
                {"question": f"Where is {name}?", "answer": f"In {neighborhood}, Kadıköy, Istanbul."},
                {"question": "Do they take reservations?", "answer": "Contact the restaurant directly to check."},
            ],
        }
    prompt = f"""Istanbul restaurant guide. Write structured data in English.

Restaurant: {name}
Neighborhood: {neighborhood}
Cuisine: {cuisine} (kebap)
Location: lat {lat}, lng {lng}
District: Kadıköy, Istanbul

Return ONLY valid JSON:
{{
  "llm_summary": "2-3 sentence summary. Include neighborhood, kebap style, what makes it notable.",
  "sentiment_summary": "One sentence about atmosphere.",
  "tags": ["Kebap", "Turkish Cuisine", "{neighborhood}", "Kadıköy"],
  "faq": [
    {{"question": "What type of kebap does {name} serve?", "answer": "..."}},
    {{"question": "Where is {name} located?", "answer": "..."}},
    {{"question": "Is reservation recommended at {name}?", "answer": "..."}},
    {{"question": "What is the price range at {name}?", "answer": "..."}},
    {{"question": "What are the most popular dishes at {name}?", "answer": "..."}},
    {{"question": "Is {name} suitable for families?", "answer": "..."}}
  ]
}}"""
    try:
        r = groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role":"user","content":prompt}],
            max_tokens=500, temperature=0.3,
        )
        text = r.choices[0].message.content.strip()
        m = re.search(r"\{.*\}", text, re.DOTALL)
        if m:
            return json.loads(m.group())
    except Exception as e:
        print(f"  Groq hatası ({name}): {e}")
    return {
        "llm_summary": f"{name} is a kebap restaurant in {neighborhood}, Kadıköy.",
        "sentiment_summary": "A traditional kebap spot.",
        "tags": ["Kebap", "Kadıköy"],
        "faq": [],
    }

added_items = []

for c in candidates:
    print(f"\n→ {c['name']}")

    # Nominatim ile mahalle bul
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
        print(f"  Nominatim hatası: {e}")
    time.sleep(1.1)

    # Mahalle → ilçe kontrolü (Kadıköy olduğunu doğrula)
    district = hood_map.get(neighborhood, "")
    if neighborhood and district and district != "Kadıköy":
        print(f"  Atlanıyor: {neighborhood} → {district} (Kadıköy değil)")
        continue
    # Eşleme yoksa koordinat kontrolü yap (bbox zaten Kadıköy sınırında)
    if not district and c["lat"] and c["lng"]:
        if not (40.950 <= c["lat"] <= 41.015 and 28.980 <= c["lng"] <= 29.075):
            print(f"  Atlanıyor: koordinat bbox dışında")
            continue

    # Mahalle haritaya ekle (eğer yoksa)
    if neighborhood and neighborhood not in hood_map:
        hood_map[neighborhood] = "Kadıköy"
        print(f"  Yeni mahalle eşlemesi eklendi: {neighborhood} → Kadıköy")

    cuisine = c["osm_cuisine"] or "kebap"
    enriched = groq_enrich(c["name"], neighborhood or "Kadıköy", cuisine, c["lat"], c["lng"])
    time.sleep(0.5)

    entry = {
        "id": uuid.uuid4().hex[:8],
        "slug": c["slug"],
        "name": c["name"],
        "city": "İstanbul",
        "citySlug": "istanbul",
        "neighborhood": neighborhood or "Kadıköy",
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
        "features": {
            "terrace": False, "parking": False, "wifi": False,
            "reservation": False, "romantic": False, "seaView": False,
            "liveMusic": False, "vegan": False,
        },
        "tags": enriched.get("tags", ["Kebap", "Kadıköy"]),
        "sentimentSummary": enriched.get("sentiment_summary",""),
        "llmSummary": enriched.get("llm_summary",""),
        "faq": enriched.get("faq", []),
        "lastUpdated": "2026-04-25",
        "verifiedData": False,
        "confidenceScore": 0.5,
        "specialFeatures": {},
        "highlights": [f"Kebap restaurant in {neighborhood or 'Kadıköy'}", "Kadıköy district"],
    }

    new_rest.append(entry)
    added_items.append(entry)
    all_slugs.add(c["slug"])
    all_coords.add((round(c["lat"],4), round(c["lng"],4)))
    print(f"  Eklendi ✓")

# Güncellenmiş hood_map kaydet
with open(HOOD_MAP, "w", encoding="utf-8") as f:
    json.dump(hood_map, f, ensure_ascii=False, indent=2)

# new_restaurants.json kaydet
with open(NEW_FILE, "w", encoding="utf-8") as f:
    json.dump(new_rest, f, ensure_ascii=False, indent=2)

print(f"\n✓ {len(added_items)} yeni Kadıköy kebap restoranı eklendi.")

if not added_items:
    sys.exit(0)

# ── Google Maps rating çek ────────────────────────────────────────────────────
print("\nGoogle Maps rating çekiliyor...")

async def scrape_place(page, r):
    name = r["name"]
    lat, lng = r.get("lat"), r.get("lng")
    query = f"{name} kadıköy istanbul"
    url = f"https://www.google.com/maps/search/{query}/@{lat},{lng},17z" if lat else f"https://www.google.com/maps/search/{query}"
    result = {"avgRating": None, "reviewCount": None}
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=18000)
        await page.wait_for_timeout(3500)
        full_text = await page.inner_text("body")
        spans = await page.query_selector_all("span")
        for span in spans[:200]:
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
        print(f"  Hata ({name}): {str(e)[:60]}")
    return result

async def run_scraper():
    targets = [r for r in added_items if r.get("avgRating") is None]
    print(f"Taranacak: {len(targets)} restoran")

    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox","--disable-blink-features=AutomationControlled"],
        )
        ctx = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36",
            locale="tr-TR",
        )
        page = await ctx.new_page()
        await page.add_init_script(
            "Object.defineProperty(navigator,'webdriver',{get:()=>undefined});"
        )

        for r in targets:
            res = await scrape_place(page, r)
            r["avgRating"] = res["avgRating"]
            r["reviewCount"] = res["reviewCount"]
            print(f"  {r['name']}: {res['avgRating']} ({res['reviewCount']} yorum)")
            await asyncio.sleep(2)

        await browser.close()

    # Güncellenen değerleri new_restaurants.json'a yaz
    slug_to_item = {r["slug"]: r for r in added_items}
    for entry in new_rest:
        if entry["slug"] in slug_to_item:
            updated = slug_to_item[entry["slug"]]
            entry["avgRating"] = updated["avgRating"]
            entry["reviewCount"] = updated["reviewCount"]

    with open(NEW_FILE, "w", encoding="utf-8") as f:
        json.dump(new_rest, f, ensure_ascii=False, indent=2)
    print("✓ Rating'ler kaydedildi.")

asyncio.run(run_scraper())
