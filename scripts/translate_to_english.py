# -*- coding: utf-8 -*-
"""
1. llm_summary: Yapılandırılmış veriden İngilizce yeniden üretir.
2. sentiment_summary: Bilinen Türkçe cümleleri çevirir.
3. FAQ sorular: Sözlük çevirisi.
4. FAQ cevaplar: Fiyat/rezervasyon kalıplarını İngilizceye dönüştürür.
5. scenario_summary: Bilinen kalıpları çevirir.

API gerektirmez.
Kullanım: python scripts/translate_to_english.py
"""

import json
import re

INPUT_FILE  = "data/processed/istanbul.json"
OUTPUT_FILE = "data/processed/istanbul.json"

# ── Fiyat sembolü ─────────────────────────────────────────────────────────────
def price_label(p):
    return {1: "budget-friendly", 2: "mid-range", 3: "upscale", 4: "fine dining"}.get(p, "mid-range")

def price_symbol(p):
    return {1: "₺", 2: "₺₺", 3: "₺₺₺", 4: "₺₺₺₺"}.get(p, "₺₺")

# ── İngilizce llm_summary üret ───────────────────────────────────────────────
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
    highlights   = r.get("highlights") or []
    sig_dish     = (r.get("special_features") or {}).get("signatureDish") or \
                   (r.get("specialFeatures") or {}).get("signatureDish") or ""

    # Cümle 1: Temel tanım
    location = f"{hood}, {city}" if hood else city
    sentence1 = f"{name} is a {cuisine} restaurant in {location}."

    # Cümle 2: Fiyat + atmosfer
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
    if features.get("laptopFriendly"):
        feature_phrases.append("laptop-friendly environment")

    # Tag'lerden ipucu al
    tag_features = []
    for t in tags:
        tl = t.lower()
        if "manzara" in tl or "view" in tl:
            if "sea view" not in feature_phrases: tag_features.append("scenic views")
        if "romantik" in tl or "romantic" in tl:
            if "romantic atmosphere" not in feature_phrases: tag_features.append("romantic setting")
        if "iş" in tl or "business" in tl:
            tag_features.append("ideal for business lunches")
        if "aile" in tl or "family" in tl:
            tag_features.append("family-friendly")
        if "gece" in tl or "late" in tl:
            tag_features.append("open late")

    all_features = list(dict.fromkeys(feature_phrases + tag_features))[:3]

    if all_features:
        sentence2 = f"A {pl} venue offering {', '.join(all_features)}."
    else:
        sentence2 = f"A {pl} venue with a welcoming atmosphere."

    # Cümle 3: Popüler yemekler veya puan
    parts = []
    if popular:
        parts.append(f"Popular dishes include {', '.join(popular[:3])}.")
    elif sig_dish:
        parts.append(f"Known for its {sig_dish}.")
    if rating and review_count:
        parts.append(f"Rated {rating}/5 based on {review_count:,} reviews.")
    elif rating:
        parts.append(f"Rated {rating}/5.")

    sentence3 = " ".join(parts) if parts else ""

    return " ".join(filter(None, [sentence1, sentence2, sentence3]))


# ── Sentiment çevirileri ──────────────────────────────────────────────────────
SENTIMENT_MAP = {
    "Ziyaretçiler genel olarak memnuniyetlerini dile getiriyor.":
        "Visitors are generally satisfied.",
    "Misafirler yüksek kalitesini övdü.":
        "Guests praised the high quality.",
    "Misafirler romantik atmosferi övdü.":
        "Guests praised the romantic atmosphere.",
    "Misafirler pizza çeşitlerini övdü.":
        "Guests praised the pizza variety.",
    "Misafirler fiyat/performans dengesini övdü.":
        "Guests praised the value for money.",
    "Misafirler yemeklerin lezzetini ve özenli hazırlanmasını övdü.":
        "Guests praised the flavor and careful preparation of the dishes.",
    "Misafirler, güler yüzlü hizmeti ve güzel manzarayı övdü.":
        "Guests praised the friendly service and the beautiful view.",
    "Misafirler, restoranın gerçek ve leziz yemeklerini övdü.":
        "Guests praised the restaurant's authentic and delicious food.",
    "Misafirler, özellikle romantik atmosferi ve lezzetli yemeklerden övgüyle söz ediyor.":
        "Guests especially praised the romantic atmosphere and delicious food.",
    "Misafirler, özellikle manzarası ve uygun fiyatlarından övgüyle bahsediyor.":
        "Guests especially praised the view and affordable prices.",
    "Romantik atmosferi ve muhteşem manzarası övülüyor.":
        "Its romantic atmosphere and stunning view are highly praised.",
    "Ziyaretçiler tarafından çok sevilen ve tavsiye edilen bir restoran.":
        "A highly loved and recommended restaurant.",
    "Ziyaretçilerin çoğu memnun kalmamış görünmektedir.":
        "Most visitors appear to be unsatisfied.",
}

def translate_sentiment(text: str) -> str:
    if not text:
        return text
    s = text.strip()
    if s in SENTIMENT_MAP:
        return SENTIMENT_MAP[s]
    # Genel pattern çevirileri
    result = text
    result = re.sub(r'Ziyaretçilerin büyük çoğunluğu.*?%(\d+).*?restoranın\s+', r'The vast majority of visitors (\1%) praise the restaurant\'s ', result)
    result = re.sub(r'Ziyaretçilerin büyük çoğunluğu.*?restoranın\s+', "The vast majority of visitors praise the restaurant's ", result)
    result = re.sub(r'Ziyaretçiler.*?memnuniyetlerini dile getiriyor', "Visitors express their satisfaction", result)
    result = re.sub(r'Misafirler.*?övdü\.?$', "Guests expressed praise.", result)
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
    result = re.sub(r'\bölüyor\b', "rate", result, flags=re.IGNORECASE)
    result = re.sub(r'\bpuan\b', "rating", result, flags=re.IGNORECASE)
    return result


# ── FAQ soru çevirileri ───────────────────────────────────────────────────────
QUESTION_MAP = {
    "Rezervasyon var mı?": "Is reservation available?",
    "Rezervasyon gerekiyor mu?": "Is reservation required?",
    "Rezervasyon gerekli mi?": "Is reservation required?",
    "Rezervasyon yapabilir miyiz?": "Can we make a reservation?",
    "Rezervasyon yapılabiliyor mu?": "Can reservations be made?",
    "Fiyatlar nasıl?": "What are the prices?",
    "Fiyatlar ne kadar?": "How much does it cost?",
    "Popüler yemekler nelerdir?": "What are the popular dishes?",
    "Popüler yemekler neler?": "What are the popular dishes?",
    "Otopark var mı?": "Is parking available?",
    "Restoranda otopark var mı?": "Is there parking at the restaurant?",
    "WiFi var mı?": "Is WiFi available?",
    "Restoranda Wi-Fi var mı?": "Is there Wi-Fi at the restaurant?",
    "Restoranda WiFi var mı?": "Is there WiFi at the restaurant?",
    "Nerede ve nasıl ulaşılır?": "Where is it and how to get there?",
    "Restorana nasıl ulaşabilirim?": "How can I get to the restaurant?",
    "Restorana nasıl gidilir?": "How do I get to the restaurant?",
    "Nerede?": "Where is it?",
    "Nerede bulurum?": "Where can I find it?",
    "Nerede bulabilirim?": "Where can I find it?",
    "Cocuklar/aileler için uygun mu?": "Is it suitable for children/families?",
    "Cocuklar için uygun mu?": "Is it suitable for children?",
    "Cocuklar ve aileler için uygun mu?": "Is it suitable for children and families?",
    "Çocuklar/aileler için uygun mu?": "Is it suitable for children/families?",
    "Çocuklar için uygun mu?": "Is it suitable for children?",
    "Çocuklar ve aileler için uygun mu?": "Is it suitable for children and families?",
    "Vegan seçenekleri var mı?": "Are vegan options available?",
    "Vegan seçenekler var mı?": "Are there vegan options?",
    "Teras var mı?": "Is there a terrace?",
    "Restoranda teras var mı?": "Is there a terrace at the restaurant?",
    "Restoranın terası var mı?": "Does the restaurant have a terrace?",
    "Diyet/alerji seçenekleri var mı?": "Are there dietary/allergy options?",
    "Ortam/atmosfer nasıl?": "What is the ambiance like?",
    "Özel günler/organizasyon için uygun mu?": "Is it suitable for special occasions?",
    "Ozel gunler/organizasyonlar icin uygun mu?": "Is it suitable for special occasions?",
    "Konum avantajları nelerdir?": "What are the location advantages?",
    "İş yemekleri için uygun mu?": "Is it suitable for business lunches?",
    "Romantik akşam yemeği için uygun mu?": "Is it suitable for a romantic dinner?",
    "Açık alan/teras var mı?": "Is there outdoor seating/terrace?",
    "Canlı müzik var mı?": "Is there live music?",
    "Paket servis var mı?": "Is takeaway available?",
    "Çalışma saatleri nedir?": "What are the opening hours?",
    "Kaçta açılıyor ve kapanıyor?": "What time does it open and close?",
    "Glutensiz seçenekler var mı?": "Are there gluten-free options?",
    "Vejetaryen seçenekler var mı?": "Are there vegetarian options?",
    "Alkollü içecek servis ediliyor mu?": "Are alcoholic beverages served?",
    "Manzara var mı?": "Is there a view?",
    "Deniz manzarası var mı?": "Is there a sea view?",
    "Grup rezervasyonu yapılabiliyor mu?": "Can group reservations be made?",
    "Engelli erişimi var mı?": "Is there disabled access?",
    "Kredi kartı kabul ediliyor mu?": "Is credit card accepted?",
    "Sigara içilebilir mi?": "Is smoking allowed?",
    "Çocuk menüsü var mı?": "Is there a children's menu?",
    "Özel diyet seçenekleri var mı?": "Are there special dietary options?",
    "Laptop dostu mu?": "Is it laptop-friendly?",
    "Dış mekan oturma alanı var mı?": "Is there outdoor seating?",
}

def translate_question(q: str) -> str:
    q = q.strip()
    return QUESTION_MAP.get(q, q)  # Bulamazsa orijinali bırak

def translate_answer(a: str) -> str:
    if not a:
        return a
    result = a

    # Fiyat kalıpları — tüm varyantları yakala
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

    # Rezervasyon kalıpları
    result = re.sub(r'Rezervasyon\s*önerilir[,.]?\s*ancak\s*zorunlu\s*değildir\.?', 'Reservations recommended but not required.', result)
    result = re.sub(r'Rezervasyon\s*önerilir\.?', 'Reservations recommended.', result)
    result = re.sub(r'Rezervasyon\s*gereklidir\.?', 'Reservation required.', result)
    result = re.sub(r'[Rr]ezervasyon\s*yap[ıi]lmamaktad[ıi]r\.?', 'Reservations are not accepted.', result)
    result = re.sub(r'[Rr]ezervasyon\s*yap[ıi]lmaz\.?', 'Reservations are not accepted.', result)
    result = re.sub(r'[Hh]ay[ıi]r[,.]?\s*rezervasyon\s*yok\.?', 'No, reservations not available.', result)
    result = re.sub(r'[Hh]ay[ıi]r[,.]?\s*rezervasyon\s*yap[ıi]lmamaktad[ıi]r\.?', 'No, reservations are not accepted.', result)
    result = re.sub(r'[Hh]ay[ıi]r[,.]?\s*rezervasyon\s*yapman[ıi]za\s*gerek\s*yoktur\.?', 'No, reservations are not required.', result)
    result = re.sub(r'[Ee]vet[,.]?\s*rezervasyon\s*yapabilirsiniz\.?', 'Yes, reservations can be made.', result)
    result = re.sub(r'[Ee]vet[,.]?\s*rezervasyon\s*önerilmektedir\.?', 'Yes, reservations are recommended.', result)

    # Evet/Hayır kalıpları
    result = re.sub(r'^[Hh]ay[ıi]r[,.]?\s*mevcut\s*değildir\.?$', 'No, not available.', result.strip())
    result = re.sub(r'^[Hh]ay[ıi]r[,.]?\s*$', 'No.', result.strip())
    result = re.sub(r'^[Ee]vet[,.]?\s*mevcuttur\.?$', 'Yes, available.', result.strip())
    result = re.sub(r'^[Ee]vet[,.]?\s*$', 'Yes.', result.strip())
    result = re.sub(r'^[Hh]ay[ıi]r\.?$', 'No.', result.strip())
    result = re.sub(r'^[Ee]vet\.?$', 'Yes.', result.strip())

    return result


# ── Scenario çevirisi ─────────────────────────────────────────────────────────
SCENARIO_TRANSLATIONS = {
    # Budget
    r'[Bb]ütçe dostu': 'budget-friendly',
    r'[Uu]ygun fiyat': 'affordable',
    r'[Ee]konomik': 'economical',
    # Vegetarian
    r'[Vv]ejetaryen': 'vegetarian',
    r'[Vv]egan': 'vegan',
    r'[Bb]itki bazlı': 'plant-based',
    # Late night
    r'[Gg]ece geç': 'late night',
    r'[Gg]eç saate kadar': 'until late hours',
    # Romantic
    r'[Rr]omantik': 'romantic',
    r'[Çç]ift': 'couple',
    # Family
    r'[Aa]ile': 'family',
    r'[Çç]ocuk': 'child',
    # Quick lunch
    r'[Hh]ızlı': 'quick',
    r'[Öö]ğle yemeği': 'lunch',
    # Tourist
    r'[Tt]urist': 'tourist',
    r'[Tt]arihi': 'historic',
    # Birthday
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


# ── Ana işlem ─────────────────────────────────────────────────────────────────
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
    return result


def main():
    with open(INPUT_FILE, encoding="utf-8") as f:
        data = json.load(f)

    translated = [translate_restaurant(r) for r in data]

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(translated, f, ensure_ascii=False, indent=2)

    print(f"Tamamlandı! {len(translated)} restoran işlendi.")
    print("Sonraki adım: python scripts/json_to_ts.py")


if __name__ == "__main__":
    main()
