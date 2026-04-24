# -*- coding: utf-8 -*-
"""
Her benzersiz neighborhood için Nominatim'den ilçe (district/town) bilgisi çeker.
Çıktı: data/neighborhood_to_district.json
"""

import json, time, requests

INPUT = "data/processed/istanbul.json"
OUTPUT = "data/neighborhood_to_district.json"
NOMINATIM = "https://nominatim.openstreetmap.org/reverse"

with open(INPUT, encoding="utf-8") as f:
    restaurants = json.load(f)

# Unique neighborhood → koordinat eşlemesi (ilk restoranın koordinatını kullan)
hood_coords = {}
for r in restaurants:
    hood = r.get("neighborhood", "").strip()
    lat, lng = r.get("lat"), r.get("lng")
    if hood and lat and lng and hood not in hood_coords:
        hood_coords[hood] = (lat, lng)

print(f"{len(hood_coords)} unique neighborhood bulundu", flush=True)

# Mevcut haritayı yükle (varsa devam et)
try:
    with open(OUTPUT, encoding="utf-8") as f:
        district_map = json.load(f)
except:
    district_map = {}

headers = {"User-Agent": "Restoralla/1.0 (github.com/restoralla)"}

done = 0
for hood, (lat, lng) in hood_coords.items():
    if district_map.get(hood):  # skip only if already filled
        continue

    try:
        r = requests.get(
            NOMINATIM,
            params={"lat": lat, "lon": lng, "format": "json", "zoom": 14, "addressdetails": 1},
            headers=headers,
            timeout=10,
        )
        if r.status_code == 200:
            addr = r.json().get("address", {})
            district = addr.get("town") or addr.get("city_district") or addr.get("suburb") or ""
            district_map[hood] = district
            hood_safe = hood.encode("ascii", "replace").decode()
            district_safe = district.encode("ascii", "replace").decode()
            print(f"  {hood_safe} -> {district_safe}", flush=True)
        else:
            district_map[hood] = ""
    except Exception as e:
        print(f"  HATA ({hood.encode('ascii','replace').decode()}): {str(e)[:40]}", flush=True)
        district_map[hood] = ""

    done += 1
    if done % 20 == 0:
        with open(OUTPUT, "w", encoding="utf-8") as f:
            json.dump(district_map, f, ensure_ascii=False, indent=2)
        print(f">>> Kayit: {done}/{len(hood_coords)}", flush=True)

    time.sleep(1.1)  # Nominatim rate limit: max 1 req/s

with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(district_map, f, ensure_ascii=False, indent=2)

print(f"\n[OK] {len(district_map)} neighborhood haritasi olusturuldu -> {OUTPUT}", flush=True)
