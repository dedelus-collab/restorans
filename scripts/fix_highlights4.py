# -*- coding: utf-8 -*-
"""Kırık karışık Türkçe/İngilizce highlight'ları düzeltir ve kalanları çevirir."""
import json, re, sys
sys.stdout.reconfigure(encoding="utf-8")

INPUT = "data/processed/istanbul.json"
TR_CHARS = re.compile(r'[şçğüöıŞÇĞÜÖİâîû]')

with open(INPUT, encoding="utf-8") as f:
    data = json.load(f)

# Tam cümle çevirileri — kelime seviyesi yok, sadece tam kalıplar
RULES = [
    # Kırık önceki çeviriler düzeltme
    (r"mid-range pricing\w+\s+\w+\s+seçenekleri", "mid-range dining options"),
    (r"Turkish cuisine\w+\s+\w+\s+dishesi", "delicious dishes of Turkish cuisine"),
    (r"hızlı and freundlich servis\.?", "fast and friendly service"),
    (r"romantik and manzaralı yemekler for ideal atmosfer", "ideal atmosphere for romantic and scenic dining"),
    (r"iş yemeği and as a chef's restaurant öne çıkaran özellikler\.?",
     "features ideal for business dining and chef-level cuisine"),
    (r"rahat and mütevazi atmosfer", "relaxed and modest atmosphere"),
    (r"Mis gibi sıcacık and iyi pişmiş yemekler", "wonderfully warm and well-cooked dishes"),
    (r"Kumru and döner kebaplar", "Kumru and döner kebabs"),

    # Kalan tam kalıplar
    (r"Kumru ve döner kebaplar", "Kumru and döner kebabs"),
    (r"popüler yemekleri", "popular dishes"),
    (r"Mis gibi sıcacık ve iyi pişmiş yemekler", "wonderfully warm and well-cooked dishes"),
    (r"farklı lezzet seçenekleri", "diverse flavor options"),
    (r"güler yüzlü ve profesyonelliği yüksek personeli", "friendly and highly professional staff"),
    (r"güler yüzlü personel", "friendly staff"),
    (r"profesyonel personel", "professional staff"),
    (r"klasik ötesi kuru fasülye", "classic white bean stew"),
    (r"kuru fasülye", "white bean stew"),
    (r"rahat ve mütevazi atmosfer", "relaxed and modest atmosphere"),
    (r"klasik türk yemekleri", "classic Turkish dishes"),
    (r"romantik ve manzaralı yemekler için ideal atmosfer", "ideal atmosphere for romantic and scenic dining"),
    (r"büyüleyici atmosferi?", "enchanting atmosphere"),
    (r"türk mutfağının lezzetli yemekleri", "delicious dishes of Turkish cuisine"),
    (r"eşsiz konuma sahip restoran", "restaurant with a unique location"),
    (r"eşsiz konum", "unique location"),
    (r"tarih(i|inin) \w+ binasında?", "historic building"),
    (r"hızlı ve freundlich servis", "fast and friendly service"),
    (r"hızlı ve güvenilir servis", "fast and reliable service"),
    (r"orta fiyat aralığındaki yemek seçenekleri", "mid-range dining options"),
    (r"orta fiyat aralığında", "in the mid-range"),
    (r"uygun fiyatlı seçenekler", "affordable options"),
    (r"lezzetli türk yemekleri", "delicious Turkish dishes"),
    (r"geleneksel türk lezzetleri", "traditional Turkish flavors"),
    (r"zengin lezzet deneyimi", "rich flavor experience"),
    (r"ferah ve geniş mekan", "spacious and airy venue"),
    (r"kolay ulaşılabilir konum", "easily accessible location"),
    (r"çevre dostu uygulamalar", "eco-friendly practices"),
    (r"özel etkinlikler için uygun", "suitable for special events"),
    (r"romantik akşam yemekleri için ideal", "ideal for romantic dinners"),
    (r"çiftler için romantik atmosfer", "romantic atmosphere for couples"),
    (r"panoramik boğaz manzarası", "panoramic Bosphorus view"),
    (r"tarihi yarımadada konumlanan", "located on the historic peninsula"),
    (r"yüksek kaliteli malzemeler", "high-quality ingredients"),
    (r"el yapımı ürünler", "handcrafted products"),
    (r"taze pişirilen ekmekler", "freshly baked breads"),
    (r"zengin kahvaltı tabağı", "generous breakfast spread"),
    (r"serpme kahvaltı", "traditional Turkish spread breakfast"),
    (r"deniz mahsulleri", "seafood"),
    (r"balık yemekleri", "fish dishes"),
    (r"ızgara yemekleri", "grilled dishes"),
    (r"et yemekleri", "meat dishes"),
    (r"mevsim yemekleri", "seasonal dishes"),
    (r"çorba çeşitleri", "soup varieties"),
    (r"tatlı seçenekleri", "dessert options"),
    (r"içecek seçenekleri", "beverage options"),
    (r"geniş şarap listesi", "extensive wine list"),
    (r"yerel şaraplar", "local wines"),
    (r"enfes meze tabağı", "exquisite meze platter"),
    (r"özel kokteyl menüsü", "special cocktail menu"),
    (r"zengin kahvaltı", "hearty breakfast"),
    (r"köy kahvaltısı", "village-style breakfast"),
    (r"açık büfe kahvaltı", "open buffet breakfast"),
    (r"çocuk menüsü", "children's menu"),
    (r"paket servis", "takeaway service"),
    (r"online rezervasyon", "online reservation"),
    (r"engelli erişimi", "wheelchair accessibility"),
    (r"evcil hayvan dostu", "pet-friendly"),
    (r"sigara içilmeyen alan", "non-smoking area"),
    (r"açık hava oturma", "outdoor seating"),
    (r"özel oda", "private dining room"),
    (r"grup rezervasyonu", "group reservations"),
    (r"düğün ve organizasyonlar için uygun", "suitable for weddings and events"),
    (r"canlı müzik performansları", "live music performances"),
    (r"dj performansı", "DJ performances"),
    (r"fotoğraf çekimi için ideal", "ideal for photo opportunities"),
    (r"instagram dostu mekan", "Instagram-worthy venue"),
    (r"tarihi yapıda", "in a historic building"),
    (r"yenilenmiş tarihi bina", "renovated historic building"),
    (r"modern türk mutfağı", "modern Turkish cuisine"),
    (r"füzyon mutfak", "fusion cuisine"),
    (r"uluslararası mutfak", "international cuisine"),
    (r"vejetaryen ve vegan seçenekler", "vegetarian and vegan options"),
    (r"sağlıklı beslenme seçenekleri", "healthy eating options"),
    (r"organik ürünler", "organic products"),
    (r"glutensiz seçenekler", "gluten-free options"),
    (r"şeker.?siz seçenekler", "sugar-free options"),
]

def translate(text: str) -> str:
    t = text
    for pattern, replacement in RULES:
        t = re.sub(pattern, replacement, t, flags=re.IGNORECASE)
    return t.strip()

changed = 0
still_tr = []
for r in data:
    if not r.get("highlights"):
        continue
    new_h = []
    for h in r["highlights"]:
        translated = translate(h)
        if translated != h:
            changed += 1
            new_h.append(translated)
        else:
            new_h.append(h)
            if TR_CHARS.search(h):
                still_tr.append((r["name"], h))
    r["highlights"] = new_h

with open(INPUT, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"[OK] {changed} highlight güncellendi.")
print(f"Hala işlenemeyen: {len(still_tr)}")
for name, h in still_tr[:10]:
    print(f"  [{name}] {h}")
