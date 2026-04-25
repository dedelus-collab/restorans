# -*- coding: utf-8 -*-
"""highlights alanındaki Türkçe metinleri İngilizce'ye çevirir."""
import json, re, sys
sys.stdout.reconfigure(encoding="utf-8")

INPUT = "data/processed/istanbul.json"

with open(INPUT, encoding="utf-8") as f:
    data = json.load(f)

# Sabit çeviri tablosu — tüm dosyada geçen kalıplar
TRANSLATIONS = {
    "taze ve yerel malzemelerle hazırlanan gurme yemekler": "gourmet dishes prepared with fresh and local ingredients",
    "taze ve yerel malzemelerle hazırlanan gurme kahvaltılar": "gourmet breakfasts prepared with fresh and local ingredients",
    "taze ve yerel malzemelerle hazırlanan yemekler": "dishes prepared with fresh and local ingredients",
    "taze ve yerel malzemeler": "fresh and local ingredients",
    "tarihi ve modern dekorasyonun birleştiği romantik atmosfer": "romantic atmosphere blending historic and modern décor",
    "flawless dinner deneyimi": "flawless dinner experience",
    "sevgililer günü için ideal rezervasyon fırsatı": "ideal reservation for Valentine's Day",
    "şef restoranı ve gastronomi deneyimi": "chef's restaurant and gastronomy experience",
    "şef restoranı ve gastronomi deneyimi.": "chef's restaurant and gastronomy experience.",
    "şef restoranı olarak kaliteli servis": "quality service as a chef's restaurant",
    "şef restoranı gibi özelliklerle dikkat çekiyor.": "stands out with chef's restaurant features.",
    "şef restoranı olarak öne çıkması": "stands out as a chef's restaurant",
    "şef restoranı ve gastronomi deneyim": "chef's restaurant and gastronomy experience",
    "iş yemeği ve şef restoranı olarak öne çıkaran özellikler.": "features that stand out as a business lunch and chef's restaurant.",
    "iş toplantıları ve şef restoranı seçenekleri": "options for business meetings and chef's restaurant",
    "şef restoranı özelliği.": "chef's restaurant feature.",
    "şef restoranı olarak kaliteli servis sunar.": "offers quality service as a chef's restaurant.",
}

# Genel Türkçe kalıpları için regex tabanlı çeviriler
REGEX_TRANSLATIONS = [
    (r"taze ve yerel malzemelerle hazırlanan gurme yemekler", "gourmet dishes prepared with fresh and local ingredients"),
    (r"taze ve yerel malzemelerle hazırlanan gurme kahvaltılar", "gourmet breakfasts prepared with fresh and local ingredients"),
    (r"taze ve yerel malzemelerle hazırlanan yemekler", "dishes prepared with fresh and local ingredients"),
    (r"taze ve yerel malzemeler", "fresh and local ingredients"),
    (r"tarihi ve modern dekorasyonun birleştiği romantik atmosfer", "romantic atmosphere blending historic and modern décor"),
    (r"flawless dinner deneyimi", "flawless dinner experience"),
    (r"sevgililer günü için ideal rezervasyon fırsatı", "ideal reservation for Valentine's Day"),
    (r"şef restoranı ve gastronomi deneyimi", "chef's restaurant and gastronomy experience"),
    (r"şef restoranı olarak kaliteli servis", "quality service as a chef's restaurant"),
    (r"şef restoranı gibi özelliklerle dikkat çekiyor", "stands out with chef's restaurant features"),
    (r"şef restoranı olarak öne çıkması", "stands out as a chef's restaurant"),
    (r"şef restoranı özelliği", "chef's restaurant feature"),
    (r"şef restoranı olarak", "as a chef's restaurant"),
    (r"şef restoranı", "chef's restaurant"),
    (r"iş yemeği ve.*olarak öne çıkaran özellikler", "features that stand out for business dining"),
    (r"iş toplantıları.*seçenekleri", "options for business meetings"),
    (r"gastronomi deneyimi", "gastronomy experience"),
    (r"gastronomi deneyim", "gastronomy experience"),
    (r"romantik atmosfer", "romantic atmosphere"),
    (r"gurme yemek", "gourmet dish"),
    (r"yerel malzeme", "local ingredients"),
]

def translate(text: str) -> str:
    t = text
    for pattern, replacement in REGEX_TRANSLATIONS:
        t = re.sub(pattern, replacement, t, flags=re.IGNORECASE)
    return t

changed = 0
for r in data:
    if not r.get("highlights"):
        continue
    new_highlights = []
    for h in r["highlights"]:
        translated = translate(h)
        if translated != h:
            new_highlights.append(translated)
            changed += 1
        else:
            new_highlights.append(h)
    r["highlights"] = new_highlights

with open(INPUT, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"[OK] {changed} highlight çevirildi.")
