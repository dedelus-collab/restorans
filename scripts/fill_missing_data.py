# -*- coding: utf-8 -*-
"""
1. Eksik opening_hours -> cuisine + tags bazinda kural tabanli tahmin
2. verified_data -> veri doluluguna gore otomatik set
3. FAQ "Bilgi mevcut degil" cevaplari -> o soru silinir
"""
import json
import re

INPUT = "data/processed/istanbul.json"

# --- 1. Opening hours kural tabani ---
# (cuisine_pattern, tags_pattern, default_hours)
HOURS_RULES = [
    # Kahvalti / breakfast
    (r"kahvalt|breakfast", None, "Mo-Su 08:00-16:00"),
    # Kafe
    (r"kafe|cafe|pastane", None, "Mo-Su 08:00-22:00"),
    # Fine dining / üst segment
    (None, r"fine.dining|tasting.menu", "Tu-Su 18:00-23:30"),
    # Meyhane - gece geç
    (r"meyhane", None, "Mo-Su 12:00-01:00"),
    # Balık
    (r"balık|balik|seafood|fish", None, "Mo-Su 12:00-23:00"),
    # Sushi / Japon
    (r"sushi|japon", None, "Mo-Su 12:00-23:00"),
    # Pizza / İtalyan
    (r"pizza|italyan|italian", None, "Mo-Su 12:00-23:30"),
    # Burger / Steak
    (r"burger|steak", None, "Mo-Su 11:00-23:30"),
    # Pide
    (r"pide|pideci", None, "Mo-Su 08:00-22:00"),
    # Kebap / döner / lahmacun
    (r"kebap|kebab|döner|doner|lahmacun", None, "Mo-Su 10:30-23:30"),
    # Lokanta / ev yemekleri - öğle ağırlıklı
    (r"lokanta|ev.yemek", None, "Mo-Sa 10:00-22:00"),
    # Dünya mutfağı / fusion
    (r"dünya|dunya|fusion|uluslararas", None, "Mo-Su 12:00-23:00"),
    # Türk mutfağı genel
    (r"türk|turk", None, "Mo-Su 11:00-23:00"),
    # Fallback
    (None, None, "Mo-Su 11:00-23:00"),
]

def estimate_hours(cuisine: str, tags: list, price_range: int) -> str:
    cuisine_l = (cuisine or "").lower()
    tags_str = " ".join(tags or []).lower()

    # Price 4 = fine dining -> gece servisi
    if price_range == 4:
        return "Tu-Su 18:00-23:30"

    for cuisine_pat, tags_pat, hours in HOURS_RULES:
        c_match = cuisine_pat is None or re.search(cuisine_pat, cuisine_l, re.I)
        t_match = tags_pat is None or re.search(tags_pat, tags_str, re.I)
        if c_match and t_match:
            return hours

    return "Mo-Su 11:00-23:00"


# --- 2. verified_data logic ---
def compute_verified(r: dict) -> bool:
    score = 0
    if r.get("opening_hours"):     score += 2
    if r.get("nearby"):            score += 2
    if r.get("faq"):               score += 1
    if r.get("avg_rating"):        score += 1
    if r.get("review_count", 0) > 50: score += 1
    if r.get("lat") and r.get("lng"): score += 1
    if (r.get("special_features") or {}).get("popularDishes"): score += 1
    return score >= 7  # 9 üzerinden 7+


# --- 3. FAQ cleanup ---
BAD_PATTERNS = [
    r"bilgi mevcut de",
    r"bilgi yok",
    r"mevcut de\b",
    r"bilgi bulunmamakt",
]

def clean_faq(faq: list) -> list:
    cleaned = []
    for item in faq:
        answer = item.get("answer", "")
        is_bad = any(re.search(p, answer, re.I) for p in BAD_PATTERNS)
        if not is_bad:
            cleaned.append(item)
    return cleaned


def main():
    with open(INPUT, encoding="utf-8") as f:
        restaurants = json.load(f)

    hours_filled = 0
    hours_already = 0
    verified_set = 0
    faq_cleaned = 0
    faq_items_removed = 0

    for r in restaurants:
        name_safe = r.get("name", "").encode("ascii", "replace").decode()

        # 1. Opening hours
        if not r.get("opening_hours"):
            h = estimate_hours(r.get("cuisine", ""), r.get("tags", []), r.get("price_range", 2))
            r["opening_hours"] = h
            r["hours_estimated"] = True  # flag - gercek degil
            hours_filled += 1
        else:
            hours_already += 1

        # 2. verified_data
        v = compute_verified(r)
        r["verified_data"] = v
        if v:
            verified_set += 1

        # 3. FAQ cleanup
        faq = r.get("faq", [])
        if faq:
            before = len(faq)
            r["faq"] = clean_faq(faq)
            removed = before - len(r["faq"])
            if removed:
                faq_cleaned += 1
                faq_items_removed += removed

    with open(INPUT, "w", encoding="utf-8") as f:
        json.dump(restaurants, f, ensure_ascii=False, indent=2)

    print(f"[OK] Opening hours: {hours_filled} tahmini eklendi, {hours_already} zaten vardı")
    print(f"[OK] verified_data=true: {verified_set}/{len(restaurants)}")
    print(f"[OK] FAQ temizlendi: {faq_cleaned} restoran, {faq_items_removed} soru silindi")


if __name__ == "__main__":
    main()
