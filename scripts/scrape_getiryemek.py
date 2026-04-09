# -*- coding: utf-8 -*-
"""
GetirYemek'ten menü çeker.
URL: https://getir.com/yemek/restoran/[slug]/
h4 taglerinde yemek isimleri, h3'te kategoriler var.
"""

import json, re, asyncio, random
from urllib.parse import quote
from playwright.async_api import async_playwright

INPUT = "data/processed/istanbul.json"
SAVE_EVERY = 10
BASE = "https://getir.com"

FOOD_WORDS = [
    "kebap","köfte","pilav","çorba","salata","börek","omlet","meze","pide",
    "tatlı","pasta","pizza","burger","sandviç","döner","ızgara","tava","güveç",
    "balık","tavuk","et","lahmacun","sushi","ramen","waffle","krep",
    "soup","salad","chicken","beef","fish","dessert","appetizer","rice",
    "kahvaltı","serpme","menemen","gözleme","mantı","hummus","falafel",
    "tempura","gyoza","edamame","roll","nigiri","maki","sashimi",
    "steak","schnitzel","risotto","shawarma","wrap","burrito","taco",
    "latte","cappuccino","smoothie","milkshake","cheesecake","tiramisu",
    "baklava","künefe","kadayıf","simit","poğaça","açma","menemen",
    "corba","kofte","izgara","pilaf","borek","tatli","gozleme","manti",
]

NAV_WORDS = [
    "anasayfa","iletişim","hakkında","sepet","profil","kampanya","giriş","kayıt",
    "teslimat","kargo","şube","mağaza","bize ulaş","yardım","iade",
]

def has_food(text: str) -> bool:
    t = text.lower()
    return any(f in t for f in FOOD_WORDS)

def is_nav(text: str) -> bool:
    t = text.lower()
    return any(n in t for n in NAV_WORDS)

def make_slug(name: str) -> str:
    """Restoran adından URL slug üret."""
    slug = name.lower()
    slug = slug.replace("ş", "s").replace("ç", "c").replace("ğ", "g")
    slug = slug.replace("ü", "u").replace("ö", "o").replace("ı", "i")
    slug = slug.replace("İ", "i").replace("Ş", "s").replace("Ç", "c")
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug.strip())
    slug = re.sub(r"-+", "-", slug)
    return slug


async def find_restaurant_on_getir(page, name: str, district: str = "") -> str | None:
    """Getir Yemek'te restoranı arayıp URL döndür."""
    query = quote(f"{name} {district} istanbul".strip())
    search_url = f"{BASE}/yemek/?q={query}"

    try:
        await page.goto(search_url, wait_until="domcontentloaded", timeout=12000)
        await page.wait_for_timeout(1000 + random.randint(0, 500))
    except:
        return None

    # Sonuç kartlarını bul
    links = await page.query_selector_all("a[href*='/yemek/restoran/']")

    name_lower = name.lower()
    name_words = set(re.sub(r"[^a-z\s]", "", name_lower).split()) - {"ve", "ile", "de", "da"}

    for l in links[:10]:
        href = (await l.get_attribute("href") or "").strip()
        text = (await l.inner_text()).lower()
        href_lower = href.lower()

        # İsim kelimelerinden en az biri URL veya text'te var mı?
        slug = make_slug(name)
        first_word = list(name_words)[0] if name_words else ""

        if (first_word and first_word[:5] in href_lower) or \
           (first_word and first_word[:5] in text) or \
           (slug[:8] in href_lower):
            if not href.startswith("http"):
                href = BASE + href
            return href

    return None


async def get_menu(page, url: str) -> list:
    """Restoran sayfasından menü itemlarını çek."""
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=12000)
        await page.wait_for_timeout(1200 + random.randint(0, 800))
    except:
        return []

    # Çerez dialogunu kapat
    try:
        btn = await page.query_selector("button:has-text('Kabul')")
        if btn:
            await btn.click()
            await page.wait_for_timeout(500)
    except:
        pass

    # Lazy loading için scroll
    for _ in range(5):
        await page.mouse.wheel(0, random.randint(300, 600))
        await page.wait_for_timeout(random.randint(200, 400))
    await page.wait_for_timeout(1000)

    items = []
    seen = set()

    # h4 = yemek isimleri (en güvenilir)
    try:
        els = await page.query_selector_all("h4")
        for el in els[:50]:
            raw = (await el.inner_text()).strip().splitlines()[0]
            if raw and 2 < len(raw) < 70 and raw not in seen and not is_nav(raw):
                items.append(raw)
                seen.add(raw)
    except:
        pass

    # h3 = kategori isimleri (yiyecek ise ekle)
    if len(items) < 3:
        try:
            els = await page.query_selector_all("h3")
            for el in els[:30]:
                raw = (await el.inner_text()).strip().splitlines()[0]
                if raw and 2 < len(raw) < 60 and raw not in seen and has_food(raw) and not is_nav(raw):
                    items.append(raw)
                    seen.add(raw)
        except:
            pass

    # Yemek sinyali olan itemları filtrele veya tümünü döndür (h4 güvenilir)
    food_items = [x for x in items if has_food(x)]

    # h4'te yemek sinyali olmasa da ürün isimleri olabilir (sushi, steak adları)
    if food_items:
        return food_items[:15]
    elif len(items) >= 4:
        return items[:15]  # h4'teki tüm itemları güven
    return []


async def run():
    with open(INPUT, encoding="utf-8") as f:
        restaurants = json.load(f)

    targets = [r for r in restaurants if not r.get("menu_items")]
    print(f"[INFO] {len(targets)} restoran hedefleniyor", flush=True)

    found = 0
    not_found = 0

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
            ],
        )
        context = await browser.new_context(
            viewport={"width": 1366, "height": 768},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="tr-TR",
            timezone_id="Europe/Istanbul",
        )
        page = await context.new_page()

        for i, r in enumerate(targets):
            name_safe = r["name"].encode("ascii", "replace").decode()
            district = r.get("district", "")
            print(f"[{i+1}/{len(targets)}] {name_safe} | {district}", flush=True)

            try:
                # Önce GetirYemek'te ara
                url = await asyncio.wait_for(
                    find_restaurant_on_getir(page, r["name"], district),
                    timeout=18
                )

                if not url:
                    # Slug ile direkt dene
                    slug = make_slug(r["name"])
                    dist_slug = make_slug(district) if district else "istanbul"
                    url = f"{BASE}/yemek/restoran/{slug}-{dist_slug}-istanbul/"
                    # Kontrol et
                    try:
                        await page.goto(url, wait_until="domcontentloaded", timeout=8000)
                        await page.wait_for_timeout(500)
                        if "404" in await page.title() or page.url == BASE + "/yemek/":
                            url = None
                    except:
                        url = None

                if not url:
                    print(f"  Bulunamadi", flush=True)
                    not_found += 1
                    continue

                items = await asyncio.wait_for(get_menu(page, url), timeout=20)

                if items and len(items) >= 2:
                    for orig in restaurants:
                        if orig["id"] == r["id"]:
                            orig["menu_items"] = items
                            orig["menu_source"] = "getiryemek"
                            break
                    found += 1
                    print(f"  OK: {len(items)} item | {url.split('/')[-2]}", flush=True)
                    print(f"    -> {[x.encode('ascii','replace').decode() for x in items[:3]]}", flush=True)
                else:
                    print(f"  Menü bulunamadi ({len(items)} item) | {url.split('/')[-2]}", flush=True)
                    not_found += 1

            except asyncio.TimeoutError:
                print(f"  TIMEOUT", flush=True)
                try:
                    await page.close()
                    page = await context.new_page()
                except:
                    pass
            except Exception as e:
                print(f"  HATA: {str(e)[:80]}", flush=True)

            if (i + 1) % SAVE_EVERY == 0:
                with open(INPUT, "w", encoding="utf-8") as f:
                    json.dump(restaurants, f, ensure_ascii=False, indent=2)
                total = sum(1 for r2 in restaurants if r2.get("menu_items"))
                print(f">>> KAYIT {i+1}/{len(targets)} | Yeni: {found} | Toplam: {total}/453", flush=True)

            # İnsan gibi bekleme
            await asyncio.sleep(random.uniform(1.5, 3.5))

        await browser.close()

    with open(INPUT, "w", encoding="utf-8") as f:
        json.dump(restaurants, f, ensure_ascii=False, indent=2)

    total = sum(1 for r2 in restaurants if r2.get("menu_items"))
    print(f"\n[SONUÇ] {found} yeni menü | Toplam menülü: {total}/453", flush=True)


if __name__ == "__main__":
    asyncio.run(run())
