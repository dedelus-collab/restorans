# -*- coding: utf-8 -*-
"""Kalan Türkçe highlight'ları regex ile çevirir."""
import json, re, sys
sys.stdout.reconfigure(encoding="utf-8")

INPUT = "data/processed/istanbul.json"
TR_CHARS = re.compile(r'[şçğüöıŞÇĞÜÖİâîû]')

with open(INPUT, encoding="utf-8") as f:
    data = json.load(f)

# (pattern, replacement) — uzundan kısaya sıralı
RULES = [
    # Atmosfer / ortam
    (r"sıcak ve nezih atmosfer", "warm and refined atmosphere"),
    (r"sıcak ve samimi atmosfer", "warm and welcoming atmosphere"),
    (r"tarihi ve modern dekorasyonun birleştiği romantik atmosfer", "romantic atmosphere blending historic and modern décor"),
    (r"romantik ve iş toplantılarına uygun", "suitable for romantic dinners and business meetings"),
    (r"romantik atmosfer(de)?", "romantic atmosphere"),
    (r"şık ve modern dekorasyon", "elegant and modern décor"),
    (r"şık dekorasyon", "elegant décor"),
    (r"modern dekorasyon", "modern décor"),
    (r"tarihi atmosfer", "historic atmosphere"),
    (r"samimi atmosfer", "welcoming atmosphere"),
    (r"rahat ve samimi ortam", "relaxed and friendly environment"),
    (r"keyifli bir ortam", "enjoyable atmosphere"),
    (r"güzel bir ortam", "pleasant setting"),
    (r"ferah ortam", "spacious setting"),
    (r"sakin bir ortam", "quiet setting"),
    (r"canlı atmosfer", "lively atmosphere"),
    (r"şık atmosfer", "elegant atmosphere"),
    (r"nezih atmosfer", "refined atmosphere"),
    (r"otantik atmosfer", "authentic atmosphere"),

    # Konum / manzara
    (r"manzaralı bir konumda bulunuyor\.?", "located in a scenic setting"),
    (r"deniz manzaralı restoran", "sea-view restaurant"),
    (r"boğaz manzaralı restoran", "Bosphorus-view restaurant"),
    (r"deniz manzaralı teras", "sea-view terrace"),
    (r"manzaralı teras[ı]?", "scenic terrace"),
    (r"boğaz manzaras[ıi]", "Bosphorus view"),
    (r"deniz manzaras[ıi]", "sea view"),
    (r"panoramik manzara", "panoramic view"),
    (r"şehir manzaras[ıi]", "city view"),
    (r"tarihi yarımadada", "in the historic peninsula"),
    (r"merkezi konumda", "centrally located"),
    (r"tarihi bir binada", "in a historic building"),

    # Yemek / malzeme
    (r"taze ve özenle hazırlanmış yemekler", "freshly and carefully prepared dishes"),
    (r"taze ve yerel malzemelerle hazırlanan gurme kahvaltılar", "gourmet breakfasts with fresh local ingredients"),
    (r"taze ve yerel malzemelerle hazırlanan gurme yemekler", "gourmet dishes with fresh local ingredients"),
    (r"taze ve yerel malzemelerle hazırlanan yemekler", "dishes prepared with fresh local ingredients"),
    (r"taze ve yerel malzemeler", "fresh and local ingredients"),
    (r"yerel malzemeler", "local ingredients"),
    (r"özenle hazırlanmış yemekler", "carefully prepared dishes"),
    (r"lezzetli yemekler", "delicious dishes"),
    (r"zengin menü seçimi", "extensive menu selection"),
    (r"geniş menü seçimi", "wide menu selection"),
    (r"zengin menü", "rich menu"),
    (r"geniş menü", "extensive menu"),
    (r"çeşitli mezeler", "variety of mezes"),
    (r"taze deniz ürünleri", "fresh seafood"),
    (r"deniz ürünleri", "seafood"),
    (r"ev yapımı yemekler", "home-style cooking"),
    (r"geleneksel tarifler", "traditional recipes"),
    (r"geleneksel türk mutfağı", "traditional Turkish cuisine"),
    (r"türk mutfağı", "Turkish cuisine"),
    (r"yunan mutfağı", "Greek cuisine"),
    (r"akdeniz mutfağı", "Mediterranean cuisine"),
    (r"osmanlı mutfağı", "Ottoman cuisine"),
    (r"anadolu mutfağı", "Anatolian cuisine"),

    # Özellikler
    (r"flawless dinner deneyimi", "flawless dinner experience"),
    (r"gastronomi deneyimi", "gastronomy experience"),
    (r"gastronomi deneyim", "gastronomy experience"),
    (r"şef restoranı ve gastronomi deneyimi", "chef's restaurant and gastronomy experience"),
    (r"şef restoranı olarak kaliteli servis sunar\.?", "offers quality service as a chef's restaurant"),
    (r"şef restoranı gibi özelliklerle dikkat çekiyor\.?", "stands out with chef's restaurant features"),
    (r"şef restoranı olarak öne çıkması", "stands out as a chef's restaurant"),
    (r"şef restoranı olarak", "as a chef's restaurant"),
    (r"şef restoranı özelliği\.?", "chef's restaurant feature"),
    (r"şef restoranı", "chef's restaurant"),
    (r"iş toplantıları ve.*seçenekleri", "options for business meetings and dining"),
    (r"iş yemeği.*olarak öne çıkaran özellikler\.?", "features ideal for business dining"),
    (r"iş yemekleri ve çiftler için uygun atmosfer\.?", "atmosphere ideal for business lunches and couples"),
    (r"iş yemekleri için uygun", "suitable for business lunches"),
    (r"iş toplantılarına uygun", "suitable for business meetings"),
    (r"büyük gruplar için uygun", "suitable for large groups"),
    (r"aileler için uygun", "family-friendly"),
    (r"vejetaryen seçenekler", "vegetarian options"),
    (r"vegan seçenekler", "vegan options"),
    (r"gluten.?siz seçenekler", "gluten-free options"),
    (r"rezervasyon önerilir", "reservation recommended"),
    (r"sevgililer günü için ideal rezervasyon fırsatı", "ideal reservation for Valentine's Day"),
    (r"sevgililer günü için ideal", "ideal for Valentine's Day"),
    (r"özel geceler için ideal", "ideal for special evenings"),
    (r"hafta sonu brunch için ideal bir seçim\.?", "ideal choice for weekend brunch"),
    (r"hafta sonu için ideal", "ideal for weekends"),
    (r"brunch seçeneği", "brunch option"),
    (r"gece geç saatlere kadar açık", "open until late at night"),
    (r"geç saatlere kadar açık", "open until late"),
    (r"24 saat açık", "open 24 hours"),

    # Fiyat / servis
    (r"orta fiyat aralığı ve standart.* hizmet sunumu\.?", "mid-range pricing with standard service"),
    (r"orta fiyat aralığı", "mid-range pricing"),
    (r"uygun fiyatlı seçenekler", "affordable options"),
    (r"uygun fiyatlı", "affordable"),
    (r"kaliteli hizmet", "quality service"),
    (r"hızlı servis", "fast service"),
    (r"özenli servis", "attentive service"),

    # Pop. özellikler
    (r"canlı müzik", "live music"),
    (r"açık teras", "open terrace"),
    (r"bahçe", "garden seating"),
    (r"vale park", "valet parking"),
    (r"ücretsiz otopark", "free parking"),
    (r"wifi", "WiFi"),

    # Ortak Türkçe sözcükler (kısa, en sona)
    (r"\bve\b", "and"),
    (r"\bbir\b", "a"),
    (r"\biçin\b", "for"),
    (r"\bolan\b", ""),
    (r"\bolan\.?$", ""),
]

def translate(text: str) -> str:
    t = text
    for pattern, replacement in RULES:
        t = re.sub(pattern, replacement, t, flags=re.IGNORECASE)
    # Baştaki/sondaki boşlukları ve noktalama düzeltmeleri
    t = t.strip().strip(",").strip()
    if t and t[-1] not in ".!?":
        pass  # nokta ekleme
    return t

changed = 0
still_tr = []
for r in data:
    if not r.get("highlights"):
        continue
    new_h = []
    for h in r["highlights"]:
        if TR_CHARS.search(h):
            translated = translate(h)
            if TR_CHARS.search(translated):
                still_tr.append((r["name"], h, translated))
            new_h.append(translated)
            changed += 1
        else:
            new_h.append(h)
    r["highlights"] = new_h

with open(INPUT, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"[OK] {changed} highlight işlendi.")
if still_tr:
    print(f"\nHala Türkçe karakter içeren {len(still_tr)} highlight:")
    for name, orig, trans in still_tr[:15]:
        print(f"  [{name}]\n    orijinal: {orig}\n    sonuç:    {trans}")
