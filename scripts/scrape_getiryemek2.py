# -*- coding: utf-8 -*-
"""
GetirYemek'ten requests ile menü çeker (tarayıcı gerekmez, SSR).
Slug tabanlı URL: https://getir.com/yemek/restoran/[slug]/
"""

import json, re, time, random
import requests
from bs4 import BeautifulSoup

INPUT = "data/processed/istanbul.json"
SAVE_EVERY = 15
BASE = "https://getir.com/yemek/restoran"
SEARCH_API = "https://food-client-api-gateway.getirapi.com/restaurants"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "tr-TR,tr;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

FOOD_WORDS = [
    "kebap","köfte","pilav","çorba","salata","börek","omlet","meze","pide",
    "tatlı","pasta","pizza","burger","sandviç","döner","ızgara","tava","güveç",
    "balık","tavuk","et","lahmacun","sushi","ramen","waffle","krep",
    "soup","salad","chicken","beef","fish","dessert","appetizer","rice",
    "kahvaltı","serpme","menemen","gözleme","mantı","hummus","falafel",
    "tempura","gyoza","edamame","roll","nigiri","maki","sashimi","wrap",
    "steak","schnitzel","risotto","shawarma","burrito","taco","cheesecake",
    "tiramisu","baklava","künefe","kadayıf","simit","poğaça",
    "corba","kofte","izgara","pilaf","borek","tatli","gozleme","manti",
    "iskender","adana","urfa","lahmacun","kumpir","durum",
]

def has_food(text: str) -> bool:
    t = text.lower()
    return any(f in t for f in FOOD_WORDS)


def slugify(text: str) -> str:
    """TR karakterlerini normalize et, slug yap."""
    TR = {"ş":"s","ç":"c","ğ":"g","ü":"u","ö":"o","ı":"i","â":"a","î":"i","û":"u",
          "Ş":"s","Ç":"c","Ğ":"g","Ü":"u","Ö":"o","İ":"i","I":"i","Â":"a"}
    for k, v in TR.items():
        text = text.replace(k, v)
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"\s+", "-", text.strip())
    text = re.sub(r"-+", "-", text)
    return text


def extract_menu_from_html(html: str, min_items=3) -> list:
    """HTML'den h4 tabanlı menü itemlarını çıkar."""
    soup = BeautifulSoup(html, "html.parser")
    items = []
    seen = set()

    for h4 in soup.find_all("h4"):
        text = h4.get_text(strip=True).splitlines()[0] if h4.get_text() else ""
        text = text.strip()
        if not text or len(text) < 2 or len(text) > 80:
            continue
        if text in seen:
            continue
        seen.add(text)
        items.append(text)

    if len(items) < min_items:
        # h3 kategorilerden yemek olanları ekle
        for h3 in soup.find_all("h3"):
            text = h3.get_text(strip=True).splitlines()[0]
            text = text.strip()
            if not text or len(text) < 2 or len(text) > 60:
                continue
            if text in seen or not has_food(text):
                continue
            seen.add(text)
            items.append(text)

    return items[:15]


def get_menu_by_slug(slug: str, session: requests.Session) -> list:
    """Verilen slug ile GetirYemek sayfasını çek ve menüyü döndür."""
    url = f"{BASE}/{slug}/"
    try:
        r = session.get(url, timeout=10)
        if r.status_code != 200:
            return []
        items = extract_menu_from_html(r.text)
        return items
    except Exception as e:
        return []


def build_candidate_slugs(name: str, district: str) -> list:
    """Restoran adı ve ilçeden olası GetirYemek slug listesi üret."""
    name_slug = slugify(name)
    dist_slug = slugify(district) if district else ""
    candidates = []

    # En olası format: name-district-istanbul
    if dist_slug:
        candidates.append(f"{name_slug}-{dist_slug}-istanbul")
        candidates.append(f"{name_slug}-istanbul-{dist_slug}")

    # Sadece isim ve istanbul
    candidates.append(f"{name_slug}-istanbul")
    candidates.append(f"{name_slug}")

    # İlk kelime + istanbul
    first_word = name_slug.split("-")[0]
    if first_word != name_slug and dist_slug:
        candidates.append(f"{first_word}-{dist_slug}-istanbul")
        candidates.append(f"{first_word}-istanbul")

    return candidates


def search_on_getir_api(name: str, session: requests.Session) -> list | None:
    """
    GetirYemek'in food-client-api'sini kullanarak restoran slug listesi bul.
    Bu endpoint /restaurants search yapabiliyorsa kullan.
    """
    # Slug ile direkt /restaurants endpoint'ini dene
    slug = slugify(name)
    api_headers = {
        **HEADERS,
        "Accept": "application/json",
        "Origin": "https://getir.com",
        "Referer": "https://getir.com/",
    }
    try:
        # Slug'dan restaurant bul
        r = session.get(
            f"https://food-client-api-gateway.getirapi.com/restaurants?slug={slug}",
            headers=api_headers, timeout=8
        )
        if r.status_code == 200:
            data = r.json()
            restaurants = data.get("data", {}).get("restaurants", [])
            return [r.get("slug") for r in restaurants if r.get("slug") and "istanbul" in r.get("slug","")]
    except:
        pass
    return None


def run():
    with open(INPUT, encoding="utf-8") as f:
        restaurants = json.load(f)

    targets = [r for r in restaurants if not r.get("menu_items")]
    print(f"[INFO] {len(targets)} restoran hedefleniyor (requests, no browser)", flush=True)

    session = requests.Session()
    session.headers.update(HEADERS)

    found = 0
    not_found = 0

    for i, r in enumerate(targets):
        name_safe = r["name"].encode("ascii", "replace").decode()
        district = r.get("district", "")
        print(f"[{i+1}/{len(targets)}] {name_safe} | {district}", flush=True)

        items = []
        matched_slug = None

        # 1. Arama API dene (hızlı)
        api_slugs = search_on_getir_api(r["name"], session)
        if api_slugs:
            for slug in api_slugs[:3]:
                menu = get_menu_by_slug(slug, session)
                if menu and len(menu) >= 3:
                    items = menu
                    matched_slug = slug
                    break

        # 2. Slug tahminleri ile dene
        if not items:
            candidates = build_candidate_slugs(r["name"], district)
            for slug in candidates[:4]:
                menu = get_menu_by_slug(slug, session)
                if menu and len(menu) >= 3:
                    items = menu
                    matched_slug = slug
                    break
                time.sleep(random.uniform(0.3, 0.7))

        if items and len(items) >= 2:
            for orig in restaurants:
                if orig["id"] == r["id"]:
                    orig["menu_items"] = items
                    orig["menu_source"] = "getiryemek"
                    break
            found += 1
            print(f"  OK: {len(items)} item | slug: {matched_slug}", flush=True)
            print(f"    -> {[x.encode('ascii','replace').decode() for x in items[:3]]}", flush=True)
        else:
            not_found += 1
            print(f"  Bulunamadi", flush=True)

        if (i + 1) % SAVE_EVERY == 0:
            with open(INPUT, "w", encoding="utf-8") as f:
                json.dump(restaurants, f, ensure_ascii=False, indent=2)
            total = sum(1 for r2 in restaurants if r2.get("menu_items"))
            print(f">>> KAYIT {i+1}/{len(targets)} | Yeni: {found} | Toplam: {total}/453", flush=True)

        # İnsan gibi bekleme
        time.sleep(random.uniform(0.8, 2.0))

    with open(INPUT, "w", encoding="utf-8") as f:
        json.dump(restaurants, f, ensure_ascii=False, indent=2)

    total = sum(1 for r2 in restaurants if r2.get("menu_items"))
    print(f"\n[SONUÇ] {found} yeni menü | Toplam: {total}/453", flush=True)


if __name__ == "__main__":
    run()
