# -*- coding: utf-8 -*-
"""
GetirYemek'ten __NEXT_DATA__ ile menü çeker.
- requests kütüphanesi, tarayıcı gerekmez
- productCategories > products > name → gerçek menü isimleri
- Slug tabanlı URL, farklı varyasyonlar dener
"""

import json, re, time, random
import requests
from bs4 import BeautifulSoup

INPUT = "data/processed/istanbul.json"
SAVE_EVERY = 15
BASE = "https://getir.com/yemek/restoran"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "tr-TR,tr;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
}

TR_MAP = {
    "ş": "s", "ç": "c", "ğ": "g", "ü": "u", "ö": "o", "ı": "i",
    "â": "a", "î": "i", "û": "u",
    "Ş": "s", "Ç": "c", "Ğ": "g", "Ü": "u", "Ö": "o", "İ": "i", "I": "i",
}


def slugify(text: str) -> str:
    for k, v in TR_MAP.items():
        text = text.replace(k, v)
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"\s+", "-", text.strip())
    text = re.sub(r"-+", "-", text)
    return text


def extract_menu_from_next_data(html: str) -> list:
    """
    __NEXT_DATA__ içindeki productCategories'den ürün isimlerini çıkar.
    Fiyat da varsa ekle.
    """
    soup = BeautifulSoup(html, "html.parser")
    nd = soup.find("script", id="__NEXT_DATA__")
    if not nd:
        return []

    try:
        data = json.loads(nd.string)
    except:
        return []

    # Yolu bul: props.pageProps.initialState.restaurantDetail.menu.productCategories
    try:
        state = data["props"]["pageProps"]["initialState"]
        product_cats = state["restaurantDetail"]["menu"]["productCategories"]
    except (KeyError, TypeError):
        return []

    items = []
    seen = set()
    for cat in product_cats:
        for product in cat.get("products", []):
            name = product.get("name", "").strip()
            price = product.get("priceText", "")
            if not name or name in seen or len(name) < 2:
                continue
            seen.add(name)
            if price:
                items.append(f"{name} ({price})")
            else:
                items.append(name)
        if len(items) >= 15:
            break

    return items[:15]


def build_slug_candidates(name: str, district: str, lat: float = None, lon: float = None) -> list:
    """Olası GetirYemek slug'larını üret."""
    n = slugify(name)
    d = slugify(district) if district else ""
    candidates = []

    # Format 1: name-district-istanbul (en yaygın)
    if d:
        candidates.append(f"{n}-{d}-istanbul")
    candidates.append(f"{n}-istanbul")

    # Format 2: name-mah-district-istanbul (mahalle kısa adı)
    # Bazı sluglar: "hamdi-restaurant-istanbul" gibi
    # name'in son kelimesi "restaurant/cafe/bistro" ise kısalt
    clean_n = re.sub(r"\b(restaurant|cafe|bistro|bar|lokanta|lokantasi|evi|koftecisi|kebap|pizza|grill)\b", "", n, flags=re.I)
    clean_n = re.sub(r"-+", "-", clean_n).strip("-")
    if clean_n != n:
        if d:
            candidates.append(f"{clean_n}-{d}-istanbul")
        candidates.append(f"{clean_n}-istanbul")

    # İlk kelime
    first = n.split("-")[0]
    if first != n and len(first) > 2:
        if d:
            candidates.append(f"{first}-{d}-istanbul")
        candidates.append(f"{first}-istanbul")

    return list(dict.fromkeys(candidates))  # deduplicate


def try_get_menu(slug: str, session: requests.Session) -> list:
    url = f"{BASE}/{slug}/"
    try:
        r = session.get(url, timeout=10)
        if r.status_code != 200:
            return []
        return extract_menu_from_next_data(r.text)
    except Exception:
        return []


def run():
    with open(INPUT, encoding="utf-8") as f:
        restaurants = json.load(f)

    targets = [r for r in restaurants if not r.get("menu_items")]
    print(f"[INFO] {len(targets)} restoran hedefleniyor (GetirYemek NEXT_DATA)", flush=True)

    session = requests.Session()
    session.headers.update(HEADERS)

    found = 0

    for i, r in enumerate(targets):
        name_safe = r["name"].encode("ascii", "replace").decode()
        district = r.get("district", "")
        lat = r.get("lat")
        lon = r.get("lon")
        print(f"[{i+1}/{len(targets)}] {name_safe}", flush=True)

        items = []
        matched_slug = None

        candidates = build_slug_candidates(r["name"], district, lat, lon)

        for slug in candidates[:6]:
            menu = try_get_menu(slug, session)
            if menu and len(menu) >= 2:
                items = menu
                matched_slug = slug
                break
            time.sleep(random.uniform(0.3, 0.6))

        if items:
            for orig in restaurants:
                if orig["id"] == r["id"]:
                    orig["menu_items"] = items
                    orig["menu_source"] = "getiryemek"
                    break
            found += 1
            print(f"  OK: {len(items)} item | {matched_slug}", flush=True)
            print(f"    -> {[x.encode('ascii','replace').decode() for x in items[:3]]}", flush=True)
        else:
            print(f"  Bulunamadi", flush=True)

        if (i + 1) % SAVE_EVERY == 0:
            with open(INPUT, "w", encoding="utf-8") as f:
                json.dump(restaurants, f, ensure_ascii=False, indent=2)
            total = sum(1 for r2 in restaurants if r2.get("menu_items"))
            print(f">>> KAYIT {i+1}/{len(targets)} | Yeni: {found} | Toplam: {total}/453", flush=True)

        time.sleep(random.uniform(0.5, 1.5))

    with open(INPUT, "w", encoding="utf-8") as f:
        json.dump(restaurants, f, ensure_ascii=False, indent=2)

    total = sum(1 for r2 in restaurants if r2.get("menu_items"))
    print(f"\n[SONUÇ] {found} yeni menü | Toplam: {total}/453", flush=True)


if __name__ == "__main__":
    run()
