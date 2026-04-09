# -*- coding: utf-8 -*-
"""
OSM (OpenStreetMap) Restoran Scraper
Ücretsiz, API anahtarı gerekmez.

Kullanım:
  pip install requests
  python scripts/scrape_osm.py --city Istanbul --limit 500
  python scripts/scrape_osm.py --city Ankara --limit 200
"""

import requests
import json
import argparse
import time
from pathlib import Path

CITY_NAMES = {
    "istanbul": "İstanbul",
    "ankara": "Ankara",
    "izmir": "İzmir",
    "antalya": "Antalya",
    "bursa": "Bursa",
}

def fetch_restaurants(city_en: str, limit: int = 500) -> list[dict]:
    """OpenStreetMap Overpass API'den restoran verisi çeker."""

    query = f"""
    [out:json][timeout:90];
    area["name:en"="{city_en}"]["boundary"="administrative"]["admin_level"~"4|6"]->.searchArea;
    (
      node["amenity"="restaurant"](area.searchArea);
      way["amenity"="restaurant"](area.searchArea);
    );
    out body;
    """

    print(f"[OSM] {city_en} için veri çekiliyor...")

    response = requests.post(
        "https://overpass-api.de/api/interpreter",
        data={"data": query},
        timeout=120,
    )
    response.raise_for_status()

    elements = response.json().get("elements", [])
    print(f"[OSM] {len(elements)} restoran bulundu.")

    restaurants = []
    for el in elements[:limit]:
        tags = el.get("tags", {})
        name = tags.get("name") or tags.get("name:tr")
        if not name:
            continue

        city_tr = CITY_NAMES.get(city_en.lower(), city_en)
        slug = slugify(name)

        restaurant = {
            "id": str(el.get("id")),
            "slug": slug,
            "name": name,
            "city": city_tr,
            "city_slug": city_en.lower(),
            "neighborhood": tags.get("addr:suburb") or tags.get("addr:district") or "",
            "cuisine": tags.get("cuisine", "").replace(";", ", "),
            "price_range": parse_price_range(tags.get("price_range")),
            "avg_rating": None,
            "review_count": 0,
            "address": build_address(tags),
            "lat": el.get("lat") or el.get("center", {}).get("lat"),
            "lng": el.get("lon") or el.get("center", {}).get("lon"),
            "phone": tags.get("phone") or tags.get("contact:phone"),
            "website": tags.get("website") or tags.get("contact:website"),
            "opening_hours": tags.get("opening_hours", ""),
            "features": extract_features(tags),
            "tags": extract_tags(tags),
            "llm_summary": "",         # generate_summaries.py ile doldurulacak
            "sentiment_summary": "",   # generate_summaries.py ile doldurulacak
            "confidence_score": 0.7,
            "verified_data": False,
            "last_updated": time.strftime("%Y-%m-%d"),
        }
        restaurants.append(restaurant)

    return restaurants


def slugify(text: str) -> str:
    import re
    replacements = {
        "ş": "s", "ğ": "g", "ü": "u", "ö": "o", "ı": "i", "ç": "c",
        "Ş": "S", "Ğ": "G", "Ü": "U", "Ö": "O", "İ": "I", "Ç": "C",
    }
    for tr, en in replacements.items():
        text = text.replace(tr, en)
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def build_address(tags: dict) -> str:
    parts = filter(None, [
        tags.get("addr:street"),
        tags.get("addr:housenumber"),
        tags.get("addr:suburb"),
        tags.get("addr:city"),
    ])
    return ", ".join(parts)


def parse_price_range(value: str | None) -> int:
    if not value:
        return 2
    mapping = {"1": 1, "cheap": 1, "2": 2, "moderate": 2, "3": 3, "expensive": 3, "4": 4, "luxury": 4}
    return mapping.get(str(value).lower(), 2)


def extract_features(tags: dict) -> dict:
    return {
        "terrace": tags.get("outdoor_seating") == "yes",
        "parking": tags.get("parking") is not None,
        "wifi": tags.get("internet_access") in ["wlan", "wifi", "yes"],
        "reservation": tags.get("reservation") in ["yes", "recommended", "required"],
        "romantic": False,
        "seaView": False,
        "liveMusic": tags.get("live_music") == "yes",
        "vegan": tags.get("diet:vegan") in ["yes", "only"],
    }


def extract_tags(tags: dict) -> list[str]:
    result = []
    cuisine = tags.get("cuisine", "")
    if cuisine:
        result.extend(cuisine.replace(";", ",").split(","))
    if tags.get("outdoor_seating") == "yes":
        result.append("teras")
    if tags.get("diet:vegetarian") == "yes":
        result.append("vejetaryen")
    if tags.get("diet:vegan") == "yes":
        result.append("vegan")
    neighborhood = tags.get("addr:suburb") or tags.get("addr:district")
    if neighborhood:
        result.append(neighborhood.lower())
    return [t.strip().lower() for t in result if t.strip()]


def save(restaurants: list[dict], city: str):
    out_dir = Path("data/raw")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{city.lower()}.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(restaurants, f, ensure_ascii=False, indent=2)
    print(f"[OK] {len(restaurants)} restoran kaydedildi -> {out_file}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--city", default="Istanbul", help="İngilizce şehir adı")
    parser.add_argument("--limit", type=int, default=500, help="Maksimum restoran sayısı")
    args = parser.parse_args()

    restaurants = fetch_restaurants(args.city, args.limit)
    save(restaurants, args.city)


if __name__ == "__main__":
    main()
