# -*- coding: utf-8 -*-
"""
Her restoran icin OSM'den yakin transit (metro/tramvay/vapur/marmaray)
ve landmark (muze/tarihi yer/turistik attraction) bilgisini hesaplar.

Stratejiler:
- Tek bulk Overpass sorgusu ile Istanbul'daki tum ilgili POI'leri cek
- Her restoran icin haversine ile en yakinlari lokal hesapla
- Rate limit yemeyiz, 453 restoran 1-2 dakikada biter

Output: istanbul.json'a `nearby` alani eklenir:
{
  "transit": [
    {"name": "Sultanahmet Tramway Stop", "type": "tram", "distance_m": 240, "walk_min": 3},
    ...
  ],
  "landmarks": [
    {"name": "Hagia Sophia", "type": "museum", "distance_m": 180, "walk_min": 2},
    ...
  ]
}
"""

import json
import math
import sys
import time
import requests

INPUT = "data/processed/istanbul.json"
POI_CACHE = "data/osm_pois_istanbul.json"

OVERPASS_URLS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.openstreetmap.fr/api/interpreter",
]

# Istanbul siniri icin bbox (kabaca): lat 40.80-41.30, lon 28.40-29.50
BBOX = "40.80,28.40,41.30,29.50"

QUERY = f"""
[out:json][timeout:120];
(
  node["railway"="station"]["station"~"subway|light_rail"]({BBOX});
  node["railway"="station"]["subway"="yes"]({BBOX});
  node["station"="subway"]({BBOX});
  node["railway"="tram_stop"]({BBOX});
  node["public_transport"="stop_position"]["train"="yes"]({BBOX});
  node["amenity"="ferry_terminal"]({BBOX});
  node["public_transport"="station"]["ferry"="yes"]({BBOX});
  node["tourism"="attraction"]["name"]({BBOX});
  node["tourism"="museum"]["name"]({BBOX});
  node["historic"~"."]["name"]({BBOX});
  way["tourism"="attraction"]["name"]({BBOX});
  way["tourism"="museum"]["name"]({BBOX});
  way["historic"~"."]["name"]({BBOX});
);
out center tags;
""".strip()


def haversine_m(lat1, lon1, lat2, lon2):
    R = 6371000
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2 * R * math.asin(math.sqrt(a))


def classify_transit(tags: dict) -> str | None:
    if tags.get("railway") == "tram_stop":
        return "tramvay"
    if tags.get("amenity") == "ferry_terminal" or tags.get("ferry") == "yes":
        return "vapur"
    if tags.get("subway") == "yes" or tags.get("station") == "subway":
        return "metro"
    station = tags.get("station", "")
    if "subway" in station:
        return "metro"
    if "light_rail" in station:
        return "metro"
    if tags.get("train") == "yes":
        return "marmaray"
    return None


def classify_landmark(tags: dict) -> str | None:
    if tags.get("tourism") == "museum":
        return "muze"
    if tags.get("tourism") == "attraction":
        return "attraction"
    h = tags.get("historic")
    if h:
        if h in ("monument", "memorial"):
            return "anit"
        if h in ("castle", "fort", "citywall"):
            return "kale"
        if h in ("church", "mosque", "synagogue", "place_of_worship"):
            return "dini"
        if h == "archaeological_site":
            return "arkeoloji"
        return "tarihi"
    return None


def fetch_pois():
    for url in OVERPASS_URLS:
        print(f"[OSM] {url} ...", flush=True)
        try:
            r = requests.post(url, data={"data": QUERY}, timeout=180)
            if r.status_code == 200:
                data = r.json()
                print(f"[OSM] OK: {len(data.get('elements', []))} element", flush=True)
                return data
            else:
                print(f"  HTTP {r.status_code}", flush=True)
        except Exception as e:
            print(f"  HATA: {str(e)[:80]}", flush=True)
    return None


def load_or_fetch_pois():
    try:
        with open(POI_CACHE, encoding="utf-8") as f:
            cached = json.load(f)
        print(f"[CACHE] {len(cached.get('elements', []))} POI yuklendi", flush=True)
        return cached
    except Exception:
        pass

    data = fetch_pois()
    if data:
        with open(POI_CACHE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
    return data


def extract_pois(data: dict):
    transit_pois = []
    landmark_pois = []

    for el in data.get("elements", []):
        tags = el.get("tags", {}) or {}
        name = tags.get("name") or tags.get("name:tr") or tags.get("name:en")
        if not name:
            continue

        if el.get("type") == "node":
            lat, lon = el.get("lat"), el.get("lon")
        else:
            c = el.get("center", {})
            lat, lon = c.get("lat"), c.get("lon")
        if lat is None or lon is None:
            continue

        t_type = classify_transit(tags)
        if t_type:
            transit_pois.append({"name": name, "type": t_type, "lat": lat, "lon": lon})
            continue

        l_type = classify_landmark(tags)
        if l_type:
            landmark_pois.append({"name": name, "type": l_type, "lat": lat, "lon": lon})

    # Duplicate landmark isimlerini temizle (coklu giris olabilir)
    seen_l = {}
    for p in landmark_pois:
        key = p["name"].lower()
        if key not in seen_l:
            seen_l[key] = p
    landmark_pois = list(seen_l.values())

    seen_t = {}
    for p in transit_pois:
        key = (p["name"].lower(), p["type"])
        if key not in seen_t:
            seen_t[key] = p
    transit_pois = list(seen_t.values())

    print(f"[POI] transit={len(transit_pois)} landmark={len(landmark_pois)}", flush=True)
    return transit_pois, landmark_pois


def nearest_for_restaurant(lat, lng, pois, max_distance_m, top_k):
    rows = []
    for p in pois:
        d = haversine_m(lat, lng, p["lat"], p["lon"])
        if d <= max_distance_m:
            rows.append((d, p))
    rows.sort(key=lambda x: x[0])
    out = []
    for d, p in rows[:top_k]:
        out.append({
            "name": p["name"],
            "type": p["type"],
            "distance_m": int(round(d)),
            "walk_min": max(1, int(round(d / 80))),
        })
    return out


def main():
    data = load_or_fetch_pois()
    if not data:
        print("[HATA] POI verisi alinamadi", flush=True)
        sys.exit(1)

    transit_pois, landmark_pois = extract_pois(data)

    with open(INPUT, encoding="utf-8") as f:
        restaurants = json.load(f)

    enriched = 0
    for i, r in enumerate(restaurants):
        lat = r.get("lat")
        lng = r.get("lng")
        if not lat or not lng:
            continue

        transit = nearest_for_restaurant(lat, lng, transit_pois, max_distance_m=1500, top_k=3)
        landmarks = nearest_for_restaurant(lat, lng, landmark_pois, max_distance_m=1500, top_k=5)

        if transit or landmarks:
            r["nearby"] = {"transit": transit, "landmarks": landmarks}
            enriched += 1

        if (i + 1) % 50 == 0:
            print(f"  islendi: {i+1}/{len(restaurants)} | zenginlesen: {enriched}", flush=True)

    with open(INPUT, "w", encoding="utf-8") as f:
        json.dump(restaurants, f, ensure_ascii=False, indent=2)

    print(f"\n[OK] {enriched}/{len(restaurants)} restorana 'nearby' eklendi -> {INPUT}", flush=True)


if __name__ == "__main__":
    main()
