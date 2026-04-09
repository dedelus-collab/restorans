# -*- coding: utf-8 -*-
"""
Ham OSM JSON verisini Next.js'in kullandigi TypeScript dosyasina donusturur.
Kullanim:
  python scripts/json_to_ts.py
"""
import json
import re
from pathlib import Path

CITY_FIX = {
    "istanbul": "\u0130stanbul",
    "ankara": "Ankara",
    "izmir": "\u0130zmir",
    "antalya": "Antalya",
    "bursa": "Bursa",
}

def fix_city(city_slug):
    return CITY_FIX.get(city_slug.lower(), city_slug)

def to_ts_value(v):
    if v is None:
        return "undefined"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return str(v)
    if isinstance(v, str):
        escaped = v.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
        return f'"{escaped}"'
    if isinstance(v, list):
        items = ", ".join(to_ts_value(i) for i in v)
        return f"[{items}]"
    if isinstance(v, dict):
        pairs = ", ".join(f"{k}: {to_ts_value(val)}" for k, val in v.items())
        return f"{{{pairs}}}"
    return f'"{v}"'

def convert(input_path: str, output_path: str):
    with open(input_path, encoding="utf-8") as f:
        raw = json.load(f)

    # City adini duzelt
    for r in raw:
        r["city"] = fix_city(r.get("city_slug", ""))

    # Slug cakismalarini onle
    seen_slugs: dict[str, int] = {}
    for r in raw:
        slug = r["slug"] or "restoran"
        if slug in seen_slugs:
            seen_slugs[slug] += 1
            r["slug"] = f"{slug}-{seen_slugs[slug]}"
        else:
            seen_slugs[slug] = 0

    lines = []
    lines.append('import type { Restaurant } from "./restaurants";')
    lines.append("")
    lines.append("export const istanbulRestaurants: Restaurant[] = [")

    for r in raw:
        lines.append("  {")
        lines.append(f'    id: {to_ts_value(r["id"])},')
        lines.append(f'    slug: {to_ts_value(r["slug"])},')
        lines.append(f'    name: {to_ts_value(r["name"])},')
        lines.append(f'    city: {to_ts_value(r["city"])},')
        lines.append(f'    citySlug: {to_ts_value(r["city_slug"])},')
        lines.append(f'    neighborhood: {to_ts_value(r["neighborhood"])},')
        lines.append(f'    cuisine: {to_ts_value(r["cuisine"])},')
        if r.get("cuisine_slug"):
            lines.append(f'    cuisineSlug: {to_ts_value(r["cuisine_slug"])},')
        lines.append(f'    priceRange: {r["price_range"]} as 1|2|3|4,')
        lines.append(f'    avgRating: {r["avg_rating"] if r["avg_rating"] is not None else 0},')
        lines.append(f'    reviewCount: {r["review_count"]},')
        lines.append(f'    address: {to_ts_value(r["address"])},')
        lines.append(f'    lat: {r["lat"] or 0},')
        lines.append(f'    lng: {r["lng"] or 0},')
        if r.get("phone"):
            lines.append(f'    phone: {to_ts_value(r["phone"])},')
        if r.get("website"):
            lines.append(f'    website: {to_ts_value(r["website"])},')
        lines.append(f'    openingHours: {to_ts_value(r["opening_hours"])},')
        if r.get("hours_estimated"):
            lines.append(f'    hoursEstimated: true,')
        lines.append(f'    features: {to_ts_value(r["features"])},')
        lines.append(f'    tags: {to_ts_value(r["tags"])},')
        lines.append(f'    sentimentSummary: {to_ts_value(r["sentiment_summary"])},')
        lines.append(f'    llmSummary: {to_ts_value(r["llm_summary"])},')
        lines.append(f'    lastUpdated: {to_ts_value(r["last_updated"])},')
        lines.append(f'    verifiedData: {to_ts_value(r["verified_data"])},')
        lines.append(f'    confidenceScore: {r["confidence_score"]},')
        if r.get("highlights"):
            lines.append(f'    highlights: {to_ts_value(r["highlights"])},')
        if r.get("has_reviews"):
            lines.append(f'    hasReviews: true,')
        if r.get("special_features"):
            sf = r["special_features"]
            sf_parts = []
            if sf.get("signatureDish"):
                sf_parts.append(f'signatureDish: {to_ts_value(sf["signatureDish"])}')
            if sf.get("signatureDishes"):
                sf_parts.append(f'signatureDishes: {to_ts_value(sf["signatureDishes"])}')
            if sf.get("popularDishes"):
                sf_parts.append(f'popularDishes: {to_ts_value(sf["popularDishes"])}')
            if sf.get("dietaryOptions"):
                sf_parts.append(f'dietaryOptions: {to_ts_value(sf["dietaryOptions"])}')
            if sf.get("noiseLevel"):
                sf_parts.append(f'noiseLevel: {to_ts_value(sf["noiseLevel"])}')
            if sf.get("avgMealCost") is not None:
                sf_parts.append(f'avgMealCost: {sf["avgMealCost"]}')
            if sf.get("laptopFriendly"):
                sf_parts.append(f'laptopFriendly: true')
            if sf.get("outdoorHeating"):
                sf_parts.append(f'outdoorHeating: true')
            if sf.get("groupTables"):
                sf_parts.append(f'groupTables: true')
            if sf.get("lighting"):
                sf_parts.append(f'lighting: {to_ts_value(sf["lighting"])}')
            if sf.get("criticalMinus"):
                sf_parts.append(f'criticalMinus: {to_ts_value(sf["criticalMinus"])}')
            if sf.get("standoutPlus"):
                sf_parts.append(f'standoutPlus: {to_ts_value(sf["standoutPlus"])}')
            if sf.get("contextualRatings"):
                cr = sf["contextualRatings"]
                cr_parts = []
                for k in ["businessLunch", "romanticDate", "familyDining", "soloVisit", "groupDining"]:
                    if cr.get(k) is not None:
                        cr_parts.append(f'{k}: {cr[k]}')
                if cr_parts:
                    sf_parts.append(f'contextualRatings: {{{", ".join(cr_parts)}}}')
            if sf_parts:
                lines.append(f'    specialFeatures: {{{", ".join(sf_parts)}}},')
        if r.get("scenario_summary"):
            ss = r["scenario_summary"]
            ss_parts = []
            for k in ["birthday", "budget", "vegetarian", "quickLunch", "tourist", "romantic", "family", "lateNight"]:
                if ss.get(k):
                    ss_parts.append(f'{k}: {to_ts_value(ss[k])}')
            if ss_parts:
                lines.append(f'    scenarioSummary: {{{", ".join(ss_parts)}}},')
        if r.get("faq"):
            faq_items = ", ".join(
                f'{{question: {to_ts_value(item["question"])}, answer: {to_ts_value(item["answer"])}}}'
                for item in r["faq"]
            )
            lines.append(f'    faq: [{faq_items}],')
        if r.get("data_freshness"):
            df = r["data_freshness"]
            lines.append(f'    dataFreshness: {{lastVerified: {to_ts_value(df["lastVerified"])}, source: {to_ts_value(df["source"])}, confidence: {to_ts_value(df["confidence"])}}},')
        if r.get("menu_items"):
            lines.append(f'    menuItems: {to_ts_value(r["menu_items"])},')
        if r.get("price_detail"):
            pd = r["price_detail"]
            pd_parts = ", ".join(f'{k}: {to_ts_value(v)}' for k, v in pd.items() if v)
            lines.append(f'    priceDetail: {{{pd_parts}}},')
        # Rezervasyon linkleri - koordinatlardan Google Maps, varsa website
        lat, lng = r.get("lat"), r.get("lng")
        name_enc = r["name"].replace(" ", "+")
        gmap_url = f"https://www.google.com/maps/search/{name_enc}/@{lat},{lng},17z" if lat and lng else None
        res_parts = []
        if gmap_url:
            res_parts.append(f'googleMaps: {to_ts_value(gmap_url)}')
        if r.get("website"):
            res_parts.append(f'website: {to_ts_value(r["website"])}')
        if res_parts:
            lines.append(f'    reservationLinks: {{{", ".join(res_parts)}}},')
        if r.get("photo_url"):
            lines.append(f'    photoUrl: {to_ts_value(r["photo_url"])},')
        if r.get("nearby"):
            nb = r["nearby"]
            nb_parts = []
            if nb.get("transit"):
                items = ", ".join(to_ts_value(t) for t in nb["transit"])
                nb_parts.append(f'transit: [{items}]')
            if nb.get("landmarks"):
                items = ", ".join(to_ts_value(l) for l in nb["landmarks"])
                nb_parts.append(f'landmarks: [{items}]')
            if nb_parts:
                lines.append(f'    nearby: {{{", ".join(nb_parts)}}},')
        lines.append("  },")

    lines.append("];")

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"[OK] {len(raw)} restoran -> {output_path}")

if __name__ == "__main__":
    # processed varsa onu kullan (llm_summary dolu), yoksa raw
    import os
    src = "data/processed/istanbul.json" if os.path.exists("data/processed/istanbul.json") else "data/raw/istanbul.json"
    convert(src, "data/istanbul.ts")
