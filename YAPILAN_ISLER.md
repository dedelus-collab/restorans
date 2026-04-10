# Retoralla — Yapılan İşler

## Proje Nedir?
İstanbul restoranları için yapay zeka botlarının (ChatGPT, Perplexity vb.) referans kaynak olarak kullanacağı AI-native platform.

---

## Altyapı

### Next.js Kurulumu
- Next.js 16.2.2, TypeScript, Tailwind CSS
- App Router yapısı: `/`, `/istanbul`, `/istanbul/[slug]`

### AI-Native Dosyalar
- `public/robots.txt` — GPTBot, ChatGPT-User, PerplexityBot, ClaudeBot, anthropic-ai açık bırakıldı
- `public/.well-known/llms.txt` — AI botları için platform açıklaması ve API kullanım örnekleri
- Her restoran sayfasına Schema.org JSON-LD eklendi (Restaurant, AggregateRating, GeoCoordinates)

### API
- `GET /api/restaurants` — city, tags, cuisine, maxPrice, minRating filtreleri
- `GET /api/restaurants/[id]` — tekil restoran JSON

### Sitemap
- `app/sitemap.ts` — tüm şehir ve restoran sayfaları dinamik olarak üretiliyor

---

## Veri Pipeline

### 1. OSM Scraping (`scripts/scrape_osm.py`)
- OpenStreetMap Overpass API'den İstanbul restoranları çekildi
- **453 restoran** toplandı

### 2. Adres Doldurma (`scripts/enrich_addresses.py`)
- Nominatim reverse geocoding ile 453/453 adres dolduruldu

### 3. Google Maps Puanları (`scripts/scrape_ratings.py`)
- Playwright ile rating, review_count, cuisine, opening_hours, tags çekildi
- 440 restoran için puan bilgisi dolduruldu

### 4. İçerik Zenginleştirme (`scripts/enrich_content.py`)
- Tag zenginleştirme (mahalle bazlı romantik/manzaralı tespiti)
- 453 restoran işlendi

### 5. Özet Üretimi (`scripts/generate_summaries.py`)
- Groq llama-3.1-8b-instant ile llm_summary + sentiment_summary üretildi
- 453 restoran için temel özet oluşturuldu

### 6. Gerçek Yorum Scraping (`scripts/scrape_reviews.py`)
- Playwright ile Google Maps'ten gerçek kullanıcı yorumları çekildi
- Groq llama-3.3-70b ile zengin içerik üretildi
- 57 restoran tamamlandı (gerçek yoruma dayalı)

### 7. Special Features Çıkarımı (`scripts/extract_special_features.py`)
- Kural tabanlı: contextualRatings, noiseLevel, avgMealCost, dietaryOptions — 453/453
- Groq tabanlı: signatureDishes, standoutPlus, criticalMinus — 57 yorumlu restoran

### 8. Özet Zenginleştirme (`scripts/enrich_summaries.py`) ← DEVAM EDİYOR
- Playwright olmadan sadece mevcut veri + Groq ile daha uzun/kaliteli özetler
- Hedef: 453/453 restoran için 4-5 cümlelik kaliteli llm_summary

---

## Veri Durumu (Güncel)

| Alan | Dolu | Toplam |
|------|------|--------|
| Temel bilgiler | 453 | 453 |
| Puan & yorum sayısı | 440 | 453 |
| Adres | 453 | 453 |
| Mutfak türü | 391 | 453 |
| Çalışma saatleri | 225 | 453 |
| llm_summary | 453 | 453 |
| Gerçek yoruma dayalı içerik | ~62 | 453 |
| specialFeatures | 453 | 453 |
| contextualRatings | 453 | 453 |

---

## Sayfa Yapısı

### `/istanbul` (Şehir Sayfası)
- Dataset + ItemList JSON-LD
- Mahalle gruplandırması
- Restoran listesi (puan, etiket, fiyat)

### `/istanbul/[slug]` (Restoran Sayfası)
- Restaurant Schema.org JSON-LD (tüm alanlar)
- AI Özeti (llm_summary)
- Temel bilgiler, çalışma saatleri, harita linki
- Bağlamsal Puanlar (iş yemeği, romantik, aile...)
- İmza Yemekler
- Yorum Analizi (standoutPlus, criticalMinus)
- Highlights
- Özellikler, Diyet Seçenekleri, Etiketler
- Güven sinyalleri (confidenceScore, lastUpdated)
- Makine-okunabilir JSON linki

---

## Kullanılan Teknolojiler
- **Next.js 16.2.2** — App Router, TypeScript, Tailwind
- **Groq API** — llama-3.1-8b-instant, llama-3.3-70b-versatile
- **Playwright** — Google Maps scraping
- **OpenStreetMap** — Overpass API (ücretsiz restoran verisi)
- **Nominatim** — Reverse geocoding (ücretsiz adres)

---

## Bekleyen İşler
- [ ] enrich_summaries.py tamamlanması (393 restoran kaldı)
- [ ] json_to_ts.py çalıştırıp TypeScript güncelleme
- [ ] Vercel'e deploy
