# -*- coding: utf-8 -*-
"""Kalan unmapped mahalleleri manuel olarak eşle."""
import json, sys
sys.stdout.reconfigure(encoding='utf-8')

OUTPUT = "data/neighborhood_to_district.json"

with open(OUTPUT, encoding="utf-8") as f:
    d = json.load(f)

MANUAL = {
    "Bakırköy": "Bakırköy",
    "Balat Mahallesi": "Fatih",
    "Ortaköy Mahallesi": "Beşiktaş",
    "Fatih Mahallesi": "Fatih",
    "Feriköy Mahallesi": "Şişli",
    "Cumhuriyet": "Şişli",
    "Hasanpaşa Mahallesi": "Kadıköy",
    "Akşemsettin Mahallesi": "Fatih",
    "Ekinoba Mahallesi": "Çekmeköy",
    "Şirinevler Mahallesi": "Bahçelievler",
    "Şamlar Mahallesi": "Arnavutköy",
    "İdealtepe Mahallesi": "Maltepe",
    "Türkali Mahallesi": "Beşiktaş",
    "Postane": "Beyoğlu",
    "Ömerli Mahallesi": "Çekmeköy",
    "Zühtüpaşa Mahallesi": "Kadıköy",
    "Hacı Kasım Mahallesi": "Fatih",
    "Kuleli Mahallesi": "Beşiktaş",
    "Ergenekon Mahallesi": "Şişli",
    "Ataşehir": "Ataşehir",
    "Küçükbakkalköy Mahallesi": "Ataşehir",
    "Yayla": "Güngören",
    "Kalenderhane Mahallesi": "Fatih",
    "Sakızağacı Mahallesi": "Beyoğlu",
    "Alibey Mahallesi": "Kâğıthane",
    "Hacımimi": "Fatih",
    "Zümrütevler Mahallesi": "Maltepe",
    "Çakmak Mahallesi": "Ümraniye",
    "Mimaroba Mahallesi": "Büyükçekmece",
    "Beşiktaş": "Beşiktaş",
    "Levazım Mahallesi": "Beşiktaş",
    "Baltalimanı Mahallesi": "Sarıyer",
    "Mimar Sinan Mahallesi": "Kadıköy",
    "Çekmeköy": "Çekmeköy",
    "Çatalmeşe Mahallesi": "Büyükçekmece",
    "Meclis Mahallesi": "Kâğıthane",
    "İnönü Mahallesi": "Şişli",
    "Orhantepe Mahallesi": "Kartal",
    "Feyzullah Mahallesi": "Fatih",
}

count = 0
for hood, district in MANUAL.items():
    if not d.get(hood):
        d[hood] = district
        print(f"  {hood} -> {district}")
        count += 1

with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(d, f, ensure_ascii=False, indent=2)

filled = sum(1 for v in d.values() if v)
print(f"\n[OK] Added {count} manual mappings. Total: {filled}/{len(d)}")
