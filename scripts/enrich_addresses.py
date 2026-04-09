# -*- coding: utf-8 -*-
"""
Nominatim (OpenStreetMap) ile koordinattan adres ve mahalle bilgisi doldurur.
Ucretsiz, API key gerekmez.

Kullanim:
  python scripts/enrich_addresses.py
"""

import json
import time
import requests
from pathlib import Path

HEADERS = {"User-Agent": "restorans/1.0 (restoran veritabani)"}


def reverse_geocode(lat: float, lng: float) -> dict:
    url = "https://nominatim.openstreetmap.org/reverse"
    params = {"lat": lat, "lon": lng, "format": "json", "accept-language": "tr"}
    r = requests.get(url, params=params, headers=HEADERS, timeout=10)
    r.raise_for_status()
    return r.json()


def extract_address(geo: dict) -> tuple[str, str]:
    addr = geo.get("address", {})

    # Mahalle: neighbourhood > suburb > quarter > district
    neighborhood = (
        addr.get("neighbourhood")
        or addr.get("suburb")
        or addr.get("quarter")
        or addr.get("city_district")
        or ""
    )

    # Sokak adresi
    road = addr.get("road") or addr.get("pedestrian") or ""
    house = addr.get("house_number") or ""
    street = f"{road} {house}".strip() if house else road

    district = addr.get("city_district") or addr.get("suburb") or ""
    city = addr.get("city") or addr.get("town") or "Istanbul"

    full_address = ", ".join(filter(None, [street, neighborhood, district, city]))

    return neighborhood, full_address


def enrich(input_path: str, output_path: str):
    with open(input_path, encoding="utf-8") as f:
        restaurants = json.load(f)

    missing = [r for r in restaurants if not r.get("address") or not r.get("neighborhood")]
    print(f"[INFO] {len(missing)} restoran dolduruluyor...")

    for i, r in enumerate(missing):
        lat, lng = r.get("lat"), r.get("lng")
        if not lat or not lng:
            continue
        try:
            geo = reverse_geocode(lat, lng)
            neighborhood, address = extract_address(geo)
            if not r.get("neighborhood"):
                r["neighborhood"] = neighborhood
            if not r.get("address"):
                r["address"] = address
            name = r['name'].encode('ascii', 'replace').decode()
            addr_safe = address.encode('ascii', 'replace').decode()
            print(f"[{i+1}/{len(missing)}] {name} -> {addr_safe}")
            time.sleep(1.1)  # Nominatim limiti: max 1 req/sn
        except Exception as e:
            name = r['name'].encode('ascii', 'replace').decode()
            print(f"  [ERROR] {name}: {str(e)[:80]}")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(restaurants, f, ensure_ascii=False, indent=2)

    has_addr = sum(1 for r in restaurants if r.get("address"))
    print(f"\n[OK] Adres dolu: {has_addr}/{len(restaurants)} -> {output_path}")
    print("[SONRAKI] python scripts/json_to_ts.py")
    import sys; sys.stdout.flush()


if __name__ == "__main__":
    enrich("data/processed/istanbul.json", "data/processed/istanbul.json")
