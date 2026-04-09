# -*- coding: utf-8 -*-
"""
Duplicate slug'lari duzeltir.
- Zincir restoranlar (Big Chefs, Kofteci Ramiz...): slug + mahalle-slug
- Diger: slug + sira numarasi
- Bos slug: isimden uret
"""
import json
import re
import unicodedata

INPUT = "data/processed/istanbul.json"

TR_MAP = str.maketrans({
    "ş": "s", "ç": "c", "ğ": "g", "ü": "u", "ö": "o", "ı": "i",
    "â": "a", "î": "i", "û": "u",
    "Ş": "s", "Ç": "c", "Ğ": "g", "Ü": "u", "Ö": "o", "İ": "i", "I": "i",
    "ñ": "n", "é": "e", "è": "e", "ê": "e",
})

def slugify(text: str) -> str:
    s = text.translate(TR_MAP).lower()
    # ASCII disi kalanlari normalize et
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-z0-9\s-]", "", s).strip()
    s = re.sub(r"[\s_]+", "-", s)
    s = re.sub(r"-+", "-", s)
    return s[:60].rstrip("-")


def hood_slug(neighborhood: str) -> str:
    s = slugify(neighborhood)
    # "mahallesi" ve benzeri suffixleri at
    s = re.sub(r"-(mahallesi|mahalle|mah)$", "", s)
    return s.split("-")[0]  # sadece ilk kelime yeterli


def main():
    with open(INPUT, encoding="utf-8") as f:
        restaurants = json.load(f)

    # 1. Bos slug'lari isimden uret
    for r in restaurants:
        if not r.get("slug") or not re.search(r"[a-z]", r.get("slug", "")):
            r["slug"] = slugify(r.get("name", f"restoran-{r['id']}")) or f"restoran-{r['id']}"
            print(f"  [YEN?] {r['name'].encode('ascii','replace').decode()} -> {r['slug']}")

    # 2. Duplicate'lari tespit et
    from collections import Counter
    counts = Counter(r["slug"] for r in restaurants)
    dupes = {s for s, c in counts.items() if c > 1}
    print(f"\nDuplicate slug sayisi: {len(dupes)}")
    for s in sorted(dupes):
        names = [r["name"].encode("ascii","replace").decode() for r in restaurants if r["slug"] == s]
        print(f"  {s}: {names}")

    # 3. Duzelt — her duplicate gruba mahalle slug'i ekle
    for slug in dupes:
        group = [r for r in restaurants if r["slug"] == slug]
        # Tum gruba mahalle ekle
        seen = {}
        for r in group:
            hood = hood_slug(r.get("neighborhood") or "")
            new_slug = f"{slug}-{hood}" if hood else slug
            # Eger bu yeni slug da cakisiyorsa numara ekle
            if new_slug in seen:
                seen[new_slug] += 1
                r["slug"] = f"{new_slug}-{seen[new_slug]}"
            else:
                seen[new_slug] = 0
                r["slug"] = new_slug

    # 4. Hala duplicate var mi? (mahalleler de aynıysa)
    counts2 = Counter(r["slug"] for r in restaurants)
    still_dupes = {s for s, c in counts2.items() if c > 1}
    if still_dupes:
        print(f"\nHala duplicate: {still_dupes}")
        for slug in still_dupes:
            group = [r for r in restaurants if r["slug"] == slug]
            for i, r in enumerate(group):
                if i > 0:
                    r["slug"] = f"{slug}-{i+1}"

    # 5. Son kontrol
    counts3 = Counter(r["slug"] for r in restaurants)
    final_dupes = {s for s, c in counts3.items() if c > 1}
    print(f"\nSon duplicate sayisi: {len(final_dupes)}")

    with open(INPUT, "w", encoding="utf-8") as f:
        json.dump(restaurants, f, ensure_ascii=False, indent=2)

    print(f"[OK] {len(restaurants)} restoran kaydedildi")


if __name__ == "__main__":
    main()
