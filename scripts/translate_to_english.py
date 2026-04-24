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
    # Dietary / allergy
    (r"[Dd]iyet[/,\s]*alerji\s+se[çc]ene[ğg]i\s+var\s*m[ıi]", "Are there dietary/allergy options?"),
    (r"[Dd]iyet[/,\s]*alerji\s+se[çc]enekleri\s+nelerdir", "What are the dietary/allergy options?"),
    (r"[Dd]iyet\s+se[çc]enekleri\s+var\s*m[ıi]", "Are there dietary options?"),
    (r"[Vv]egan\s+veya\s+diyet\s+yemek(?:leri)?\s+var\s*m[ıi]", "Are there vegan or dietary options?"),
    (r"[Vv]egan\s+veya\s+diyet\s+se[çc]enekleri\s+var\s*m[ıi]", "Are there vegan or dietary options?"),
    (r"[Vv]egan[/,]\s*vejeteryan\s+se[çc]enekleri\s+var\s*m[ıi]", "Are there vegan/vegetarian options?"),
    (r"[Vv]egan\s+yemek\s+se[çc]ene[ğg]i\s+var\s*m[ıi]", "Are there vegan options?"),
    # Popular dishes
    (r"[Nn]eler\s+pop[üu]ler", "What are the popular dishes?"),
    (r"[Hh]angi\s+yemekler\s+pop[üu]ler", "Which dishes are popular?"),
    (r"[Nn]eler\s+tavsiye\s+edilir", "What is recommended?"),
    (r"[Nn]eler\s+t[üu]ketebilirim", "What can I eat here?"),
    # Opening hours / late night
    (r"[Gg]e[çc]\s+saatlere\s+kadar\s+a[çc][ıi]k\s*m[ıi]s[ıi]n[ıi]z", "Are you open until late?"),
    (r"[Gg]e[çc]\s+saatlere\s+kadar\s+a[çc][ıi]k\s*m[ıi]y[ıi]z", "Is it open until late?"),
    (r"[Gg]ece\s+saatlerinde\s+a[çc][ıi]k\s*m[ıi]", "Is it open late at night?"),
    # Large groups
    (r"[Bb][üu]y[üu]k\s+gruplar\s+i[çc]in\s+uygun\s*mu", "Is it suitable for large groups?"),
    (r"[Bb][üu]y[üu]k\s+grup\s+i[çc]in\s+uygun\s+alan", "Is there a suitable area for large groups?"),
    (r"[Gg]ruplar\s+i[çc]in\s+uygun\s*mu", "Is it suitable for groups?"),
    # Romantic atmosphere
    (r"[Rr]estoranda\s+romantik\s+bir\s+atmosfer\s+var\s*m[ıi]", "Is there a romantic atmosphere at the restaurant?"),
    (r"[Rr]estoran\s+romantik\s+mi", "Is the restaurant romantic?"),
    # Children and families
    (r"[Rr]estoranda\s+[çc]ocuklar\s+ve\s+aileler\s+i[çc]in\s+uygun", "Is the restaurant child and family-friendly?"),
    (r"[Çç]ocuklar\s+i[çc]in\s+uygun\s+mu[yz]", "Is it suitable for children?"),
    (r"[Çç]ocuklar\s+i[çc]in\s+[öo]zel\s+men[üu]\s+var\s*m[ıi]", "Is there a special children's menu?"),
    (r"[Aa]ileler\s+i[çc]in\s+[öo]zel\s+[çc]ocuk\s+yemek", "Is there a special children's menu for families?"),
    # Special occasions
    (r"[Oo]zel\s+gunler?\s+veya\s+organizasyon(?:lar)?\s+i[çc]in\s+uygun\s*mu", "Is it suitable for special occasions?"),
    (r"[Dd]o[ğg]um\s+g[üu]n[üu]\s+organizasyon(?:u)?\s+i[çc]in\s+uygun\s*mu", "Is it suitable for a birthday party?"),
    (r"[Dd]o[ğg]um\s+g[üu]n[üu]\s+organizasyon(?:u)?\s+yapabilir\s+misiniz", "Can you organize a birthday party?"),
    (r"[Dd]o[ğg]um\s+g[üu]n[üu]\s+organizasyon(?:u)?\s+yapabilir\s+miyiz", "Can we have a birthday party?"),
    # Location advantages
    (r"[Rr]estoranın\s+konumunda\s+ne\s+gibi\s+avantajlar\s+var", "What are the location advantages?"),
    (r"[Rr]estoranın\s+konumu\s+ne\s+kadar\s+avantajlı", "How convenient is the restaurant's location?"),
    # Reservation
    (r"[Rr]ezervasyon\s+gerektirir\s*mi", "Is reservation required?"),
    # Credit card
    (r"[Kk]redi\s+kart[ıi]\s+ge[çc]iyor\s*mu", "Is credit card accepted?"),
    (r"[Kk]redi\s+kart[ıi]\s+kabul\s+edilir\s*mi", "Is credit card accepted?"),
    # View
    (r"[Mm]anzaral[ıi]\s*m[ıi]", "Is there a view?"),
    # Why visit
    (r"[Nn]eden\s+bu\s+restorana\s+gitmeliyim", "Why should I visit this restaurant?"),
    # Special menu
    (r"[öo]zel\s+bir\s+men[üu]s[üu]\s+var\s*m[ıi]", "Is there a special menu?"),
    # Private room
    (r"[öo]zel\s+bir\s+odas[ıi]\s+var\s*m[ıi]", "Is there a private room?"),
    # Friend group
    (r"bir\s+grup\s+arkada[şs]\s+i[çc]in\s+uygun\s*mu", "Is it suitable for a group of friends?"),
    # Nearby ferry
    (r"[Yy]ak[ıi]n\s+bir\s+vapur\s+istasyon", "Is there a nearby ferry station?"),
    # Address / location
    (r"adresi?\s+nerede", "What is the address?"),
    (r"lokasyon(?:u)?\s+nerede", "Where is the location?"),
    (r"konumu?\s+nerede", "Where is it located?"),
    # Opening hours
    (r"[Aa][çc][ıi]l[ıi][şs]\s+saatleri?\s+ne", "What are the opening hours?"),
    (r"[Gg]e[çc]\s+saatlere\s+kadar\s+a[çc][ıi]k\s*m[ıi]", "Is it open until late?"),
    # Bring own drinks
    (r"[Dd][ıi][şs]ar[ıi]dan\s+i[çc]ecek\s+getirilebilir\s*mi", "Can we bring our own drinks?"),
    # Music
    (r"hangi\s+m[üu]zikler\s+[çc]al[ıi]n[ıi]yor", "What music is played at the restaurant?"),
    # Atmosphere / ambiance
    (r"[Rr]estoran[ıi]n\s+atmosferi\s+ne", "What is the restaurant's atmosphere like?"),
    (r"[Rr]estoran[ıi]n\s+atmosferi\s+nas[ıi]l", "What is the restaurant's atmosphere like?"),
    (r"[Aa]tmosferi?\s+ne\s+gibi", "What is the atmosphere like?"),
    # View from terrace
    (r"teras[ıi]nda\s+ne\s+gibi\s+manzara", "What views are available on the terrace?"),
    # Romantic
    (r"[Rr]omantik\s+bir\s+yer\s*mi", "Is it a romantic place?"),
    (r"[Rr]estoran\s+romantik\s+bir\s+atmosfer\s+sunuyor\s*mu", "Does the restaurant offer a romantic atmosphere?"),
    # Cuisine type
    (r"mutfak\s+t[üu]r[üu]n[üu]\s+[öo][ğg]renebilir\s+miyim", "Can I learn about the restaurant's cuisine?"),
    (r"mutfak\s+t[üu]r[üu]\s+nedir", "What is the restaurant's cuisine type?"),
    # Birthday
    (r"[Dd]o[ğg]um\s+g[üu]n[üu]\s+i[çc]in\s+uygun\s+bir\s+yer\s*mi", "Is it suitable for a birthday?"),
    # Families and children
    (r"[Aa]ileler\s+ve\s+[çc]ocuklar\s+i[çc]in\s+uygun\s+m[üu]", "Is it suitable for families and children?"),
    (r"[çc]ocuklar\s+i[çc]in\s+uygun\s+muyuz", "Is it suitable for children?"),
    # Special events service
    (r"[Öo]zel\s+g[üu]nler\s+(?:ve\s+organizasyonlar\s+)?i[çc]in\s+(?:hizmet\s+veriyorsunuz|organizasyon\s+yapabilir\s+miyiz)", "Do you provide service for special occasions?"),
    (r"[Öo]zel\s+g[üu]nler\s+i[çc]in\s+organizasyon\s+yapabilir\s+miyiz", "Can we organize special events?"),
    # How to get there
    (r"[Nn]ereden\s+gelebilirim", "How can I get there?"),
    (r"[Nn]erden\s+gelebiliriz", "How can we get there?"),
    # Distance to landmark
    (r"ne\s+kadar\s+uzakl[ıi]kta", "How far is it?"),
    # Location
    (r"[Nn]erede\s+yer\s+al[ıi]yor", "Where is it located?"),
    (r"[Rr]estoran[ıi]n\s+konumu\s+ne(?:\s*\?)$", "What is the restaurant's location?"),
    (r"[Rr]estoran[ıi]n\s+manzaras[ıi]\s+nas[ıi]l", "What is the restaurant's view like?"),
    # Nearby
    (r"[Rr]estoran[ıi]n\s+yak[ıi]nlar[ıi]nda\s+ne\s+var", "What is near the restaurant?"),
    # Broad restaurant-name + Turkish question patterns
    (r"'[ıiuü]n?\s+(?:manzaras[ıi]|konumu|atmosferi|teras[ıi])\s+nas[ıi]l", "What is it like?"),
    (r"'[na]\s+(?:yakın|ne\s+kadar\s+uzakl)", "How far is it?"),
    # How is X prepared
    (r"nas[ıi]l\s+haz[ıi]rlan[ıi]r", "How is it prepared?"),
    # Which types / groups
    (r"hangi\s+t[üu]r\s+gruplar\s+uygun", "What types of groups is it suitable for?"),
    (r"hangi\s+t[üu]r\s+(?:yemek|lezzet)", "What kind of food is served?"),
    (r"hangi\s+yemekler\s+(?:daha\s+)?uygun", "Which dishes are recommended?"),
    (r"hangi\s+yemekler\s+geleneksel", "Which dishes are traditional?"),
    (r"hangi\s+mutfak\s+t[üu]r[üu]", "What cuisine types are available?"),
    # What options/alternatives
    (r"ne\s+gibi\s+(?:se[çc]enek|alternatif)\s+(?:var|sunmakta)", "What options are available?"),
    (r"ne\s+gibi\s+avantajlar\s+var", "What advantages are there?"),
    (r"ne\s+gibi\s+(?:hizmet|[öo]zellik)\s+(?:sunuyor|var)", "What services are offered?"),
    (r"ne\s+gibi\s+imk[âa]nlar\s+var", "What facilities are available?"),
    # Night out options
    (r"gece\s+keyfi\s+i[çc]in\s+ne\s+gibi", "What options are available for a night out?"),
    # Dinner suitable
    (r"[Gg]ece\s+yeme[ğg]i\s+i[çc]in\s+uygun\s+m[üu]", "Is it suitable for dinner?"),
    # How far
    (r"ne\s+kadar\s+mesafede", "How far is it?"),
    (r"ne\s+kadar\s+uzakta", "How far is it?"),
    # Where are you located
    (r"[Nn]erede\s+bulunuyor(?:sunuz)?", "Where are you located?"),
    # Nearest landmark question
    (r"yak[ıi]n[ıi]nda\s+m[ıi]", "Is it nearby?"),
    # What children advantages
    (r"[çc]ocuklar\s+i[çc]in\s+ne\s+gibi\s+avantajlar", "What advantages are there for children?"),
    # Neler var (what is available)
    (r"[çc]ocuklar[/,]?\s*aileler\s+i[çc]in\s+neler\s+var", "What is available for children/families?"),
    (r"i[çc]in\s+neler\s+var\s*\?", "What is available?"),
    # Cuisine related
    (r"geleneksel\s+T[üu]rk\s+mutfa[ğg][ıi]ndan", "Which dishes are traditional Turkish cuisine?"),
    (r"mutfak\s+t[üu]r[üu]n[üu]n\s+yan[ıi]\s+s[ıi]ra", "Besides the cuisine type, what else is there?"),
    (r"mutfak\s+t[üu]r[üu]ne?\s+g[öo]re", "According to the cuisine type,"),
    # Catch-all: anything still in Turkish with common endings
    (r"nelerdir\s*\?$", "What are the options?"),
    (r"var\s+m[ıi]\s*\?$", "Is it available?"),
    (r"uygun\s+mu[yz]?\s*\?$", "Is it suitable?"),
    (r"uygun\s+m[üu]\s*\?$", "Is it suitable?"),
    (r"m[ıi]s[ıi]n[ıi]z\s*\?$", "Is that the case?"),
    (r"mudur\s*\?$", "Is it so?"),
    (r"midir\s*\?$", "Is it so?"),
    (r"nas[ıi]l\s*\?$", "What is it like?"),
    (r"nedir\s*\?$", "What is it?"),
    (r"neler\s*\?$", "What is available?"),
    (r"hangisi\s*\?$", "Which one?"),
    (r"hangisidir\s*\?$", "Which one is it?"),
    (r"ne\s*\?$", "What is it?"),
    (r"m[ıiuü]\s*\?$", "Is it available?"),
    (r"sunuyor\s+mu\s*\?$", "Is it offered?"),
    (r"sunmaktad[ıi]r\s*\?$", "Is it offered?"),
    (r"var\s*\?$", "Is it available?"),
    (r"nereden\s*\?$", "Where from?"),
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
    # "sunmuyor/sunmamaktadır" variants
    result = re.sub(r'\bsunmamaktad[ıi]r\b', 'does not offer', result, flags=re.IGNORECASE)
    result = re.sub(r'\bsunmuyor\b', 'does not offer', result, flags=re.IGNORECASE)
    result = re.sub(r'\boluşmaktad[ıi]r\b', 'consists of', result, flags=re.IGNORECASE)
    result = re.sub(r'\bodaklanmaktad[ıi]r\b', 'focuses on', result, flags=re.IGNORECASE)
    result = re.sub(r'\balmaktad[ıi]r\b', 'receives', result, flags=re.IGNORECASE)
    result = re.sub(r'\byararlanalamaz\b', 'cannot use', result, flags=re.IGNORECASE)
    result = re.sub(r'\byararlan[ıi]lamamaktad[ıi]r\b', 'cannot be used', result, flags=re.IGNORECASE)
    result = re.sub(r'\bcanlı\b', 'live', result, flags=re.IGNORECASE)
    result = re.sub(r'\bkarakteristik\b', 'characteristic', result, flags=re.IGNORECASE)
    result = re.sub(r'\balan[ıi]nda\b', 'in the field of', result, flags=re.IGNORECASE)
    result = re.sub(r'\bmutfa[ğg][ıi]na\b', 'cuisine', result, flags=re.IGNORECASE)
    result = re.sub(r'\bikisi\s+de\b', 'both', result, flags=re.IGNORECASE)
    result = re.sub(r'\bikisi\b', 'both', result, flags=re.IGNORECASE)
    result = re.sub(r'\byemeyin\b', "don't eat", result, flags=re.IGNORECASE)
    result = re.sub(r'\bsahip\b', 'has', result, flags=re.IGNORECASE)
    result = re.sub(r'\byak[ıi]nlardaki\b', 'nearby', result, flags=re.IGNORECASE)
    result = re.sub(r'\bhat(?:lar[ıi]ndan|lar[ıi])\b', 'lines', result, flags=re.IGNORECASE)
    # General "sunmuyoruz" → "not available"
    result = re.sub(r'\bWi-?Fi\s+(?:service\s+)?sunmuyoruz\.?', 'Wi-Fi is not available.', result, flags=re.IGNORECASE)
    result = re.sub(r'\bWi-?Fi\s+(?:service\s+)?sunulmamaktad[ıi]r\.?', 'Wi-Fi is not available.', result, flags=re.IGNORECASE)
    result = re.sub(r'\bWi-?Fi\s+(?:service\s+)?verilmemektedir\.?', 'Wi-Fi is not available.', result, flags=re.IGNORECASE)
    result = re.sub(r'\b[Oo]topark\s+(?:service\s+)?sunmuyoruz\.?', 'Parking is not available.', result, flags=re.IGNORECASE)
    result = re.sub(r'\b[Oo]topark\s+(?:service\s+)?sunulmamaktad[ıi]r\.?', 'Parking is not available.', result, flags=re.IGNORECASE)
    result = re.sub(r'\b[Oo]topark\s+(?:service\s+)?verilmemektedir\.?', 'Parking is not available.', result, flags=re.IGNORECASE)
    result = re.sub(r'\b([Çç]ocuk\s+dostu\s+bir\s+atmosphere)\s+sunmuyoruz\.?', 'We do not offer a child-friendly atmosphere.', result)
    result = re.sub(r'\b(romantic\s+an?\s+atmosphere)\s+sunmuyoruz\.?', 'We do not offer a romantic atmosphere.', result, flags=re.IGNORECASE)
    result = re.sub(r'\b(\w[\w\s]*?)\s+sunmuyoruz\.?', r'\1 is not available.', result, flags=re.IGNORECASE)
    result = re.sub(r'\b(\w[\w\s]*?)\s+sunulmamaktad[ıi]r\.?', r'\1 is not available.', result, flags=re.IGNORECASE)
    result = re.sub(r'\b(\w[\w\s]*?)\s+verilmemektedir\.?', r'\1 is not provided.', result, flags=re.IGNORECASE)
    # "bulunmuyor" → "is not available" / "there is no"
    result = re.sub(r'\bteras\s+bulunmuyor\.?', 'There is no terrace.', result, flags=re.IGNORECASE)
    result = re.sub(r'\b(\w[\w\s]*?)\s+bulunmuyor\.?', r'There is no \1.', result, flags=re.IGNORECASE)
    result = re.sub(r'bulunmuyor\b', 'is not available', result, flags=re.IGNORECASE)
    # "bulunmaktadır" → "is available"
    result = re.sub(r'bulunmaktad[ıi]r\b', 'is available', result, flags=re.IGNORECASE)
    # "yapılmamaktadır" → "is not arranged"
    result = re.sub(r'yap[ıi]lmamaktad[ıi]r\b', 'is not arranged', result, flags=re.IGNORECASE)
    # "konumlanmaktadır" → "is located"
    result = re.sub(r'konumlanmaktad[ıi]r\b', 'is located', result, flags=re.IGNORECASE)
    # "tanınmaktadır" → "is known"
    result = re.sub(r'tan[ıi]nmaktad[ıi]r\b', 'is known', result, flags=re.IGNORECASE)
    # "tavsiye ediyoruz" → "we recommend"
    result = re.sub(r'tavsiye\s+ediyoruz\b', 'we recommend', result, flags=re.IGNORECASE)
    # "uzaklıktayız" stuck to previous word (e.g. "stopuzaklıktayız") → ". [X] away."
    result = re.sub(r'(\w+)uzakl[ıi]ktay[ıi]z\.?', r'\1.', result, flags=re.IGNORECASE)
    result = re.sub(r'\buzakl[ıi]ktay[ıi]z\b', 'away', result, flags=re.IGNORECASE)
    # "durağından X minutes" → "stop, X minutes"
    result = re.sub(r'\s+dura[ğg][ıi]ndan\s+(\d+)\s*(min|minutes|dakika)', r' stop, \1 \2', result, flags=re.IGNORECASE)
    result = re.sub(r'\s+dura[ğg][ıi]ndan\b', ' stop,', result, flags=re.IGNORECASE)
    result = re.sub(r'\btramvay\s+dura[ğg][ıi]ndan\b', 'tram stop,', result, flags=re.IGNORECASE)
    result = re.sub(r'\bmarmaray\s+dura[ğg][ıi]ndan\b', 'Marmaray stop,', result, flags=re.IGNORECASE)

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

    # ── Transit phrase patterns ────────────────────────────────────────────
    # "X ile N dakika içinde ulaşılabilir." → "Accessible by X in N minutes."
    result = re.sub(
        r'([Mm]etro|[Tt]ramvay|[Vv]apur|[Mm]armaray|[Oo]töbüs|[Mm]inibüs|[Ff]erry)\s+ile\s+(\d+(?:[-–]\d+)?)\s*dakika\s+i[çc]inde\s+ula[şs][ıi]labilir\.?',
        lambda m: f'Accessible by {m.group(1).lower()} in {m.group(2)} minutes.',
        result, flags=re.IGNORECASE
    )
    # "vapur ile N dakika içinde ulaşılabilir" (already caught above) - also vapur without "ile"
    result = re.sub(r'vapur\s+ile\s+(\d+)\s*dakika', r'by ferry in \1 minutes', result, flags=re.IGNORECASE)
    result = re.sub(r',\s+ile\s+ula[şs][ıi]labilir\.?', ' are accessible from here.', result, flags=re.IGNORECASE)
    result = re.sub(r'\s+ile\s+ula[şs][ıi]labilir\.?', ' is accessible.', result, flags=re.IGNORECASE)
    # "N dakika mesafede." → "N minutes away."
    result = re.sub(r'\b(\d+(?:[-–]\d+)?)\s*(?:dakika|dk)\s+mesafede\.?', r'\1 minutes away.', result, flags=re.IGNORECASE)
    result = re.sub(r'\b(\d+)\s*(?:dakika|dk)\s+(?:i[çc]inde|uzakl[ıi][ğg][ıi]nda)\.?', r'\1 minutes away.', result, flags=re.IGNORECASE)
    # "N dakika and M dakika mesafede." → "N and M minutes away."
    result = re.sub(r'\b(\d+)\s*(?:dakika|dk)\s+and\s+(\d+)\s*(?:dakika|dk)\s+mesafede\.?', r'\1 and \2 minutes away.', result, flags=re.IGNORECASE)
    # "X metro istasyonuna N dakika" / "Y metro istasyonuna M dakika bulunmaktayız"
    # "bulunmaktayız" → "we are located"
    result = re.sub(r'\bbulunmaktay[ıi]z\b', 'we are located', result, flags=re.IGNORECASE)

    # ── Location answer patterns ───────────────────────────────────────────
    # "X Mahallesi'ndedir and ..." → "Located in X neighborhood and ..."
    result = re.sub(
        r"^([A-Z\u00c7\u011e\u0130\u00d6\u015e\u00dc][a-zA-Z\u00e7\u011f\u0131\u015f\u00f6\u015f\u00fc\s]+?)[Mm]ahallesi'ndedir\s+(?:and|ve)\s+",
        lambda m: f'Located in {m.group(1).strip()} neighborhood, and ',
        result, flags=re.IGNORECASE
    )
    # "X gibi yerlere yakın konumdadır." → "conveniently located near X and similar places."
    result = re.sub(
        r'(.+?)\s+gibi\s+yerlere\s+yak[ıi]n\s+konumdad[ıi]r\.?',
        lambda m: f'Conveniently located near {m.group(1).strip()} and similar places.',
        result, flags=re.IGNORECASE
    )
    # "X gibi önemli landmarklara yakın" → "near X and other notable landmarks"
    result = re.sub(
        r'(.+?)\s+gibi\s+[öo]nemli\s+landmarklara\s+yak[ıi]n\.?',
        lambda m: f'Near notable landmarks such as {m.group(1).strip()}.',
        result, flags=re.IGNORECASE
    )
    # "Located in X neighborhood. vapur ile N dakika içinde ulaşılabilir."
    result = re.sub(
        r'(Located in \w[\w\s]+ neighborhood\.)\s+vapur\s+ile\s+(\d+)\s*dakika\s+i[çc]inde\s+ula[şs][ıi]labilir\.?',
        lambda m: f'{m.group(1)} Accessible by ferry in {m.group(2)} minutes.',
        result, flags=re.IGNORECASE
    )
    # "X tramvay durağı yakınında, tramvay ile N dakika içinde ulaşılabilir."
    result = re.sub(
        r'([A-Z\u00c7\u011e\u0130\u00d6\u015e\u00dc][a-zA-Z\u00e7\u011f\u0131\u015f\u00f6\u015f\u00fc\s]+?)\s+tramvay\s+dura[ğg][ıi]\s+yak[ıi]n[ıi]nda[,.]?\s*tramvay\s+ile\s+(\d+)\s*dakika\s+i[çc]inde\s+ula[şs][ıi]labilir\.?',
        lambda m: f'{m.group(2)} min by tram from {m.group(1).strip()} tram stop.',
        result, flags=re.IGNORECASE
    )
    # "X Mahallesi'ndedir and tramvay ile Y gibi yerlere yakın konumdadır."
    result = re.sub(
        r"([A-Z\u00c7\u011e\u0130\u00d6\u015e\u00dc][a-zA-Z\u00e7\u011f\u0131\u015f\u00f6\u015f\u00fc\s]+?)[Mm]ahallesi'ndedir\s+and\s+tramvay\s+ile\s+(.+?)\s+gibi\s+yerlere\s+yak[ıi]n\s+konumdad[ıi]r\.?",
        lambda m: f'Located in {m.group(1).strip()} neighborhood, near {m.group(2).strip()} by tram.',
        result, flags=re.IGNORECASE
    )

    # ── Dishes / cuisine patterns ──────────────────────────────────────────
    # "X gibi dishes is available." → "X are available."
    result = re.sub(r'(.+?)\s+gibi\s+dishes\s+is\s+available\.?', r'\1 and similar dishes are available.', result, flags=re.IGNORECASE)
    # "X gibi lezzetli dishes we offer." → "X and more are available."
    result = re.sub(r'(.+?)\s+gibi\s+lezzetli\s+dishes\s+(?:we\s+offer|sunuluyor|is\s+available)\.?', r'\1 and more are available.', result, flags=re.IGNORECASE)
    # "Yes, child-friendly. ortam." → "Yes, child-friendly."
    result = re.sub(r'(Yes,\s+(?:child-friendly|family-friendly))\.\s+ortam\.?', r'\1.', result, flags=re.IGNORECASE)
    # "bir restoran olarak bilinmektedir." trailing suffix
    result = re.sub(r'\s+bir\s+restoran\s+olarak\s+bilinmektedir\.?$', '.', result, flags=re.IGNORECASE)
    # "bir yerdir." trailing suffix
    result = re.sub(r'\s+bir\s+(?:yer|mekan|restoran)\.?$', '.', result, flags=re.IGNORECASE)
    # "Restoranın adı X olduğu için, ..." → strip prefix
    result = re.sub(r'[Rr]estoranın\s+adı\s+\w[\w\s]+\s+oldu[ğg]u\s+için[,.]?\s*', '', result, flags=re.IGNORECASE)
    # "uygun bir yer olarak görülmektedir." → "is considered a suitable venue."
    result = re.sub(r'uygun\s+bir\s+yer\s+olarak\s+g[öo]r[üu]lmektedir\.?', 'is considered a suitable venue.', result, flags=re.IGNORECASE)
    # "büyük gruplar and özel günler için uygun bir yerdir." (lowercase start = mid-sentence)
    result = re.sub(r'^b[üu]y[üu]k\s+gruplar\s+(?:and|ve)\s+[öo]zel\s+g[üu]nler\s+i[çc]in\s+uygun\s+bir\s+(?:yer|mekan)\.?$',
                    'Suitable for large groups and special occasions.', result.strip(), flags=re.IGNORECASE)
    result = re.sub(r'^do[ğg]um\s+g[üu]n[üu]\s+(?:and|ve)\s+[öo]zel\s+g[üu]nler\s+i[çc]in\s+ideal\s+bir\s+(?:yer|mekan)\.?$',
                    'Ideal for birthdays and special occasions.', result.strip(), flags=re.IGNORECASE)
    # "büyük gruplar için ideal olan X, doğum günü partilerine also uygun bir yer." → caught above but catch lowercase
    result = re.sub(r'^b[üu]y[üu]k\s+gruplar\s+i[çc]in\s+ideal\s+olan\s+\w[\w\s]+[,.]?\s*do[ğg]um\s+g[üu]n[üu]\s+partilerine\s+also\s+uygun\s+bir\s+yer\.?$',
                    'Ideal for large groups and birthday events.', result.strip(), flags=re.IGNORECASE)
    # "Evet, Çiya Kebap 2 restoranı özel günler and organizasyonlar için ideal bir seçenek. Romantik and manzaralı terası ile misafirlerinizi ağırlayabilirsiniz."
    result = re.sub(
        r'[Ee]vet[,.]?\s*\w[\w\s&2]+\s+restoranı\s+[öo]zel\s+g[üu]nler\s+(?:and|ve)\s+organizasyonlar\s+i[çc]in\s+ideal\s+bir\s+se[çc]enek\.\s*[Rr]omantik\s+(?:and|ve)\s+manzaral[ıi]\s+teras[ıi]\s+ile\s+misafirlerinizi\s+a[ğg][ıi]rlayabilirsiniz\.?',
        'Yes, ideal for special occasions and events. The romantic terrace with scenic views is perfect for hosting guests.',
        result, flags=re.IGNORECASE
    )
    # "formal kıyafetli misafirleri kabul ediyor." → "Formally dressed guests are welcome."
    result = re.sub(r'formal\s+k[ıi]yafetli\s+misafirleri\s+kabul\s+ediyor\.?', 'Formally dressed guests are welcome.', result, flags=re.IGNORECASE)
    # "Türk Mutfağı'nın zengin lezzetlerini sunuyor" → "serves the rich flavors of Turkish cuisine"
    result = re.sub(r"T[üu]rk\s+[Mm]utfa[ğg][ıi]['']?n[ıi]n\s+zengin\s+lezzetlerini\s+sunuyor\.?",
                    'serves the rich flavors of Turkish cuisine.', result, flags=re.IGNORECASE)
    # "Kadıköy Şehremaneti and X gibi tarihi landmarklar yakınındadır" → "near historic landmarks like X"
    result = re.sub(r'(.+?)\s+gibi\s+tarihi\s+landmarklar\s+yak[ıi]n[ıi]ndad[ıi]r\.?',
                    lambda m: f'Near historic landmarks such as {m.group(1).strip()}.', result, flags=re.IGNORECASE)
    # "gece keyfini en iyi şekilde yaşayabileceğiniz bir yer" → "a great place for a night out"
    result = re.sub(r'gece\s+keyfini\s+en\s+iyi\s+[şs]ekilde\s+ya[şs]ayabilece[ğg]iniz\s+bir\s+yer\.?',
                    'a great place for a night out.', result, flags=re.IGNORECASE)
    # "Gece saatine kadar açık olan restoranda, Türk mutfağından lezzetli dishes..."
    result = re.sub(
        r'[Gg]ece\s+saatine\s+kadar\s+a[çc][ıi]k\s+olan\s+restoranda[,.]?\s*T[üu]rk\s+mutfa[ğg][ıi]ndan\s+lezzetli\s+',
        'Open late. Delicious ', result, flags=re.IGNORECASE
    )
    # "A scenic restaurant. X and Y gibi yakın landmark'lara sahip."
    result = re.sub(
        r'(.+?)\s+gibi\s+yak[ıi]n\s+landmark[\'\u2019]?lara\s+sahip\.?',
        lambda m: f'Near landmarks such as {m.group(1).strip()}.', result, flags=re.IGNORECASE
    )
    # "Located in X neighborhood. Accessible via Marmaray hattı ile Y or Z istasyonlarından"
    result = re.sub(r'Marmaray\s+hatt[ıi]\s+ile\s+', 'via Marmaray from ', result, flags=re.IGNORECASE)
    # "X or Y istasyonlarından" → "X or Y stations"
    result = re.sub(r'(\w[\w\s]+)\s+istasyonlar[ıi]ndan\.?', r'\1 stations.', result, flags=re.IGNORECASE)
    # "ortam." as trailing word → remove
    result = re.sub(r'\.\s+ortam\.$', '.', result, flags=re.IGNORECASE)
    result = re.sub(r'\s+ortam\.$', '.', result, flags=re.IGNORECASE)
    # "Evet, Çiya Kebap 2 restoranı..." catch remaining restaurant name + Turkish
    result = re.sub(r'[Ee]vet[,.]?\s*\w[\w\s&\d]+restoran[ıi]\s+', 'Yes, this restaurant ', result, flags=re.IGNORECASE)

    # ── More specific answer patterns ─────────────────────────────────────
    # "X gibi lezzetlerimiz vardır." → "X are available dishes."
    result = re.sub(r'(.+?)\s+gibi\s+lezzetlerimiz\s+vard[ıi]r\.?', r'\1 are available.', result, flags=re.IGNORECASE)
    # "Evet, N minutes away. ulaşılabilir." → strip trailing Turkish
    result = re.sub(r'(\d+\s+minutes?\s+away)\.\s+ula[şs][ıi]labilir\.?', r'\1.', result, flags=re.IGNORECASE)
    # "geç saate kadar açıkız." → "We are open until late."
    result = re.sub(r'^ge[çc]\s+saate?\s+kadar\s+a[çc][ıi]k[ıi]z\.?$', 'We are open until late.', result.strip(), flags=re.IGNORECASE)
    # "b[üu]y[üu]k gruplar için reservation yapabilirsiniz." → "Reservations for large groups can be made."
    result = re.sub(r'b[üu]y[üu]k\s+gruplar\s+i[çc]in\s+reservation\s+yapabilirsiniz\.?',
                    'Reservations for large groups can be made.', result, flags=re.IGNORECASE)
    # "yer almaktadır" → "is located"
    result = re.sub(r'\byer\s+almaktad[ıi]r\b', 'is located', result, flags=re.IGNORECASE)
    # "X restoranı regional mutfak türüdür." → "A regional cuisine restaurant."
    result = re.sub(r'\w[\w\s]+restoranı\s+regional\s+mutfak\s+t[üu]r[üu]d[üu]r\.?',
                    'A regional cuisine restaurant.', result, flags=re.IGNORECASE)
    result = re.sub(r'regional\s+mutfak\s+t[üu]r[üu]d[üu]r\.?', 'serves regional cuisine.', result, flags=re.IGNORECASE)
    # "restorana yakın bir yerdir." → "is near the restaurant."
    result = re.sub(r'restorana\s+yak[ıi]n\s+bir\s+(?:yer|mekan)\.?', 'is near the restaurant.', result, flags=re.IGNORECASE)
    # "ile ulaşabilirsiniz." → "are accessible."
    result = re.sub(r'\s+ile\s+ula[şs]abilirsiniz\.?', ' are accessible.', result, flags=re.IGNORECASE)
    # "Evet, X restorana yakın bir yerdir." → "Yes, X is near the restaurant."
    result = re.sub(r'[Ee]vet[,.]?\s*(.+?)\s+restorana\s+yak[ıi]n\s+bir\s+(?:yer|mekan)\.?',
                    r'Yes, \1 is near the restaurant.', result, flags=re.IGNORECASE)
    # "Restoran, büyük gruplar için reservation önermektedir..." → "The restaurant recommends reservations for large groups."
    result = re.sub(r'[Rr]estoran[,.]?\s*b[üu]y[üu]k\s+gruplar\s+i[çc]in\s+reservation\s+[öo]nermektedir[^.]*\.',
                    'The restaurant recommends reservations for large groups.', result, flags=re.IGNORECASE)
    # "X neighborhood'nin güvenli and pleasant bir bölgesindedir" → "in a safe and pleasant area"
    result = re.sub(r"neighborhood[''\u2019]?[ıi]?nin\s+g[üu]venli\s+and\s+pleasant\s+bir\s+b[öo]lgesindedir\.?",
                    'neighborhood, in a safe and pleasant area.', result, flags=re.IGNORECASE)
    # "etinin lezzetiyle and sunumuyla müşterilerin beğenisini kazanmaktadır." → strip
    result = re.sub(r'[,.]?\s*etinin\s+lezzetiyle\s+and\s+sunumuyla\s+m[üu][şs]terilerin\s+be[ğg]enisini\s+kazanmaktad[ıi]r\.?',
                    '.', result, flags=re.IGNORECASE)
    # "Restoran'ın en is one of the popular dishes., " → strip "Restoran'ın en"
    result = re.sub(r"[Rr]estoran[''\u2019]?[ıi]n\s+en\s+(?=is\s+one\s+of)", '', result, flags=re.IGNORECASE)
    # "., " double punctuation cleanup
    result = re.sub(r'\.,\s+', '. ', result)
    # "Yakın landmark olarak X (N min) is nearby." → "Nearby landmark: X (N min)."
    result = re.sub(r'[Yy]ak[ıi]n\s+landmark\s+olarak\s+(.+?)\s+is\s+nearby\.?',
                    r'Nearby landmark: \1.', result, flags=re.IGNORECASE)
    # "Located in X neighborhood. yer almaktadır." → clean double location
    result = re.sub(r'(Located in \w[\w\s]+ neighborhood\.)\s+(?:yer\s+almaktad[ıi]r|bulunmaktad[ıi]r)\.?',
                    r'\1', result, flags=re.IGNORECASE)
    # "büyük gruplar ideal for olan X, birthday events also uygun." → catch-all
    result = re.sub(r'b[üu]y[üu]k\s+gruplar\s+ideal\s+for\s+(?:olan\s+)?\w[\w\s]+[,.]?\s*birthday\s+events\s+also\s+uygun\.?',
                    'Ideal for large groups and birthday events.', result, flags=re.IGNORECASE)
    # "Gece yemeği suitable for olan restoran, X neighborhood'nin..." → catch
    result = re.sub(r'[Gg]ece\s+yeme[ğg]i\s+suitable\s+for\s+(?:olan\s+)?restoran[,.]?\s*',
                    'Suitable for dinner. ', result, flags=re.IGNORECASE)
    # "müşterilerin ihtiyaçları karşılanmakta and daha iyi bir ... deneyimi" → strip
    result = re.sub(r',?\s+bu\s+sayede\s+m[üu][şs]terilerin\s+ihtiya[çc]lar[ıi]\s+kar[şs][ıi]lanmakta[^.]*\.',
                    '.', result, flags=re.IGNORECASE)
    # "Karaköy tramvay (3 min), Kadıköy and Üsküdar İskelesi vapur (3 min), Karaköy vapur (5 min) ile ulaşabilirsiniz."
    result = re.sub(r'(.+?)\s+ile\s+ula[şs]abilirsiniz\.?', r'Accessible via \1.', result, flags=re.IGNORECASE)
    # "doğum gününüzü unutulmaz kılacaktır." → "will make your birthday unforgettable."
    result = re.sub(r'do[ğg]um\s+g[üu]n[üu]n[üu]z[üu]\s+unutulmaz\s+k[ıi]lacakt[ıi]r\.?',
                    'will make your birthday unforgettable.', result, flags=re.IGNORECASE)
    # "İmroz'un romantic ortamı and fresh balık flavors" → "İmroz's romantic atmosphere and fresh fish flavors"
    result = re.sub(r"([\w'\u2019]+)'?un\s+romantic\s+ortam[ıi]\s+and\s+fresh\s+(\w+)\s+flavors",
                    r"\1's romantic atmosphere and fresh \2 flavors", result, flags=re.IGNORECASE)
    # "ortamı" → "atmosphere" (safe, distinct suffix)
    result = re.sub(r'\bortam[ıi]\b', 'atmosphere', result, flags=re.IGNORECASE)
    result = re.sub(r'\bortam\b', 'atmosphere', result, flags=re.IGNORECASE)
    # "X ve Y" between Turkish landmark names → keep "and"
    result = re.sub(r'\s+ve\s+(?=[A-Z\u00c7\u011e\u0130\u00d6\u015e\u00dc])', ' and ', result)
    # "müşterilerin" → "customers'"
    result = re.sub(r'm[üu][şs]terilerin\b', "customers'", result, flags=re.IGNORECASE)
    # "Azcı restoranı regional mutfak türüdür." already handled above
    # "t[üu]r[üu]d[üu]r" → "type"
    result = re.sub(r'\bt[üu]r[üu]d[üu]r\.?', 'type.', result, flags=re.IGNORECASE)
    # "vard[ıi]r" → "are available"
    result = re.sub(r'\bvard[ıi]r\.?', 'are available.', result, flags=re.IGNORECASE)
    # "önermektedir" → "recommends"
    result = re.sub(r'\b[öo]nermektedir\b', 'recommends', result, flags=re.IGNORECASE)
    # "kar[şs][ıi]lanmakta" → "are met"
    result = re.sub(r'\bkar[şs][ıi]lanmakta\b', 'are met', result, flags=re.IGNORECASE)
    # ".dir" leftover suffix from "yakın bir yerdir" → strip
    result = re.sub(r'(is nearby|is near the restaurant|is near the hotel|is located)\.?dir\.?', r'\1.', result, flags=re.IGNORECASE)
    result = re.sub(r'(is nearby|is near|is located)\b\.?$', r'\1.', result.strip(), flags=re.IGNORECASE)
    # "Evet, children/families suitable for." → "Yes, suitable for children and families."
    result = re.sub(r'[Ee]vet[,.]?\s*children/?families\s+suitable\s+for\.?', 'Yes, suitable for children and families.', result, flags=re.IGNORECASE)
    # "Evet, X saatleri among açıkız." → "Yes, open from X."
    result = re.sub(r'[Ee]vet[,.]?\s*([\d:]+[-–][\d:]+)\s+saatleri\s+among\s+a[çc][ıi]k[ıi]z\.?',
                    r'Yes, open \1.', result, flags=re.IGNORECASE)
    # "saatleri among açıkız" / "saatleri arasında açıkız"
    result = re.sub(r'saatleri\s+(?:among|aras[ıi]nda)\s+a[çc][ıi]k[ıi]z\.?', 'open.', result, flags=re.IGNORECASE)
    # "X gibi klasik Yunan yemeklerini deneyebileceğiniz için gideyim." → "to try classic Greek dishes like X."
    result = re.sub(r'(.+?)\s+gibi\s+klasik\s+Yunan\s+yemeklerini\s+deneyebilece[ğg]iniz\s+i[çc]in\s+gideyim\.?',
                    r'You should visit to try classic Greek dishes like \1.', result, flags=re.IGNORECASE)
    # "X gibi historic yerlere yakın bir is located." → "Located near historic places like X."
    result = re.sub(r'(.+?)\s+gibi\s+historic\s+yerlere\s+yak[ıi]n\s+bir\s+is\s+located\.?',
                    r'Located near historic places like \1.', result, flags=re.IGNORECASE)
    # "Gece yemeği suitable for olan X, büyük gruplar için also özel/special services sunabilir/can offer." → combined
    result = re.sub(r'[Gg]ece\s+yeme[ğg]i\s+suitable\s+for\s+(?:olan\s+)?[\w\s&]+[,.]?\s*b[üu]y[üu]k\s+gruplar\s+i[çc]in\s+also\s+(?:[öo]zel|special)\s+services\s+(?:sunabilir|can\s+offer)\.?',
                    'Suitable for dinner. Can offer special services for large groups.', result, flags=re.IGNORECASE)
    # "Osmanlı İmparatorluğu'nun kültürünü yansıtan unique bir deneyim sunan bir restoran." → "A restaurant offering a unique experience reflecting Ottoman culture."
    result = re.sub(r"Osmanl[ıi]\s+[İi]mparatorlu[ğg]u[''\u2019]?nun\s+k[üu]lt[üu]r[üu]n[üu]\s+yans[ıi]tan\s+unique\s+bir\s+deneyim\s+sunan\s+bir\s+restoran\.?",
                    'A restaurant offering a unique experience reflecting Ottoman culture.', result, flags=re.IGNORECASE)
    # "bir is located." cleanup
    result = re.sub(r'\bbir\s+is\s+located\.?', 'is located.', result, flags=re.IGNORECASE)
    # "also özel" → "also special"
    result = re.sub(r'\balso\s+[öo]zel\b', 'also special', result, flags=re.IGNORECASE)
    # "sunabilir" → "can offer"
    result = re.sub(r'\bsunabilir\b', 'can offer', result, flags=re.IGNORECASE)
    # "deneyebileceğiniz için" → "so you can try"
    result = re.sub(r'\bdeneyebilece[ğg]iniz\s+i[çc]in\b', 'so you can try', result, flags=re.IGNORECASE)
    # "deneyebilirsiniz" → "you can try"
    result = re.sub(r'\bdeneyebilirsiniz\b', 'you can try', result, flags=re.IGNORECASE)
    # "gibi klasik" → "classic ... like"  -- word order fix
    result = re.sub(r'(.+?)\s+gibi\s+klasik\s+(\w[\w\s]+)\s+yemekleri?\b',
                    r'classic \2 dishes like \1', result, flags=re.IGNORECASE)
    # "X yemekleri deneyebilirsiniz" → "you can try X dishes"
    result = re.sub(r'(\w[\w\s]+)\s+yemekleri\s+deneyebilirsiniz\.?', r'you can try \1 dishes.', result, flags=re.IGNORECASE)
    # "kültürünü yansıtan" → "reflecting the culture of"
    result = re.sub(r"k[üu]lt[üu]r[üu]n[üu]\s+yans[ıi]tan\b", 'reflecting the culture of', result, flags=re.IGNORECASE)
    # ── Safe word-level Turkish fallback translations ──────────────────────
    # Only distinct Turkish words that won't match English text
    result = re.sub(r'\bveya\b', 'or', result, flags=re.IGNORECASE)
    result = re.sub(r'\bancak\b(?=\s)', 'however', result, flags=re.IGNORECASE)
    result = re.sub(r'\bfakat\b(?=\s)', 'but', result, flags=re.IGNORECASE)
    result = re.sub(r'\b[çc][üu]nk[üu]\b', 'because', result, flags=re.IGNORECASE)
    result = re.sub(r'\borganizasyon\b', 'event', result, flags=re.IGNORECASE)
    result = re.sub(r'\borganizasyonlar[ıi]?\b', 'events', result, flags=re.IGNORECASE)
    result = re.sub(r'\bdo[ğg]um\s+g[üu]n[üu]\b', 'birthday', result, flags=re.IGNORECASE)
    result = re.sub(r'\b[öo]zel\s+g[üu]nleri?\b', 'special occasions', result, flags=re.IGNORECASE)
    result = re.sub(r'\b[öo]zel\s+g[üu]n\b', 'special occasion', result, flags=re.IGNORECASE)
    result = re.sub(r'\b[çc]ocuklar\b', 'children', result, flags=re.IGNORECASE)
    result = re.sub(r'\baileler\b', 'families', result, flags=re.IGNORECASE)
    result = re.sub(r'\bmisafirler[ıi]?\b', 'guests', result, flags=re.IGNORECASE)
    result = re.sub(r'\bhizmetler\b', 'services', result, flags=re.IGNORECASE)
    result = re.sub(r'\bhizmet\s+vermektedir\b', 'provides service', result, flags=re.IGNORECASE)
    result = re.sub(r'\bhizmet\s+sunmaktad[ıi]r\b', 'provides service', result, flags=re.IGNORECASE)
    result = re.sub(r'\bkabul\s+edebilir\b', 'can accommodate', result, flags=re.IGNORECASE)
    result = re.sub(r'\ba[ğg][ıi]rlayabilirsiniz\b', 'you can host', result, flags=re.IGNORECASE)
    result = re.sub(r'\ba[ğg][ıi]rlayabiliriz\b', 'we can host', result, flags=re.IGNORECASE)
    result = re.sub(r'\byap[ıi]labilmektedir\b', 'can be organized', result, flags=re.IGNORECASE)
    result = re.sub(r'\bgörebilirsiniz\b', 'you can see', result, flags=re.IGNORECASE)
    result = re.sub(r'\bdeneyimleyebilirsiniz\b', 'you can experience', result, flags=re.IGNORECASE)
    result = re.sub(r'\blistelenmi[şs]tir\b', 'is listed', result, flags=re.IGNORECASE)
    result = re.sub(r'\bzen[ğg]in\b', 'rich', result, flags=re.IGNORECASE)
    result = re.sub(r'\besinlenilmi[şs]\b', 'inspired', result, flags=re.IGNORECASE)
    result = re.sub(r'\besinlenilerek\b', 'inspired by', result, flags=re.IGNORECASE)
    result = re.sub(r'\bgeleneksel\b', 'traditional', result, flags=re.IGNORECASE)
    result = re.sub(r'\bkeyifli\b', 'pleasant', result, flags=re.IGNORECASE)
    result = re.sub(r'\byap[ıi]l[ıi]labilmektedir\b', 'can be organized', result, flags=re.IGNORECASE)
    result = re.sub(r'\b[öo]nerilir\b', 'is recommended', result, flags=re.IGNORECASE)
    result = re.sub(r'\bolmaktad[ıi]r\b', 'is', result, flags=re.IGNORECASE)
    result = re.sub(r'\bolmad[ıi][ğg][ıi]\s+i[çc]in\b', 'as there is no', result, flags=re.IGNORECASE)
    result = re.sub(r'\b[üu]niversitesi\b', 'University', result, flags=re.IGNORECASE)
    result = re.sub(r'\bsa[ğg]lar\b', 'provides', result, flags=re.IGNORECASE)
    result = re.sub(r'\bk[ıi]yafetli\b', 'dressed', result, flags=re.IGNORECASE)
    result = re.sub(r'\bromantik\b', 'romantic', result, flags=re.IGNORECASE)
    result = re.sub(r'\blezzetli\b', 'delicious', result, flags=re.IGNORECASE)
    result = re.sub(r'\bmanzaral[ıi]\b', 'scenic', result, flags=re.IGNORECASE)
    result = re.sub(r'\b[Gg][üu]zel\b', 'beautiful', result, flags=re.IGNORECASE)
    result = re.sub(r'\btarihi\b', 'historic', result, flags=re.IGNORECASE)
    result = re.sub(r'\bk[üu]lt[üu]rel\b', 'cultural', result, flags=re.IGNORECASE)
    result = re.sub(r'\bbo[ğg]az\b(?!\s*\w*köp)', 'Bosphorus', result, flags=re.IGNORECASE)
    result = re.sub(r'\byak[ıi]nda\b', 'nearby', result, flags=re.IGNORECASE)
    result = re.sub(r'\byak[ıi]n[ıi]nda\b', 'nearby', result, flags=re.IGNORECASE)
    result = re.sub(r'\bkonumdad[ıi]r\b', 'is located', result, flags=re.IGNORECASE)
    result = re.sub(r'\bbulunmaktad[ıi]r\b', 'is available', result, flags=re.IGNORECASE)
    result = re.sub(r'\bbulunmaz\b', 'is not available', result, flags=re.IGNORECASE)
    result = re.sub(r'\bsahiptir\b', 'has', result, flags=re.IGNORECASE)
    result = re.sub(r'\bsunar[ıi]z\b', 'we offer', result, flags=re.IGNORECASE)
    result = re.sub(r'\bsunulmaktad[ıi]r\b', 'is served', result, flags=re.IGNORECASE)
    result = re.sub(r'\bger[çc]ekle[şs]tirilir\b', 'can be arranged', result, flags=re.IGNORECASE)
    result = re.sub(r'\bger[çc]ekle[şs]tirebilirsiniz\b', 'you can arrange', result, flags=re.IGNORECASE)
    result = re.sub(r'\bge[çc]\s+saate?\s+kadar\s+a[çc][ıi]k\b', 'open until late', result, flags=re.IGNORECASE)
    result = re.sub(r'\bge[çc]\s+saatlere\s+kadar\b', 'until late', result, flags=re.IGNORECASE)
    result = re.sub(r'\bmahallesi\b', 'neighborhood', result, flags=re.IGNORECASE)
    result = re.sub(r'\bsemtinde\b', 'district', result, flags=re.IGNORECASE)
    result = re.sub(r'\bb[öo]lgesinde\b', 'area', result, flags=re.IGNORECASE)
    # "dakika" remaining after partial transit translations
    result = re.sub(r'\b(\d+)\s*dakika\b', r'\1 minutes', result, flags=re.IGNORECASE)
    # "partilerine" remaining
    result = re.sub(r'\bpartilerine\b', 'events', result, flags=re.IGNORECASE)
    # "uygun" remaining
    result = re.sub(r'\bi[çc]in\s+uygun\b', 'suitable for', result, flags=re.IGNORECASE)
    result = re.sub(r'\bi[çc]in\s+ideal\b', 'ideal for', result, flags=re.IGNORECASE)
    # "also uygun" → "also suitable"
    result = re.sub(r'\balso\s+uygun\.?', 'also suitable.', result, flags=re.IGNORECASE)
    # bare "uygun" → "suitable"
    result = re.sub(r'\buygun\b', 'suitable', result, flags=re.IGNORECASE)

    # ── Additional Turkish word/phrase patterns ───────────────────────────
    # "Burada X, Y." → "Here X and Y."
    result = re.sub(r'\bBurada\b', 'Here', result, flags=re.IGNORECASE)
    # "neighborhood'ndeyiz" → "neighborhood."
    result = re.sub(r"neighborhood[''\u2019]?\w*ndeyiz\.?", 'neighborhood.', result, flags=re.IGNORECASE)
    # "X hattı (N dk) ile kolayca ulaşılabilir" → "X line (N min), easily accessible"
    result = re.sub(
        r'(\w[\w\s\-]+)\s+hatt[ıi]\s*\((\d+)\s*dk\)\s+ile\s+kolayca\s+ula[şs][ıi]labilir\.?',
        lambda m: f'{m.group(1).strip()} line ({m.group(2)} min), easily accessible.',
        result, flags=re.IGNORECASE
    )
    # "kolayca ulaşılabilir" → "easily accessible"
    result = re.sub(r'\bkolayca\s+ula[şs][ıi]labilir\b', 'easily accessible', result, flags=re.IGNORECASE)
    # "until late açık olan bir restorandır." → "Open until late."
    result = re.sub(r'^until\s+late\s+a[çc][ıi]k\s+olan\s+bir\s+restoran[ıi]?d[ıi]r\.?$',
                    'Open until late.', result.strip(), flags=re.IGNORECASE)
    # "until late açık olduğu için gece yemeği suitable for bir yerdir." → "Open until late, suitable for dinner."
    result = re.sub(r'until\s+late\s+a[çc][ıi]k\s+oldu[ğg]u\s+i[çc]in\s+gece\s+yeme[ğg]i\s+suitable\s+for\s+bir\s+(?:yer|mekan)d[ıi]r\.?',
                    'Open until late, suitable for dinner.', result, flags=re.IGNORECASE)
    # "sağlıklı" → "healthy"
    result = re.sub(r'\bsa[ğg]l[ıi]kl[ıi]\b', 'healthy', result, flags=re.IGNORECASE)
    # "yüksek puanlı" → "highly rated"
    result = re.sub(r'\by[üu]ksek\s+puanl[ıi]\b', 'highly rated', result, flags=re.IGNORECASE)
    # "Türk mutfağını sunan bir X restoranıdır" → "a Turkish cuisine X restaurant"
    result = re.sub(r'T[üu]rk\s+mutfa[ğg][ıi]n[ıi]\s+sunan\s+bir\b', 'a Turkish cuisine', result, flags=re.IGNORECASE)
    # "restoranıdır" → "restaurant."
    result = re.sub(r'\brestoran[ıi]?d[ıi]r\.?', 'restaurant.', result, flags=re.IGNORECASE)
    # "yöntemlerle" → "methods"
    result = re.sub(r'\by[öo]ntemlerle\b', 'methods', result, flags=re.IGNORECASE)
    # "hazırlanmaktadır" → "is prepared"
    result = re.sub(r'\bhaz[ıi]rlanmaktad[ıi]r\.?', 'is prepared.', result, flags=re.IGNORECASE)
    # "kalbinde" → "in the heart of"
    result = re.sub(r'\bkalbinde\b', 'in the heart of', result, flags=re.IGNORECASE)
    # "yakın değil" → "not close"
    result = re.sub(r'\byak[ıi]n\s+de[ğg]il\b', 'not close', result, flags=re.IGNORECASE)
    # "uzakta olduğu için" → "as it is far"
    result = re.sub(r'\buzakta\s+oldu[ğg]u\s+i[çc]in\b', 'as it is far,', result, flags=re.IGNORECASE)
    # "özel araçla gelmeniz gerekebilir" → "you may need to come by private transport"
    result = re.sub(r'[öo]zel\s+ara[çc]la\s+gelmeniz\s+gerekebilir\.?',
                    'you may need to come by private transport.', result, flags=re.IGNORECASE)
    # "Located in Restoranın konumu X neighborhood." → "Located in X neighborhood."
    result = re.sub(r'Located\s+in\s+[Rr]estan?oran[ıi]?n\s+konumu\s+', 'Located in ', result, flags=re.IGNORECASE)
    # "olup, X'e yakın olması and..." → "close to X and..."
    result = re.sub(u'\\bolup[,.]?\\s*(\\w[\\w\\s\u0027\u2019]+)[\u0027\u2019]?e\\s+yak[\u0131i]n\\s+olmas[\u0131i]\\s+and\\b',
                    r'close to \1 and', result, flags=re.IGNORECASE)
    # "gibi seçeneklerle avantajlıdır" → "and similar features."
    result = re.sub(r'\s+gibi\s+se[çc]eneklerle\s+avantajl[ıi]d[ıi]r\.?', ' and similar features.', result, flags=re.IGNORECASE)
    # "mekanlarına" / "mekanlara" → "venues"
    result = re.sub(r'\bmekanlar[ıi]n[a]?\b', 'venues', result, flags=re.IGNORECASE)
    result = re.sub(r'\bmekanlar[ıi]\b', 'venues', result, flags=re.IGNORECASE)
    result = re.sub(r'\bmekan[ıi]\b', 'venue', result, flags=re.IGNORECASE)
    # "X gibi önemli landmarklar yakınlarında is nearby." → "Near notable landmarks such as X."
    result = re.sub(r'(.+?)\s+gibi\s+[öo]nemli\s+landmarklar\s+yak[ıi]nlar[ıi]nda\s+is\s+nearby\.?',
                    r'Near notable landmarks such as \1.', result, flags=re.IGNORECASE)
    # "konumu sayesinde" → "due to its location"
    result = re.sub(r'\bkonumu\s+sayesinde\b', 'due to its location', result, flags=re.IGNORECASE)
    # "ayrıca" → "also"
    result = re.sub(r'\bayr[ıi]ca\b', 'also', result, flags=re.IGNORECASE)
    # "teraslı" → "with terrace"
    result = re.sub(r'\bteras(?:l[ıi])\b', 'with terrace', result, flags=re.IGNORECASE)
    # "aile dostu" → "family-friendly"
    result = re.sub(r'\baile\s+dostu\b', 'family-friendly', result, flags=re.IGNORECASE)
    # "sunuyor" → "offers"
    result = re.sub(r'\bsunuyor\b', 'offers', result, flags=re.IGNORECASE)
    # "kahvaltı menüsünü sunmuyor" → "does not offer a breakfast menu"
    result = re.sub(r'\bkahvalt[ıi]\s+men[üu]s[üu]n[üu]\s+sunmuyor\.?', 'does not offer a breakfast menu.', result, flags=re.IGNORECASE)
    # "yakın bölgelerde bulunan kahvaltı salonlarından can be preferred" → "nearby breakfast places can be preferred"
    result = re.sub(r'yak[ıi]n\s+b[öo]lgelerde\s+bulunan\s+kahvalt[ıi]\s+salonlar[ıi]ndan\s+can\s+be\s+preferred\.?',
                    'nearby breakfast venues can be preferred.', result, flags=re.IGNORECASE)
    # "farklı saatlerde hizmet can offer" → "can offer service at different hours"
    result = re.sub(r'farkl[ıi]\s+saatlerde\s+hizmet\s+can\s+offer\.?', 'can offer service at different hours.', result, flags=re.IGNORECASE)
    # "her gün açık and yemek servisi sunuyor" → "Open every day and offers food service"
    result = re.sub(r'her\s+g[üu]n\s+a[çc][ıi]k\s+and\s+yemek\s+servisi\s+sunuyor\.?', 'Open every day and offers food service.', result, flags=re.IGNORECASE)
    # "hizmet can offer" → "can offer service"
    result = re.sub(r'\bhizmet\s+can\s+offer\.?', 'can offer service.', result, flags=re.IGNORECASE)
    # "tamamen vegan olan restoranımızda" → "At our fully vegan restaurant,"
    result = re.sub(r'tamamen\s+vegan\s+olan\s+restoran[ıi]m[ıi]zda\b', 'At our fully vegan restaurant,', result, flags=re.IGNORECASE)
    # "diyet or alerji sorunu olan kişiler suitable for dishes we offer" → "we offer suitable dishes for those with dietary or allergy concerns"
    result = re.sub(r'diyet\s+or\s+alerji\s+sorunu\s+olan\s+ki[şs]iler\s+suitable\s+for\s+dishes\s+we\s+offer\.?',
                    'we offer suitable dishes for guests with dietary or allergy concerns.', result, flags=re.IGNORECASE)
    # "canlı müzik ile keyfinizi" → "live music to enhance your experience"
    result = re.sub(r'canl[ıi]\s+m[üu]zik\s+ile\s+keyfinizi\s+[^.]+\.',
                    'live music to enhance your experience.', result, flags=re.IGNORECASE)
    # "X gibi yerlere yakın konumdadır" → "conveniently located near X"  (already handled above, but add fallback)
    # "konumundadır" → "is located"
    result = re.sub(r'\bkonumundad[ıi]r\b', 'is located', result, flags=re.IGNORECASE)
    # "bulunmaktayız" → "we are located"
    result = re.sub(r'\bbulunmaktay[ıi]z\b', 'we are located', result, flags=re.IGNORECASE)
    # "yarımada" → "peninsula"
    result = re.sub(r'\byar[ıi]mada\b', 'peninsula', result, flags=re.IGNORECASE)
    # "yanı sıra" → "as well as"
    result = re.sub(r'\byan[ıi]\s+s[ıi]ra\b', 'as well as', result, flags=re.IGNORECASE)
    # "X'nın/X'nun kültürünü yansıtan" → "reflecting X's culture"
    result = re.sub(r"(\w+)[''\u2019]?(?:n[ıi]n|nun|nın)\s+k[üu]lt[üu]r[üu]n[üu]\s+yans[ıi]tan\b",
                    r"reflecting \1's culture", result, flags=re.IGNORECASE)
    # "bir grilled" → "a grilled"
    result = re.sub(r'\bbir\s+grilled\b', 'a grilled', result, flags=re.IGNORECASE)
    # "bir restoran" → "a restaurant" (only when followed by English)
    result = re.sub(r'\bbir\s+restoran\b(?!\s+[a-z])', 'a restaurant', result, flags=re.IGNORECASE)
    # "bir atmosfer" → "an atmosphere"
    result = re.sub(r'\bbir\s+atmosfer\b', 'an atmosphere', result, flags=re.IGNORECASE)
    # "bir deneyim" → "an experience"
    result = re.sub(r'\bbir\s+deneyim\b', 'an experience', result, flags=re.IGNORECASE)
    # "en yakın noktası" → "closest point"
    result = re.sub(r'\ben\s+yak[ıi]n\s+noktas[ıi]\b', 'closest point', result, flags=re.IGNORECASE)
    # "Restoranının en yakın noktası, X'e only N minutes away." → "The closest point is X, only N minutes away."
    result = re.sub(u'[Rr]estoran[\u0131i]n[\u0131i]n\\s+closest\\s+point[,.]?\\s*(.+?)[\u0027\u2019]?e\\s+only\\s+',
                    r'Only ', result, flags=re.IGNORECASE)
    # "menüsü" → "menu"
    result = re.sub(r'\bmen[üu]s[üu]\b', 'menu', result, flags=re.IGNORECASE)
    # "arasında" → "between" (only when between numbers like "07:00-23:00 arasında")
    result = re.sub(r'([\d:]+\s*[-–]\s*[\d:]+)\s+aras[ıi]nda\b', r'\1', result, flags=re.IGNORECASE)
    # "seçeneklerle" → "options"
    result = re.sub(r'\bse[çc]eneklerle\b', 'options', result, flags=re.IGNORECASE)
    # "ile birlikte" → "along with"
    result = re.sub(r'\bile\s+birlikte\b', 'along with', result, flags=re.IGNORECASE)
    # "bulunabilir" → "can be found"
    result = re.sub(r'\bbulunabilir\b', 'can be found', result, flags=re.IGNORECASE)
    # "sunan bir" → "offering a"
    result = re.sub(r'\bsunan\s+bir\b', 'offering a', result, flags=re.IGNORECASE)
    # "ile" standalone → "with/via" (careful: only when between two nouns, risky — skip)
    # "iyi" standalone as adjective → skip (too risky)
    # "olmasının" → "being" or skip
    result = re.sub(r'\bolmas[ıi]n[ıi]n\b', 'being', result, flags=re.IGNORECASE)
    # "hizmet" standalone → "service"
    result = re.sub(r'\bhizmet\b', 'service', result, flags=re.IGNORECASE)
    # "yemek servisi" → "food service"
    result = re.sub(r'\byemek\s+servisi\b', 'food service', result, flags=re.IGNORECASE)
    # "sunmaktadır" → "offers"
    result = re.sub(r'\bsunmaktad[ıi]r\b', 'offers', result, flags=re.IGNORECASE)
    # "yer almaktadır" → "is located" (already handled earlier but add fallback)
    # "Gece yemeği suitable for olan X..." already handled
    # Clean up: "bir" before English adjectives
    result = re.sub(r'\bbir\s+(scenic|romantic|traditional|modern|popular|historic|beautiful|pleasant|delicious)\b', r'a \1', result, flags=re.IGNORECASE)
    # "X gibi historic yerlere yakın (bir )is located." → "Located near historic places like X."
    result = re.sub(r'(.+?)\s+gibi\s+historic\s+yerlere\s+yak[ıi]n\s+(?:bir\s+)?is\s+located\.?',
                    r'Located near historic places like \1.', result, flags=re.IGNORECASE)
    # "X gibi historic landmarklar nearby" → "Near historic landmarks such as X."
    result = re.sub(r'(.+?)\s+gibi\s+historic\s+landmarklar\s+nearby\.?',
                    r'Near historic landmarks such as \1.', result, flags=re.IGNORECASE)
    # "landmarklara yakın" → "near landmarks"
    result = re.sub(r'\blandmarklara\s+yak[ıi]n\b', 'near landmarks', result, flags=re.IGNORECASE)
    # "mekanlara yakın" / "mekanlara near" → "near venues"
    result = re.sub(r'\bmekanlar[ae]\s+(?:yak[ıi]n|near\b)', 'near venues', result, flags=re.IGNORECASE)
    # "arasındadır" → "is among"
    result = re.sub(r'\baras[ıi]ndad[ıi]r\.?', 'is among.', result, flags=re.IGNORECASE)
    # "popüler dishes arasındadır" / "is a popular dish" cleanup
    result = re.sub(r'\bpop[üu]ler\s+dishes\s+(?:is\s+among|aras[ıi]ndad[ıi]r)\.?', 'is a popular dish.', result, flags=re.IGNORECASE)
    # "seçeneği" → "option", "seçenekleri" → "options"
    result = re.sub(r'\bse[çc]enekleri\b', 'options', result, flags=re.IGNORECASE)
    result = re.sub(r'\bse[çc]ene[ğg]i\b', 'option', result, flags=re.IGNORECASE)
    # "konumda" → "location"
    result = re.sub(r'\bkonumda\b', 'location', result, flags=re.IGNORECASE)
    # "yakın konumda" / "yakın location" → "nearby"
    result = re.sub(r'\byak[ıi]n\s+(?:konumda|location)\b', 'nearby', result, flags=re.IGNORECASE)
    # "yakın" standalone → "nearby"
    result = re.sub(r'\byak[ıi]n\b', 'nearby', result, flags=re.IGNORECASE)
    # "alt yapısı" → "infrastructure"
    result = re.sub(r'\balt\s+yap[ıi]s[ıi]\b', 'infrastructure', result, flags=re.IGNORECASE)
    # "bilgiye erişemiyorum" → "I don't have specific information"
    result = re.sub(r'(?:spesifik\s+)?(?:\w+\s+)?bilgiye\s+eri[şs]emiyorum\.?',
                    "I don't have specific information about this.", result, flags=re.IGNORECASE)
    # "arasında" → "among"
    result = re.sub(r'\baras[ıi]nda\b', 'among', result, flags=re.IGNORECASE)
    # "bölgesindedir" → "is in the area"
    result = re.sub(r'\bb[öo]lgesindedir\.?', 'is in the area.', result, flags=re.IGNORECASE)
    # "yaşamasına olanak" → "to have"
    result = re.sub(r'\bya[şs]amas[ıi]na\s+olanak\b', 'to have', result, flags=re.IGNORECASE)
    # "dinner suitable for restoran," → "Suitable for dinner."
    result = re.sub(r'dinner\s+suitable\s+for\s+restoran[,.]?\s*', 'Suitable for dinner. ', result, flags=re.IGNORECASE)
    # bare "restoran" at start of sentence → remove
    result = re.sub(r'^restoran[,.]?\s+', '', result.strip(), flags=re.IGNORECASE)
    # "restoranda" → "At the restaurant"
    result = re.sub(r'\brestoranda\b', 'At the restaurant,', result, flags=re.IGNORECASE)
    # "X gibi historic yerlerin nearby bulunuyor" → "Near historic places like X."
    result = re.sub(r'(.+?)\s+gibi\s+historic\s+yerlerin\s+nearby\s+bulunuyor\.?',
                    r'Near historic places like \1.', result, flags=re.IGNORECASE)
    # "X gibi historic landmarkların yakınlarında we are located" → "Located near historic landmarks such as X."
    result = re.sub(r'(.+?)\s+gibi\s+historic\s+landmarklar[ıi]n\s+yak[ıi]nlar[ıi]nda\s+we\s+are\s+located\.?',
                    r'Located near historic landmarks such as \1.', result, flags=re.IGNORECASE)
    # "gibi historic yerlere nearby bulunmakta olup" → "near historic places like X,"
    result = re.sub(r'(.+?)\s+gibi\s+historic\s+yerlere\s+nearby\s+(?:bulunmakta\s+olup|is\s+located)[,.]?\s*',
                    r'Located near historic places like \1. ', result, flags=re.IGNORECASE)
    # "gibi popüler bölgelere kısa mesafede" → "a short distance from popular areas like X"
    result = re.sub(r'(.+?)\s+gibi\s+pop[üu]ler\s+b[öo]lgelere\s+k[ıi]sa\s+mesafede\b',
                    r'a short distance from popular areas such as \1', result, flags=re.IGNORECASE)
    # "kısa mesafede" → "a short distance away"
    result = re.sub(r'\bk[ıi]sa\s+mesafede\b', 'a short distance away', result, flags=re.IGNORECASE)
    # "yemeklerindendir" → "is one of the famous dishes"
    result = re.sub(r'en\s+famous\s+yemeklerindendir\.?', 'among the most famous dishes.', result, flags=re.IGNORECASE)
    result = re.sub(r'\byemeklerindendir\.?', 'is one of the famous dishes.', result, flags=re.IGNORECASE)
    # "Bu dishes" → "These dishes"
    result = re.sub(r'\bBu\s+dishes\b', 'These dishes', result, flags=re.IGNORECASE)
    # "güneyinde" → "in the south of"
    result = re.sub(r'\bg[üu]neyinde\b', 'in the south of', result, flags=re.IGNORECASE)
    # "yetiştirilen" → "grown"
    result = re.sub(r'\byeti[şs]tirilen\b', 'grown', result, flags=re.IGNORECASE)
    # "kullanılarak yapılır" → "are made using"
    result = re.sub(r'\bkullan[ıi]larak\s+yap[ıi]l[ıi]r\.?', 'are made using.', result, flags=re.IGNORECASE)
    result = re.sub(r'\bkullan[ıi]larak\b', 'using', result, flags=re.IGNORECASE)
    # "imkanlar" → "options"
    result = re.sub(r'\bimkanlar\b', 'options', result, flags=re.IGNORECASE)
    result = re.sub(r'\bimkan[ıi]\b', 'option', result, flags=re.IGNORECASE)
    # "hizmeti" → "service"
    result = re.sub(r'\bhizmeti\b', 'service', result, flags=re.IGNORECASE)
    # "Gruplar for" → "For groups,"
    result = re.sub(r'\b[Gg]ruplar\s+for\b', 'For groups,', result, flags=re.IGNORECASE)
    # "yemek fiyatları" → "food prices"
    result = re.sub(r'\byemek\s+fiyatlar[ıi]\b', 'food prices', result, flags=re.IGNORECASE)
    # "orta seviyede" → "mid-range"
    result = re.sub(r'\borta\s+seviyede\b', 'mid-range', result, flags=re.IGNORECASE)
    # "nın/nün/nun/nın" possessive suffix after proper noun → "'s"
    result = re.sub(r"(\w+)[''\u2019]?n[ıiüu]n\s+food\s+prices", r"\1's food prices", result, flags=re.IGNORECASE)
    # "tanır" → (remove trailing "tanır" after translation artifacts)
    result = re.sub(r'\s+tan[ıi]r\.?$', '.', result.strip(), flags=re.IGNORECASE)
    # "sebze" → "vegetables"
    result = re.sub(r'\bsebze\b', 'vegetables', result, flags=re.IGNORECASE)
    # "et and sebze" → "meat and vegetables" (catch "et" = "meat" when next to vegetables/dishes)
    result = re.sub(r'\bet\s+and\s+vegetables\b', 'meat and vegetables', result, flags=re.IGNORECASE)
    result = re.sub(r'\bkaliteli\s+et\b', 'quality meat', result, flags=re.IGNORECASE)
    # "spesifik servis saatleri" → "specific service hours"
    result = re.sub(r'\bspesifik\s+servis\s+saatleri\b', 'specific service hours', result, flags=re.IGNORECASE)
    # "gibi dishes," where preceding is already-translated dish names → "and similar dishes,"
    result = re.sub(r'\s+gibi\s+dishes[,.]', ' and similar dishes.', result, flags=re.IGNORECASE)
    # "gibi imkanlar we offer" → "and similar options we offer"
    result = re.sub(r'\s+gibi\s+(?:imkanlar|options)\s+we\s+offer\.?', ' and more, we offer.', result, flags=re.IGNORECASE)
    # "bulunuyor" → "is available/located"
    result = re.sub(r'\bbulunuyor\b', 'is available', result, flags=re.IGNORECASE)
    # "bulunmakta" → "is located"
    result = re.sub(r'\bbulunmakta\b', 'is located', result, flags=re.IGNORECASE)
    # "olup" → "and" (connector)
    result = re.sub(r'\bolup[,.]?\s*', ', ', result, flags=re.IGNORECASE)
    # "Türkiye'nin" → "Turkey's"
    result = re.sub(u"T[\\u00fc\\u0075]rkiye['\u2019]?nin\\b", "Turkey's", result, flags=re.IGNORECASE)
    # "X gibi historic yapıları gösterir" → "shows historic buildings like X."
    result = re.sub(r'(.+?)\s+gibi\s+historic\s+yap[ıi]lar[ıi]\s+g[öo]sterir\.?',
                    r'The view includes historic buildings such as \1.', result, flags=re.IGNORECASE)
    # "gibi historic yapıların manzarası izlenebiliyor" → "showing historic buildings like X"
    result = re.sub(r'(.+?)\s+gibi\s+historic\s+yap[ıi]lar[ıi]n\s+manzaras[ıi]\s+izlenebiliyor\.?',
                    r'Views of historic buildings such as \1 can be seen.', result, flags=re.IGNORECASE)
    # "X gibi yemeklerimiz popüler" → "X and similar dishes are popular."
    result = re.sub(r'(.+?)\s+gibi\s+yemeklerimiz\s+pop[üu]ler\.?',
                    r'\1 and similar dishes are popular.', result, flags=re.IGNORECASE)
    # "saatleri among açık we are located" → "open [time]"
    result = re.sub(r'([\d:]+[-–][\d:]+)\s+saatleri\s+(?:among|aras[ıi]nda)\s+a[çc][ıi]k\s+we\s+are\s+located\.?',
                    r'Open \1.', result, flags=re.IGNORECASE)
    # "yapabiliyor, birthday gibi" → "can organize events like birthdays."
    result = re.sub(r'special\s+occasion\s+events\s+yap[ıi]labiliyor[,.]?\s*(\w+)\s+gibi\.?',
                    r'can organize special events such as \1.', result, flags=re.IGNORECASE)
    result = re.sub(r'\byap[ıi]labiliyor\b', 'can be organized', result, flags=re.IGNORECASE)
    result = re.sub(r'\byapabiliyor\b', 'can organize', result, flags=re.IGNORECASE)
    # "birthday gibi" → "such as birthdays"
    result = re.sub(r'\bbirthday\s+gibi\.?', 'such as birthdays.', result, flags=re.IGNORECASE)
    # "manzarası" → "view"
    result = re.sub(r'\bmanzaras[ıi]\b', 'view', result, flags=re.IGNORECASE)
    # "izlenebiliyor" → "can be seen"
    result = re.sub(r'\bizlenebiliyor\b', 'can be seen', result, flags=re.IGNORECASE)
    # "gösterir" → "shows"
    result = re.sub(r'\bg[öo]sterir\b', 'shows', result, flags=re.IGNORECASE)
    # "yapıları" / "yapıların" → "buildings"
    result = re.sub(r'\byap[ıi]lar[ıi]n[ıi]\b', 'buildings', result, flags=re.IGNORECASE)
    result = re.sub(r'\byap[ıi]lar[ıi]\b', 'buildings', result, flags=re.IGNORECASE)
    # "N kişiye kadar" → "up to N people"
    result = re.sub(r'\b(\d+)\s+ki[şs]iye\s+kadar\b', r'up to \1 people', result, flags=re.IGNORECASE)
    # "salon" → "hall"
    result = re.sub(r'\bsalon\b', 'hall', result, flags=re.IGNORECASE)
    # "özel menüler" → "special menus"
    result = re.sub(r'\b[öo]zel\s+men[üu]ler\b', 'special menus', result, flags=re.IGNORECASE)
    # "menüler" → "menus", "menüsü" already handled
    result = re.sub(r'\bmen[üu]ler\b', 'menus', result, flags=re.IGNORECASE)
    # "yemeklerimiz" → "our dishes"
    result = re.sub(r'\byemeklerimiz\b', 'our dishes', result, flags=re.IGNORECASE)
    # "popüler" → "popular"
    result = re.sub(r'\bpop[üu]ler\b', 'popular', result, flags=re.IGNORECASE)
    # "idealdir" → "is ideal"
    result = re.sub(r'\bidealdir\.?', 'is ideal.', result, flags=re.IGNORECASE)
    # "bir salon var" → "there is a hall"
    result = re.sub(r'\bbir\s+hall\s+var\b', 'there is a hall', result, flags=re.IGNORECASE)
    # "var" after noun → "available/there is"
    result = re.sub(r'\bvar\b(?=\s+and\b|\s*$)', 'available', result, flags=re.IGNORECASE)
    # "yemek" standalone → "food"
    result = re.sub(r'\byemek\b', 'food', result, flags=re.IGNORECASE)
    # "gibi" trailing at end of sentence → remove
    result = re.sub(r'\s+gibi\.?\s*$', '.', result.strip(), flags=re.IGNORECASE)
    # "X gibi lezzetlerimizden bazılarıdır." → "X are some of our popular dishes."
    result = re.sub(r'(.+?)\s+gibi\s+lezzetlerimizden\s+baz[ıi]lar[ıi]d[ıi]r\.?',
                    r'\1 are some of our popular dishes.', result, flags=re.IGNORECASE)
    # "X gibi historic yerlere nearby konumumuz is nearby." → "Located near historic places like X."
    result = re.sub(r'(.+?)\s+gibi\s+historic\s+yerlere\s+nearby\s+(?:konumumuz\s+)?is\s+nearby\.?',
                    r'Located near historic places like \1.', result, flags=re.IGNORECASE)
    # "gibi yemekleri deneyebilme fırsatını offers" → "and similar dishes are available to try."
    result = re.sub(r'\s+gibi\s+(?:yemekleri|dishes)\s+deneyebilme\s+f[ıi]rsat[ıi]n[ıi]\s+offers\.?',
                    ' and similar dishes are available to try.', result, flags=re.IGNORECASE)
    # "tarafından sevilen" → "beloved by"
    result = re.sub(r'\btaraf[ıi]ndan\s+sevilen\b', 'beloved by', result, flags=re.IGNORECASE)
    # "sağlıyor" → "provides"
    result = re.sub(r'\bsa[ğg]l[ıi]yor\b', 'provides', result, flags=re.IGNORECASE)
    # "terası yok" → "no terrace"
    result = re.sub(r'\bteras[ıi]\s+yok[,.]?\b', 'no terrace,', result, flags=re.IGNORECASE)
    # "N:NN'a/e kadar açık kalıyoruz" → "open until N:NN."
    result = re.sub(r"(\d{1,2}:\d{2})['\u2019]?[ae]\s+kadar\s+a[çc][ıi]k\s+kal[ıi]yoruz\.?",
                    r'open until \1.', result, flags=re.IGNORECASE)
    # "kadar açık kalıyoruz" → "open until late"
    result = re.sub(r'\bkadar\s+a[çc][ıi]k\s+kal[ıi]yoruz\.?', 'open until late.', result, flags=re.IGNORECASE)
    # "ziyaret edilebiliyor" → "can be visited"
    result = re.sub(r'\bziyaret\s+edilebiliyor\.?', 'can be visited.', result, flags=re.IGNORECASE)
    # "gibi yakındaki historic places ziyaret edilebiliyor" → "nearby historic places like X can be visited."
    result = re.sub(r'(.+?)\s+gibi\s+nearby(?:daki)?\s+historic\s+places\s+(?:can\s+be\s+visited|ziyaret\s+edilebiliyor)\.?',
                    r'Nearby historic places such as \1 can be visited.', result, flags=re.IGNORECASE)
    # "deniz mahsulleri" → "seafood"
    result = re.sub(r'\bdeniz\s+mahsulleri\b', 'seafood', result, flags=re.IGNORECASE)
    # "balık" → "fish"
    result = re.sub(r'\bbal[ıi]k\b', 'fish', result, flags=re.IGNORECASE)
    # "üzerine odaklanmış" → "focused on"
    result = re.sub(r'\b[üu]zerine\s+odaklanm[ıi][şs]\b', 'focused on', result, flags=re.IGNORECASE)
    # "konumumuz" → "our location"
    result = re.sub(r'\bkonumumuz\b', 'our location', result, flags=re.IGNORECASE)
    # "X gibi near(by) landmarks we are located." → "We are located near landmarks such as X."
    result = re.sub(r'(.+?)\s+gibi\s+near(?:by)?\s+landmarks\s+we\s+are\s+located\.?',
                    r'We are located near landmarks such as \1.', result, flags=re.IGNORECASE)
    # "klasik lezzetlerinden" → "among the classic flavors of"
    result = re.sub(r'\bklasik\s+lezzetlerinden\b', 'offering classic flavors such as', result, flags=re.IGNORECASE)
    # "lezzetlerinden" → "flavors of"
    result = re.sub(r'\blezzetlerinden\b', 'flavors of', result, flags=re.IGNORECASE)
    # "gibi children beloved by" → fix word order
    result = re.sub(r'(.+?)\s+gibi\s+children\s+beloved\s+by\s+(?:yemekleri|dishes|food)\s+offers',
                    r'Offers child-friendly dishes such as \1.', result, flags=re.IGNORECASE)
    # "yakındaki" → "nearby"
    result = re.sub(r'\byak[ıi]ndaki\b', 'nearby', result, flags=re.IGNORECASE)
    # "yakınlarında" → "nearby"
    result = re.sub(r'\byak[ıi]nlar[ıi]nda\b', 'nearby', result, flags=re.IGNORECASE)
    # "yakınımızda" → "near us"
    result = re.sub(r'\byak[ıi]n[ıi]m[ıi]zda\b', 'near us.', result, flags=re.IGNORECASE)
    # "X gibi historic landmarklar yakınımızda" → "Historic landmarks such as X are nearby."
    result = re.sub(r'(.+?)\s+gibi\s+historic\s+landmarklar\s+(?:yak[ıi]n[ıi]m[ıi]zda|near\s+us)\.?',
                    r'Historic landmarks such as \1 are nearby.', result, flags=re.IGNORECASE)
    # "X gibi historic landmarkların nearby we are located" → "We are located near historic landmarks such as X."
    result = re.sub(r'(.+?)\s+gibi\s+historic\s+landmarklar[ıi]n\s+nearby\s+we\s+are\s+located\.?',
                    r'We are located near historic landmarks such as \1.', result, flags=re.IGNORECASE)
    # "X gibi nearby landmark'lar" → fix
    result = re.sub(u'(.+?)\\s+gibi\\s+nearby\\s+landmark[\u2019\\s]?lar\\b',
                    r'nearby landmarks such as \1', result, flags=re.IGNORECASE)
    # "gibi delicious options dolu" → "and similar delicious options are available."
    result = re.sub(r'\s+gibi\s+delicious\s+options\s+dolu\.?', ' and similar delicious options are available.', result, flags=re.IGNORECASE)
    # "dolu" → "full" / "available"
    result = re.sub(r'\bdolu\b', 'available', result, flags=re.IGNORECASE)
    # "X gibi imkanlarımız yok" → "We don't have X and similar amenities."
    result = re.sub(r'(.+?)\s+gibi\s+imkanlar[ıi]m[ıi]z\s+yok\.?',
                    r"We don't have \1 and similar amenities.", result, flags=re.IGNORECASE)
    # "imkanlarımız yok" fallback
    result = re.sub(r'\bimkanlar[ıi]m[ıi]z\s+yok\.?', "These amenities are not available.", result, flags=re.IGNORECASE)
    # "orta büyüklükte" → "medium-sized"
    result = re.sub(r'\borta\s+b[üu]y[üu]kl[üu]kte\b', 'medium-sized', result, flags=re.IGNORECASE)
    # "atmosferimiz" → "our atmosphere"
    result = re.sub(r'\batmosferimiz\b', 'our atmosphere', result, flags=re.IGNORECASE)
    # "Türk mutfağından" → "featuring Turkish cuisine:"
    result = re.sub(r'\bT[üu]rk\s+mutfa[ğg][ıi]ndan\b', 'from Turkish cuisine:', result, flags=re.IGNORECASE)
    # "X gibi delicious yemekleri denemenizi öneririm" → "I recommend trying Turkish dishes like X."
    result = re.sub(r'(?:from\s+Turkish\s+cuisine:\s+)?(.+?)\s+gibi\s+delicious\s+(?:yemekleri|dishes)\s+denemenizi\s+[öo]neririm\.?',
                    r'I recommend trying delicious dishes such as \1.', result, flags=re.IGNORECASE)
    # ", nda " prefix (leftover Turkish suffix) → ","
    result = re.sub(r',\s+nda\s+', ', ', result, flags=re.IGNORECASE)
    # "X saatleri among açık" → "Open X."
    result = re.sub(r'([\d:]+\s*[-–]\s*[\d:]+)\s+saatleri?\s+among\s+a[çc][ıi]k(?:\s+kal[ıi]yoruz)?\.?',
                    r'Open \1.', result, flags=re.IGNORECASE)
    # "saatleri among açık" (without time) → "open."
    result = re.sub(r'saatleri?\s+among\s+a[çc][ıi]k(?:\s+kal[ıi]yoruz)?\.?', 'open.', result, flags=re.IGNORECASE)
    # "saatleri among provides service" → "open."
    result = re.sub(r'([\d:]+\s*[-–]\s*[\d:]+)\s+saatleri?\s+among\s+provides\s+service\.?',
                    r'Open \1.', result, flags=re.IGNORECASE)
    # "Gece saatleri X among açık kalıyoruz" → "Open X throughout the night."
    result = re.sub(r'[Gg]ece\s+saatleri?\s+([\d:]+\s*[-–]\s*[\d:]+)\s+(?:among|aras[ıi]nda)\s+a[çc][ıi]k\s+kal[ıi]yoruz\.?',
                    r'Open \1 throughout the night.', result, flags=re.IGNORECASE)
    # "kolayca ulaşabilirsiniz" → "Easily accessible."
    result = re.sub(r'\bkolayca\s+ula[şs]abilirsiniz\.?', 'Easily accessible.', result, flags=re.IGNORECASE)
    # "vapur with Easily accessible." → "Easily accessible by ferry."
    result = re.sub(r'vapur\s+with\s+Easily\s+accessible\.?', 'Easily accessible by ferry.', result, flags=re.IGNORECASE)
    # "mahallesinde" → "neighborhood"
    result = re.sub(r'\bmahallesi?nde\b', 'neighborhood', result, flags=re.IGNORECASE)
    # "X'te/X'ta located" → "Located in X,"
    result = re.sub(u"(\\w+)['\u2019]?t[ae]\\s+located[,.]?\\s*", r'Located in \1, ', result, flags=re.IGNORECASE)
    # "sabah" → "morning"
    result = re.sub(r'\bsabah\b', 'morning', result, flags=re.IGNORECASE)
    # "öğleden sonra" → "afternoon"
    result = re.sub(r'\b[öo][ğg]leden\s+sonra\b', 'afternoon', result, flags=re.IGNORECASE)
    # "saatleri is among" → "hours."
    result = re.sub(r'saatleri?\s+is\s+among\.?', 'hours.', result, flags=re.IGNORECASE)
    # "zaman dilimi" → "time period"
    result = re.sub(r'\bzaman\s+dilimi\b', 'time period', result, flags=re.IGNORECASE)
    # "Geceli bir restoran olarak" → "As a late-night restaurant,"
    result = re.sub(r'[Gg]eceli\s+bir\s+restoran\s+olarak\b', 'As a late-night restaurant,', result, flags=re.IGNORECASE)
    # "açılış saatleri" → "opening hours"
    result = re.sub(r'\ba[çc][ıi]l[ıi][şs]\s+saatleri?\b', 'opening hours', result, flags=re.IGNORECASE)
    # "günün her saatinde açık olduğu for farklılık göstermiyor" → "are consistent throughout the day."
    result = re.sub(r'g[üu]n[üu]n\s+her\s+saatinde\s+a[çc][ıi]k\s+oldu[ğg]u\s+for\s+farkl[ıi]l[ıi]k\s+g[öo]stermiyor\.?',
                    'are consistent throughout the day.', result, flags=re.IGNORECASE)
    # "saatleri" standalone → "hours"
    result = re.sub(r'\bsaatleri?\b', 'hours', result, flags=re.IGNORECASE)
    # "Pazartesi'den Pazar'a kadar" → "Monday to Sunday,"
    result = re.sub(u"Pazartesi['\u2019]?den\\s+Pazar['\u2019]?a\\s+kadar\\b", 'Monday to Sunday,', result, flags=re.IGNORECASE)
    # "durumundayız" → remove
    result = re.sub(r'\bdurumundayız\.?', '', result, flags=re.IGNORECASE)
    result = re.sub(r'\bdurumundayiz\.?', '', result, flags=re.IGNORECASE)
    # "durakları" / "duraksları" → "stops"
    result = re.sub(r'\bduraks?lar[ıi]\b', 'stops', result, flags=re.IGNORECASE)
    # "erişilebilir" → "accessible"
    result = re.sub(r'\beri[şs]ilebilir\b', 'accessible', result, flags=re.IGNORECASE)
    # "orta konumunda" → "centrally located"
    result = re.sub(r'\borta\s+konumunda\b', 'centrally located', result, flags=re.IGNORECASE)
    # "muhteşem" → "magnificent"
    result = re.sub(r'\bmuhte[şs]em\b', 'magnificent', result, flags=re.IGNORECASE)
    # "sunar" → "offers"
    result = re.sub(r'\bsunar\b', 'offers', result, flags=re.IGNORECASE)
    # "konumudur" → "is its location."
    result = re.sub(r'\bkonumudur\.?', 'is its location.', result, flags=re.IGNORECASE)
    # "avantajı" → "advantage"
    result = re.sub(r'\bavantaj[ıi]\b', 'advantage', result, flags=re.IGNORECASE)
    # "ulaşımını provides" → "provides easy access"
    result = re.sub(r'ula[şs][ıi]m[ıi]n[ıi]\s+provides\.?', 'provides easy access.', result, flags=re.IGNORECASE)
    # "kolayca erişilebilir" / "kolayca accessible" → "easily accessible"
    result = re.sub(r'\bkolayca\s+(?:eri[şs]ilebilir|accessible)\b', 'easily accessible', result, flags=re.IGNORECASE)
    # "nın/nun bir avantajı" prefix (leftover possessive) → remove
    result = re.sub(r"^,?\s*n[ıiüu]n\s+bir\s+advantage[,.]?\s*", '', result.strip(), flags=re.IGNORECASE)
    # "yerlere nearby" → "nearby places"
    result = re.sub(r'\byerlere\s+nearby\b', 'nearby places', result, flags=re.IGNORECASE)
    # "olması" → "being" → remove in context
    result = re.sub(r',?\s+nearby\s+olmas[ıi][,.]?\s*', ', nearby, ', result, flags=re.IGNORECASE)
    # "kolayca ulaşmak mümkün" → "is easily accessible."
    result = re.sub(r'\bkolayca\s+ula[şs]mak\s+m[üu]mk[üu]n\.?', 'is easily accessible.', result, flags=re.IGNORECASE)
    # "geceye kadar açık olduğu for" → "being open until late,"
    result = re.sub(r'\bgeceye\s+kadar\s+a[çc][ıi]k\s+oldu[ğg]u\s+for[,.]?\s*', 'being open until late, ', result, flags=re.IGNORECASE)
    # "gece food" → "late-night food"
    result = re.sub(r'\bgece\s+food\b', 'late-night food', result, flags=re.IGNORECASE)
    # "ihtiyacınızı karşılayabilirsiniz" → "can meet your needs."
    result = re.sub(r'\bihtiyac[ıi]n[ıi]z[ıi]\s+kar[şs][ıi]layabilirsiniz\.?', 'can meet your needs.', result, flags=re.IGNORECASE)
    # "transit noktalarından ulaşılabilir" → "transit stops are accessible."
    result = re.sub(r'(?:transit\s+)?noktalar[ıi]ndan\s+ula[şs][ıi]labilir\.?', 'transit stops are accessible.', result, flags=re.IGNORECASE)
    # "N:NN'a/e kadar açık" (standalone) → "open until N:NN."
    result = re.sub(u"(\\d{1,2}:\\d{2})['\u2019]?[ae]\\s+kadar\\s+a[\\xe7c][\\u0131i]k\\.?",
                    r'open until \1.', result, flags=re.IGNORECASE)
    # "kolayca" standalone → "easily"
    result = re.sub(r'\bkolayca\b', 'easily', result, flags=re.IGNORECASE)
    # "olması" standalone leftover → remove
    result = re.sub(r'\bolmas[ıi]\b', '', result, flags=re.IGNORECASE)
    # "kadar açık" standalone → "open until late"
    result = re.sub(r'\bkadar\s+a[çc][ıi]k\b', 'open until late', result, flags=re.IGNORECASE)
    # "Bilmiyorum" → "I don't have this information."
    result = re.sub(r'^[Bb]ilmiyorum\.?$', "I don't have this information.", result.strip())
    # "şef, olarak" / "şef olarak" → "As a chef-driven restaurant,"
    result = re.sub(r'\b[şs]ef[,.]?\s+olarak\b', 'As a chef-driven restaurant,', result, flags=re.IGNORECASE)
    # "şef" → "chef"
    result = re.sub(r'\b[şs]ef\b', 'chef', result, flags=re.IGNORECASE)
    # "olarak" → "as"
    result = re.sub(r'\bolarak\b', 'as', result, flags=re.IGNORECASE)
    # "seçeneğimiz yok" / "seçeneklerimiz yok" → "not available"
    result = re.sub(r'\bse[çc]ene[ğg]?(?:imiz|lerimiz)\s+yok\.?', 'not available.', result, flags=re.IGNORECASE)
    # "Vegan/vejetaryen seçeneğimiz yok" → "Vegan/vegetarian options are not available."
    result = re.sub(r'[Vv]egan/?(?:vejetaryen|vejeteryan)?\s+se[çc]ene[ğg]?(?:imiz|lerimiz)\s+yok\.?',
                    'Vegan/vegetarian options are not available.', result, flags=re.IGNORECASE)
    # "seçeneğimiz" / "seçeneklerimiz" → "our options"
    result = re.sub(r'\bse[çc]eneklerimiz\b', 'our options', result, flags=re.IGNORECASE)
    result = re.sub(r'\bse[çc]ene[ğg]imiz\b', 'our option', result, flags=re.IGNORECASE)
    # "Lütfen" → "Please"
    result = re.sub(r'\bl[üu]tfen\b', 'Please', result, flags=re.IGNORECASE)
    # "bizimle iletişime geçin" → "contact us"
    result = re.sub(r'\bbizimle\s+ileti[şs]ime\s+ge[çc]in\.?', 'contact us.', result, flags=re.IGNORECASE)
    # "reservation yapın" → "make a reservation"
    result = re.sub(r'\breservation\s+yap[ıi]n\.?', 'make a reservation.', result, flags=re.IGNORECASE)
    # "gidebilirsiniz" → "you can visit"
    result = re.sub(r'\bgidebilirsiniz\b', 'you can visit', result, flags=re.IGNORECASE)
    # "nearby bulunması due to gidebilirsiniz" → "are nearby, worth a visit."
    result = re.sub(r'nearby\s+(?:bulunmas[ıi]\s+)?due\s+to\s+(?:you\s+can\s+visit|gidebilirsiniz)\.?',
                    'are nearby, making it worth a visit.', result, flags=re.IGNORECASE)
    # "esinlenerek hazırlanan" → "inspired and prepared"
    result = re.sub(r'\besinlenerek\s+haz[ıi]rlanan\b', 'inspired and crafted', result, flags=re.IGNORECASE)
    # "hazırlıyoruz" → "we prepare"
    result = re.sub(r'\bhaz[ıi]rl[ıi]yoruz\.?', 'we prepare.', result, flags=re.IGNORECASE)
    # "hazırlanmış" → "prepared"
    result = re.sub(r'\bhaz[ıi]rlanm[ıi][şs]\b', 'prepared', result, flags=re.IGNORECASE)
    # "Doğum gününüzü özel hale getirmek for" → "To make your birthday special,"
    result = re.sub(r'[Dd]o[ğg]um\s+g[üu]n[üu]n[üu]z[üu]\s+[öo]zel\s+hale\s+getirmek\s+for\b',
                    'To make your birthday special,', result, flags=re.IGNORECASE)
    # "özel hale getirmek" → "to make special"
    result = re.sub(r'\b[öo]zel\s+hale\s+getirmek\b', 'to make special', result, flags=re.IGNORECASE)
    # "seçebilirsiniz" → "you can choose"
    result = re.sub(r'\bse[çc]ebilirsiniz\b', 'you can choose', result, flags=re.IGNORECASE)
    # "olanakları" / "olanağı" → "opportunities"
    result = re.sub(r'\bolanak(?:lar[ıi]|[ıi])\b', 'options', result, flags=re.IGNORECASE)
    # "tercih edebilirsiniz" → "you can prefer/choose"
    result = re.sub(r'\btercih\s+edebilirsiniz\b', 'you can choose', result, flags=re.IGNORECASE)
    # "ziyaret edebilirsiniz" → "you can visit"
    result = re.sub(r'\bziyaret\s+edebilirsiniz\b', 'you can visit', result, flags=re.IGNORECASE)
    # "Lütfen rezervasyon / reservation" cleanup
    result = re.sub(r'[Ll]utfen\s+(?:rezervasyon|reservation)', 'Please make a reservation', result, flags=re.IGNORECASE)
    # "mutfağı with birleştirerek" → "combining X cuisine"
    result = re.sub(r'mutfa[ğg][ıi]\s+with\s+birle[şs]tirerek\b', 'cuisine, combining', result, flags=re.IGNORECASE)
    # "birleştirerek" → "combining"
    result = re.sub(r'\bbirle[şs]tirerek\b', 'combining', result, flags=re.IGNORECASE)
    # "servis seçeneklerimiz" → "our service options"
    result = re.sub(r'\bservis\s+(?:our\s+options|se[çc]eneklerimiz)\b', 'our service options', result, flags=re.IGNORECASE)
    # "in advance reservation yapın" → "please reserve in advance"
    result = re.sub(r'in\s+advance\s+reservation\s+yap[ıi]n\.?', 'please reserve in advance.', result, flags=re.IGNORECASE)
    # "atmosferi" → "atmosphere"
    result = re.sub(r'\batmosferi\b', 'atmosphere', result, flags=re.IGNORECASE)
    # ".dir." suffix artifact → remove
    result = re.sub(r'\.dir\.', '.', result, flags=re.IGNORECASE)
    # "iletişime geçerek" → "by contacting us,"
    result = re.sub(r'\bileti[şs]ime\s+ge[çc]erek[,.]?\s*', 'by contacting us, ', result, flags=re.IGNORECASE)
    # "iletişime geçmeniz gerekir" → "please contact us."
    result = re.sub(r'\bileti[şs]ime\s+ge[çc]meniz\s+gerekir\.?', 'please contact us.', result, flags=re.IGNORECASE)
    # "taleplerinizi iletebilirsiniz" → "you can submit your requests."
    result = re.sub(r'(?:event\s+)?taleplerinizi\s+iletebilirsiniz\.?', 'you can submit your event requests.', result, flags=re.IGNORECASE)
    # "iletebilirsiniz" → "you can submit"
    result = re.sub(r'\biletebilirsiniz\b', 'you can submit', result, flags=re.IGNORECASE)
    # "özel günlerinizi unutulmaz hale getirmek for" → "to make your special days unforgettable,"
    result = re.sub(r'[öo]zel\s+g[üu]nlerinizi\s+unutulmaz\s+hale\s+getirmek\s+for\b',
                    'to make your special days unforgettable,', result, flags=re.IGNORECASE)
    # "unutulmaz hale getirmek for" → "to make unforgettable,"
    result = re.sub(r'\buntutulmaz\s+hale\s+getirmek\s+for\b', 'to make unforgettable,', result, flags=re.IGNORECASE)
    # "tasarlanmıştır" → "is designed."
    result = re.sub(r'\btasarlanm[ıi][şs]t[ıi]r\.?', 'is designed.', result, flags=re.IGNORECASE)
    # "olabilir" → "may be available"
    result = re.sub(r'\bolabilir\b', 'may be available', result, flags=re.IGNORECASE)
    # "daha fazla bilgi for" → "for more information,"
    result = re.sub(r'\bdaha\s+fazla\s+bilgi\s+for\b', 'for more information,', result, flags=re.IGNORECASE)
    # "sunabiliriz" → "we can offer"
    result = re.sub(r'\bsunabiliriz\b', 'we can offer', result, flags=re.IGNORECASE)
    # "Fiyatını bilmiyorum" → "I don't know the price,"
    result = re.sub(r'\bFiyat[ıi]n[ıi]\s+bilmiyorum[,.]?\s*', "I don't know the price, ", result, flags=re.IGNORECASE)
    # "popular bir food olduğu for" → "as it's a popular dish,"
    result = re.sub(r'popular\s+bir\s+food\s+oldu[ğg]u\s+for\b', "as it's a popular dish,", result, flags=re.IGNORECASE)
    # "denemenizi öneririm" → "I recommend you try it."
    result = re.sub(r'\bdenemenizi\s+[öo]neririm\.?', 'I recommend you try it.', result, flags=re.IGNORECASE)
    # "özel alanları" → "special areas"
    result = re.sub(r'\b[öo]zel\s+alanlar[ıi]\b', 'special areas', result, flags=re.IGNORECASE)
    # "birthday organizasyonu also yapabilirsiniz" → "You can also organize a birthday event."
    result = re.sub(r'\bbirthday\s+(?:event|organizasyonu)\s+also\s+yapabilirsiniz\.?',
                    'You can also organize a birthday event.', result, flags=re.IGNORECASE)
    # "birthday organizasyonu yapabilirsiniz" → "You can organize a birthday event."
    result = re.sub(r'\bbirthday\s+(?:event|organizasyonu)\s+yapabilirsiniz\.?',
                    'You can organize a birthday event.', result, flags=re.IGNORECASE)
    # "organizasyonu" → "event"
    result = re.sub(r'\borganizasyonu\b', 'event', result, flags=re.IGNORECASE)
    # "yapabilirsiniz" → "you can arrange"
    result = re.sub(r'\byapabilirsiniz\b', 'you can arrange', result, flags=re.IGNORECASE)
    # "iletişime geçebilirsiniz" → "you can contact us"
    result = re.sub(r'\bileti[şs]ime\s+ge[çc]ebilirsiniz\.?', 'you can contact us.', result, flags=re.IGNORECASE)
    # "reservation for bizimle iletişime geçebilirsiniz" → "For reservations, contact us."
    result = re.sub(r'reservation\s+for\s+bizimle\s+(?:ileti[şs]ime\s+ge[çc]ebilirsiniz|you\s+can\s+contact\s+us)\.?',
                    'For reservations, contact us.', result, flags=re.IGNORECASE)
    # "bizimle" → "with us"
    result = re.sub(r'\bbizimle\b', 'with us', result, flags=re.IGNORECASE)
    # "büyük For groups, event yapabilirsiniz" → "For large groups, you can arrange an event."
    result = re.sub(r'b[üu]y[üu]k\s+For\s+groups[,.]?\s+event\s+(?:yapabilirsiniz|you\s+can\s+arrange)\.?',
                    'For large groups, you can arrange an event.', result, flags=re.IGNORECASE)
    # "gibi" before already-English text → "such as" / "like"
    result = re.sub(r'\bgibi\s+(?=nearby|historic|landmark|scenic|delicious|popular|special)', 'such as ', result, flags=re.IGNORECASE)
    # Remaining "gibi" in middle of sentence between proper nouns → "such as"
    result = re.sub(r'\bgibi\b', 'such as', result, flags=re.IGNORECASE)
    # "bir is in the area." → remove "bir"
    result = re.sub(r'\bbir\s+is\s+in\s+the\s+area\.?', 'is in the area.', result, flags=re.IGNORECASE)
    # "neighborhood'nin" → "neighborhood's" (Turkish possessive on English word)
    result = re.sub(u"neighborhood['\u2019]?nin\\b", "neighborhood's", result, flags=re.IGNORECASE)
    # "bir food deneyimi to have" → "a dining experience"
    result = re.sub(r'\bbir\s+food\s+deneyimi\s+to\s+have\.?', 'a pleasant dining experience.', result, flags=re.IGNORECASE)
    # "bir yemek deneyimi" → "a dining experience"
    result = re.sub(r'\bbir\s+(?:yemek|food)\s+(?:deneyimi|experience)\b', 'a dining experience', result, flags=re.IGNORECASE)
    # "deneyimi" → "experience"
    result = re.sub(r'\bdeneyimi\b', 'experience', result, flags=re.IGNORECASE)
    # "nın terasından" → "From the terrace of" (when preceded by restaurant name)
    result = re.sub(r",\s+n[ıiüu]n\s+teras[ıi]ndan\b", "'s terrace shows", result, flags=re.IGNORECASE)
    # "iş yemeği" → "business lunch"
    result = re.sub(r'\bi[şs]\s+yeme[ğg]i\b', 'business lunch', result, flags=re.IGNORECASE)
    # "gece yemeği" → "dinner"
    result = re.sub(r'\bgece\s+yeme[ğg]i\b', 'dinner', result, flags=re.IGNORECASE)
    # "huzurlu" → "cozy"
    result = re.sub(r'\bhuzurlu\b', 'cozy', result, flags=re.IGNORECASE)
    # "etrafındaki" → "surrounding"
    result = re.sub(r'\betraf[ıi]ndaki\b', 'surrounding', result, flags=re.IGNORECASE)
    # "yer aldığı için" → "because it is located"
    result = re.sub(r'\byer\s+ald[ıi][ğg][ıi]\s+i[çc]in\b', 'because it is located', result, flags=re.IGNORECASE)
    # "diğer" → "other"
    result = re.sub(r'\bdi[ğg]er\b', 'other', result, flags=re.IGNORECASE)
    # "bulunan" (as adjective) → "located" / remove in certain contexts
    result = re.sub(r'\bbulunan\b', 'located', result, flags=re.IGNORECASE)
    # "boyunca" → "throughout"
    result = re.sub(r'\bboyunca\b', 'throughout', result, flags=re.IGNORECASE)
    # "kahvaltı için" → "for breakfast"
    result = re.sub(r'\bkahvalt[ıi]\s+i[çc]in\b', 'for breakfast', result, flags=re.IGNORECASE)
    # "için" standalone → "for"
    result = re.sub(r'\bi[çc]in\b', 'for', result, flags=re.IGNORECASE)
    # "olan" → remove (often just "which is/that is" connector in half-translated text)
    result = re.sub(r'\bolan\b', '', result, flags=re.IGNORECASE)
    # "ile" → "with" (standalone connector — risky but mostly safe in translated context)
    result = re.sub(r'\s+ile\s+', ' with ', result, flags=re.IGNORECASE)
    # "de" / "da" suffix indicators → skip (too risky as English words)
    # "bir yer" → "a place"
    result = re.sub(r'\bbir\s+yer\b', 'a place', result, flags=re.IGNORECASE)
    # "bir ideal" / "bir suitable" cleanup from translations
    result = re.sub(r'\bbir\s+(ideal|suitable)\b', r'\1', result, flags=re.IGNORECASE)
    # "gece saatleri boyunca açık olan restoran" → "Open throughout the night"
    result = re.sub(r'[Gg]ece\s+saatleri\s+(throughout\s+)?a[çc][ıi]k\s+(?:olan\s+)?restoran[,.]?\s*', 'Open late. ', result, flags=re.IGNORECASE)
    # "ideal for bir yer" → "an ideal place for"
    result = re.sub(r'ideal\s+for\s+bir\s+yer\.?', 'an ideal place.', result, flags=re.IGNORECASE)
    # "neighborhood'ndeki" → "neighborhood's"
    result = re.sub(u"neighborhood['\u2019]?ndeki\\b", "neighborhood's", result, flags=re.IGNORECASE)
    # "X restoranı," as subject prefix → "X,"
    result = re.sub(r'(\w[\w\s&]+)\s+restoran[ıi][,.]?\s*', r'\1, ', result, flags=re.IGNORECASE)
    # double comma cleanup
    result = re.sub(r',\s*,', ',', result)

    # ── Final cleanup ──────────────────────────────────────────────────────
    # Double spaces
    result = re.sub(r'  +', ' ', result)
    # ". ." double period
    result = re.sub(r'\.\s+\.', '.', result)
    # "and and"
    result = re.sub(r'\band\s+and\b', 'and', result, flags=re.IGNORECASE)
    # "is is"
    result = re.sub(r'\bis\s+is\b', 'is', result, flags=re.IGNORECASE)
    # Trailing commas before period
    result = re.sub(r',\s*\.$', '.', result)
    # "Located in X neighborhood. is located" → fix
    result = re.sub(r'(Located in \w[\w\s]+ neighborhood\.)\s+is located\.?', r'\1', result, flags=re.IGNORECASE)

    # Trailing mixed Turkish remnants after partial translation
    result = re.sub(r'\s*\.\s*$', '.', result.strip())

    # ── Remaining Turkish vocab ────────────────────────────────────────────────
    result = re.sub(r'\bbir\s+tercih\b', 'a choice', result, flags=re.IGNORECASE)
    result = re.sub(r'\btasarlanm[ıi][şs]\s+bir\s+lokantad[ıi]r\b', 'is a restaurant designed for this', result, flags=re.IGNORECASE)
    result = re.sub(r'\btasarlanm[ıi][şs]\b', 'designed', result, flags=re.IGNORECASE)
    result = re.sub(r'\blokantad[ıi]r\b', 'is a restaurant', result, flags=re.IGNORECASE)
    result = re.sub(r'\byer\s+almakta\b', 'is featured', result, flags=re.IGNORECASE)
    result = re.sub(r'\bdetayl[ıi]\s+bilgi\b', 'detailed information', result, flags=re.IGNORECASE)
    result = re.sub(r'\bbir\s+atmosphere\s+sunan\b', 'offering an atmosphere', result, flags=re.IGNORECASE)
    result = re.sub(r'\bsunan\b', 'offering', result, flags=re.IGNORECASE)
    result = re.sub(r'\b[öo]zel\s+g[üu]nlerinizde\b', 'on your special occasions', result, flags=re.IGNORECASE)
    result = re.sub(r'\bunutulmaz\s+deneyimler\s+yaratmak\b', 'to create unforgettable experiences', result, flags=re.IGNORECASE)
    result = re.sub(r'\bunutulmaz\b', 'unforgettable', result, flags=re.IGNORECASE)
    result = re.sub(r'\bdeneyimler\b', 'experiences', result, flags=re.IGNORECASE)
    result = re.sub(r'\byaratmak\b', 'to create', result, flags=re.IGNORECASE)
    result = re.sub(r'\bideal\s+for\s+bir\s+se[çc]enektir\b', 'is an ideal choice', result, flags=re.IGNORECASE)
    result = re.sub(r'\bbir\s+se[çc]enektir\b', 'is a great choice', result, flags=re.IGNORECASE)
    result = re.sub(r'\bT[üu]rk\s+mutfa[ğg][ıi]n[ıi]n\b', "Turkish cuisine's", result, flags=re.IGNORECASE)
    result = re.sub(r'\ben\s+leziz\s+yemeklerini\b', 'most delicious dishes', result, flags=re.IGNORECASE)
    result = re.sub(r'\bleziz\b', 'delicious', result, flags=re.IGNORECASE)
    result = re.sub(r'\b[bB][üu]y[üu]k\s+(?=For\s+groups)', 'Large ', result)
    result = re.sub(r'\b[bB][üu]y[üu]k\b', 'large', result, flags=re.IGNORECASE)
    result = re.sub(r'\bBilmiyorum,\s+but\b', "I'm not sure, but", result, flags=re.IGNORECASE)
    # More vocabulary
    result = re.sub(r'\b[çc]ocuk\s+dostu\b', 'child-friendly', result, flags=re.IGNORECASE)
    result = re.sub(r'\byer\s+alan\b', 'located in', result, flags=re.IGNORECASE)
    result = re.sub(r'\byak[ıi]nlar[ıi]ndad[ıi]r\b', 'is nearby', result, flags=re.IGNORECASE)
    result = re.sub(r'\bm[üu]mk[üu]n\b', 'possible', result, flags=re.IGNORECASE)
    result = re.sub(r'\bme[şs]hur\b', 'famous', result, flags=re.IGNORECASE)
    result = re.sub(r'\bklasik\b', 'classic', result, flags=re.IGNORECASE)
    result = re.sub(r'\bgastronomi\b', 'gastronomy', result, flags=re.IGNORECASE)
    result = re.sub(r'\bhizmet\b', 'service', result, flags=re.IGNORECASE)
    result = re.sub(r'\bpek\s+[çc]ok\b', 'many', result, flags=re.IGNORECASE)
    result = re.sub(r'\bayn[ıi]\s+zamanda\b', 'also', result, flags=re.IGNORECASE)
    result = re.sub(r'\bturistik\b', 'touristic', result, flags=re.IGNORECASE)
    result = re.sub(r'\baland[ıi]r\b', 'is an area', result, flags=re.IGNORECASE)
    result = re.sub(r'\brestoran[ıi]m[ıi]z\b', 'our restaurant', result, flags=re.IGNORECASE)
    result = re.sub(r'\brestoran[ıi]n\b', "the restaurant's", result, flags=re.IGNORECASE)
    result = re.sub(r'\bilgi\b', 'information', result, flags=re.IGNORECASE)
    result = re.sub(r'\bmevcut\s+de[ğg]ildir\b', 'is not available', result, flags=re.IGNORECASE)
    result = re.sub(r'\bmevcuttur\b', 'is available', result, flags=re.IGNORECASE)
    result = re.sub(r'\bmevcut\b', 'available', result, flags=re.IGNORECASE)
    result = re.sub(r'\bözel\s+men[üu]\b', 'special menu', result, flags=re.IGNORECASE)
    result = re.sub(r'\bözel\s+alan\b', 'private area', result, flags=re.IGNORECASE)
    result = re.sub(r'\bözel\s+oda\b', 'private room', result, flags=re.IGNORECASE)
    result = re.sub(r'\b[öo]zel\b', 'special', result, flags=re.IGNORECASE)
    result = re.sub(r'\byüksek\s+puan\b', 'high ratings', result, flags=re.IGNORECASE)
    result = re.sub(r'\bayrıca\b', 'also', result, flags=re.IGNORECASE)

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
