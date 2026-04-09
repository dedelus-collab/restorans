# -*- coding: utf-8 -*-
"""
menufiyatlar.com ve menuvefiyat.com.tr'den gercek menu verileri ceker.
DuckDuckGo ile restoran sayfasini bulup menu itemlarini alir.

Kullanim: python scripts/scrape_menu_sites.py
"""

import json
import re
import time
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "tr-TR,tr;q=0.9",
}

NOISE = {
    "hakkında", "iletişim", "anasayfa", "home", "copyright", "gizlilik",
    "kullanım koşulları", "bize ulaşın", "galeri", "photos", "similar posts",
    "yazi gezinmesi", "yazı gezinmesi", "scroll", "next", "previous",
    "sosyal medya", "takip et", "paylaş", "abone ol", "bülten",
}


def clean_text(text: str) -> str:
    text = re.sub(r'\d+[\s.,]*(TL|₺|lira)?', '', text)
    text = re.sub(r'\(.*?\)', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def is_valid_item(text: str) -> bool:
    if len(text) < 3 or len(text) > 60:
        return False
    lower = text.lower()
    if any(n in lower for n in NOISE):
        return False
    if re.match(r'^[\d\s₺TL.,\-+%]+$', text):
        return False
    return True


def search_ddg(name: str, site: str) -> str | None:
    """DuckDuckGo'da belirli sitede restoran arar."""
    query = f"{name} istanbul menu site:{site}"
    try:
        r = requests.get(
            f"https://html.duckduckgo.com/html/?q={query.replace(' ', '+')}",
            headers=HEADERS, timeout=8
        )
        soup = BeautifulSoup(r.text, 'html.parser')
        for result in soup.select('.result'):
            url_el = result.select_one('.result__url')
            if url_el:
                url = url_el.get_text().strip()
                if site in url and 'menu' in url.lower():
                    if not url.startswith('http'):
                        url = 'https://' + url
                    return url
        # Fallback: ilk sonuc
        first = soup.select_one('.result__url')
        if first:
            url = first.get_text().strip()
            if site in url:
                if not url.startswith('http'):
                    url = 'https://' + url
                return url
    except:
        pass
    return None


def scrape_page(url: str) -> list:
    """Sayfa URL'sinden menu itemlarini ceker."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code != 200:
            return []
        soup = BeautifulSoup(r.text, 'html.parser')
        items = []
        seen = set()
        for tag in ['h2', 'h3', 'h4', 'li', 'td', 'th']:
            for el in soup.select(tag):
                text = clean_text(el.get_text().strip())
                if text and text not in seen and is_valid_item(text):
                    items.append(text)
                    seen.add(text)
        return items[:12]
    except:
        return []


def main():
    input_path = "data/processed/istanbul.json"

    with open(input_path, encoding="utf-8") as f:
        restaurants = json.load(f)

    total = len(restaurants)
    found = 0
    print(f"[INFO] {total} restoran icin menu taranacak...", flush=True)

    SITES = ["menufiyatlar.com", "menuvefiyat.com.tr"]

    for i, r in enumerate(restaurants):
        if r.get("menu_source") in ("yemeksepeti", "website") or len(r.get("menu_items") or []) >= 5:
            continue

        name_safe = r["name"].encode("ascii", "replace").decode()
        print(f"[{i+1}/{total}] {name_safe}", flush=True)

        items = []
        source = None

        for site in SITES:
            url = search_ddg(r["name"], site)
            if url:
                # İsim doğrulama - URL veya sayfada restoran adının ilk kelimesi geçmeli
                name_first = r["name"].split()[0].lower()
                if name_first not in url.lower():
                    print(f"  {site}: eslesme yok, atlandi", flush=True)
                    time.sleep(1)
                    continue
                print(f"  {site}: {url[:60]}", flush=True)
                items = scrape_page(url)
                if len(items) >= 3:
                    source = site
                    break
            time.sleep(1)  # DDG rate limit

        if items and len(items) >= 3:
            for orig in restaurants:
                if orig["id"] == r["id"]:
                    orig["menu_items"] = items
                    orig["menu_source"] = source
                    break
            found += 1
            print(f"  OK: {len(items)} item | {[x.encode('ascii','replace').decode() for x in items[:3]]}", flush=True)
        else:
            print(f"  Bulunamadi", flush=True)

        if (i + 1) % 15 == 0:
            with open(input_path, "w", encoding="utf-8") as f:
                json.dump(restaurants, f, ensure_ascii=False, indent=2)
            print(f">>> KAYIT: {i+1}/{total} | Bulunan: {found}", flush=True)

        time.sleep(2)

    with open(input_path, "w", encoding="utf-8") as f:
        json.dump(restaurants, f, ensure_ascii=False, indent=2)

    print(f"\n[OK] {found}/{total} restoran icin gercek menu bulundu", flush=True)
    print("[SONRAKI] python scripts/json_to_ts.py", flush=True)


if __name__ == "__main__":
    main()
