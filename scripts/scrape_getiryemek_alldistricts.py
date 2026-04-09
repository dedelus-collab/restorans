# -*- coding: utf-8 -*-
"""
Her restoran için 39 İstanbul ilçesini dener.
[name-slug]-[district-slug]-istanbul formatı.
GetirYemek SSR -> requests ile menü çekme.
"""

import json, re, time, random, sys
import requests
from bs4 import BeautifulSoup

INPUT = "data/processed/istanbul.json"
SAVE_EVERY = 20
BASE = "https://getir.com/yemek/restoran"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "tr-TR,tr;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
}

TR_MAP = {
    "ş":"s","ç":"c","ğ":"g","ü":"u","ö":"o","ı":"i",
    "â":"a","î":"i","û":"u",
    "Ş":"s","Ç":"c","Ğ":"g","Ü":"u","Ö":"o","İ":"i","I":"i",
}

# İstanbul'un 39 ilçesi
DISTRICTS = [
    "adalar","arnavutkoy","atasehir","avcilar","bagcilar","bahcelievler",
    "bakirkoy","basaksehir","bayrampasa","besiktas","beykoz","beylikduzu",
    "beyoglu","buyukcekmece","catalca","cekmekoy","esenler","esenyurt",
    "eyupsultan","fatih","gaziosmanpasa","gungoren","kadikoy","kagithane",
    "kartal","kucukcekmece","maltepe","pendik","sancaktepe","sariyer",
    "silivri","sisli","sultanbeyli","sultangazi","sile","tuzla",
    "umraniye","uskudar","zeytinburnu",
]


def slugify(t: str) -> str:
    for k, v in TR_MAP.items():
        t = t.replace(k, v)
    t = t.lower()
    t = re.sub(r"[^a-z0-9\s-]", "", t)
    t = re.sub(r"\s+", "-", t.strip())
    return re.sub(r"-+", "-", t)


def extract_menu(html: str) -> list:
    soup = BeautifulSoup(html, "html.parser")
    nd = soup.find("script", id="__NEXT_DATA__")
    if not nd:
        return []
    try:
        cats = json.loads(nd.string)["props"]["pageProps"]["initialState"][
            "restaurantDetail"]["menu"]["productCategories"]
        items, seen = [], set()
        for cat in cats:
            for p in cat.get("products", []):
                n = p.get("name", "").strip()
                price = p.get("priceText", "")
                if n and n not in seen and 1 < len(n) < 80:
                    seen.add(n)
                    items.append(f"{n} ({price})" if price else n)
            if len(items) >= 15:
                break
        return items[:15]
    except:
        return []


def try_slug(slug: str, session: requests.Session) -> list:
    url = f"{BASE}/{slug}/"
    try:
        r = session.get(url, timeout=8)
        if r.status_code == 200:
            return extract_menu(r.text)
    except:
        pass
    return []


def run():
    with open(INPUT, encoding="utf-8") as f:
        restaurants = json.load(f)

    targets = [r for r in restaurants if not r.get("menu_items")]
    print(f"[INFO] {len(targets)} restoran | 39 ilçe × her restoran", flush=True)

    session = requests.Session()
    session.headers.update(HEADERS)

    found = 0

    for i, r in enumerate(targets):
        name_safe = r["name"].encode("ascii", "replace").decode()
        n_slug = slugify(r["name"])

        # İsimden gürültü temizle
        clean_slug = re.sub(r"\b(restaurant|cafe|bistro|bar|lokanta|lokantasi|evi|koftecisi|grill|house)\b", "", n_slug)
        clean_slug = re.sub(r"-+", "-", clean_slug).strip("-")

        print(f"[{i+1}/{len(targets)}] {name_safe}", flush=True, end="")

        found_slug = None
        items = []

        # Önce neighborhood'dan district tahmin et
        hood = r.get("neighborhood", "")
        # Bazı neighborhood isimleri ilçe adıyla aynı
        hood_slug = slugify(hood.replace(" Mahallesi", "").replace(" mahallesi", ""))

        # Önce tahmin et: hood_slug ile dene
        priority_slugs = []
        if hood_slug and hood_slug in DISTRICTS:
            priority_slugs.append(f"{n_slug}-{hood_slug}-istanbul")
            if clean_slug != n_slug:
                priority_slugs.append(f"{clean_slug}-{hood_slug}-istanbul")

        # Sonra tüm ilçeleri dene
        for slug_base in ([n_slug] + ([clean_slug] if clean_slug != n_slug else [])):
            for district in (priority_slugs and [] or DISTRICTS):
                if district in priority_slugs:
                    continue
                priority_slugs.append(f"{slug_base}-{district}-istanbul")

        for slug in priority_slugs:
            menu = try_slug(slug, session)
            if menu and len(menu) >= 2:
                items = menu
                found_slug = slug
                break
            time.sleep(0.15)  # ~6 req/sec

        if items:
            for orig in restaurants:
                if orig["id"] == r["id"]:
                    orig["menu_items"] = items
                    orig["menu_source"] = "getiryemek"
                    break
            found += 1
            print(f" -> OK ({len(items)} item) | {found_slug.split('-istanbul')[0][-25:]}", flush=True)
        else:
            print(f" -> yok", flush=True)

        if (i + 1) % SAVE_EVERY == 0:
            with open(INPUT, "w", encoding="utf-8") as f:
                json.dump(restaurants, f, ensure_ascii=False, indent=2)
            total = sum(1 for r2 in restaurants if r2.get("menu_items"))
            print(f">>> KAYIT {i+1}/{len(targets)} | Yeni: {found} | Toplam: {total}/453", flush=True)

    with open(INPUT, "w", encoding="utf-8") as f:
        json.dump(restaurants, f, ensure_ascii=False, indent=2)

    total = sum(1 for r2 in restaurants if r2.get("menu_items"))
    print(f"\n[SONUÇ] +{found} menü | Toplam: {total}/453", flush=True)


if __name__ == "__main__":
    run()
