# -*- coding: utf-8 -*-
"""
Cuisine alanlarini normalize eder.
Raw deger -> standart Turkce label (slug + display).
Koleksiyon sayfalarinin temeli.
"""
import json
import re

INPUT = "data/processed/istanbul.json"

# (raw_pattern, canonical_slug, canonical_display)
# Siraya gore ilk eslesme kazanir — daha spesifik usttte olmali
CUISINE_MAP = [
    # Kebap ailesi
    (r"kebap|kebab|adana|urfa|iskender|lahmacun|tantuni", "kebap", "Kebap"),
    # Balik & deniz urunleri
    (r"seafood|fish|balik|deniz|midye|rodos", "balik", "Balık"),
    # Pizza & italyan
    (r"pizza|pizzeria|italian|italyan", "pizza-italyan", "Pizza & İtalyan"),
    # Sushi & Japon
    (r"sushi|japon|japanese|noodle|ramen", "sushi-japon", "Sushi & Japon"),
    # Burger & Amerikan
    (r"burger|amerikan|american|steak.*house|steak_house", "burger-steak", "Burger & Steak"),
    # Pide & pideci
    (r"pide|pideci", "pide", "Pide"),
    # Kahvalti
    (r"breakfast|kahvalt", "kahvalti", "Kahvaltı"),
    # Meyhane
    (r"meyhane|meze", "meyhane", "Meyhane"),
    # Lokanta & ev yemekleri
    (r"lokanta|ev.yemek|local|regional|anadolu|naturel", "lokanta", "Lokanta"),
    # Kafe & pastane
    (r"cafe|kafe|kahve|pastane|tatlı", "kafe", "Kafe"),
    # Vegan
    (r"vegan|vejetaryen", "vegan", "Vegan"),
    # Asya
    (r"korean|chinese|thai|asian|indonesian|georgian|balkan|greek|mexican|mediterranean|european", "dunya-mutfagi", "Dünya Mutfağı"),
    # Turk genel (en sona — cok generic)
    (r"turkish|turk|türk|köfte|kıymalı|Turkish_and_International|fine_dining", "turk-mutfagi", "Türk Mutfağı"),
    # Genel / bilinmiyor
    (r"international|fusion|modern", "uluslararasi", "Uluslararası"),
]

def normalize(raw: str) -> tuple[str, str]:
    """Returns (slug, display) for given raw cuisine string."""
    s = (raw or "").lower().strip()
    if not s:
        return "turk-mutfagi", "Türk Mutfağı"  # default
    for pattern, slug, display in CUISINE_MAP:
        if re.search(pattern, s, re.IGNORECASE):
            return slug, display
    # Fallback: ilk kelimeyi capitalize et
    first = re.sub(r"[^a-zA-ZğüşöçıĞÜŞÖÇİ\s]", "", raw.split(",")[0]).strip()
    return first.lower().replace(" ", "-"), first.title()


def main():
    with open(INPUT, encoding="utf-8") as f:
        restaurants = json.load(f)

    changed = 0
    for r in restaurants:
        raw = r.get("cuisine") or ""
        slug, display = normalize(raw)
        r["cuisine_raw"] = raw          # orijinali sakla
        r["cuisine_slug"] = slug        # URL icin
        r["cuisine"] = display          # gosterim
        changed += 1

    with open(INPUT, "w", encoding="utf-8") as f:
        json.dump(restaurants, f, ensure_ascii=False, indent=2)

    # Dagilim raporu
    dist = {}
    for r in restaurants:
        k = r["cuisine"]
        dist[k] = dist.get(k, 0) + 1
    print(f"[OK] {changed} restoran normalize edildi\n")
    print("Dagilim:")
    for k, v in sorted(dist.items(), key=lambda x: -x[1]):
        print(f"  {v:3d}  {k.encode('ascii','replace').decode()}")


if __name__ == "__main__":
    main()
