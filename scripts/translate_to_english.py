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

# ── Cuisine name translation ───────────────────────────────────────────────────
CUISINE_TR = {
    "Türk Mutfağı": "Turkish cuisine",
    "Turk Mutfagi": "Turkish cuisine",
    "Balık": "Fish & seafood",
    "Balik": "Fish & seafood",
    "Kafe": "Café",
    "Kahvaltı": "Breakfast",
    "Kahvalti": "Breakfast",
    "Kebap": "Kebap",
    "Lokanta": "Turkish eatery",
    "Meyhane": "Meyhane (Turkish tavern)",
    "Pide": "Pide (Turkish flatbread)",
    "Pizza & İtalyan": "Pizza & Italian",
    "Pizza & Italyan": "Pizza & Italian",
    "Sushi & Japon": "Sushi & Japanese",
    "Dünya Mutfağı": "World cuisine",
    "Dunya Mutfagi": "World cuisine",
    "Uluslararası": "International",
    "Uluslararasi": "International",
    "Vegan": "Vegan",
    "İtalyan": "Italian",
    "Italyan": "Italian",
    "Burger & Steak": "Burger & Steak",
}

def translate_cuisine(c: str) -> str:
    return CUISINE_TR.get(c, c) if c else c

# ── English llm_summary generator ─────────────────────────────────────────────
def generate_english_summary(r: dict) -> str:
    name         = r.get("name", "")
    hood         = r.get("neighborhood", "")
    city         = r.get("city", "Istanbul")
    cuisine      = translate_cuisine(r.get("cuisine", "Turkish cuisine"))
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

def _extract_pct(text: str):
    """Return integer percentage if found, else None."""
    m = re.search(r'%\s*(\d+)', text)
    return int(m.group(1)) if m else None

def _sentiment_label(pct):
    if pct is None or pct >= 90: return "The vast majority of visitors"
    if pct >= 75: return f"The majority of visitors ({pct}%)"
    if pct >= 60: return f"Most visitors ({pct}%)"
    return f"Visitors ({pct}%)"

def translate_sentiment(text: str) -> str:
    if not text:
        return text
    s = text.strip()
    if s in SENTIMENT_MAP:
        return SENTIMENT_MAP[s]

    # ── Exact / near-exact known patterns ─────────────────────────────────────
    # Already mostly English — just clean up leftover words
    if re.match(r'^(The vast majority|Most visitors|Visitors|Guests|Its |A highly)', s):
        pass  # will be cleaned below
    else:
        # ── Generate clean English from Turkish patterns ─────────────────────
        pct = _extract_pct(s)
        label = _sentiment_label(pct)

        # Pattern: "X% memnuniyet" / "X%'i satisfied" / "X%'i ... praise"
        if re.search(r'genel\s+(?:olarak\s+)?memnun|genel\s+memnuniyet|memnuniyet\s+hissi', s, re.IGNORECASE):
            return f"{label} are satisfied with their experience."
        if re.search(r'(?:atmospherinden?|atmosferinden?)\s+(?:satisfied|memnun)', s, re.IGNORECASE):
            return f"{label} are satisfied with the atmosphere."
        if re.search(r'lezzetl\w+\s+(?:kahvalt|breakfast)', s, re.IGNORECASE):
            return f"{label} praise the delicious breakfast options."
        if re.search(r'(?:kahvalt|breakfast).{0,40}(?:memnun|satisfied|praise|leziz|delicious)', s, re.IGNORECASE):
            return f"{label} praise the breakfast options and overall experience."
        if re.search(r'(?:deniz\s*[üu]r[üu]nleri|seafood|bal[ıi]k).{0,40}(?:taze|fresh|praise|övdü|lezzet)', s, re.IGNORECASE):
            return f"{label} praise the fresh seafood and dining experience."
        if re.search(r'(?:romantik|romantic).{0,40}(?:atmosfer|view|manzara)', s, re.IGNORECASE):
            return f"{label} praise the romantic atmosphere and the view."
        if re.search(r'(?:manzara|view|bosphorus|boğaz).{0,50}(?:praise|övdü|övüyor|beğen)', s, re.IGNORECASE):
            return f"{label} praise the view and overall dining experience."
        if re.search(r'(?:hizmet|servis|service)\s+(?:hız|kalite|quality|speed)', s, re.IGNORECASE):
            return f"{label} praise the quality and speed of service."
        if re.search(r'(?:fiyat[\s/]*perfor|uygun\s*fiyat|value\s*for|price)', s, re.IGNORECASE):
            return f"{label} appreciate the value for money."
        if re.search(r'temizli[ğg]|hygiene|hijyen', s, re.IGNORECASE):
            return f"{label} highlight the cleanliness and friendly staff."
        if re.search(r'kebap|kebab|adana|lahmacun|döner|doner', s, re.IGNORECASE):
            return f"{label} praise the kebap dishes and overall experience."
        if re.search(r'pizza|italyan|pasta', s, re.IGNORECASE):
            return f"{label} praise the pizza and Italian dishes."
        if re.search(r'sushi|japon|ramen', s, re.IGNORECASE):
            return f"{label} praise the sushi and Japanese cuisine."
        if re.search(r'mantı|manti|börek|borek', s, re.IGNORECASE):
            return f"{label} enjoy the traditional Turkish dishes."
        if re.search(r'meze|meyhane|rak[ıi]', s, re.IGNORECASE):
            return f"{label} praise the meze selection and meyhane atmosphere."
        if re.search(r'pastane|pasta\s+shop|cake|tatlı', s, re.IGNORECASE):
            return f"{label} praise the pastry and cake selection."
        if re.search(r'kahve|coffee|çay|tea', s, re.IGNORECASE):
            return f"{label} appreciate the coffee and beverage selection."
        if re.search(r'(?:yemek|dish|food).{0,60}(?:lezzet|delicious|kalite|quality)', s, re.IGNORECASE):
            return f"{label} praise the food quality and overall experience."
        if re.search(r'(?:atmosfer|atmosphere|ortam).{0,60}(?:praise|beğen|övdü|sıcak|warm)', s, re.IGNORECASE):
            return f"{label} praise the atmosphere and service."
        if re.search(r'satisfied|memnun|beğen|praise|övdü|takdir', s, re.IGNORECASE):
            pct_str = f" ({pct}%)" if pct else ""
            return f"{label}{pct_str} are satisfied with the dining experience."
        # Generic positive
        if re.search(r'pozitif|positive|olumlu', s, re.IGNORECASE):
            pct_str = f" ({pct}%)" if pct else ""
            return f"Overall reviews are positive{pct_str}."
        # Generic fallback with percentage
        if pct:
            return f"{label} ({pct}%) are satisfied with this restaurant."
        return f"Visitors are generally satisfied with this restaurant."

    result = s
    # ── Clean up partially-translated text ────────────────────────────────────
    # Remove full Turkish sentences after English prefix
    result = re.sub(r"(The vast majority of visitors[^.]*praise the restaurant's)\s+[^A-Z\d].{0,300}$",
                    lambda m: m.group(1) + " the food and overall experience.",
                    result, flags=re.DOTALL)
    # Word-level cleanups
    result = re.sub(r'\bZiyaret[çc]iler\b', "Visitors", result)
    result = re.sub(r'\bMisafirler\b', "Guests", result)
    result = re.sub(r'\bziyaret[çc]ilerin\b', "visitors'", result, flags=re.IGNORECASE)
    result = re.sub(r'\bvisitors\'\s+', "visitors ", result, flags=re.IGNORECASE)
    result = re.sub(r'\blezzetli\b', "delicious", result, flags=re.IGNORECASE)
    result = re.sub(r'\batmosfer(?:ini?|den?|e)?\b', "atmosphere", result, flags=re.IGNORECASE)
    result = re.sub(r'\bhizmet(?:i|ini|den|e)?\b', "service", result, flags=re.IGNORECASE)
    result = re.sub(r'\byemekler(?:ini?|den?|e)?\b', "dishes", result, flags=re.IGNORECASE)
    result = re.sub(r'\bmemnun(?:iyet)?\b', "satisfied", result, flags=re.IGNORECASE)
    result = re.sub(r'\b[öo]v[üu]yor\b', "praise", result, flags=re.IGNORECASE)
    result = re.sub(r'\b[öo]vd[üu]\b', "praised", result, flags=re.IGNORECASE)
    result = re.sub(r'\b[öo]vg[üu]\b', "praise", result, flags=re.IGNORECASE)
    result = re.sub(r'\bservis\b', "service", result, flags=re.IGNORECASE)
    result = re.sub(r'\bkalite(?:si)?\b', "quality", result, flags=re.IGNORECASE)
    result = re.sub(r'\bgenel\s+olarak\b', "overall", result, flags=re.IGNORECASE)
    result = re.sub(r'\bolumlu\b', "positive", result, flags=re.IGNORECASE)
    result = re.sub(r'\belev[şs]tir\w*\b', "criticism", result, flags=re.IGNORECASE)
    result = re.sub(r'\beleştirilen\b', "criticized", result, flags=re.IGNORECASE)
    result = re.sub(r'\btavsiye\b', "recommended", result, flags=re.IGNORECASE)
    result = re.sub(r'\bbeğen\w*\b', "appreciated", result, flags=re.IGNORECASE)
    result = re.sub(r'\btakdir\b', "appreciate", result, flags=re.IGNORECASE)
    result = re.sub(r'\byüksek\s+puan\b', "high ratings", result, flags=re.IGNORECASE)
    result = re.sub(r'\bpuan\b', "rating", result, flags=re.IGNORECASE)
    result = re.sub(r'\bpozitif\b', "positive", result, flags=re.IGNORECASE)
    # Strip leftover Turkish sentence fragments
    result = re.sub(r'\s+[A-Za-z\u00c7\u011e\u0130\u00d6\u015e\u00dc][a-z\u00e7\u011f\u0131\u015f\u00f6\u015f\u00fc]+(?:\w*[ıiuüçğşö]\w*)\s*[^.!?]*[.!?]?$', '.', result, flags=re.IGNORECASE)
    # Fix double percentage: "Visitors (10%) (10%)" → "Visitors (10%)"
    result = re.sub(r'(\(\d+%\))\s+\1', r'\1', result)
    result = re.sub(r'(\(\d+%\))\s+\(\d+%\)', r'\1', result)

    result = result.strip().rstrip(',;')
    if result and not result[-1] in '.!?':
        result += '.'

    # Truncated sentences — fix dangling English stubs
    result = re.sub(r'^(Visitors are generally)\.$', 'Visitors are generally satisfied.', result)
    result = re.sub(r'^(Its)\.$', 'Its atmosphere and food are highly praised.', result)
    result = re.sub(r'^(A highly loved and recommended)\.$', 'A highly loved and recommended restaurant.', result)
    result = re.sub(r'^Visitors Ed\.$', 'Visitors expressed satisfaction.', result)
    result = re.sub(r'^Visitors\.$', 'Visitors are generally satisfied.', result)
    result = re.sub(r'^Visitors,\.$', 'Visitors are generally satisfied.', result)
    result = re.sub(r'^Visitors\s+[A-Z]\w+\.$', 'Visitors are generally satisfied.', result)
    result = re.sub(r'^Visitors,?\s+restorandan\s+overall\.$', 'Visitors are overall satisfied with the restaurant.', result)
    result = re.sub(r'^Guests\s+atmosphere\s+\w+\.$', 'Guests praised the atmosphere.', result)

    # Final check: if still contains Turkish diacritics, regenerate from context
    if re.search(r'[çğışöşüÇĞİÖŞÜ]', result):
        pct = _extract_pct(s)
        label = _sentiment_label(pct)
        pct_str = f" ({pct}%)" if pct else ""
        if re.search(r'atmosfer|atmosphere|ortam', s, re.IGNORECASE):
            return f"{label}{pct_str} praise the atmosphere and overall dining experience."
        if re.search(r'yemek|dish|food|lezzet|delicious', s, re.IGNORECASE):
            return f"{label}{pct_str} praise the food and overall dining experience."
        if re.search(r'servis|hizmet|service', s, re.IGNORECASE):
            return f"{label}{pct_str} praise the service and dining experience."
        if re.search(r'manzara|view|deniz', s, re.IGNORECASE):
            return f"{label}{pct_str} praise the view and dining experience."
        return f"{label}{pct_str} are satisfied with this restaurant."

    return result


# ── FAQ question translation ───────────────────────────────────────────────────
QUESTION_MAP = {
    # Reservation
    "Rezervasyon var mı?": "Is reservation available?",
    "Rezervasyon gerekiyor mu?": "Is reservation required?",
    "Rezervasyon gerekli mi?": "Is reservation required?",
    "Rezervasyon gerekir mi?": "Is reservation required?",
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
    "Ozel gunler/organizasyonlar i\u00e7in uygun mu?": "Is it suitable for special occasions?",
    "Restoranda özel günler için organizasyon yapabilir miyim?": "Can I organize a special event at the restaurant?",
    "Restoranın özel günler için organizasyon yapabilir mi?": "Can the restaurant organize special events?",
    # Location
    "Konum avantajları nelerdir?": "What are the location advantages?",
    "Nerede bulunuyorsunuz?": "Where are you located?",
    "Nerede bulunuyor?": "Where is it located?",
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
    "Diyet veya alerji seçenekleri var mı?": "Are there dietary/allergy options?",
    "Neler var menu?": "What is on the menu?",
    "Ula\u015f\u0131m nas\u0131l?": "How can I get there?",
    "Landmarklar yak\u0131n m\u0131?": "Are there nearby landmarks?",
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
    # Recommendation / dishes
    (r'[Nn]eler\s*tavsiye\s*ediyorsunuz', "What do you recommend?"),
    (r'[Nn]e\s*tavsiye\s*edersiniz', "What do you recommend?"),
    (r'[Hh]angilerini\s*tavsiye\s*edersiniz', "Which dishes do you recommend?"),
    # Where to eat / location
    (r'[Nn]erede\s*yemek\s*yiyebiliriz', "Where can we eat?"),
    (r'[Nn]erede\s*yemek\s*yenebilir', "Where can we eat?"),
    # Landmarks
    (r'[Yy]ak[ıi]n.*landmark', "Are there nearby landmarks?"),
    (r'[Yy]ak[ıi]n.*tarihi.*yer', "Are there historic sites nearby?"),
    (r'[Yy]ak[ıi]n.*m[üu]ze', "Are there nearby museums?"),
    # Terrace / condition
    (r'[Tt]eras.*ne\s*durumda', "What is the terrace situation?"),
    (r'[Tt]eras.*var\s*m[ıi]', "Is there a terrace?"),
    # Nightlife
    (r'[Gg]ece\s*hayat[ıi].*nas[ıi]l', "How is the nightlife connection?"),
    (r'[Gg]ece\s*hayat[ıi].*ili[şs]ki', "How is the restaurant related to nightlife?"),
    # Special / unique feature
    (r'en\s*[öo]zel\s*y[öo]n[üu]\s*ne', "What makes it special?"),
    (r'[öo]zel.*ne.*\?', "What makes it special?"),
    # Scenic / view
    (r'[Mm]anzara.*var\s*m[ıi]', "Is there a view?"),
    (r'[Dd]eniz\s*manzara.*var\s*m[ıi]', "Is there a sea view?"),
    # Ambiance
    (r'[Oo]rtam.*nas[ıi]l', "What is the ambiance like?"),
    (r'[Aa]tmos.*nas[ıi]l', "What is the atmosphere like?"),
    # Business
    (r'[İi][şs]\s*yeme[ğg]i.*uygun', "Is it suitable for business lunches?"),
    # Alcohol
    (r'[Aa]lkol.*servis', "Are alcoholic beverages served?"),
    # Opening hours
    (r'[Çç]al[ıi][şs]ma\s*saat', "What are the opening hours?"),
    (r'ka[çc]ta\s*a[çc][ıi]l[ıi]yor', "What time does it open?"),
    # Restaurant-name specific patterns (catch-all with restaurant name in question)
    (r"'[na]\s+nas[ıi]l\s+gidilir", "How can I get to the restaurant?"),
    (r"[''\u2019][ıiuü]n\s+konum\s+avantajlar", "What are the location advantages?"),
    (r"[Rr]estoran[''\u2019]?[ıi]n\s+konum\s+avantajlar", "What are the location advantages?"),
    (r"[Kk]onum.*avantajl[ıi]\s*m[ıi]", "Is the location convenient?"),
    (r"[Rr]estoran.*yak[ıi]n[ıi]nda\s+ne\s+var", "What is near the restaurant?"),
    (r"[Rr]estoran[ıi]n\s+yak[ıi]n[ıi]nda\s+ne\s+var", "What is near the restaurant?"),
    (r"[Rr]estoranda\s+[çc]ocuklar\s+(?:kabul|uygun)", "Are children welcome at the restaurant?"),
    (r"[Rr]estoranda\s+[çc]ocuklar\s+i[çc]in\s+uygunluk", "Is the restaurant child-friendly?"),
    (r"[Rr]estoranda\s+[öo]zel\s+g[üu]nler\s+i[çc]in\s+organizasyon", "Does the restaurant organize special events?"),
    (r"[Rr]estoran.*do[ğg]um\s+g[üu]n[üu].*organizasyon", "What birthday event services are available?"),
    (r"[Gg]ece\s+hayat[ıi]\s+var\s+m[ıi]", "Is there a nightlife scene nearby?"),
    (r"[Dd]iyette?\s+veya\s+(?:alerjik|alerji)", "Are there options for dietary or allergy needs?"),
    (r"[Hh]angisi?\s+(?:daha\s+)?uygun\s+olur", "Which would you recommend?"),
    (r"ne\s+t[üu]r\s+hizmet.*sunuyor", "What services are offered?"),
    (r"[Vv]egan\s+se[çc]enek.*var\s*m[ıi]", "Are vegan options available?"),
    # Seating
    (r"[Oo]turma\s+alan[ıi]\s+var\s*m[ıi]", "Is there seating available?"),
    (r"[Aa][çc][ıi]k\s+(?:alan|hava|oturma)", "Is there outdoor seating?"),
    # Transit
    (r"yak[ıi]n\s+(?:metro|tramvay|tram|otob[üu]s)\s+(?:istasyon|dura[ğg])", "Is there a nearby metro/tram station?"),
    (r"metro\s+(?:istasyon|dura[ğg]).*var\s*m[ıi]", "Is there a nearby metro station?"),
    (r"tramvay\s+dura[ğg].*var\s*m[ıi]", "Is there a nearby tram stop?"),
    # Waiting time
    (r"beklemek\s+zorunda", "Do I have to wait long?"),
    (r"bekleme\s+s[üu]resi", "What is the waiting time?"),
    # Romantic / evening
    (r"romantik\s+(?:bir\s+)?ak[şs]am\s+i[çc]in\s+uygun", "Is it suitable for a romantic evening?"),
    (r"romantik\s+(?:bir\s+)?(?:akşam|yemek|ortam)", "Is it suitable for a romantic dinner?"),
    # Dietary options
    (r"[Dd]iyet\s+se[çc]ene[ğg]i\s+var\s*m[ıi]", "Are there dietary options?"),
    (r"[Vv]egan\s*/\s*vejetaryen.*diyet.*var\s*m[ıi]", "Are there vegan/vegetarian/dietary options?"),
    (r"[Vv]ejetaryen.*se[çc]enek.*var\s*m[ıi]", "Are there vegetarian options?"),
    # Landmarks
    (r"ne\s+gibi\s+landmark", "What landmarks are nearby?"),
    (r"[Tt]eras[ıi]nda\s+ne\s+gibi\s+imkan", "What facilities are available on the terrace?"),
    (r"[Tt]eras.*ne\s+gibi\s+(?:imkan|hizmet|[öo]zellik)", "What facilities are available on the terrace?"),
    (r"[Tt]eras.*(?:nas[ıi]l|ne\s+sunuyor)", "What does the terrace offer?"),
    (r"yak[ıi]n.*landmark.*var\s*m[ıi]", "Are there nearby landmarks?"),
    # Groups
    (r"(?:gruplar|b[üu]y[üu]k\s+grup)\s+i[çc]in\s+[öo]zel\s+(?:alan|b[öo]lme)", "Is there a private area for groups?"),
    (r"(?:gruplar|grup)\s+i[çc]in\s+uygun\s*m[ıi]", "Is it suitable for groups?"),
    # Open on weekends / specific days
    (r"[Pp]azar\s+g[üu]nleri?\s+a[çc][ıi]k\s*m[ıi]", "Is it open on Sundays?"),
    (r"hafta\s+sonu\s+a[çc][ıi]k\s*m[ıi]", "Is it open on weekends?"),
    # Specific question types
    (r"ne\s+kadar\s+uzakl[ıi]k\s+var", "How far is it?"),
    (r"neden\s+.+\s+tercih\s+edece[ğg]im", "Why should I choose this restaurant?"),
    (r"yak[ıi]n[ıi]nda.*kilise|yak[ıi]n[ıi]nda.*cami|yak[ıi]n[ıi]nda.*m[üu]ze", "Are there nearby landmarks?"),
    (r"gitmeden\s+[öo]nce\s+restoranda", "What would you recommend to eat before visiting?"),
    (r"[Oo]zel\s+g[üu]nler?/organizasyon\s+i[çc]in\s+uygun", "Is it suitable for special occasions?"),
    (r"restoran[ıi]\s+b[üu]y[üu]k\s+gruplar\s+i[çc]in", "Is this restaurant suitable for large groups?"),
    (r"[Rr]estoran.*mutfak\s+t[üu]r[üu]n[üu]\s+nas[ıi]l\s+tan[ıi]mlars[ıi]n", "How would you describe the restaurant's cuisine?"),
    (r"ne\s+t[üu]r\s+bir\s+deneyim", "What kind of experience is offered?"),
    (r"en\s+[öo]zel\s+(?:yeme[ğg]i|[üu]r[üu]n[üu])\s+ne", "What is the most special dish?"),
    (r"'da\s+ne\s+t[üu]r\s+yemekler\s+var", "What kind of food is served?"),
    (r"'[ıi]\s+nerede\s+bulabilirim", "Where can I find it?"),
    (r"[Nn]erede\s+bulunuyor", "Where is it located?"),
    (r"[Uu]la[şs][ıi]m\s+nas[ıi]l", "How can I get there?"),
    (r"[Ll]andmark.*yak[ıi]n", "Are there nearby landmarks?"),
    (r"yak[ıi]n.*landmark", "Are there nearby landmarks?"),
    (r"[Dd]iyet\s+veya\s+alerji", "Are there dietary/allergy options?"),
    (r"[Vv]egan\s*/\s*vegeta", "Are there vegan/vegetarian options?"),
    (r"[Vv]egan\s*[/,]\s*s[ou][iy]a", "Are there vegan/soy options?"),
    (r"[Mm]en[üu].*ne\s+var", "What is on the menu?"),
    (r"ne\s+t[üu]r\s+yemek", "What kind of food is served?"),
    # Cuisine style
    (r"mutfak\s+tarz[ıi]n[ıi].*nas[ıi]l\s+tan[ıi]yabilirim", "How would you describe the restaurant's cuisine?"),
    (r"mutfak\s+tarz[ıi]n[ıi].*nas[ıi]l\s+tan[ıi]mlars[ıi]n[ıi]z", "How would you describe the restaurant's cuisine?"),
    (r"mutfak\s+tarz[ıi]n[ıi].*nas[ıi]l\s+tan[ıi]mlar", "How would you describe the restaurant's cuisine?"),
    (r"mutfak\s+tarz[ıi]", "What is the restaurant's cuisine style?"),
    (r"geleneksel\s+[Mm]utfak.*m[ıi]d[ıi]r", "Does the restaurant serve traditional cuisine?"),
    # View / terrace beauty
    (r"teras[ıi]\s+ve\s+manzaras[ıi]\s+ne\s+kadar\s+g[üu]zel", "How beautiful is the terrace and the view?"),
    (r"manzaras[ıi]\s+ne\s+kadar\s+g[üu]zel", "How scenic is the view?"),
    # Nearby landmarks by type
    (r"yak[ıi]n.*[Ss]aray.*m[ıi]", "Is the palace nearby?"),
    (r"yak[ıi]n.*[Yy]al[ıi].*m[ıi]", "Is the waterfront mansion nearby?"),
    (r"yak[ıi]n.*[Pp]azar.*m[ıi]", "Is the market nearby?"),
    (r"yak[ıi]n.*[Çç]ar[şs][ıi].*m[ıi]", "Is the market/bazaar nearby?"),
    (r"yak[ıi]n.*[Cc]ami.*m[ıi]", "Is the mosque nearby?"),
    (r"yak[ıi]n.*[Kk]ilise.*m[ıi]", "Is the church nearby?"),
    (r"yak[ıi]n.*[Hh]amam.*m[ıi]", "Is the hammam nearby?"),
    (r"yak[ıi]n.*m[ıi]s[ıi]n[ıi]z", "Is it nearby?"),
    (r"yak[ıi]n.*m[ıi]y[ıi]z", "Are we near it?"),
    (r"yak[ıi]nda.*m[ıi]s[ıi]n[ıi]z", "Are you located nearby?"),
    (r"yak[ıi]nda.*m[ıi]y[ıi]z", "Are we nearby?"),
    # Why visit
    (r"[Nn]eden.*gideyim", "Why should I visit?"),
    (r"[Nn]eden.*tercih\s+edeyim", "Why should I choose this restaurant?"),
    (r"[Nn]eden.*se[çc]meliyim", "Why should I choose this restaurant?"),
    # When to go
    (r"[Rr]estorana\s+ne\s+zaman\s+gitmeli", "When is the best time to visit?"),
    (r"ne\s+zaman\s+gitmeli", "When is the best time to visit?"),
    # Business events
    (r"i[şs]\s+yeme[ğg]i\s+organizasyon.*nas[ıi]l", "How does the restaurant handle business lunch events?"),
    # Where to stay nearby
    (r"konumuna\s+g[öo]re\s+nerede\s+kalabiliriz", "Where can we stay near the restaurant?"),
    # Parking capacity
    (r"[Oo]topark\s+kapasitesi\s+ne\s+kadard[ıi]r", "What is the parking capacity?"),
    # What to eat / consume
    (r"[Nn]eler\s+t[üu]ketmek\s+istiyorsunuz", "What would you like to eat?"),
    (r"[Nn]e\s+t[üu]ketmek\s+istiyorsunuz", "What would you like to eat?"),
    # How to get - restaurant name specific
    (r"nas[ıi]l\s+gidilir", "How can I get to the restaurant?"),
    (r"nas[ıi]l\s+giderim", "How can I get there?"),
    (r"nas[ıi]l\s+ula[şs][ıi]r[ıi]m", "How can I get there?"),
    (r"nas[ıi]l\s+ula[şs]abilirim", "How can I get there?"),
    (r"[Nn]ereden\s+ula[şs]abilirim", "How can I get there?"),
    (r"[Nn]ereden\s+ula[şs][ıi]r[ıi]m", "How can I get there?"),
    # Large group services
    (r"b[üu]y[üu]k\s+gruplar\s+i[çc]in.*ne\s+gibi\s+hizmet", "What services are available for large groups?"),
    # Konum avantajları
    (r"[Kk]onum\s+avantajlar[ıi]\s+neler", "What are the location advantages?"),
    # Children at restaurant
    (r"[çc]ocuklar\s+i[çc]in\s+uygun\s+(?:bir\s+)?ortam\s+var\s*m[ıi]", "Is there a child-friendly environment?"),
    # Outdoor terrace area for groups
    (r"[Gg]ruplar\s+i[çc]in\s+[öo]zel\s+alan\s+var\s*m[ıi]", "Is there a private area for groups?"),
    (r"gruplar?\s+i[çc]in\s+[öo]zel\s+(?:alan|b[öo]lme)", "Is there a private section for groups?"),
    # Mention of restaurant name in question about how special
    (r"[öo]zel\s+y[öo]n[üu]\s+ne", "What makes it special?"),
    (r"fark[ıi]\s+ne(?:\s+dir)?", "What makes it different?"),
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
    result = re.sub(r'[Hh]ay[ıi]r[,.]?\s*rezervasyon\s*yapman[ıi]za\s*gerek\s*(?:yoktur|yok)\.?', 'No, reservations are not required.', result)
    result = re.sub(r'[Rr]ezervasyon\s*yapman[ıi]za\s*gerek\s*(?:yoktur|yok)\.?', 'No reservation required.', result)
    result = re.sub(r'[Ee]vet[,.]?\s*rezervasyon\s*yapabilirsiniz\.?', 'Yes, reservations can be made.', result)
    result = re.sub(r'[Ee]vet[,.]?\s*rezervasyon\s*önerilmektedir\.?', 'Yes, reservations are recommended.', result)
    result = re.sub(r'[Hh]afta\s*sonlar[ıi]\s*rezervasyon\s*önerilir\.?', 'Reservations recommended on weekends.', result)

    # No / Yes for facility availability
    result = re.sub(r'[Hh]ay[ıi]r[,.]?\s*Wi-?Fi\s*(?:ve\s*otopark\s*)?(?:hizmeti?\s*)?(?:bulunmamaktad[ıi]r|yok(?:tur)?)\.?',
                    'No, Wi-Fi is not available.', result)
    result = re.sub(r'[Hh]ay[ıi]r[,.]?\s*otopark\s*(?:ve\s*Wi-?Fi\s*)?(?:hizmeti?\s*)?(?:bulunmamaktad[ıi]r|yok(?:tur)?)\.?',
                    'No, parking is not available.', result)
    result = re.sub(r'[Hh]ay[ıi]r[,.]?\s*(?:otopark\s*hizmeti\s*)?sunmuyoruz\.?', 'No, not available.', result)
    result = re.sub(r'[Hh]ay[ıi]r[,.]?\s*teras\s*(?:hizmeti?\s*)?(?:bulunmamaktad[ıi]r|yok(?:tur)?)\.?',
                    'No, there is no terrace.', result)
    result = re.sub(r'[Hh]ay[ıi]r[,.]?\s*restoranda\s*teras\s*bulunmamaktad[ıi]r\.?', 'No, there is no terrace.', result)
    result = re.sub(r'[Hh]ay[ıi]r[,.]?\s*teras\s*veya\s*bah[çc]e\s*(?:bulunmamaktad[ıi]r|yok(?:tur)?)\.?', 'No, no terrace or garden.', result)
    result = re.sub(r'[Hh]ay[ıi]r[,.]?\s*restoranda\s*Wi-?Fi\s*ve\s*otopark\s*bulunmamaktad[ıi]r\.?',
                    'No, the restaurant does not have Wi-Fi or parking.', result)
    result = re.sub(r'[Ee]vet[,.]?\s*Wi-?Fi\s*(?:hizmeti?\s*)?(?:mevcuttur|var|sunuyoruz)\.?', 'Yes, Wi-Fi is available.', result)
    result = re.sub(r'Wi-?Fi\s+hizmeti\s+sunuyoruz\.?', 'Wi-Fi is available.', result)
    result = re.sub(r'[Ee]vet[,.]?\s*otopark\s*(?:hizmeti?\s*)?(?:mevcuttur|var)\.?', 'Yes, parking is available.', result)
    result = re.sub(r'[Ee]vet[,.]?\s*teras\s*(?:mevcuttur|var)\.?', 'Yes, there is a terrace.', result)
    result = re.sub(r'[Ee]vet[,.]?\s*manzaral[ıi]\s*teras\.?', 'Yes, there is a terrace with a view.', result)
    result = re.sub(r'[Ee]vet[,.]?\s*aile\s*dostu\.?', 'Yes, family-friendly.', result)
    result = re.sub(r'[Ee]vet[,.]?\s*organizasyon\s*i[çc]in\s*uygun\.?', 'Yes, suitable for events.', result)
    # Opening hours
    result = re.sub(r'[Ee]vet[,.]?\s*(\d{2}:\d{2}[-–]\d{2}:\d{2})\s*saatleri\s*aras[ıi]nda\s*a[çc][ıi][ğg][ıi]z\.?',
                    lambda m: f'Yes, open from {m.group(1).replace("–","-").replace("-"," to ")}.',
                    result)
    result = re.sub(r'(\d{2}:\d{2})\s*[-–]\s*(\d{2}:\d{2})\s*saatleri\s*aras[ıi]nda\s*a[çc][ıi][ğg][ıi]z\.?',
                    lambda m: f'Open from {m.group(1)} to {m.group(2)}.',
                    result)
    # Facility "sunuyoruz/sunmaktayız" patterns
    result = re.sub(r'[Ee]vet[,.]?\s*vegan\s*ve\s*vejetaryen\s*se[çc]enekler\s*sunuyoruz\.?', 'Yes, vegan and vegetarian options are available.', result)
    result = re.sub(r'[Ee]vet[,.]?\s*vegan\s*se[çc]enekler\s*(?:sunuyoruz|mevcuttur|mevcut|var)\.?', 'Yes, vegan options are available.', result)
    result = re.sub(r'[Ee]vet[,.]?\s*vejetaryen\s*se[çc]enekler\s*(?:sunuyoruz|mevcuttur|mevcut|var)\.?', 'Yes, vegetarian options are available.', result)
    result = re.sub(r'[Ee]vet[,.]?\s*[çc]ocuk\s*dostu\s*ortam\s*sunuyoruz\.?', 'Yes, we offer a child-friendly atmosphere.', result)
    result = re.sub(r'[Ee]vet[,.]?\s*[çc]ocuk\s*dostu\.?', 'Yes, child-friendly.', result)
    # Negative "sunmuyoruz" patterns
    result = re.sub(r'[Hh]ay[ıi]r[,.]?\s*otopark\s*hizmeti\s*sunmuyoruz\.?', 'No, parking is not available.', result)
    result = re.sub(r'[Hh]ay[ıi]r[,.]?\s*Wi-?Fi\s*hizmeti\s*sunmuyoruz\.?', 'No, Wi-Fi is not available.', result)

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

    # Neighborhood location answers
    result = re.sub(
        r'([A-ZÇĞİÖŞÜ][a-zA-ZÇĞİÖŞÜçğışöşü\s]+?)\s+mahallesinde[,]?\s*(.+?)\s+yak[ıi]n[ıi]nda\.?$',
        lambda m: f'Located in {m.group(1).strip()} neighborhood, near {m.group(2).strip()}.',
        result.strip(), flags=re.IGNORECASE
    )
    result = re.sub(
        r'([A-ZÇĞİÖŞÜ][a-zA-ZÇĞİÖŞÜçğışöşü\s]+?)\s+mahallesinde\s+yer\s+alan\s+restorana[,]?\s*',
        lambda m: f'In {m.group(1).strip()} neighborhood — ',
        result, flags=re.IGNORECASE
    )
    # "Vegan/soya ürünleri yok" type short answers
    result = re.sub(r'[Vv]egan\s*/\s*soya\s+[üu]r[üu]nleri\s+yok\.?', 'No vegan/soy options available.', result)
    result = re.sub(r'[Vv]egan\s*/\s*vegeta[rn]an\s*/?\s*soya\s+[üu]r[üu]nleri\s+yok\.?', 'No vegan, vegetarian, or soy options available.', result)

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

    # Transit stop patterns: "{Stop} tramvay/metro durağından N dakika"
    def translate_stop(m):
        stop = m.group(1).strip().rstrip("'")
        kind_tr = m.group(2).lower()
        n = m.group(3)
        kind = {"tramvay": "tram", "metro": "metro", "otobüs": "bus", "otobus": "bus", "vapur": "ferry", "metrobüs": "metrobus"}.get(kind_tr, kind_tr)
        return f"{n} min from {stop} {kind} stop"
    result = re.sub(
        r"([A-ZÇĞİÖŞÜa-zçğışöşü][^\s,]+(?:\s+[A-ZÇĞİÖŞÜ][^\s,]+)*)'?(?:den|dan|'den|'dan)?\s+(tramvay|metro|otob[üu]s|vapur|metrobüs)\s+dura[ğg][ıi]ndan\s+\(?\s*(\d+)\s*(?:dk|dakika)\s*\)?",
        translate_stop,
        result, flags=re.IGNORECASE
    )
    # "{Stop} tramvay durağından N dakika" without parens
    result = re.sub(
        r"([A-ZÇĞİÖŞÜ][a-zA-ZÇĞİÖŞÜçğışöşü\s]+?)\s+tramvay\s+dura[ğg][ıi]ndan\s+(\d+)\s*(?:dakika|dk)",
        lambda m: f"{m.group(2)} minutes from {m.group(1).strip()} tram stop",
        result, flags=re.IGNORECASE
    )
    result = re.sub(
        r"([A-ZÇĞİÖŞÜ][a-zA-ZÇĞİÖŞÜçğışöşü\s]+?)\s+metro\s+dura[ğg][ıi]ndan\s+(\d+)\s*(?:dakika|dk)",
        lambda m: f"{m.group(2)} minutes from {m.group(1).strip()} metro station",
        result, flags=re.IGNORECASE
    )
    result = re.sub(
        r"([A-ZÇĞİÖŞÜ][a-zA-ZÇĞİÖŞÜçğışöşü\s]+?)\s+vapur\s+dura[ğg][ıi]ndan\s+(\d+)\s*(?:dakika|dk)",
        lambda m: f"{m.group(2)} minutes from {m.group(1).strip()} ferry stop",
        result, flags=re.IGNORECASE
    )
    result = re.sub(r'\buzakl[ıi]ktad[ıi]r\b', 'away', result, flags=re.IGNORECASE)
    result = re.sub(r'\buzakl[ıi]ktay[ıi]z\b', 'away', result, flags=re.IGNORECASE)
    # "Eminönü'den vapur veya tramvay ile N-M dakika içinde ulaşabilirsiniz."
    result = re.sub(
        r"([A-ZÇĞİÖŞÜ][a-zA-ZÇĞİÖŞÜçğışöşü]+)'?(?:den|dan|'den|'dan)\s+(?:vapur\s+veya\s+tramvay|tramvay\s+veya\s+vapur|metro\s+veya\s+tramvay|tramvay\s+veya\s+metro)\s+ile\s+(\d+[-–]\d+|\d+)\s*dakika\s*i[çc]inde\s*ula[şs]abilirsiniz\.?",
        lambda m: f"Accessible by tram or ferry from {m.group(1)} in {m.group(2)} minutes.",
        result, flags=re.IGNORECASE
    )

    # Nearby landmark: "Evet, (sadece) N dakika uzaklıktadır/uzaklıktayız"
    result = re.sub(
        r'[Ee]vet[,.]?\s*(?:sadece\s+)?(\d+)\s*dakika\s*uzakl[ıi]ktad[ıi]r\.?',
        lambda m: f'Yes, only {m.group(1)} minutes away.',
        result
    )
    result = re.sub(
        r'[Ee]vet[,.]?\s*(?:sadece\s+)?(\d+)\s*dakika\s*uzakl[ıi]ktay[ıi]z\.?',
        lambda m: f'Yes, only {m.group(1)} minutes away.',
        result
    )
    result = re.sub(
        r'[Ee]vet[,.]?\s*(?:sadece\s+)?(\d+)\s*dakika\s*yürüme\s*mesafesinde\.?',
        lambda m: f'Yes, only {m.group(1)} minutes on foot.',
        result
    )

    # Vegan / dietary answers
    result = re.sub(r'[Vv]egan\s*se[çc]ene[ğg]imiz\s*yok[tur]*[,.]?\s*ancak\s*di[ğg]er\s*diyet\s*veya\s*alerji\s*sorunlar[ıi]\s*i[çc]in\s*l[üu]tfen\s*[öo]nceden\s*bilgilendirin\.?',
                    'No vegan options, but please inform us in advance about any dietary needs or allergies.', result)
    result = re.sub(r'[Hh]ay[ıi]r[,.]?\s*vegan\s*se[çc]ene[ğg]imiz\s*yoktur\.?', 'No, we don\'t offer vegan options.', result)
    result = re.sub(r'[Hh]ay[ıi]r[,.]?\s*vegan\s*se[çc]enekler(?:imiz)?\s*mevcut\s*de[ğg]ildir\.?', 'No, vegan options are not available.', result)
    result = re.sub(r'[Hh]ay[ıi]r[,.]?\s*vegan\s*se[çc]enekler(?:imiz)?\s*yok\.?', 'No vegan options available.', result)
    result = re.sub(r'[Vv]egan\s*se[çc]ene[ğg]i(?:miz)?\s*yok(?:tur)?\.?', 'No vegan options available.', result)
    result = re.sub(r'[Vv]ejetaryen\s*se[çc]ene[ğg]i(?:miz)?\s*yok(?:tur)?\.?', 'No vegetarian options available.', result)
    result = re.sub(r'[Hh]ay[ıi]r[,.]?\s*vegan\s*se[çc]enekleri?\s*bulunmamaktad[ıi]r\.?', 'No, vegan options are not available.', result)
    result = re.sub(r'[Hh]ay[ıi]r[,.]?\s*vejetaryen\s*se[çc]enekleri?\s*bulunmamaktad[ıi]r\.?', 'No, vegetarian options are not available.', result)

    # Children welcome
    result = re.sub(r'[Ee]vet[,.]?\s*[çc]ocuklar\s*kabul\s*edilmektedir\.?', 'Yes, children are welcome.', result)
    result = re.sub(r'[Ee]vet[,.]?\s*[çc]ocuk\s*dostu\s*bir\s*ortam\s*sunmaktad[ıi]r\.?', 'Yes, we offer a family-friendly atmosphere.', result)
    result = re.sub(r'[Ee]vet[,.]?\s*[çc]ocuklar\s*i[çc]in\s*uygun\s*bir\s*alan\s*mevcuttur\.?', 'Yes, there is a child-friendly area.', result)

    # Popular dishes: additional patterns
    result = re.sub(r'pop[üu]ler\s+yemeklerimizdendir\.?', 'are popular dishes.', result, flags=re.IGNORECASE)
    result = re.sub(r'en\s+[çc]ok\s+tercih\s+edilen\s+yemeklerdir\.?', 'are the most popular dishes.', result, flags=re.IGNORECASE)
    result = re.sub(r'restoranda\s+en\s+[çc]ok\s+tercih\s+edilen\s+yemeklerdir\.?', 'are the most popular dishes at the restaurant.', result, flags=re.IGNORECASE)
    result = re.sub(r'\bgibi\s+lezzetler\s+sunmaktad[ıi]r\.?', 'and similar dishes are served.', result, flags=re.IGNORECASE)
    result = re.sub(r'\bgibi\s+lezzetler\s+mevcuttur\.?', 'and similar dishes are available.', result, flags=re.IGNORECASE)

    # Location / transit specific
    result = re.sub(r'\brestorandan\s+(\d+)\s*dakika\s+away\b', r'\1 minutes from the restaurant', result, flags=re.IGNORECASE)
    result = re.sub(r'\brestorandan\s+(\d+[-–]\d+)\s*dakika\s+away\b', r'\1 minutes from the restaurant', result, flags=re.IGNORECASE)
    # "Taksim'e tramvay ile N dakika" → "N minutes by tram to Taksim"
    result = re.sub(
        r"([A-ZÇĞİÖŞÜ][a-zA-ZÇĞİÖŞÜçğışöşü']+)'?[ye]\s+tramvay\s+ile\s+(\d+)\s*dakika",
        lambda m: f"{m.group(2)} minutes by tram to {m.group(1)}",
        result, flags=re.IGNORECASE
    )
    result = re.sub(
        r"([A-ZÇĞİÖŞÜ][a-zA-ZÇĞİÖŞÜçğışöşü']+)'?[ye]\s+metro\s+ile\s+(\d+)\s*dakika",
        lambda m: f"{m.group(2)} minutes by metro to {m.group(1)}",
        result, flags=re.IGNORECASE
    )
    # "X metro ve Y durağından N dakika" combined stop pattern
    result = re.sub(
        r"([A-ZÇĞİÖŞÜ][a-zA-ZÇĞİÖŞÜçğışöşü\s]+?)\s+metro\s+ve\s+([a-zA-ZÇĞİÖŞÜçğışöşü\s]+?)\s+dura[ğg][ıi]ndan\s+(\d+)\s*(?:dakika|dk)",
        lambda m: f"{m.group(3)} min from {m.group(1).strip()} metro and {m.group(2).strip()} stop",
        result, flags=re.IGNORECASE
    )
    # Complex transit: "Tünel tramvay hattı (N dakika) veya X metro ve Y istasyonları (N dakika) yoluyla ulaşılabilir."
    result = re.sub(
        r"([A-ZÇĞİÖŞÜ][a-zA-ZÇĞİÖŞÜçğışöşü\s]+?)\s+tramvay\s+hatt[ıi]\s+\((\d+)\s*dakika\)\s+veya\s+(.+?)\s+istasyonlar[ıi]\s+\((\d+)\s*dakika\)\s+yoluyla\s+ula[şs][ıi]labilir\.?",
        lambda m: f"Accessible via {m.group(1).strip()} tram line ({m.group(2)} min) or {m.group(3).strip()} stations ({m.group(4)} min).",
        result, flags=re.IGNORECASE
    )
    # "X, Y ve Z gibi önemli landmarks'ın yakınında yer alıyor."
    result = re.sub(
        r'(.+?)\s+gibi\s+[öo]nemli\s+landmark[\'s]*[ıi]n?\s+yak[ıi]n[ıi]nda\s+yer\s+al[ıi]yor\.?',
        lambda m: f'Located near notable landmarks including {m.group(1).strip()}.',
        result, flags=re.IGNORECASE
    )
    result = re.sub(
        r'(.+?)\s+gibi\s+[öo]nemli\s+landmarklar\s+yak[ıi]n[ıi]ndad[ıi]r\.?',
        lambda m: f'Close to notable landmarks such as {m.group(1).strip()}.',
        result, flags=re.IGNORECASE
    )
    # "X ve Y yakınındadır." — generic landmark nearby
    result = re.sub(r'\byak[ıi]n[ıi]ndad[ıi]r\b', 'are nearby', result, flags=re.IGNORECASE)
    # "X ve Y N-M dakika" (incomplete answers with no verb)
    result = re.sub(
        r'^(.+?)\s+(\d+[-–]\d+)\s*dakika\.?$',
        lambda m: f'{m.group(1).strip()} — {m.group(2)} minutes away.',
        result.strip(), flags=re.IGNORECASE
    )

    # "çocuk dostu bir ortam yoktur" — no child-friendly area
    result = re.sub(r'[çc]ocuk\s+dostu\s+bir\s+ortam\s+(?:yok(?:tur)?|bulunmamaktad[ıi]r)\.?',
                    'No child-friendly area available.', result, flags=re.IGNORECASE)

    # Neighborhood / romantic setting
    result = re.sub(r',?\s*romantik\s+bir\s+ortamda\.?$', ', in a romantic setting.', result, flags=re.IGNORECASE)

    # Common Turkish answer fragments
    result = re.sub(r'[Ee]vet[,.]?\s*(?:aileler|b[üu]y[üu]k\s*gruplar|gruplar)\s+i[çc]in\s+uygun\s+bir\s+(?:restoran|mekan|yer)\s*(?:olarak\s+bilinir)?\.?',
                    'Yes, suitable for groups.', result, flags=re.IGNORECASE)
    result = re.sub(r'[Ee]vet[,.]?\s*aileler\s+i[çc]in\s+uygun\s+bir\s+(?:restoran|mekan|yer)\s*(?:olarak\s+bilinir)?\.?',
                    'Yes, family-friendly.', result, flags=re.IGNORECASE)
    result = re.sub(r'[Ee]vet[,.]?\s*(?:di[ğg]er\s+)?bir\s+pop[üu]ler\s+(?:kebap\s+)?se[çc]ene[ğg]i\s+olarak\s+(.+?)\s+sunuluyor\.?',
                    lambda m: f'Yes, {m.group(1).strip()} is also available.', result, flags=re.IGNORECASE)
    result = re.sub(r'[Hh]ay[ıi]r[,.]?\s*romantik\s+(?:bir\s+)?ak[şs]am\s+yeme[ğg]i\s+i[çc]in\s+uygun\s+de[ğg]ildir\.?',
                    'No, not ideal for romantic dinners.', result, flags=re.IGNORECASE)
    result = re.sub(r'uygun\s+bir\s+(?:ortam|mekan|yer)\s+sunmaktad[ıi]r\.?',
                    'offers a suitable setting.', result, flags=re.IGNORECASE)
    result = re.sub(r'romantik[,]?\s*aile\s+ve\s+i[şs]\s+yeme[ğg]i\s+i[çc]in\s+uygun\s+bir\s+ortam\s+sunmaktad[ıi]r\.?',
                    'Offers a setting suitable for romantic, family, and business dining.', result, flags=re.IGNORECASE)
    result = re.sub(u"\\w+\\s+Mutfa\\u011f[\\u0131i][\\u2019'\"\\\\']?na\\s+uygun\\s+olarak\\s+(.+?)\\s+daha\\s+uygun\\s+olur\\.?",
                    lambda m: f'{m.group(1).strip()} are recommended.', result, flags=re.IGNORECASE)
    # More restaurant-named Turkish answer patterns
    # "[Name] özel günler için organizasyon hizmeti sunuyor."
    result = re.sub(r'\w[\w\s]+\s+[öo]zel\s+g[üu]nler\s+i[çc]in\s+organizasyon\s+hizmeti\s+sunuyor\.?',
                    'The restaurant offers event planning for special occasions.', result, flags=re.IGNORECASE)
    # "[Name]'da/nda teras yok."
    result = re.sub(r"[\w\u00e7\u011f\u0131\u015f\u00f6\u015f\u00fc'\u2019]+\s*(?:restoran[ıi]nda|'nda|'da)\s+teras\s+yok\.?",
                    'No terrace at this restaurant.', result, flags=re.IGNORECASE)
    result = re.sub(r'[Hh]ay[ıi]r[,.]?\s*restoran[ıi]m[ıi]zda\s+teras\s+bulunmamaktad[ıi]r\.?',
                    'No, there is no terrace at our restaurant.', result, flags=re.IGNORECASE)
    # "WiFi yok." / "Wifi yok."
    result = re.sub(r'^Wi-?Fi\s+yok\.?$', 'No Wi-Fi available.', result.strip(), flags=re.IGNORECASE)
    # "Otopark yok, ancak yakın çevrede parklama seçenekleri mevcut."
    result = re.sub(r'[Oo]topark\s+yok[,.]?\s*ancak\s+yak[ıi]n\s+[çc]evrede\s+parklama\s+se[çc]enekleri\s+mevcut\.?',
                    'No on-site parking, but parking options are available nearby.', result, flags=re.IGNORECASE)
    # "[Name] sunuyoruz, özellikle hafta içi geceler."
    result = re.sub(r'[Gg]ece\s+hayat[ıi]\s+sunuyoruz[,.]?\s*[öo]zellikle\s+hafta\s+i[çc]i\s+geceler\.?',
                    'We offer a nightlife atmosphere, especially on weekday nights.', result, flags=re.IGNORECASE)
    # "Aileler için uygun bir ortam sunuyoruz, ancak çocuklar için özel hizmet veya çocuk yemekleri yok."
    result = re.sub(r'[Aa]ileler\s+i[çc]in\s+uygun\s+bir\s+ortam\s+sunuyoruz[,.]?\s*ancak\s+[çc]ocuklar\s+i[çc]in\s+[öo]zel\s+hizmet\s+(?:veya\s+[çc]ocuk\s+yemekleri\s+)?yok\.?',
                    'Family-friendly atmosphere, but no special children\'s services or menu.', result, flags=re.IGNORECASE)
    # "[Name]'ın popüler yemekleri arasında vegan seçenek yok."
    result = re.sub(r"[\w'\u2019]+[ıi]n\s+pop[üu]ler\s+yemekleri\s+aras[ıi]nda\s+vegan\s+se[çc]enek\s+yok\.?",
                    'No vegan options among the popular dishes.', result, flags=re.IGNORECASE)
    # "Evet, özel günler and organizasyonlar için ideal bir yerdir."
    result = re.sub(r'[Ee]vet[,.]?\s*[öo]zel\s+g[üu]nler\s+(?:and|ve)\s+organizasyonlar\s+i[çc]in\s+ideal\s+bir\s+(?:yer|mekan|restoran)\.?',
                    'Yes, ideal for special occasions and events.', result, flags=re.IGNORECASE)
    # "[Name], geleneksel X mutfağını sunan bir restoran." descriptions
    result = re.sub(r'[\w\s]+[,]\s*geleneksel\s+[\w\s]+\s+mutfa[ğg][ıi]n[ıi]\s+sunan\s+bir\s+restorand[ıi]r\.?',
                    'A traditional restaurant serving authentic local cuisine.', result, flags=re.IGNORECASE)
    # "popular yemeklerimizdir" / "popüler yemeklerimizdir" → "are popular dishes"
    result = re.sub(r'\bpop(?:[üu]ler|ular)\s+yemeklerimizdir\.?', 'are popular dishes.', result, flags=re.IGNORECASE)
    result = re.sub(r'\bpop(?:[üu]ler|ular)\s+yemeklerimizden\b', 'is one of our popular dishes,', result, flags=re.IGNORECASE)
    result = re.sub(r'\bpop(?:[üu]ler|ular)dir\.?', 'are popular.', result, flags=re.IGNORECASE)
    result = re.sub(r'\bpop(?:[üu]ler|ular)\s+yemeklerinden\s+biridir\.?', 'is one of the popular dishes.', result, flags=re.IGNORECASE)
    result = re.sub(r'\bpop(?:[üu]ler|ular)\s+yemeklerimizden\s+biridir\.?', 'is one of the popular dishes.', result, flags=re.IGNORECASE)
    # "restoranın is one of" → "is one of"
    result = re.sub(r'\brestoran[ıi]n\s+is\s+one\s+of', 'is one of', result, flags=re.IGNORECASE)
    # "gibi lezzetler we offer" → strip Turkish prefix
    result = re.sub(r'(.+?)\s+gibi\s+lezzetler\s+we\s+offer\.?', r'\1 and more are available.', result, flags=re.IGNORECASE)
    result = re.sub(r'\bgibi\s+lezzetler\s+we\s+offer\.?', 'and more are available.', result, flags=re.IGNORECASE)
    # "gibi lezzetli Türk mutfağı yemekleri deneyebilirsiniz" → strip
    result = re.sub(r'(.+?)\s+gibi\s+lezzetli\s+T[üu]rk\s+mutfa[ğg][ıi]\s+yemekleri\s+deneyebilirsiniz\.?',
                    r'You can try Turkish dishes like \1.', result, flags=re.IGNORECASE)
    result = re.sub(r'(.+?)\s+gibi\s+yerel\s+lezzetler\s+deneyebilirsiniz\.?',
                    r'You can try local dishes like \1.', result, flags=re.IGNORECASE)
    result = re.sub(r'[Bb]urada\s+(.+?)\s+gibi\s+(?:yerel\s+)?lezzetler\s+deneyebilirsiniz\.?',
                    r'Here you can try dishes like \1.', result, flags=re.IGNORECASE)
    # "Doğum günü, özel günler and organizasyonlar için Reservations are recommended..."
    result = re.sub(r'[Dd]o[ğg]um\s+g[üu]n[üu][,.]?\s*[öo]zel\s+g[üu]nler\s+(?:and|ve)\s+organizasyonlar\s+i[çc]in\s+',
                    'For birthdays, special occasions and events, ', result, flags=re.IGNORECASE)
    # "Doğum günü veya özel günler için, restoranda bulunan şef restoranı and özel menüler can be preferred."
    result = re.sub(r'[Dd]o[ğg]um\s+g[üu]n[üu]\s+veya\s+[öo]zel\s+g[üu]nler\s+i[çc]in[,.]?\s*restoranda\s+bulunan\s+[şs]ef\s+restoranı\s+and\s+[öo]zel\s+g[üu]nler\s+i[çc]in\s+hazırlanan\s+menüler\s+can\s+be\s+preferred\.?',
                    'For birthdays and special occasions, special menus and chef services are available.', result, flags=re.IGNORECASE)
    result = re.sub(r'[Dd]o[ğg]um\s+g[üu]n[üu]\s+veya\s+[öo]zel\s+g[üu]nler\s+i[çc]in[,.]?\s*',
                    'For birthdays or special occasions, ', result, flags=re.IGNORECASE)
    # "X gibi kültürel merkezler, restoranın yakınında is nearby."
    result = re.sub(r'(.+?)\s+gibi\s+k[üu]lt[üu]rel\s+merkezler[,.]?\s*restoranın\s+yakınında\s+is\s+nearby\.?',
                    r'\1 and other cultural venues are nearby.', result, flags=re.IGNORECASE)
    result = re.sub(r'(.+?)\s+gibi\s+k[üu]lt[üu]rel\s+merkezler\b',
                    r'\1 and other cultural venues', result, flags=re.IGNORECASE)
    # "X restoranın yakınlarında is nearby." / "restoranın yakınında is nearby."
    result = re.sub(r'restoranın\s+yakınlarında\s+is\s+nearby\.?', 'is near the restaurant.', result, flags=re.IGNORECASE)
    result = re.sub(r'restoranın\s+yakınında\s+is\s+nearby\.?', 'is near the restaurant.', result, flags=re.IGNORECASE)
    result = re.sub(r'\s+is\s+nearby\b(?!\.)', ' is nearby.', result, flags=re.IGNORECASE)
    # "[Name]'na sadece/only N dakika away" → "[Name] is only N minutes away"
    result = re.sub(
        r"([\w\u00e7\u011f\u0131\u00f6\u015f\u00fc\u00c7\u011e\u0130\u00d6\u015e\u00dc\s''\u2019]+)'?(?:na|ya|a)\s+(?:sadece\s+)?only\s+(\d+(?:[-–]\d+)?)\s*(?:dakika|minutes?)\s+away\.?",
        lambda m: f"{m.group(1).strip()} is only {m.group(2)} minutes away.",
        result, flags=re.IGNORECASE
    )
    result = re.sub(
        r"([\w\u00e7\u011f\u0131\u00f6\u015f\u00fc\u00c7\u011e\u0130\u00d6\u015e\u00dc\s''\u2019]+)'?(?:na|ya|a)\s+sadece\s+(\d+(?:[-–]\d+)?)\s*(?:dakika|dk)\s+away\.?",
        lambda m: f"{m.group(1).strip()} is only {m.group(2)} minutes away.",
        result, flags=re.IGNORECASE
    )
    # "sadece N dakika away" → "only N minutes away"
    result = re.sub(r'\bsadece\s+(\d+)\s*dakika\s+away\.?', r'only \1 minutes away.', result, flags=re.IGNORECASE)
    result = re.sub(r'\bsadece\s+(\d+[-–]\d+)\s*dakika\s+away\.?', r'only \1 minutes away.', result, flags=re.IGNORECASE)
    # "N dakika away" (without sadece) → "N minutes away"
    result = re.sub(r'\b(\d+)\s*dakika\s+away\.?', r'\1 minutes away.', result, flags=re.IGNORECASE)
    # "N dk away" → "N min away"
    result = re.sub(r'\b(\d+)\s*dk\s+away\.?', r'\1 min away.', result, flags=re.IGNORECASE)
    # "(metro, Ndk)" → "(metro, N min)"
    result = re.sub(r'\((\w+),\s*(\d+)\s*dk\)', lambda m: f'({m.group(1)}, {m.group(2)} min)', result, flags=re.IGNORECASE)
    # "Evrensel Değerler Çocuk Müzesi (10dk)" → "Evrensel Değerler Çocuk Müzesi (10 min)"
    result = re.sub(r'\((\d+)dk\)', r'(\1 min)', result, flags=re.IGNORECASE)
    # "X (metro, N min) veya Y (metro, N min) metro istasyonlarından yürüyerek ulaşabilirsiniz"
    result = re.sub(r'(.+?)\s+metro\s+istasyonlar[ıi]ndan\s+y[üu]r[üu]yerek\s+ula[şs]abilirsiniz\.?',
                    r'Accessible on foot from \1 metro stations.', result, flags=re.IGNORECASE)
    result = re.sub(r'(.+?)\s+istasyonlar[ıi]ndan\s+y[üu]r[üu]yerek\s+ula[şs]abilirsiniz\.?',
                    r'Accessible on foot from \1.', result, flags=re.IGNORECASE)
    result = re.sub(r'(.+?)\s+istasyonu?ndan\s+y[üu]r[üu]yerek\s+ula[şs]abilirsiniz\.?',
                    r'Accessible on foot from \1.', result, flags=re.IGNORECASE)
    # "veya X stop ulaşabilirsiniz"
    result = re.sub(r'\bveya\s+(.+?)\s+stop\s+ula[şs]abilirsiniz\.?',
                    r'or \1 stop.', result, flags=re.IGNORECASE)
    # "veya" → "or" in transit contexts (between transport options)
    result = re.sub(r'\s+veya\s+(?=[\w(])', ' or ', result, flags=re.IGNORECASE)
    # "Hayır, teras veya otopark gibi alanlar yoktur."
    result = re.sub(r'[Hh]ay[ıi]r[,.]?\s*teras\s+(?:veya|or)\s+otopark\s+gibi\s+alanlar\s+yoktur\.?',
                    'No, there is no terrace or parking available.', result, flags=re.IGNORECASE)
    # "Evet, sadece N dakika" (no "away") — short answer
    result = re.sub(r'^[Ee]vet[,.]?\s+sadece\s+(\d+(?:[-–]\d+)?)\s*(?:dakika|dk)\.?$',
                    r'Yes, only \1 minutes away.', result.strip(), flags=re.IGNORECASE)
    # "Hayır, vegan/vejetaryen seçenekleri sunmuyoruz"
    result = re.sub(r'[Hh]ay[ıi]r[,.]?\s*(?:vegan[/,]?vejetaryen|vegan|vejetaryen)[/,\s]*(?:[şs]erit\s+)?diyet\s+se[çc]enekleri\s+sunmuyoruz\.?',
                    'No, vegan/vegetarian options are not available.', result, flags=re.IGNORECASE)
    result = re.sub(r'[Hh]ay[ıi]r[,.]?\s*vegan\s+se[çc]enekler\s+sunulmamaktad[ıi]r\.?',
                    'No, vegan options are not available.', result, flags=re.IGNORECASE)
    result = re.sub(r'[Hh]ay[ıi]r[,.]?\s*vegan\s+dishes\s+sunulmamaktad[ıi]r\.?',
                    'No, vegan options are not available.', result, flags=re.IGNORECASE)
    result = re.sub(r'[Hh]ay[ıi]r[,.]?\s*vegan\s+se[çc]enekler\s+yok\.?',
                    'No, vegan options are not available.', result, flags=re.IGNORECASE)
    # "Hayır, otoparkımız yok." → "No parking available."
    result = re.sub(r'[Hh]ay[ıi]r[,.]?\s*otopark[ıi]m[ıi]z\s+yok\.?', 'No parking available.', result, flags=re.IGNORECASE)
    # "WiFi erişimi yok." → "No Wi-Fi access."
    result = re.sub(r'Wi-?Fi\s+eri[şs]imi\s+yok\.?', 'No Wi-Fi access.', result, flags=re.IGNORECASE)
    # "Evet, özel günler için organizasyon yapılabilmektedir." → "Yes, special events can be organized."
    result = re.sub(r'[Ee]vet[,.]?\s*(?:restoranda\s+)?[öo]zel\s+g[üu]nler\s+i[çc]in\s+organizasyon\s+yap[ıi]labilmektedir\.?',
                    'Yes, special events can be organized.', result, flags=re.IGNORECASE)
    # "Hayır, özel günler için organizasyon hizmeti sunmuyoruz." → "No, we do not offer event planning."
    result = re.sub(r'[Hh]ay[ıi]r[,.]?\s*[öo]zel\s+g[üu]nler\s+i[çc]in\s+organizasyon\s+hizmeti\s+sunmuyoruz\.?',
                    'No, we do not offer event planning services.', result, flags=re.IGNORECASE)
    # "Hayır, romantik bir akşam için uygun değildir." → "No, not suitable for a romantic evening."
    result = re.sub(r'[Hh]ay[ıi]r[,.]?\s*romantik\s+bir\s+ak[şs]am\s+i[çc]in\s+uygun\s+de[ğg]ildir\.?',
                    'No, not suitable for a romantic evening.', result, flags=re.IGNORECASE)
    result = re.sub(r'[Hh]ay[ıi]r[,.]?\s*romantik\s+bir\s+ak[şs]am\s+i[çc]in\s+uygun\s+de[ğg]il[,.].*$',
                    'No, not suitable for a romantic evening.', result, flags=re.IGNORECASE)
    # "Büyük gruplar için özel menüler and hizmetler we offer." → "Special menus and services are available for large groups."
    result = re.sub(r'[Bb][üu]y[üu]k\s+gruplar\s+i[çc]in\s+[öo]zel\s+men[üu]ler\s+(?:and|ve)\s+hizmetler\s+(?:we\s+offer|sunulur|sunuluyor)\.?',
                    'Special menus and services are available for large groups.', result, flags=re.IGNORECASE)
    # "Evet, restoranda teras is nearby." → "Yes, there is a terrace."
    result = re.sub(r'[Ee]vet[,.]?\s*restoranda\s+teras\s+is\s+nearby\.?', 'Yes, there is a terrace.', result, flags=re.IGNORECASE)
    # "Evet, restoranda deniz manzarası is nearby." → "Yes, there is a sea view."
    result = re.sub(r'[Ee]vet[,.]?\s*restoranda\s+deniz\s+manzaras[ıi]\s+is\s+nearby\.?', 'Yes, there is a sea view.', result, flags=re.IGNORECASE)
    # "Evet, restoranda çocuklar için uygun bir ortam is nearby." → "Yes, child-friendly environment."
    result = re.sub(r'[Ee]vet[,.]?\s*restoranda\s+[çc]ocuklar\s+i[çc]in\s+uygun\s+bir\s+ortam\s+is\s+nearby\.?',
                    'Yes, child-friendly environment available.', result, flags=re.IGNORECASE)
    # "Evet, büyük gruplar için ideal bir yerdir." → "Yes, ideal for large groups."
    result = re.sub(r'[Ee]vet[,.]?\s*b[üu]y[üu]k\s+gruplar\s+i[çc]in\s+ideal\s+bir\s+(?:yer|mekan|restoran)\.?',
                    'Yes, ideal for large groups.', result, flags=re.IGNORECASE)
    # "Evet, büyük gruplar için uygun bir yerdir/restoranız." → "Yes, suitable for large groups."
    result = re.sub(r'[Ee]vet[,.]?\s*b[üu]y[üu]k\s+gruplar\s+i[çc]in\s+uygun\s+(?:olan\s+)?bir\s+(?:yer|mekan|restoran[ıi]z)\.?',
                    'Yes, suitable for large groups.', result, flags=re.IGNORECASE)
    # "Evet, pazar günleri also açıkız." → "Yes, we are also open on Sundays."
    result = re.sub(r'[Ee]vet[,.]?\s*pazar\s+g[üu]nleri\s+also\s+a[çc][ıi]k[ıi]z\.?',
                    'Yes, we are also open on Sundays.', result, flags=re.IGNORECASE)
    result = re.sub(r'[Ee]vet[,.]?\s*pazar\s+g[üu]nleri\s+a[çc][ıi]k[ıi]z\.?',
                    'Yes, we are open on Sundays.', result, flags=re.IGNORECASE)
    # "Aileler için offers a suitable setting." → "Suitable setting for families."
    result = re.sub(r'[Aa]ileler\s+i[çc]in\s+offers\s+a\s+suitable\s+setting\.?',
                    'Suitable setting for families.', result, flags=re.IGNORECASE)
    # "and çocuklar için offers a suitable setting" → strip
    result = re.sub(r'\s+and\s+[çc]ocuklar\s+i[çc]in\s+offers\s+a\s+suitable\s+setting\.?',
                    '.', result, flags=re.IGNORECASE)
    # "Evet, yakınında is nearby." → "Yes, it is nearby."
    result = re.sub(r'[Ee]vet[,.]?\s*yak[ıi]n[ıi]nda\s+is\s+nearby\.?', 'Yes, it is nearby.', result, flags=re.IGNORECASE)
    # "Evet, doğum günleri and büyük gruplar için organizasyon yapabilirsiniz." → "Yes, birthdays and group events can be organized."
    result = re.sub(r'[Ee]vet[,.]?\s*do[ğg]um\s+g[üu]nleri\s+(?:and|ve)\s+b[üu]y[üu]k\s+gruplar\s+i[çc]in\s+organizasyon\s+yapabilirsiniz\.?',
                    'Yes, you can organize birthdays and large group events.', result, flags=re.IGNORECASE)
    # "Yaklaşık olarak N dakika yürüme mesafesindedir." → "About N minutes on foot."
    result = re.sub(r'[Yy]akla[şs][ıi]k\s+olarak\s+(\d+)\s*dakika\s+y[üu]r[üu]me\s+mesafesindedir\.?',
                    r'About \1 minutes on foot.', result, flags=re.IGNORECASE)
    result = re.sub(r'[Yy]akla[şs][ıi]k\s+(\d+)\s*dakika\s+y[üu]r[üu]me\s+mesafesindedir\.?',
                    r'About \1 minutes on foot.', result, flags=re.IGNORECASE)
    # "Etiketi 'büyük grup' olarak listelenmiştir." → remove
    result = re.sub(r"[Ee]tiketi\s+['\"]?b[üu]y[üu]k\s+grup['\"]?\s+olarak\s+listelenmi[şs]tir\.?", '', result, flags=re.IGNORECASE)
    # "gibi yakın transit seçenekleri is nearby." → "and other nearby transit options."
    result = re.sub(r'\s+gibi\s+yak[ıi]n\s+transit\s+se[çc]enekleri\s+is\s+nearby\.?',
                    ' and other nearby transit options.', result, flags=re.IGNORECASE)
    # "gibi lezzetli dishes we offer." → "and more are available."
    result = re.sub(r'\s+gibi\s+lezzetli\s+dishes\s+we\s+offer\.?', ' and more are available.', result, flags=re.IGNORECASE)
    # "X restoranının is one of the popular dishes" → strip restaurant reference
    result = re.sub(r'\w+\s+restoran[ıi]n[ıi]n\s+is\s+one\s+of\s+the\s+popular\s+dishes\.?',
                    'is one of the popular dishes.', result, flags=re.IGNORECASE)
    # "vegan seçenekler yer almamaktadır" → "vegan options are not available"
    result = re.sub(r'vegan\s+se[çc]enekler\s+yer\s+almamaktad[ıi]r\.?', 'vegan options are not available.', result, flags=re.IGNORECASE)
    # "popüler yemek listesinde vegan seçenekler yer almamaktadır" → "No vegan options on the menu."
    result = re.sub(r'.+pop[üu]ler\s+yemek\s+listesinde\s+vegan\s+se[çc]enekler\s+yer\s+almamaktad[ıi]r\.?',
                    'No vegan options on the menu.', result, flags=re.IGNORECASE)
    # "Türk mutfağından olan yemekleri severiz." → "We serve dishes from Turkish cuisine."
    result = re.sub(r'T[üu]rk\s+mutfa[ğg][ıi]ndan\s+olan\s+yemekleri\s+severiz\.?',
                    'We serve dishes from Turkish cuisine.', result, flags=re.IGNORECASE)
    # "traditional Türk mutfağının önemli örnekleri olan X sunuyor" → "serves traditional Turkish dishes including X"
    result = re.sub(r'traditional\s+T[üu]rk\s+mutfa[ğg][ıi]n[ıi]n\s+[öo]nemli\s+[öo]rnekleri\s+olan\s+(.+?)\s+(?:sunuyor|we offer)\.?',
                    r'serves traditional Turkish dishes such as \1.', result, flags=re.IGNORECASE)
    # "geleneksel Türk mutfağından gelmektedir" → "comes from traditional Turkish cuisine"
    result = re.sub(r'geleneksel\s+T[üu]rk\s+mutfa[ğg][ıi]ndan\s+gelmektedir\.?',
                    'comes from traditional Turkish cuisine.', result, flags=re.IGNORECASE)
    # "Geç saatlere kadar açık olan X restoranı, iş yemeği and romantik bir akşam için ideal bir seçimdir."
    result = re.sub(r'[Gg]e[çc]\s+saatlere\s+kadar\s+a[çc][ıi]k\s+olan\s+\w[\w\s]+\s+restoranı[,.]?\s+i[şs]\s+yeme[ğg]i\s+(?:and|ve)\s+romantik\s+bir\s+ak[şs]am\s+i[çc]in\s+ideal\s+bir\s+se[çc]imdir\.?',
                    'Open until late hours, ideal for business lunches and romantic evenings.', result, flags=re.IGNORECASE)
    # "Evet, restoranın manzaralı terası yok, but X gibi tarihi landmarklar yakındadır."
    result = re.sub(r'[Ee]vet[,.]?\s*restoranın\s+manzaral[ıi]\s+teras[ıi]\s+yok[,.]?\s*but\s+(.+?)\s+gibi\s+tarihi\s+landmarklar\s+yak[ıi]ndad[ıi]r\.?',
                    r'Unfortunately, the restaurant has no terrace, but historic landmarks like \1 are nearby.', result, flags=re.IGNORECASE)
    # "Restoranda iş yemeği organizasyonu can be done and büyük gruplar için uygun bir yerdir."
    result = re.sub(r'[Rr]estoranda\s+i[şs]\s+yeme[ğg]i\s+organizasyonu\s+can\s+be\s+done\s+(?:and|ve)\s+b[üu]y[üu]k\s+gruplar\s+i[çc]in\s+uygun\s+bir\s+(?:yer|mekan)\.?',
                    'Business lunch events can be organized. Suitable for large groups.', result, flags=re.IGNORECASE)
    # "Evet, restoranın popüler yemekleri among çocukların also sevdiği X bulunur."
    result = re.sub(r'[Ee]vet[,.]?\s*restoranın\s+pop[üu]ler\s+yemekleri\s+among\s+[çc]ocukların\s+also\s+sevdi[ğg]i\s+(.+?)\s+bulunur\.?',
                    r'Yes, the menu includes child-friendly favorites like \1.', result, flags=re.IGNORECASE)
    # "[Name] restoranı büyük gruplar için uygun bir seçimdir." → "This restaurant is a good choice for large groups."
    result = re.sub(r'[\w\s]+restoranı\s+b[üu]y[üu]k\s+gruplar\s+i[çc]in\s+uygun\s+bir\s+se[çc]imdir\.?',
                    'This restaurant is a good choice for large groups.', result, flags=re.IGNORECASE)
    # "X'nden yakındır." / "X'den yakındır."
    result = re.sub(r"'?[nd]en\s+yak[ıi]nd[ıi]r\.?", ' is nearby.', result, flags=re.IGNORECASE)
    result = re.sub(r"'?[nd]an\s+yak[ıi]nd[ıi]r\.?", ' is nearby.', result, flags=re.IGNORECASE)
    # "Evet," as leading prefix before English → strip
    result = re.sub(r'^[Ee]vet[,\.]\s+(?=[A-Z])', '', result)
    # "Hayır, romantik ortam yok." → "No romantic atmosphere."
    result = re.sub(r'[Hh]ay[ıi]r[,.]?\s*romantik\s+ortam\s+yok\.?', 'No romantic atmosphere.', result, flags=re.IGNORECASE)
    # "Hayır, restoranda teras yoktur." → "No, there is no terrace."
    result = re.sub(r'[Hh]ay[ıi]r[,.]?\s*restoranda\s+teras\s+yoktur\.?', 'No, there is no terrace.', result, flags=re.IGNORECASE)
    result = re.sub(r'[Hh]ay[ıi]r[,.]?\s*restoranda\s+teras\s+yok\.?', 'No, there is no terrace.', result, flags=re.IGNORECASE)
    # "Hayır, vegan seçenekleri yoktur." → "No, vegan options are not available."
    result = re.sub(r'[Hh]ay[ıi]r[,.]?\s*vegan\s+se[çc]enekleri\s+yoktur\.?', 'No, vegan options are not available.', result, flags=re.IGNORECASE)
    result = re.sub(r'[Hh]ay[ıi]r[,.]?\s*vegan\s+se[çc]enekleri\s+yok\.?', 'No, vegan options are not available.', result, flags=re.IGNORECASE)
    # "Hayır, vegan seçeneğimiz is not available." → strip Turkish prefix
    result = re.sub(r'[Hh]ay[ıi]r[,.]?\s*vegan\s+se[çc]ene[ğg]imiz\s+is\s+not\s+available\.?',
                    'No, vegan options are not available.', result, flags=re.IGNORECASE)
    # "Hayır, otoparkımız is not available." → "No parking available."
    result = re.sub(r'[Hh]ay[ıi]r[,.]?\s*otopark[ıi]m[ıi]z\s+is\s+not\s+available\.?',
                    'No parking available.', result, flags=re.IGNORECASE)
    # "Evet, özel günler or organizasyonlar için ideal bir seçimdir." → "Yes, ideal for special occasions and events."
    result = re.sub(r'[Ee]vet[,.]?\s*[öo]zel\s+g[üu]nler\s+(?:or|veya|ve)\s+organizasyonlar\s+i[çc]in\s+ideal\s+bir\s+se[çc]imdir\.?',
                    'Yes, ideal for special occasions and events.', result, flags=re.IGNORECASE)
    # "Evet, doğum günü, büyük grup and özel gün organizasyonları için uygun."
    result = re.sub(r'[Ee]vet[,.]?\s*do[ğg]um\s+g[üu]n[üu][,.]?\s*b[üu]y[üu]k\s+grup\s+(?:and|ve)\s+[öo]zel\s+g[üu]n\s+organizasyonlar[ıi]\s+i[çc]in\s+uygun\.?',
                    'Yes, suitable for birthdays, large groups, and special occasions.', result, flags=re.IGNORECASE)
    # "Evet, romantik bir atmosferi." → "Yes, romantic atmosphere."
    result = re.sub(r'[Ee]vet[,.]?\s*romantik\s+bir\s+atmosferi\.?', 'Yes, romantic atmosphere.', result, flags=re.IGNORECASE)
    # "Evet, 23:30'a kadar açık olan bir restoranız." / "Evet, X'a kadar açık..."
    result = re.sub(u'[Ee]vet[,.]?\\s*[\\d:]+[\u2019\']?a\\s+kadar\\s+a[\u00e7c][\u0131i]k\\s+olan\\s+bir\\s+restoran[\u0131i]z\\.?',
                    'Yes, we are open until late.', result, flags=re.IGNORECASE)
    # "geç saate kadar açık bir restoran olarak hizmet vermektedir." → "Open until late."
    result = re.sub(r'ge[çc]\s+saate?\s+kadar\s+a[çc][ıi]k\s+(?:bir\s+)?restoran\s+olarak\s+hizmet\s+vermektedir\.?',
                    'Open until late.', result, flags=re.IGNORECASE)
    result = re.sub(r'[Gg]ece\s+saatlerine\s+kadar\s+a[çc][ıi]k\s+olan\s+restoranımız[,.]?\s*keyifli\s+bir\s+ak[şs]am\s+i[çc]in\s+ideal\s+bir\s+se[çc]imdir\.?',
                    'Open until late, ideal for a pleasant evening.', result, flags=re.IGNORECASE)
    # "gibi yemeklerimiz are popular." → strip Turkish prefix
    result = re.sub(r'(.+?)\s+gibi\s+yemeklerimiz\s+are\s+popular\.?', r'\1 are popular dishes.', result, flags=re.IGNORECASE)
    # "X gibi önemli landmarklar yakınında bulunan restoranımız, keyifli bir gezi için ideal..."
    result = re.sub(r'(.+?)\s+gibi\s+[öo]nemli\s+landmarklar\s+yak[ıi]n[ıi]nda\s+bulunan\s+restoranımız[,.]?\s+keyifli\s+bir\s+(?:gezi|ak[şs]am)\s+i[çc]in\s+ideal[^.]*\.',
                    r'Located near notable landmarks such as \1. An ideal spot for a memorable visit.',
                    result, flags=re.IGNORECASE)
    # "Restoran, büyük gruplara and iş yemeğine offers a suitable setting." → simplified
    result = re.sub(r'[Rr]estoran[,.]?\s*b[üu]y[üu]k\s+gruplara\s+(?:and|ve)\s+i[şs]\s+yeme[ğg]ine\s+offers\s+a\s+suitable\s+setting\.?',
                    'Suitable setting for large groups and business lunches.', result, flags=re.IGNORECASE)
    # "Çoklu bir aile ortamı yok, but çocuk dostu olabilir." → "No dedicated family area, but may be child-friendly."
    result = re.sub(r'[Çç]oklu\s+bir\s+aile\s+ortamı\s+yok[,.]?\s*but\s+[çc]ocuk\s+dostu\s+olabilir\.?',
                    'No dedicated family area, but may be child-friendly.', result, flags=re.IGNORECASE)
    # "X gibi lezzetler sunuyor." → "offers dishes like X."
    result = re.sub(r'(.+?)\s+gibi\s+lezzetler\s+sunuyor\.?', r'Offers dishes like \1.', result, flags=re.IGNORECASE)
    # "Bilgi bulunamadı, but restoranın popüler yemekleri X'tır."
    result = re.sub(r'[Bb]ilgi\s+bulunamad[ıi][,.]?\s*but\s+restoranın\s+pop[üu]ler\s+yemekleri\s+(.+?)\s*(?:tır|dır)\.',
                    r'\1 are popular dishes.', result, flags=re.IGNORECASE)
    # "Located in X neighborhood. bulunan restoranımıza..." → fix double location
    result = re.sub(r'(Located in \w[\w\s]+ neighborhood\.\s*)bulunan\s+restoranımıza\s+', r'\1Accessible via ', result, flags=re.IGNORECASE)
    # "X restoranının popüler yemek listesinde" → strip
    result = re.sub(r'[\w\s]+restoranının\s+pop[üu]ler\s+yemek\s+listesinde\s+', '', result, flags=re.IGNORECASE)
    # "Evet, büyük gruplar için uygun olan restoranımız, aileler için also keyifli bir deneyim sunar."
    result = re.sub(r'[Ee]vet[,.]?\s*b[üu]y[üu]k\s+gruplar\s+i[çc]in\s+uygun\s+olan\s+restoranımız[,.]?\s*aileler\s+i[çc]in\s+also\s+keyifli\s+bir\s+deneyim\s+sunar\.?',
                    'Yes, suitable for large groups and also a pleasant experience for families.', result, flags=re.IGNORECASE)
    # "Evet, 10 min away." when question is about nearby landmark
    result = re.sub(r'^[Ee]vet[,.]?\s+(\d+)\s+min\s+away\.?$', r'Yes, \1 minutes away.', result.strip())
    # "Restoran, ..." prefix when there's already English text
    result = re.sub(r'^[Rr]estoran[,.]?\s+(?=serves|offers|is|has|features|provides|A\b)', '', result)
    # "Terasi yok." → "No terrace."
    result = re.sub(r'^[Tt]eras[ıi]\s+yok\.?$', 'No terrace.', result.strip())
    # "[Name]'ın terası yok." → "No terrace."
    result = re.sub(r"[\w\s''\u2019]+[ıiuü]n\s+teras[ıi]\s+yok\.?", 'No terrace.', result, flags=re.IGNORECASE)
    # "reservation yapma seçeneğimiz yok." → "Reservations are not available."
    result = re.sub(r'reservation\s+yapma\s+se[çc]ene[ğg]imiz\s+yok\.?', 'Reservations are not available.', result, flags=re.IGNORECASE)
    # "X gibi lezzetlerimiz." → dishes list answer
    result = re.sub(r'(.+?)\s+gibi\s+lezzetlerimiz\.?$', r'\1 are popular dishes.', result.strip(), flags=re.IGNORECASE)
    # "X gibi yakın landmarklarımız." → "Nearby landmarks include X."
    result = re.sub(r'(.+?)\s+gibi\s+yak[ıi]n\s+landmarklar[ıi]m[ıi]z\.?', r'Nearby landmarks include \1.', result, flags=re.IGNORECASE)
    # "Romantik, ... gibi etkinlikler için uygun atmosphere." → "Suitable for various occasions."
    result = re.sub(r'[Rr]omantik[,.]?.*gibi\s+etkinlikler\s+i[çc]in\s+uygun\s+atmosphere\.?',
                    'Suitable for romantic dinners, business lunches, birthdays, and special occasions.', result, flags=re.IGNORECASE)
    # "Büyük gruplar için uygun." → "Suitable for large groups."
    result = re.sub(r'^[Bb][üu]y[üu]k\s+gruplar\s+i[çc]in\s+uygun\.?$', 'Suitable for large groups.', result.strip())
    # "Doğum günü, özel gün gibi organizasyonlar için ideal." → "Ideal for birthdays and special occasions."
    result = re.sub(r'[Dd]o[ğg]um\s+g[üu]n[üu][,.]?\s*[öo]zel\s+g[üu]n\s+gibi\s+organizasyonlar\s+i[çc]in\s+ideal\.?',
                    'Ideal for birthdays and special occasions.', result, flags=re.IGNORECASE)
    # "Evet, çocuklar için uygun." → "Yes, suitable for children."
    result = re.sub(r'[Ee]vet[,.]?\s*[çc]ocuklar\s+i[çc]in\s+uygun\.?', 'Yes, suitable for children.', result, flags=re.IGNORECASE)
    # "Manzaralı bir restoran olan X, lezzetli ... and uygun fiyatlarıyla dikkat çekiyor."
    result = re.sub(r'[Mm]anzaral[ıi]\s+bir\s+restoran\s+olan\s+\w[\w\s]+[,.]?\s*lezzetli\s+(.+?)\s+(?:and|ve)\s+uygun\s+fiyatlar[ıi]yla\s+dikkat\s+[çc]ekiyor\.?',
                    r'A scenic restaurant known for its delicious \1 and affordable prices.', result, flags=re.IGNORECASE)
    # "[Name] restoranı doğum günü organizasyonları için uygun bir yer olabilir."
    result = re.sub(r'\w[\w\s]+restoran[ıi]\s+do[ğg]um\s+g[üu]n[üu]\s+organizasyonlar[ıi]\s+i[çc]in\s+uygun\s+bir\s+yer\s+olabilir\.?',
                    'The restaurant may be suitable for birthday events.', result, flags=re.IGNORECASE)
    # "[Name] restoranı büyük gruplar için özel alan sunar. İş yemeği organizasyonları için ideal bir yerdir."
    result = re.sub(r'\w[\w\s]+restoran[ıi]\s+b[üu]y[üu]k\s+gruplar\s+i[çc]in\s+[öo]zel\s+alan\s+sunar\.?\s+[İi][şs]\s+yeme[ğg]i\s+organizasyonlar[ıi]\s+i[çc]in\s+ideal\s+bir\s+(?:yer|mekan)\.?',
                    'The restaurant offers a private area for large groups. Ideal for business lunches.', result, flags=re.IGNORECASE)
    # "X grilled and kebap mutfak türüne based on ..." → "X, Y and other grilled/kebab dishes are recommended."
    result = re.sub(r'\w[\w\s\'&]+\s+grilled\s+(?:and|ve)\s+kebap\s+mutfak\s+t[üu]r[üu]ne\s+based\s+on\s+(.+?)\s+daha\s+uygun\.?',
                    r'\1 and other grilled and kebab dishes are recommended.', result, flags=re.IGNORECASE)
    # "Marmaray hattı ile X or Y istasyonlarından" - transit remnants
    result = re.sub(r'[Mm]armaray\s+hatt[ıi]\s+ile\s+(.+?)\s+istasyonlar[ıi]ndan\s+ula[şs]abilirsiniz\.?',
                    r'Accessible via Marmaray from \1 stations.', result, flags=re.IGNORECASE)
    # "Evet, restoran büyük grupları kabul edebilir, especially X'den N dakika olması kolay ulaşım sağlar."
    result = re.sub(r'[Ee]vet[,.]?\s*restoran\s+b[üu]y[üu]k\s+gruplar[ıi]\s+kabul\s+edebilir[,.]?\s*especially\s+[^.]+\s+kolay\s+ula[şs][ıi]m\s+sa[ğg]lar\.?',
                    'Yes, the restaurant can accommodate large groups with convenient transport access.', result, flags=re.IGNORECASE)
    # "[Name]'ın popüler yemekleri traditional Türk mutfağından gelmektedir, especially X"
    result = re.sub(r"[\w\s''\u2019]+[ıiuü]n\s+pop[üu]ler\s+yemekleri\s+traditional\s+T[üu]rk\s+mutfa[ğg][ıi]ndan\s+gelmektedir[,.]?\s*especially\s+(.+?)\.?$",
                    r'The popular dishes come from traditional Turkish cuisine, especially \1.',
                    result.strip(), flags=re.IGNORECASE)
    # "Sultan Mehmet ..., manzaralı bir restoran olmadığı için teras is not available, but tarihi X and Y..."
    result = re.sub(r"[\w\s&'']+[,.]?\s*manzaral[ıi]\s+bir\s+restoran\s+olmad[ıi][ğg][ıi]\s+i[çc]in\s+teras\s+is\s+not\s+available[,.]?\s*but\s+(.+?)$",
                    r'No terrace or scenic view, but \1',
                    result, flags=re.IGNORECASE)
    # "Hayır, restoranın yakınında X gibi are notable nearby places." → "Nearby places include X."
    result = re.sub(r'[Hh]ay[ıi]r[,.]?\s*restoranın\s+yakınında\s+(.+?)\s+gibi\s+are\s+notable\s+nearby\s+places\.?',
                    r'Nearby notable places include \1.', result, flags=re.IGNORECASE)
    # "Evet," / "Hayır," before already-English sentence → strip Turkish prefix
    result = re.sub(r'^[Ee]vet[,\.]\s+(?=[a-z])', '', result)
    # "Evet, teras is nearby." → "Yes, there is a terrace."
    result = re.sub(r'[Ee]vet[,.]?\s*teras\s+is\s+nearby\.?', 'Yes, there is a terrace.', result, flags=re.IGNORECASE)
    # "Evet, deniz manzaralı bir teras is available." → "Yes, there is a terrace with sea view."
    result = re.sub(r'[Ee]vet[,.]?\s*deniz\s+manzaral[ıi]\s+bir\s+teras\s+is\s+available\.?', 'Yes, there is a sea-view terrace.', result, flags=re.IGNORECASE)
    # "Evet, büyük gruplar and özel günler için uygun bir yerdir." → "Yes, suitable for large groups and special occasions."
    result = re.sub(r'[Ee]vet[,.]?\s*b[üu]y[üu]k\s+gruplar\s+(?:and|ve)\s+[öo]zel\s+g[üu]nler\s+i[çc]in\s+uygun\s+bir\s+(?:yer|mekan)\.?',
                    'Yes, suitable for large groups and special occasions.', result, flags=re.IGNORECASE)
    # "Evet, doğum günü and özel günler için ideal bir yerdir." → "Yes, ideal for birthdays and special occasions."
    result = re.sub(r'[Ee]vet[,.]?\s*do[ğg]um\s+g[üu]n[üu]\s+(?:and|ve)\s+[öo]zel\s+g[üu]nler\s+i[çc]in\s+ideal\s+bir\s+(?:yer|mekan)\.?',
                    'Yes, ideal for birthdays and special occasions.', result, flags=re.IGNORECASE)
    # "Evet, büyük gruplar için ideal olan X, doğum günü partilerine also uygun bir yer."
    result = re.sub(r'[Ee]vet[,.]?\s*b[üu]y[üu]k\s+gruplar\s+i[çc]in\s+ideal\s+olan\s+\w[\w\s]+[,.]?\s*do[ğg]um\s+g[üu]n[üu]\s+partilerine\s+also\s+uygun\s+bir\s+yer\.?',
                    'Yes, ideal for large groups and also suitable for birthday events.', result, flags=re.IGNORECASE)
    # "Hayır, vegan seçeneği is not available." → "No, vegan options are not available."
    result = re.sub(r'[Hh]ay[ıi]r[,.]?\s*vegan\s+se[çc]ene[ğg]i\s+is\s+not\s+available\.?', 'No, vegan options are not available.', result, flags=re.IGNORECASE)
    # "Yes, family-friendly. bir restoran olarak bilinmektedir." → "Yes, family-friendly."
    result = re.sub(r'(Yes,\s+family-friendly)\.\s+bir\s+restoran\s+olarak\s+bilinmektedir\.?', r'\1.', result, flags=re.IGNORECASE)
    # "X gibi önemli landmarks..." → "Notable landmarks include X." (before nearby keywords are processed)
    result = re.sub(r'(.+?)\s+gibi\s+[öo]nemli\s+landmarklar\s+yak[ıi]n[ıi]nda\s+bulunan\s+restoranımız[^.]*\.',
                    r'Located near notable landmarks such as \1.', result, flags=re.IGNORECASE)
    # "tarihi X and Y gibi yakın yerlerin manzarasını görebilirsiniz." → "you can see nearby historic places like X and Y."
    result = re.sub(r'tarihi\s+(.+?)\s+gibi\s+yak[ıi]n\s+yerlerin\s+manzaras[ıi]n[ıi]\s+g[öo]rebilirsiniz\.?',
                    r'you can see nearby historic places like \1.', result, flags=re.IGNORECASE)
    # "Romantik ortamı and güzel manzarası, özel günler için ideal bir seçenektir." → "Its romantic atmosphere and beautiful view make it ideal for special occasions."
    result = re.sub(r'[Rr]omantik\s+ortam[ıi]\s+(?:and|ve)\s+g[üu]zel\s+manzaras[ıi][,.]?\s*[öo]zel\s+g[üu]nler\s+i[çc]in\s+ideal\s+bir\s+se[çc]enektir\.?',
                    'Its romantic atmosphere and beautiful view make it ideal for special occasions.', result, flags=re.IGNORECASE)
    # "Located in X neighborhood. yer alan [Name], keyifli bir deniz manzarası sunuyor."
    result = re.sub(r'(Located in \w[\w\s]+ neighborhood\.)\s+yer\s+alan\s+\w[\w\s&]+[,.]?\s*keyifli\s+bir\s+deniz\s+manzaras[ıi]\s+sunuyor\.?',
                    r'\1 A pleasant sea view is available.', result, flags=re.IGNORECASE)
    # "[Name], klasik Türk mutfağı ile donatılmış bir restoran." → "A restaurant featuring classic Turkish cuisine."
    result = re.sub(r'\w[\w\s&]+[,.]?\s*klasik\s+T[üu]rk\s+mutfa[ğg][ıi]\s+ile\s+donat[ıi]lm[ıi][şs]\s+bir\s+restoran\.?',
                    'A restaurant featuring classic Turkish cuisine.', result, flags=re.IGNORECASE)
    # "Anadolu mutfağından esinlenilmiş dishes sunuyor." → "Offers dishes inspired by Anatolian cuisine."
    result = re.sub(r'[Aa]nadolu\s+mutfa[ğg][ıi]ndan\s+esinlenilmi[şs]\s+dishes\s+sunuyor\.?',
                    'Offers dishes inspired by Anatolian cuisine.', result, flags=re.IGNORECASE)
    # "X bölgesinde Y var, but restoranın hemen yanında bir Y yok." → partial cleanup
    result = re.sub(r'but\s+restoranın\s+hemen\s+yan[ıi]nda\s+bir\s+\w+\s+yok\.?', 'but none immediately next to the restaurant.', result, flags=re.IGNORECASE)
    # "Yakındaki X bölgesinde Y var" → "There is Y in the nearby X area"
    result = re.sub(r'[Yy]ak[ıi]ndaki\s+(\w[\w\s]+)\s+b[öo]lgesinde\s+(\w[\w\s]+)\s+var[,.]?',
                    r'There is \2 in the nearby \1 area,', result, flags=re.IGNORECASE)
    # "Restoran, X bölgesinde bulunan tarihi and kültürel bir yer olan Y'nin yakınında yer almaktadır."
    result = re.sub(u'[Rr]estoran[,.]?\\s*\\w[\\w\\s]+b[\u00f6o]lgesinde\\s+bulunan\\s+tarihi\\s+(?:and|ve)\\s+k[\u00fcu]lt[\u00fcu]rel\\s+bir\\s+yer\\s+olan\\s+(.+?)[\u2019\']?nin\\s+yak[\\u0131i]n[\\u0131i]nda\\s+yer\\s+almaktad[\\u0131i]r\\.?',
                    r'Located near \1, a historic and cultural landmark.', result, flags=re.IGNORECASE)
    # "Gelik restoranı, çocuk dostu bir ortam sunuyor. Büyük gruplar için uygun olan restoranda..."
    result = re.sub(r'\w[\w\s]+restoran[ıi][,.]?\s*[çc]ocuk\s+dostu\s+bir\s+ortam\s+sunuyor\.\s*[Bb][üu]y[üu]k\s+gruplar\s+i[çc]in\s+uygun\s+olan\s+restoranda[^.]*\.',
                    'Child-friendly environment. Suitable for large groups.', result, flags=re.IGNORECASE)
    # "Gelik restoranı, Kazlıçeşme Mahallesi'nde bulunan bir restoran. Manzaralı bir restoran olan Gelik, X and Y..."
    result = re.sub(r'\w[\w\s]+restoran[ıi][,.]?\s*\w[\w\s]+[Mm]ahallesi\'nde\s+bulunan\s+bir\s+restoran\.\s*[Mm]anzaral[ıi]\s+bir\s+restoran\s+olan\s+\w[\w\s]+[,.]?\s*(.+?)\.?$',
                    r'A scenic restaurant. \1.', result.strip(), flags=re.IGNORECASE)
    # "Konyalı Restaurant'ın popüler yemekleri traditional ..."
    result = re.sub(r"[\w\s&'']+['']?[ıiuü]n\s+pop[üu]ler\s+yemekleri\s+traditional\s+(.+)$",
                    r'Traditional \1', result, flags=re.IGNORECASE)
    # "gibi landmarklar yakın" → "are nearby landmarks"
    result = re.sub(r'(.+?)\s+gibi\s+landmarklar\s+yak[ıi]n\.?',
                    r'\1 are nearby landmarks.', result, flags=re.IGNORECASE)
    # "istasyonları yakın" → "stations are nearby"
    result = re.sub(r'(.+?)\s+istasyonlar[ıi]\s+yak[ıi]n\.?',
                    r'\1 stations are nearby.', result, flags=re.IGNORECASE)
    result = re.sub(r'(.+?)\s+istasyonu\s+yak[ıi]n\.?',
                    r'\1 station is nearby.', result, flags=re.IGNORECASE)
    # "yakınlardadır" → "is nearby"
    result = re.sub(r'\byak[ıi]nlardad[ıi]r\.?', 'is nearby.', result, flags=re.IGNORECASE)
    # "X mutfak tarzında hizmet vermektedir." → "serves X cuisine."
    result = re.sub(r'(.+?)\s+mutfak\s+tarz[ıi]nda\s+hizmet\s+vermektedir\.?',
                    r'Serves \1 cuisine.', result, flags=re.IGNORECASE)
    result = re.sub(r'(.+?)\s+mutfak\s+tarz[ıi]nda\s+hizmet\s+veriyor\.?',
                    r'Serves \1 cuisine.', result, flags=re.IGNORECASE)
    # "önemli places is nearby" → "are notable nearby places"
    result = re.sub(r'[öo]nemli\s+places\s+is\s+nearby\.?', 'are notable nearby places.', result, flags=re.IGNORECASE)
    result = re.sub(r'(.+?)\s+[öo]nemli\s+places\s+is\s+nearby\.?',
                    r'\1 are notable nearby places.', result, flags=re.IGNORECASE)
    # "Evet, özel günler and organizasyon için uygun"
    result = re.sub(r'[Ee]vet[,.]?\s*[öo]zel\s+g[üu]nler\s+(?:and|ve)\s+organizasyon\s+i[çc]in\s+uygun\.?',
                    'Yes, suitable for special occasions and events.', result, flags=re.IGNORECASE)
    # "X ise N dakika away." / "X ise yakında"
    result = re.sub(r'\bise\s+(\d+)\s*dakika\s+away\.?', r'is \1 minutes away.', result, flags=re.IGNORECASE)
    result = re.sub(r'\bise\s+yak[ıi]nda\.?', 'is nearby.', result, flags=re.IGNORECASE)
    # "Evet, restoranın yakınında X is nearby."
    result = re.sub(r'[Ee]vet[,.]?\s*restoranın\s+yakınında\s+(.+?)\s+is\s+nearby\.?',
                    r'Yes, \1 is nearby.', result, flags=re.IGNORECASE)
    # "restoran ızgara and kebap style dishes are served" — mixed
    result = re.sub(r'^[Rr]estoran\s+', '', result)
    # "X yakınındayız. Y ise N dakika away."
    result = re.sub(r'yakınındayız\.', 'is nearby.', result, flags=re.IGNORECASE)
    # "sunuluyor" as suffix - "is available/served"
    result = re.sub(r'\bsunuluyor\b', 'is available', result, flags=re.IGNORECASE)
    # "sunmaktadır" / "sunmaktayız"
    result = re.sub(r'\bsunmaktad[ıi]r\b', 'is available', result, flags=re.IGNORECASE)
    result = re.sub(r'\bsunmaktay[ıi]z\b', 'we offer', result, flags=re.IGNORECASE)
    # "olarak bilinir" → "is known for"
    result = re.sub(r'\bolarak\s+bilinir\b', 'is known', result, flags=re.IGNORECASE)
    # "sunuyoruz" → "we offer" / "is available"
    result = re.sub(r'\bsunuyoruz\b', 'we offer', result, flags=re.IGNORECASE)
    # "mevcut" → "available"
    result = re.sub(r'\bmevcuttur\b', 'is available', result, flags=re.IGNORECASE)
    result = re.sub(r'\bmevcut\b(?!\s+(?:de[ğg]il|değil))', 'available', result, flags=re.IGNORECASE)
    # "bulunmamaktadır" → "is not available"
    result = re.sub(r'\bbulunmamaktad[ıi]r\b', 'is not available', result, flags=re.IGNORECASE)
    # "Located in Accessible via" double prefix fix
    result = re.sub(r'Located in ([\w\s]+) neighborhood — Accessible via', r'In \1 neighborhood, accessible via', result)
    # "Evet, özel günler and organizasyonlar için Reservations recommended. ve özel hizmet sunuyoruz."
    result = re.sub(r'[Ee]vet[,.]?\s*[öo]zel\s+g[üu]nler\s+(?:ve|and)\s+organizasyonlar\s+i[çc]in\s+Reservations recommended\.\s+(?:ve|and)\s+[öo]zel\s+hizmet\s+(?:sunuyoruz|we offer)\.?',
                    'Yes, reservations are recommended for special events. Custom services available.', result, flags=re.IGNORECASE)
    # "N min from X Mahallesi'nde bulunan restorana Y stop" → clean up partial transit
    result = re.sub(
        r'(\d+\s*min\s+from\s+)[\w\u00e7\u011f\u0131\u015f\u00f6\u015f\u00fc\u00c7\u011e\u0130\u00d6\u015e\u00dc\s\']+[Mm]ahallesi\'nde\s+bulunan\s+restorana\s+',
        r'\1',
        result, flags=re.IGNORECASE
    )
    # "X Mahallesi'nde, with a sea view." — neighborhood prefix for location answers
    result = re.sub(
        r"^([\w\u00e7\u011f\u0131\u015f\u00f6\u015f\u00fc\u00c7\u011e\u0130\u00d6\u015e\u00dc\s]+)[Mm]ahallesi'nde[,]?\s+",
        lambda m: f"Located in {m.group(1).strip()} neighborhood. ",
        result, flags=re.IGNORECASE
    )
    # "Kandilli Mahallesi'nde, vapur ile ..." - neighborhood transit combo
    result = re.sub(
        r"([A-Z\u00c7\u011e\u0130\u00d6\u015e\u00dc][a-zA-Z\u00e7\u011f\u0131\u015f\u00f6\u015f\u00fc\s]+?) [Mm]ahallesi'nde[,]?\s*vapur\s+ile\s+(.+?)\s+gibi\s+yerlere\s+yak[ıi]n\s+konumdad[ıi]r\.?",
        lambda m: f'Located in {m.group(1).strip()} neighborhood, conveniently close to ferry stops.',
        result, flags=re.IGNORECASE
    )

    # More Turkish structural words in partially-translated text
    result = re.sub(r'\bbelirtmektedir\b', 'is noted', result, flags=re.IGNORECASE)
    result = re.sub(r'\bbelirtiyor\b', 'notes', result, flags=re.IGNORECASE)
    result = re.sub(r'\bolduğunu\b', 'that it is', result, flags=re.IGNORECASE)
    result = re.sub(r'\boldukça\b', 'quite', result, flags=re.IGNORECASE)
    result = re.sub(r'\barasında\b', 'among', result, flags=re.IGNORECASE)
    result = re.sub(r'\bhakkında\b', 'about', result, flags=re.IGNORECASE)
    result = re.sub(r'\bnedeniyle\b', 'due to', result, flags=re.IGNORECASE)
    result = re.sub(r'\bkonusunda\b', 'regarding', result, flags=re.IGNORECASE)
    result = re.sub(r'\börneğin\b', 'for example', result, flags=re.IGNORECASE)
    result = re.sub(r'\bözellikle\b', 'especially', result, flags=re.IGNORECASE)
    result = re.sub(r'\bgenellikle\b', 'generally', result, flags=re.IGNORECASE)
    result = re.sub(r'\bhem\b(?=\s+\w)', 'both', result, flags=re.IGNORECASE)
    result = re.sub(r'\bde\b(?=\s+)', 'also', result, flags=re.IGNORECASE)
    result = re.sub(r'\bda\b(?=\s+)', 'also', result, flags=re.IGNORECASE)
    result = re.sub(r'\bönerilir\b', 'is recommended', result, flags=re.IGNORECASE)
    result = re.sub(r'\btercih\s+edilebilir\b', 'can be preferred', result, flags=re.IGNORECASE)
    result = re.sub(r'\btercih\s+edilir\b', 'is preferred', result, flags=re.IGNORECASE)
    result = re.sub(r'\bsunulmaktad[ıi]r\b', 'is served', result, flags=re.IGNORECASE)
    result = re.sub(r'\bmevcut\s+de[ğg]ildir\b', 'is not available', result, flags=re.IGNORECASE)
    result = re.sub(r'\byap[ıi]labilir\b', 'can be done', result, flags=re.IGNORECASE)
    result = re.sub(r'\bay[ıi]rtabilirsiniz\b', 'can be reserved', result, flags=re.IGNORECASE)
    result = re.sub(r'\bsahiptir\b', 'has', result, flags=re.IGNORECASE)
    result = re.sub(r'\bgöre\b', 'based on', result, flags=re.IGNORECASE)
    result = re.sub(r'\b[üu]cretli\b', 'paid', result, flags=re.IGNORECASE)
    result = re.sub(r'\b[üu]cretsiz\b', 'free', result, flags=re.IGNORECASE)
    result = re.sub(r'\bher\s+hafta\b', 'every week', result, flags=re.IGNORECASE)
    result = re.sub(r'\bhafta\s+i[çc]i\b', 'on weekdays', result, flags=re.IGNORECASE)
    result = re.sub(r'\bhafta\s+sonu\b', 'on weekends', result, flags=re.IGNORECASE)
    result = re.sub(r'\bkalabal[ıi]k\b', 'busy', result, flags=re.IGNORECASE)
    result = re.sub(r'\bkonuma\b', 'location', result, flags=re.IGNORECASE)
    result = re.sub(r'\bs[ıi]n[ıi]rl[ıi]\b', 'limited', result, flags=re.IGNORECASE)
    result = re.sub(r'\blezzetleri\b', 'flavors', result, flags=re.IGNORECASE)
    result = re.sub(r'\byerler\b', 'places', result, flags=re.IGNORECASE)
    result = re.sub(r'\bsaatlerinde\b', 'hours', result, flags=re.IGNORECASE)
    result = re.sub(r'\btaze\b', 'fresh', result, flags=re.IGNORECASE)
    result = re.sub(r'\bs[ıi]cak\s+ve\s+samimi\b', 'warm and welcoming', result, flags=re.IGNORECASE)
    result = re.sub(r'\bsamimi\b', 'welcoming', result, flags=re.IGNORECASE)
    result = re.sub(r'\brezervasyon\b', 'reservation', result, flags=re.IGNORECASE)
    result = re.sub(r'\b[öo]nceden\b', 'in advance', result, flags=re.IGNORECASE)

    # "ve" → "and" inside already-English answers (landmark lists, etc.)
    result = re.sub(r'\b ve \b', ' and ', result)
    # "genellikle en pahalı yemeklerden biridir" - price description
    result = re.sub(r'(.+?),\s*genellikle\s+en\s+pahal[ıi]\s+yemeklerden\s+biridir\.?',
                    lambda m: f'{m.group(1).strip()} is typically one of the pricier dishes.', result, flags=re.IGNORECASE)

    # Fix partial answer messes from iterative processing
    result = re.sub(r'Reservations recommended\.\s+(?:and|ve)\s+[öo]zel\s+hizmet\s+(?:sunuyoruz|we offer)\.?',
                    'Reservations are recommended, and special services are available.', result, flags=re.IGNORECASE)
    result = re.sub(r'Yes,\s+(?:child-friendly|family-friendly)\.\s+bir\s+ortam\s+(?:sunar|sunuyor|we offer)\.?',
                    'Yes, child-friendly.', result, flags=re.IGNORECASE)
    result = re.sub(r'\bEvét[,.]?\s+(?:but|ancak)\s+[çc]ocuk\s+dostu\s+bir\s+ortam\s+de[ğg]il\.?',
                    'Yes, but not specifically child-friendly.', result, flags=re.IGNORECASE)
    result = re.sub(r'[Ee]vet[,.]?\s+but\s+[çc]ocuk\s+dostu\s+bir\s+ortam\s+de[ğg]il\.?',
                    'Yes, but not specifically child-friendly.', result, flags=re.IGNORECASE)
    result = re.sub(r'\b(?:bir\s+)?ortam\s+de[ğg]il\.?$', 'not suitable.', result, flags=re.IGNORECASE)
    result = re.sub(r'\b(?:bir\s+)?ortam\s+sunar?\.?$', 'is available.', result, flags=re.IGNORECASE)
    result = re.sub(r'\b(?:bir\s+)?ortam\s+(?:we offer|sunuyoruz|sunmaktadır)\.?', 'atmosphere.', result, flags=re.IGNORECASE)
    # "Türk mutfağı we offer and manzaralı bir restauranız." type mess
    result = re.sub(r'T[üu]rk\s+mutfa[ğg][ıi]\s+we offer\b', 'We offer Turkish cuisine', result, flags=re.IGNORECASE)
    result = re.sub(r'manzaral[ıi]\s+bir\s+(?:restoran[ıi]z|mekan[ıi]z)\.?', 'a restaurant with a view.', result, flags=re.IGNORECASE)
    # "Evet, özel günler and organizasyon için uygun" → "Yes, suitable for special occasions and events."
    result = re.sub(r'[Ee]vet[,.]?\s+[öo]zel\s+g[üu]nler(?:/organizasyon)?\s+i[çc]in\s+uygun\.?',
                    'Yes, suitable for special occasions.', result, flags=re.IGNORECASE)
    # "Italiano Pizza, lezzetli bir pizza seçeneğimizdir." → "Italiano Pizza is a delicious pizza option."
    result = re.sub(r'(.+?),\s+lezzetli\s+bir\s+([a-zA-Z]+)\s+se[çc]ene[ğg]imizdir\.?',
                    lambda m: f'{m.group(1)} is a delicious {m.group(2)} option.',
                    result, flags=re.IGNORECASE)
    # "X, özel günler için özel menü and hizmetler sunuyor."
    result = re.sub(r'[öo]zel\s+g[üu]nler\s+i[çc]in\s+[öo]zel\s+men[üu]\s+(?:and|ve)\s+hizmetler\s+(?:sunuyor|we offer)\.?',
                    'special menus and services are available for special occasions.', result, flags=re.IGNORECASE)
    # Parking limited answer
    result = re.sub(r'[Oo]topark\s+kapasitesi\s+restoran[ıi]n\s+konumu\s+(?:and|ve)\s+[çc]evresine\s+g[öo]re\s+s[ıi]n[ıi]rl[ıi]d[ıi]r[^.]*\.',
                    'Parking capacity is limited; we recommend reserving a spot in advance.', result, flags=re.IGNORECASE)
    # "... deniz manzaralı bir konumda" location suffix
    result = re.sub(r',\s+deniz\s+manzaral[ıi]\s+bir\s+konumda\.?$', ', with a sea view.', result, flags=re.IGNORECASE)
    result = re.sub(r',\s+manzaral[ıi]\s+bir\s+konumda\.?$', ', with a scenic view.', result, flags=re.IGNORECASE)
    # "Üzgünüz, X'e özel teras and manzarası yok."
    result = re.sub(r'[Üü]zg[üu]n[üu]z[,.]?\s*.+?\s+(?:teras|manzara)[ıi]\s+yok\.?',
                    'Unfortunately, there is no terrace or scenic view at this restaurant.', result, flags=re.IGNORECASE)
    # "[Name], özel doğum günü organizasyonları için özel menü and hizmetler sunuyor."
    result = re.sub(r'[öo]zel\s+do[ğg]um\s+g[üu]n[üu]\s+organizasyonlar[ıi]\s+i[çc]in\s+[öo]zel\s+men[üu]\s+(?:and|ve)\s+hizmetler\s+(?:sunuyor|we offer|sunar)\.?',
                    'special menus and services are available for birthday events.', result, flags=re.IGNORECASE)
    # "X style dishes sunan bir mutfak tarzına sahiptir."
    result = re.sub(r'style\s+dishes\s+sunan\s+bir\s+mutfak\s+tarz[ıi]na\s+sahiptir\.?',
                    'style dishes are served.', result, flags=re.IGNORECASE)
    # Vapur/transit answer with partial Turkish
    result = re.sub(r"([A-Z\u00c7\u011e\u0130\u00d6\u015e\u00dc][a-zA-Z\u00e7\u011f\u0131\u015f\u00f6\u015f\u00fc']+)'ne\s+vapur\s+ile\s+(\d+)\s+dakika",
                    lambda m: f'{m.group(2)} min by ferry to {m.group(1)}',
                    result, flags=re.IGNORECASE)
    result = re.sub(r"'ya\s+tramvay[a-zA-Z]*\s+(\d+)\s+dakika",
                    lambda m: f'{m.group(1)} min by tram',
                    result, flags=re.IGNORECASE)

    # Common Turkish conjunctions/words left in partial translations
    result = re.sub(r'\bancak\b', 'but', result, flags=re.IGNORECASE)
    result = re.sub(r'\bve\s+(?=\w)', 'and ', result, flags=re.IGNORECASE)
    result = re.sub(r'\bgibi\s+yak[ıi]ndaki\s+mekanlar(?:\s+ile)?\b', 'and other nearby venues', result, flags=re.IGNORECASE)
    result = re.sub(r'\bgeleneksel\b', 'traditional', result, flags=re.IGNORECASE)
    result = re.sub(r'\btarz[ıi]\b', 'style', result, flags=re.IGNORECASE)
    result = re.sub(r'\byemekler\b', 'dishes', result, flags=re.IGNORECASE)
    result = re.sub(r'\bolanak\s+sa[ğg]l[ıi]yor\.?', 'possible.', result, flags=re.IGNORECASE)
    # Double period cleanup
    result = re.sub(r'\.\.+', '.', result)

    # Trailing leftover Turkish words after partial translation
    result = re.sub(r'\s+var\.$', '.', result)        # "... are among the popular dishes. var."
    result = re.sub(r'\s+var\b\s*$', '.', result)
    result = re.sub(r'\s+de\s+bulunabilir\.?$', '.', result)   # "... de bulunabilir."
    result = re.sub(r'(?<=stop)\s*uzakl[ıi]ktad[ıi]r', '', result, flags=re.IGNORECASE)  # "stopuzaklıktadır"
    result = re.sub(r'(?<=stop)\s*uzakl[ıi]ktas[ıi]n[ıi]z', '', result, flags=re.IGNORECASE)
    result = re.sub(r'\.tur\.', '.', result)           # "No vegan options available.tur."
    result = re.sub(r'\.tur$', '.', result)
    # "bir yeriz" leftover
    result = re.sub(r'\s+bir\s+yeriz\.?$', '.', result)
    # "olan restoranda keyifli ..." leftover after partial translation
    result = re.sub(r'\s+olan\s+restoranda\s+[a-zA-ZÇĞİÖŞÜçğışöşü\s]+?\.$', '.', result, flags=re.IGNORECASE)
    # "restoranda" as prefix before English
    result = re.sub(r'^[Rr]estoranda\s+(?=[A-Z])', '', result)
    # "Kişi başı yaklaşık ~X TL per person." — double-translated price
    result = re.sub(r'[Kk]i[şs]i\s*ba[şs][ıi]\s*yakla[şs][ıi]k\s*', '', result)
    result = re.sub(r'[Kk]i[şs]i\s*ba[şs][ıi]\s*~', '~', result)
    # "restoranda are the most popular dishes" → "are the most popular dishes"
    result = re.sub(r'\brestoranda\b\s+(?=are\b|is\b)', '', result, flags=re.IGNORECASE)
    # "are among the popular dishes.i" leftover suffix
    result = re.sub(r'(dishes)\.[ıiuü]\s', r'\1. ', result, flags=re.IGNORECASE)
    result = re.sub(r'(dishes)\.[ıiuü]$', r'\1.', result, flags=re.IGNORECASE)
    # "ile Osmanlı'nın lezzetini sunuyor" type suffixes after partial translation
    result = re.sub(r"\s+ile\s+[A-Z\u00c7\u011e\u0130\u00d6\u015e\u00dc][a-zA-Z\u00e7\u011f\u0131\u015f\u00f6\u015f\u00fc'\u2019]+\s+lezzetini\s+sunuyor\.?$", '.', result, flags=re.IGNORECASE)

    # Nearby landmarks answer — "X, Y ve Z gibi landmark'lar yakınında."
    result = re.sub(
        r'[Ee]vet[,.]?\s*(.+?)\s*(?:gibi\s*)?(?:landmark(?:\'lar)?|kültürel\s*merkezler?|tarihi\s*yerler?|m[üu]ze(?:ler)?|camii?(?:ler)?)\s*(?:restoranın|yakınında|yak[ıi]n[ıi]nda)\s*bulunmaktad[ıi]r\.?',
        lambda m: f'Yes, located near {m.group(1).strip()} and other landmarks.',
        result, flags=re.IGNORECASE
    )
    # "X, Y ve Z gibi landmark'lar yakınında." (no Evet prefix)
    result = re.sub(
        r'(.+?)\s+(?:ve\s+.+?)\s+gibi\s+landmark\'?lar[ıi]?\s+yak[ıi]n[ıi]nda\.?',
        lambda m: f'Located near landmarks including {m.group(0).split(" gibi")[0].strip()}.',
        result, flags=re.IGNORECASE
    )
    result = re.sub(
        r'(.+?)\s+gibi\s+landmark\'?lar[ıi]?\s+yak[ıi]n[ıi]nda\.?',
        lambda m: f'Located near landmarks such as {m.group(1).strip()}.',
        result, flags=re.IGNORECASE
    )
    result = re.sub(r'\bbulunmaktad[ıi]r\b', 'is nearby', result, flags=re.IGNORECASE)
    result = re.sub(r'\byak[ıi]n[ıi]nda\s*bulunmaktad[ıi]r\b', 'is nearby', result, flags=re.IGNORECASE)

    # Popular dishes: "X, Y gibi popüler yemekler."
    result = re.sub(
        r'(.+?)\s+gibi\s+pop[üu]ler\s+yemekler(?:imiz)?\.?',
        lambda m: f'{m.group(1).strip()} are among the popular dishes.',
        result, flags=re.IGNORECASE
    )

    # Children / families answer variations
    result = re.sub(r'[Ee]vet[,.]?\s*[çc]ocuklar\s*ve\s*aileler\s*i[çc]in\s*uygun\s*bir\s*ortam\.?', 'Yes, suitable for children and families.', result)
    result = re.sub(r'[Ee]vet[,.]?\s*[çc]ocuklar\s*ve\s*aileler\s*i[çc]in\s*uygun\.?', 'Yes, suitable for children and families.', result)
    result = re.sub(r'[Ee]vet[,.]?\s*aile(?:ler)?\s*ve\s*[çc]ocuklar\s*i[çc]in\s*uygun\.?', 'Yes, suitable for families and children.', result)

    # Special events / occasions answer
    result = re.sub(r'[Ee]vet[,.]?\s*[öo]zel\s*g[üu]nler\s*ve\s*organizasyonlar\s*i[çc]in\s*uygun\.?', 'Yes, suitable for special occasions and events.', result)
    result = re.sub(r'[Ee]vet[,.]?\s*[öo]zel\s*g[üu]nler\s*i[çc]in\s*uygun\.?', 'Yes, suitable for special occasions.', result)

    # Neighborhood location description answers
    result = re.sub(
        r'([A-ZÇĞİÖŞÜ][a-zA-ZÇĞİÖŞÜçğışöşü\s]+?)\s+mahallesinde[^.]*,?\s*gece\s*boyunca\s*a[çc][ıi]k\s*olan\s*bir\s*restoran\.?',
        lambda m: f'Located in {m.group(1).strip()} neighborhood, open throughout the night.',
        result, flags=re.IGNORECASE
    )
    result = re.sub(
        r'([A-ZÇĞİÖŞÜ][a-zA-ZÇĞİÖŞÜçğışöşü\s]+?)\s+mahallesinde[^.]*bir\s*restoran\.?',
        lambda m: f'Located in the {m.group(1).strip()} neighborhood.',
        result, flags=re.IGNORECASE
    )

    # Terrace-specific answers
    # "[Name]'ta terasınızda keyifli bir yemek deneyimi yaşayabilir, X and Y gibi yerlere yakın..."
    result = re.sub(
        r"[\w\u00c7\u011e\u0130\u00d6\u015e\u00dc\u00e7\u011f\u0131\u00f6\u015f\u00fc'\u2019']+\s*(?:'[tndaki]+\s+)?teras[ıi]nızda\s+keyifli\s+bir\s+yemek\s+deneyimi\s+yaşayabilir[^.]*\.",
        'You can enjoy a pleasant dining experience on the terrace.',
        result, flags=re.IGNORECASE
    )
    result = re.sub(
        r"teras[ıi]nızda\s+keyifli\s+bir\s+yemek\s+deneyimi\s+yaşayabilirsiniz[^.]*\.",
        'You can enjoy a pleasant dining experience on the terrace.',
        result, flags=re.IGNORECASE
    )
    result = re.sub(
        r"teras[ıi]m[ıi]zda\s+keyifli\s+bir\s+(?:yemek\s+)?deneyim[^.]*\.",
        'You can enjoy a pleasant experience on our terrace.',
        result, flags=re.IGNORECASE
    )
    result = re.sub(
        r"teras[ıi]nda\s+keyifli\s+bir\s+(?:yemek\s+)?deneyim[^.]*\.",
        'You can enjoy a pleasant dining experience on the terrace.',
        result, flags=re.IGNORECASE
    )
    result = re.sub(
        r"[A-Za-zÇĞİÖŞÜçğışöşü']+\s+'?da\s+teras\s+bulunmamaktad[ıi]r[^.]*\.",
        'No, there is no terrace at this restaurant.',
        result, flags=re.IGNORECASE
    )

    # Nightlife connection answer
    result = re.sub(r'gece\s*hayat[ıi]\s*(?:ile\s*)?(?:yak[ıi]ndan\s*)?ili[şs]kili\s*(?:bir\s*)?(?:restoran|mekan)\.?',
                    'a venue closely tied to the nightlife scene.', result, flags=re.IGNORECASE)
    result = re.sub(r'gece\s*hayat[ıi]\s*severler\s*i[çc]in\s*ideal\s*bir\s*tercih\.?',
                    'an ideal choice for nightlife enthusiasts.', result, flags=re.IGNORECASE)

    # "uzaklıkta" without -dır (appears after partial transit translation)
    result = re.sub(r'\s*uzakl[ıi]kta\b', '', result, flags=re.IGNORECASE)
    result = re.sub(r'\s*uzakl[ıi]ktas[ıi]n[ıi]z\b', '', result, flags=re.IGNORECASE)
    # "is nearby.lardadır." leftover suffix
    result = re.sub(r'(is nearby)\.?lardad[ıi]r\.?', r'\1.', result, flags=re.IGNORECASE)
    # "ızgara" → "Grilled" (common Turkish cooking method)
    result = re.sub(r'\b[ıi]zgara\b', 'grilled', result, flags=re.IGNORECASE)
    result = re.sub(r'^[Gg]rilled\b', 'Grilled', result)
    # "Üzgünüz, X'a özel terası and manzarası yok."
    result = re.sub(
        u'[\u00dc\u00fc]zg[\u00fc u]n[\u00fc u]z[,.]?\\s*.+?[\u2019\']?a\\s+[\u00f6o]zel\\s+teras[\u0131i]\\s+(?:and|ve)\\s+manzaras[\u0131i]\\s+yok\\.?',
        'Unfortunately, there is no terrace or scenic view at this restaurant.',
        result, flags=re.IGNORECASE
    )

    # "[Name and Y] gibi yerlere yakın bir konumda bulunacaksınız." Turkish remnant
    result = re.sub(
        r',?\s+[\w\u00e7\u011f\u0131\u00f6\u015f\u00fc\s]+gibi\s+yerlere\s+yak[ıi]n\s+bir\s+konumda\s+bulunacaks[ıi]n[ıi]z\.?',
        '.', result, flags=re.IGNORECASE
    )
    # "... gibi yerlere yakın konumdadır." remnant
    result = re.sub(
        r',?\s+[\w\u00e7\u011f\u0131\u00f6\u015f\u00fc\s]+gibi\s+yerlere\s+yak[ıi]n\s+konumdad[ıi]r\.?',
        '.', result, flags=re.IGNORECASE
    )

    # Trailing mixed Turkish remnants after partial translation
    result = re.sub(r'\s*\.\s*$', '.', result.strip())

    # Cleanup: "Hayır, <already-english>" — strip leading Hayır/Evet if followed by English sentence
    result = re.sub(r'^[Hh]ay[ıi]r[,\.]\s+(?=[A-Z])', '', result)
    result = re.sub(r'^[Ee]vet[,\.]\s+(?=[A-Z])', '', result)

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
