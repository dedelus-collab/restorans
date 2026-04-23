# -*- coding: utf-8 -*-
"""
Translates restaurant data to English without an API.
Covers: llm_summary, sentiment_summary, FAQ (questions + answers), scenario_summary, tags.
Usage: python scripts/translate_to_english.py
"""

import json
import re

INPUT_FILE  = "data/processed/istanbul.json"
OUTPUT_FILE = "data/processed/istanbul.json"

# ── Price helpers ──────────────────────────────────────────────────────────────
def price_label(p):
    return {1: "budget-friendly", 2: "mid-range", 3: "upscale", 4: "fine dining"}.get(p, "mid-range")

# ── English llm_summary generator ─────────────────────────────────────────────
def generate_english_summary(r: dict) -> str:
    name         = r.get("name", "")
    hood         = r.get("neighborhood", "")
    city         = r.get("city", "Istanbul")
    cuisine      = r.get("cuisine", "Turkish cuisine")
    price        = r.get("price_range", 2)
    rating       = r.get("avg_rating", 0)
    review_count = r.get("review_count", 0)
    tags         = r.get("tags") or []
    features     = {k: v for k, v in (r.get("features") or {}).items() if v}
    popular      = (r.get("special_features") or {}).get("popularDishes") or \
                   (r.get("specialFeatures") or {}).get("popularDishes") or []

    location  = f"{hood}, {city}" if hood else city
    sentence1 = f"{name} is a {cuisine} restaurant in {location}."

    pl = price_label(price)
    feature_phrases = []
    if features.get("seaView") or features.get("denizManzarasi"):
        feature_phrases.append("sea view")
    if features.get("terrace") or features.get("teras"):
        feature_phrases.append("terrace seating")
    if features.get("romantic"):
        feature_phrases.append("romantic atmosphere")
    if features.get("liveMusic") or features.get("canliMuzik"):
        feature_phrases.append("live music")

    tag_features = []
    for t in tags:
        tl = t.lower()
        if ("manzara" in tl or "view" in tl) and "sea view" not in feature_phrases:
            tag_features.append("scenic views")
        if ("romantik" in tl or "romantic" in tl) and "romantic atmosphere" not in feature_phrases:
            tag_features.append("romantic setting")
        if "aile" in tl or "family" in tl:
            tag_features.append("family-friendly")

    all_features = list(dict.fromkeys(feature_phrases + tag_features))[:3]
    sentence2 = f"A {pl} venue offering {', '.join(all_features)}." if all_features \
                else f"A {pl} venue with a welcoming atmosphere."

    parts = []
    if popular:
        parts.append(f"Popular dishes include {', '.join(popular[:3])}.")
    if rating and review_count:
        parts.append(f"Rated {rating}/5 based on {review_count:,} reviews.")
    elif rating:
        parts.append(f"Rated {rating}/5.")
    sentence3 = " ".join(parts)

    return " ".join(filter(None, [sentence1, sentence2, sentence3]))


# ── Sentiment translation ──────────────────────────────────────────────────────
SENTIMENT_MAP = {
    "Ziyaretçiler genel olarak memnuniyetlerini dile getiriyor.": "Visitors are generally satisfied.",
    "Misafirler yüksek kalitesini övdü.": "Guests praised the high quality.",
    "Misafirler romantik atmosferi övdü.": "Guests praised the romantic atmosphere.",
    "Misafirler pizza çeşitlerini övdü.": "Guests praised the pizza variety.",
    "Misafirler fiyat/performans dengesini övdü.": "Guests praised the value for money.",
    "Misafirler yemeklerin lezzetini ve özenli hazırlanmasını övdü.": "Guests praised the flavor and careful preparation of the dishes.",
    "Misafirler, güler yüzlü hizmeti ve güzel manzarayı övdü.": "Guests praised the friendly service and the beautiful view.",
    "Misafirler, restoranın gerçek ve leziz yemeklerini övdü.": "Guests praised the restaurant's authentic and delicious food.",
    "Misafirler, özellikle romantik atmosferi ve lezzetli yemeklerden övgüyle söz ediyor.": "Guests especially praised the romantic atmosphere and delicious food.",
    "Misafirler, özellikle manzarası ve uygun fiyatlarından övgüyle bahsediyor.": "Guests especially praised the view and affordable prices.",
    "Romantik atmosferi ve muhteşem manzarası övülüyor.": "Its romantic atmosphere and stunning view are highly praised.",
    "Ziyaretçiler tarafından çok sevilen ve tavsiye edilen bir restoran.": "A highly loved and recommended restaurant.",
    "Ziyaretçilerin çoğu memnun kalmamış görünmektedir.": "Most visitors appear to be unsatisfied.",
}

def translate_sentiment(text: str) -> str:
    if not text:
        return text
    s = text.strip()
    if s in SENTIMENT_MAP:
        return SENTIMENT_MAP[s]
    result = text
    result = re.sub(r'Ziyaretçilerin büyük çoğunluğu.*?%(\d+).*?restoranın\s+', r"The vast majority of visitors (\1%) praise the restaurant's ", result)
    result = re.sub(r'Ziyaretçilerin büyük çoğunluğu.*?restoranın\s+', "The vast majority of visitors praise the restaurant's ", result)
    result = re.sub(r'\bZiyaretçiler\b', "Visitors", result)
    result = re.sub(r'\bMisafirler\b', "Guests", result)
    result = re.sub(r'\bziyaretçilerin\b', "visitors'", result, flags=re.IGNORECASE)
    result = re.sub(r'\blezzetli\b', "delicious", result, flags=re.IGNORECASE)
    result = re.sub(r'\batmosferi\b', "atmosphere", result, flags=re.IGNORECASE)
    result = re.sub(r'\bhizmet(i|ini)?\b', "service", result, flags=re.IGNORECASE)
    result = re.sub(r'\byemekleri\b', "dishes", result, flags=re.IGNORECASE)
    result = re.sub(r'\bmemnun\b', "satisfied", result, flags=re.IGNORECASE)
    result = re.sub(r'\bövüyor\b', "praise", result, flags=re.IGNORECASE)
    result = re.sub(r'\bövdü\b', "praised", result, flags=re.IGNORECASE)
    return result


# ── FAQ question translation ───────────────────────────────────────────────────
QUESTION_MAP = {
    # Reservation
    "Rezervasyon var mı?": "Is reservation available?",
    "Rezervasyon gerekiyor mu?": "Is reservation required?",
    "Rezervasyon gerekli mi?": "Is reservation required?",
    "Rezervasyon yapabilir miyiz?": "Can we make a reservation?",
    "Rezervasyon yapabilir miyim?": "Can I make a reservation?",
    "Rezervasyon yapılabiliyor mu?": "Can reservations be made?",
    # Price
    "Fiyatlar nasıl?": "What are the prices?",
    "Fiyatlar ne kadar?": "What are the prices?",
    "Fiyatlar ne kadardır?": "What are the prices?",
    "Fiyat aralığı nedir?": "What is the price range?",
    # Dishes
    "Popüler yemekler nelerdir?": "What are the popular dishes?",
    "Popüler yemekler neler?": "What are the popular dishes?",
    "İmza yemekler nelerdir?": "What are the signature dishes?",
    # Parking
    "Otopark var mı?": "Is parking available?",
    "Restoranda otopark var mı?": "Is there parking at the restaurant?",
    # WiFi
    "WiFi var mı?": "Is WiFi available?",
    "Wi-Fi var mı?": "Is there Wi-Fi?",
    "Restoranda Wi-Fi var mı?": "Is there Wi-Fi at the restaurant?",
    "Restoranda WiFi var mı?": "Is there WiFi at the restaurant?",
    "Restoranda Wi-Fi ve otopark var mı?": "Is there Wi-Fi and parking at the restaurant?",
    # Directions
    "Nerede ve nasıl ulaşılır?": "Where is it and how to get there?",
    "Restorana nasıl ulaşabilirim?": "How can I get to the restaurant?",
    "Restorana nasıl gidilir?": "How do I get to the restaurant?",
    "Nerede?": "Where is it?",
    "Nerede bulurum?": "Where can I find it?",
    "Nerede bulabilirim?": "Where can I find it?",
    # Children / family
    "Cocuklar/aileler için uygun mu?": "Is it suitable for children/families?",
    "Cocuklar için uygun mu?": "Is it suitable for children?",
    "Cocuklar ve aileler için uygun mu?": "Is it suitable for children and families?",
    "Çocuklar/aileler için uygun mu?": "Is it suitable for children/families?",
    "Çocuklar için uygun mu?": "Is it suitable for children?",
    "Çocuklar ve aileler için uygun mu?": "Is it suitable for children and families?",
    "Restoranda çocuklar için uygun mu?": "Is the restaurant suitable for children?",
    "Restoranda çocuklar için uygun bir alan var mı?": "Is there a child-friendly area at the restaurant?",
    "Çocuk menüsü var mı?": "Is there a children's menu?",
    # Vegan / dietary
    "Vegan seçenekleri var mı?": "Are vegan options available?",
    "Vegan seçenekler var mı?": "Are there vegan options?",
    "Vejetaryen seçenekler var mı?": "Are there vegetarian options?",
    "Glutensiz seçenekler var mı?": "Are there gluten-free options?",
    "Diyet/alerji seçenekleri var mı?": "Are there dietary/allergy options?",
    "Özel diyet seçenekleri var mı?": "Are there special dietary options?",
    # Terrace / outdoor
    "Teras var mı?": "Is there a terrace?",
    "Restoranda teras var mı?": "Is there a terrace at the restaurant?",
    "Restoranın terası var mı?": "Does the restaurant have a terrace?",
    "Açık alan/teras var mı?": "Is there outdoor seating/terrace?",
    "Dış mekan oturma alanı var mı?": "Is there outdoor seating?",
    # Ambiance
    "Ortam/atmosfer nasıl?": "What is the ambiance like?",
    # Special occasions
    "Özel günler/organizasyon için uygun mu?": "Is it suitable for special occasions?",
    "Ozel gunler/organizasyonlar icin uygun mu?": "Is it suitable for special occasions?",
    "Restoranda özel günler için organizasyon yapabilir miyim?": "Can I organize a special event at the restaurant?",
    "Restoranın özel günler için organizasyon yapabilir mi?": "Can the restaurant organize special events?",
    # Location
    "Konum avantajları nelerdir?": "What are the location advantages?",
    # Business / romantic
    "İş yemekleri için uygun mu?": "Is it suitable for business lunches?",
    "Romantik akşam yemeği için uygun mu?": "Is it suitable for a romantic dinner?",
    # Other
    "Canlı müzik var mı?": "Is there live music?",
    "Paket servis var mı?": "Is takeaway available?",
    "Çalışma saatleri nedir?": "What are the opening hours?",
    "Kaçta açılıyor ve kapanıyor?": "What time does it open and close?",
    "Alkollü içecek servis ediliyor mu?": "Are alcoholic beverages served?",
    "Manzara var mı?": "Is there a view?",
    "Deniz manzarası var mı?": "Is there a sea view?",
    "Grup rezervasyonu yapılabiliyor mu?": "Can group reservations be made?",
    "Engelli erişimi var mı?": "Is there disabled access?",
    "Kredi kartı kabul ediliyor mu?": "Is credit card accepted?",
    "Sigara içilebilir mi?": "Is smoking allowed?",
    "Laptop dostu mu?": "Is it laptop-friendly?",
}

# Regex-based question fallbacks (checked in order)
QUESTION_REGEX = [
    (r'[Ff]iyat.*ne\s*kadar', "What are the prices?"),
    (r'[Ff]iyat.*nas[ıi]l', "What are the prices?"),
    (r'[Rr]ezervasyon.*yapabilir\s*mi', "Can I make a reservation?"),
    (r'[Rr]ezervasyon.*gerekli\s*mi', "Is reservation required?"),
    (r'[Rr]ezervasyon.*var\s*m[ıi]', "Is reservation available?"),
    (r'[Çç]ocuklar.*uygun\s*mu', "Is the restaurant suitable for children?"),
    (r'[Çç]ocuklar.*alan\s*var\s*m[ıi]', "Is there a child-friendly area?"),
    (r'[Aa]ile.*uygun\s*mu', "Is it family-friendly?"),
    (r'[Öö]zel\s*g[üu]n.*organizasyon.*mi', "Can the restaurant organize special events?"),
    (r'[Öö]zel\s*g[üu]n.*uygun\s*mu', "Is it suitable for special occasions?"),
    (r'Wi-?Fi.*otopark', "Is there Wi-Fi and parking?"),
    (r'Wi-?Fi.*var\s*m[ıi]', "Is there Wi-Fi?"),
    (r'[Oo]topark.*var\s*m[ıi]', "Is there parking?"),
    (r'[Tt]eras.*var\s*m[ıi]', "Is there a terrace?"),
    (r'[Nn]as[ıi]l\s*ula[şs]', "How can I get to the restaurant?"),
    (r'[Nn]erede.*nas[ıi]l', "Where is it and how to get there?"),
    (r'[Pp]op[üu]ler\s*yemek', "What are the popular dishes?"),
]

def translate_question(q: str) -> str:
    q = q.strip()
    if q in QUESTION_MAP:
        return QUESTION_MAP[q]
    for pattern, translation in QUESTION_REGEX:
        if re.search(pattern, q, re.IGNORECASE):
            return translation
    return q  # leave as-is if not matched


# ── FAQ answer translation ─────────────────────────────────────────────────────
def translate_answer(a: str) -> str:
    if not a:
        return a
    result = a

    # Price patterns
    result = re.sub(
        r'[Kk]i[şs]i\s*ba[şs][ıi]\s*~?(\d+[-–]\d+)\s*TL[^.]*\.?',
        r'~\1 TL per person.',
        result
    )
    result = re.sub(
        r'~?(\d+[-–]\d+)\s*TL\s*(?:aras[ıi](?:nda)?|aras[ıi]d[ıi]r|aras[ıi]\s*fiyat\s*aral[ıi][ğg][ıi]ndad[ıi]r)[^.]*\.?',
        r'~\1 TL per person.',
        result
    )
    result = re.sub(
        r'(?:Orta|orta)\s*seviyede\s*fiyatlar[^,\.]*,?\s*~?(\d+[-–]\d+)\s*TL[^.]*\.?',
        r'Mid-range prices, ~\1 TL per person.',
        result
    )

    # Reservation patterns
    result = re.sub(r'[Rr]ezervasyon\s*önerilir[,.]?\s*ancak\s*zorunlu\s*değildir\.?', 'Reservations recommended but not required.', result)
    result = re.sub(r'[Rr]ezervasyon\s*önerilir\.?', 'Reservations recommended.', result)
    result = re.sub(r'[Rr]ezervasyon\s*önerilmektedir\.?', 'Reservations recommended.', result)
    result = re.sub(r'[Rr]ezervasyon\s*gereklidir\.?', 'Reservation required.', result)
    result = re.sub(r'[Rr]ezervasyon\s*yap[ıi]lmamaktad[ıi]r\.?', 'Reservations are not accepted.', result)
    result = re.sub(r'[Rr]ezervasyon\s*yap[ıi]lmaz\.?', 'Reservations are not accepted.', result)
    result = re.sub(r'[Hh]ay[ıi]r[,.]?\s*rezervasyon\s*yok\.?', 'No, reservations are not available.', result)
    result = re.sub(r'[Hh]ay[ıi]r[,.]?\s*rezervasyon\s*yap[ıi]lmamaktad[ıi]r\.?', 'No, reservations are not accepted.', result)
    result = re.sub(r'[Hh]ay[ıi]r[,.]?\s*rezervasyon\s*yapman[ıi]za\s*gerek\s*yoktur\.?', 'No, reservations are not required.', result)
    result = re.sub(r'[Ee]vet[,.]?\s*rezervasyon\s*yapabilirsiniz\.?', 'Yes, reservations can be made.', result)
    result = re.sub(r'[Ee]vet[,.]?\s*rezervasyon\s*önerilmektedir\.?', 'Yes, reservations are recommended.', result)
    result = re.sub(r'[Hh]afta\s*sonlar[ıi]\s*rezervasyon\s*önerilir\.?', 'Reservations recommended on weekends.', result)

    # No / Yes for facility availability
    result = re.sub(r'[Hh]ay[ıi]r[,.]?\s*Wi-?Fi\s*(?:ve\s*otopark\s*)?(?:hizmeti?\s*)?(?:bulunmamaktad[ıi]r|yok)\.?',
                    'No, Wi-Fi is not available.', result)
    result = re.sub(r'[Hh]ay[ıi]r[,.]?\s*otopark\s*(?:ve\s*Wi-?Fi\s*)?(?:hizmeti?\s*)?(?:bulunmamaktad[ıi]r|yok)\.?',
                    'No, parking is not available.', result)
    result = re.sub(r'[Hh]ay[ıi]r[,.]?\s*teras\s*(?:hizmeti?\s*)?(?:bulunmamaktad[ıi]r|yok)\.?',
                    'No, there is no terrace.', result)
    result = re.sub(r'[Hh]ay[ıi]r[,.]?\s*restoranda\s*Wi-?Fi\s*ve\s*otopark\s*bulunmamaktad[ıi]r\.?',
                    'No, the restaurant does not have Wi-Fi or parking.', result)
    result = re.sub(r'[Ee]vet[,.]?\s*Wi-?Fi\s*(?:hizmeti?\s*)?(?:mevcuttur|var)\.?', 'Yes, Wi-Fi is available.', result)
    result = re.sub(r'[Ee]vet[,.]?\s*otopark\s*(?:hizmeti?\s*)?(?:mevcuttur|var)\.?', 'Yes, parking is available.', result)
    result = re.sub(r'[Ee]vet[,.]?\s*teras\s*(?:mevcuttur|var)\.?', 'Yes, there is a terrace.', result)

    # Popular dishes answer — "X, Y, Z popüler yemeklerimizdir."
    result = re.sub(r'^(.+?)\s+popüler\s+yemeklerimizdir\.?$',
                    lambda m: m.group(1) + ' are our popular dishes.',
                    result, flags=re.IGNORECASE)
    result = re.sub(r'\bpopüler\s+yemeklerimizdir\b', 'are our popular dishes', result, flags=re.IGNORECASE)

    # Family-friendly answers
    result = re.sub(r'[Aa]ile\s*dostu\s*bir\s*ortam\s*sunuyoruz\.?', 'We offer a family-friendly atmosphere.', result)
    result = re.sub(r'[Ee]vet[,.]?\s*aile\s*dostu\s*bir\s*(?:ortam|mekan|yer)\.?', 'Yes, it is a family-friendly venue.', result)
    result = re.sub(r'[Ee]vet[,.]?\s*.+?\s*aile\s*dostu\s*oldu[ğg]u\s*için\s*çocuklar\s*için\s*uygun.*?\.?$',
                    'Yes, the restaurant is family-friendly and has a suitable area for children.', result, flags=re.IGNORECASE)

    # Special events / occasions
    result = re.sub(r'[Ee]vet[,.]?\s*özel\s*g[üu]nler\s*için\s*organizasyon\s*yapabilir\s*ve\s*rezervasyon\s*yapabilirsiniz\.?',
                    'Yes, you can organize special events and make reservations.', result)
    result = re.sub(r'[Ee]vet[,.]?\s*.+?\s*özel\s*g[üu]nler\s*için\s*organizasyon\s*yapabilir.*?\.?$',
                    'Yes, the restaurant can organize special events for you.', result, flags=re.IGNORECASE)

    # Transit / directions — "X mahallesinde/bölgesinde ... metro veya otobüs ile ulaşım sağlayabilirsiniz."
    result = re.sub(
        r'.+?(?:mahallesi|bölgesi|[ıi]nde|[üu]nde|[ıi]nda)[^.]*,?\s*metro\s*veya\s*otob[üu]s\s*ile\s*ula[şs][ıi]m\s*sa[ğg]layabilirsiniz\.?',
        'The restaurant is accessible by metro or bus.',
        result, flags=re.IGNORECASE
    )
    result = re.sub(
        r'.+?\s*metro\s*veya\s*otob[üu]s\s*ile\s*ula[şs][ıi]m\s*sa[ğg]layabilirsiniz\.?',
        'The restaurant is accessible by metro or bus.',
        result, flags=re.IGNORECASE
    )

    # Simple yes/no patterns (must come after more specific patterns)
    result = re.sub(r'^[Hh]ay[ıi]r[,.]?\s*mevcut\s*değildir\.?$', 'No, not available.', result.strip())
    result = re.sub(r'^[Hh]ay[ıi]r[,.]?\s*$', 'No.', result.strip())
    result = re.sub(r'^[Ee]vet[,.]?\s*mevcuttur\.?$', 'Yes, available.', result.strip())
    result = re.sub(r'^[Ee]vet[,.]?\s*$', 'Yes.', result.strip())
    result = re.sub(r'^[Hh]ay[ıi]r\.?$', 'No.', result.strip())
    result = re.sub(r'^[Ee]vet\.?$', 'Yes.', result.strip())

    return result


# ── Tag translation ────────────────────────────────────────────────────────────
TAG_MAP = {
    # Meal type
    "kahvaltı": "breakfast",
    "öğle yemeği": "lunch",
    "öğle arası": "lunch break",
    "akşam yemeği": "dinner",
    "brunch": "brunch",
    "hızlı yemek": "quick meal",
    "fast food": "fast food",
    # Ambiance / setting
    "romantik": "romantic",
    "aile": "family-friendly",
    "aile dostu": "family-friendly",
    "iş yemeği": "business lunch",
    "iş": "business",
    "grup": "group dining",
    "büyük grup": "large group",
    "solo": "solo dining",
    "gece": "late night",
    "gece geç": "late night",
    # Features
    "manzara": "scenic view",
    "manzaralı": "scenic view",
    "boğaz manzarası": "bosphorus view",
    "deniz manzarası": "sea view",
    "teras": "terrace",
    "açık hava": "outdoor",
    "bahçe": "garden",
    "rooftop": "rooftop",
    "wifi": "wifi",
    "wi-fi": "wifi",
    "otopark": "parking",
    "canlı müzik": "live music",
    "müzik": "music",
    "rezervasyon önerilir": "reservation recommended",
    "rezervasyon gerekli": "reservation required",
    # Cuisine tags
    "türk mutfağı": "turkish cuisine",
    "deniz ürünleri": "seafood",
    "balık": "fish",
    "kebap": "kebap",
    "vegan": "vegan",
    "vejetaryen": "vegetarian",
    "glutensiz": "gluten-free",
    "organik": "organic",
    # Rating / quality
    "yüksek puan": "highly rated",
    "yuksek puan": "highly rated",
    "çok beğenilenler": "most popular",
    "cok begenilenler": "most popular",
    "tavsiye edilir": "recommended",
    "popüler": "popular",
    # Concept
    "şef restoranı": "chef's restaurant",
    "fine dining": "fine dining",
    "gastronomi": "gastronomy",
    "sokak yemeği": "street food",
    "yerel lezzetler": "local flavors",
    "geleneksel": "traditional",
    "otantik": "authentic",
    "modern": "modern",
    "trendi": "trendy",
    "butik": "boutique",
    "lokal": "local",
    # Special occasions
    "özel gün": "special occasion",
    "doğum günü": "birthday",
    "yıl dönümü": "anniversary",
    "kutlama": "celebration",
}

def translate_tag(tag: str) -> str:
    key = tag.strip().lower()
    return TAG_MAP.get(key, tag)

def translate_tags(tags: list) -> list:
    if not tags:
        return tags
    return [translate_tag(t) for t in tags]


# ── Scenario translation ───────────────────────────────────────────────────────
SCENARIO_TRANSLATIONS = {
    r'[Bb]ütçe dostu': 'budget-friendly',
    r'[Uu]ygun fiyat': 'affordable',
    r'[Ee]konomik': 'economical',
    r'[Vv]ejetaryen': 'vegetarian',
    r'[Vv]egan': 'vegan',
    r'[Bb]itki bazlı': 'plant-based',
    r'[Gg]ece geç': 'late night',
    r'[Gg]eç saate kadar': 'until late hours',
    r'[Rr]omantik': 'romantic',
    r'[Çç]ift': 'couple',
    r'[Aa]ile': 'family',
    r'[Çç]ocuk': 'child',
    r'[Hh]ızlı': 'quick',
    r'[Öö]ğle yemeği': 'lunch',
    r'[Tt]urist': 'tourist',
    r'[Tt]arihi': 'historic',
    r'[Dd]oğum günü': 'birthday',
    r'[Öö]zel gün': 'special occasion',
}

def translate_scenario_value(text: str) -> str:
    if not text:
        return text
    result = text
    for pattern, replacement in SCENARIO_TRANSLATIONS.items():
        result = re.sub(pattern, replacement, result)
    return result

def translate_scenario(scenario: dict) -> dict:
    if not scenario:
        return scenario
    return {k: translate_scenario_value(v) for k, v in scenario.items()}


# ── Main processing ────────────────────────────────────────────────────────────
def translate_restaurant(r: dict) -> dict:
    result = dict(r)
    result["llm_summary"]       = generate_english_summary(r)
    result["sentiment_summary"] = translate_sentiment(r.get("sentiment_summary", "") or "")
    result["faq"]               = [
        {**f,
         "question": translate_question(f.get("question", "")),
         "answer":   translate_answer(f.get("answer", ""))}
        for f in (r.get("faq") or [])
    ]
    result["scenario_summary"]  = translate_scenario(r.get("scenario_summary") or {})
    result["tags"]              = translate_tags(r.get("tags") or [])
    return result


def main():
    with open(INPUT_FILE, encoding="utf-8") as f:
        data = json.load(f)

    translated = [translate_restaurant(r) for r in data]

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(translated, f, ensure_ascii=False, indent=2)

    print(f"Done! {len(translated)} restaurants processed.")
    print("Next step: python scripts/json_to_ts.py")


if __name__ == "__main__":
    main()
