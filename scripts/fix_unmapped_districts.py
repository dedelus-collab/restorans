# -*- coding: utf-8 -*-
"""Unmapped mahalleleri koordinatlarla farklı zoom seviyelerinde dene."""
import json, time, requests, sys
sys.stdout.reconfigure(encoding='utf-8')

INPUT = "data/processed/istanbul.json"
OUTPUT = "data/neighborhood_to_district.json"
NOMINATIM = "https://nominatim.openstreetmap.org/reverse"
HEADERS = {"User-Agent": "Restoralla/1.0 (github.com/restoralla)"}

with open(INPUT, encoding="utf-8") as f:
    restaurants = json.load(f)

with open(OUTPUT, encoding="utf-8") as f:
    district_map = json.load(f)

# Koordinat haritası
hood_coords = {}
for r in restaurants:
    hood = r.get("neighborhood", "").strip()
    lat, lng = r.get("lat"), r.get("lng")
    if hood and lat and lng and hood not in hood_coords:
        hood_coords[hood] = (lat, lng)

unmapped = [h for h, v in district_map.items() if not v]
print(f"Unmapped: {len(unmapped)}")

# Known manual mappings for common Istanbul neighborhoods
MANUAL = {
    "Tozkoparan Mahallesi": "Güngören",
    "Kılıçali Paşa": "Beyoğlu",
    "Harbiye Mahallesi": "Şişli",
    "Yeşilyurt Mahallesi": "Bakırköy",
    "Şişli": "Şişli",
    "Nisbetiye Mahallesi": "Beşiktaş",
    "Akat Mahallesi": "Beşiktaş",
    "Gökalp Mahallesi": "Zeytinburnu",
    "Kültür Mahallesi": "Bahçelievler",
    "Pınar Mahallesi": "Gaziosmanpaşa",
    "Çamlık Mahallesi": "Üsküdar",
    "Fenerbahçe Mahallesi": "Kadıköy",
    "Suadiye Mahallesi": "Kadıköy",
    "Bostancı Mahallesi": "Kadıköy",
    "Göztepe Mahallesi": "Kadıköy",
    "Koşuyolu Mahallesi": "Kadıköy",
    "Moda Mahallesi": "Kadıköy",
    "Erenköy Mahallesi": "Kadıköy",
    "Acıbadem Mahallesi": "Kadıköy",
    "Osmanağa Mahallesi": "Kadıköy",
    "Çarşı Mahallesi": "Beşiktaş",
    "Sinanpaşa Mahallesi": "Beşiktaş",
    "Vişnezade Mahallesi": "Beşiktaş",
    "Mecidiyeköy Mahallesi": "Şişli",
    "Fulya Mahallesi": "Şişli",
    "Bozkurt Mahallesi": "Şişli",
    "Hüseyinağa": "Beyoğlu",
    "Asmalı Mescit": "Beyoğlu",
    "Cihangir Mahallesi": "Beyoğlu",
    "Müeyyedzade": "Beyoğlu",
}

# Apply manual mappings first
for hood in unmapped:
    if hood in MANUAL:
        district_map[hood] = MANUAL[hood]
        print(f"  [MANUAL] {hood} -> {MANUAL[hood]}")

# For remaining, try Nominatim with different zoom levels
still_unmapped = [h for h in unmapped if not district_map.get(h)]
print(f"\nStill need geocoding: {len(still_unmapped)}")

for hood in still_unmapped:
    if hood not in hood_coords:
        print(f"  [NO COORDS] {hood}")
        continue
    lat, lng = hood_coords[hood]
    found = ""
    for zoom in [12, 10, 8]:
        try:
            r = requests.get(
                NOMINATIM,
                params={"lat": lat, "lon": lng, "format": "json", "zoom": zoom, "addressdetails": 1},
                headers=HEADERS,
                timeout=10,
            )
            if r.status_code == 200:
                addr = r.json().get("address", {})
                district = (addr.get("city_district") or addr.get("town") or
                           addr.get("suburb") or addr.get("municipality") or "")
                if district:
                    found = district
                    break
        except Exception as e:
            print(f"  ERROR {hood}: {e}")
        time.sleep(1.1)

    district_map[hood] = found
    print(f"  {hood} -> {found or '(not found)'}")
    time.sleep(0.5)

with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(district_map, f, ensure_ascii=False, indent=2)

filled = sum(1 for v in district_map.values() if v)
print(f"\n[OK] Final: {filled}/{len(district_map)} mapped")
