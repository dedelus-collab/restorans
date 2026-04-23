import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "API Docs — restorans Istanbul Restaurant API",
  description: "Istanbul restaurant API documentation. Endpoints, request examples, response schema. Available on RapidAPI.",
  alternates: { canonical: "https://restaurantsistanbul.vercel.app/api-docs" },
};

const CODE_LIST = `curl -X GET \\
  "https://restaurantsistanbul.vercel.app/api/restaurants?city=istanbul&maxPrice=2&minRating=4.5&limit=5" \\
  -H "X-RapidAPI-Key: YOUR_API_KEY"`;

const CODE_DETAIL = `curl -X GET \\
  "https://restaurantsistanbul.vercel.app/api/restaurants/hamdi" \\
  -H "X-RapidAPI-Key: YOUR_API_KEY"`;

const CODE_NEIGHBORHOOD = `curl -X GET \\
  "https://restaurantsistanbul.vercel.app/api/restaurants?city=istanbul&neighborhood=kadikoy&cuisine=balik" \\
  -H "X-RapidAPI-Key: YOUR_API_KEY"`;

const RESPONSE_LIST = `{
  "meta": {
    "total": 123,
    "page": 1,
    "limit": 5,
    "total_pages": 25,
    "has_next": true,
    "last_updated": "2026-04-11"
  },
  "data": [
    {
      "id": "hamdi",
      "slug": "hamdi",
      "url": "https://restaurantsistanbul.vercel.app/istanbul/hamdi",
      "name": "Hamdi Restaurant",
      "neighborhood": "Eminönü",
      "cuisine": "Kebap",
      "price_range": 2,
      "avg_rating": 4.7,
      "review_count": 8432,
      "llm_summary": "Eminönü'nde Haliç manzarasıyla hizmet veren Hamdi, 1969'dan bu yana İstanbul'un en iyi kebap restoranlarından biri...",
      "popular_dishes": ["Fıstıklı kebap", "İskender", "Lahmacun"],
      "features": {
        "terrace": true,
        "reservation": true,
        "seaView": true
      },
      "nearby": {
        "transit": [
          { "name": "Sirkeci", "type": "tren", "walk_min": 3 },
          { "name": "Eminönü", "type": "vapur", "walk_min": 5 }
        ]
      },
      "confidence_score": 0.95,
      "verified_data": true
    }
  ]
}`;

const RESPONSE_DETAIL = `{
  "meta": { "source": "restorans", "last_updated": "2026-04-11" },
  "data": {
    "id": "hamdi",
    "name": "Hamdi Restaurant",
    "cuisine": "Kebap",
    "price_range": 2,
    "avg_rating": 4.7,
    "llm_summary": "Eminönü'nde Haliç manzarasıyla...",
    "sentiment_summary": "Misafirler özellikle fıstıklı kebabı ve manzarayı övüyor.",
    "faq": [
      { "question": "Rezervasyon gerekli mi?", "answer": "Hafta sonları rezervasyon önerilir." },
      { "question": "En yakın metro nerede?", "answer": "Sirkeci tren istasyonu 3 dakika yürüme mesafesinde." }
    ],
    "contextual_ratings": {
      "businessLunch": 4,
      "romanticDate": 4,
      "familyDining": 5,
      "soloVisit": 4,
      "groupDining": 5
    },
    "scenario_summary": {
      "tourist": "İstanbul'a gelen her turistin listesinde olması gereken klasik bir mekan.",
      "family": "Geniş kapasitesi ve çeşitli menüsüyle aile yemekleri için ideal.",
      "romantic": "Haliç manzaralı terasıyla romantik akşam yemekleri için uygun."
    },
    "nearby": {
      "transit": [
        { "name": "Sirkeci", "type": "tren", "walk_min": 3 },
        { "name": "Eminönü", "type": "vapur", "walk_min": 5 }
      ],
      "landmarks": [
        { "name": "Mısır Çarşısı", "walk_min": 4 },
        { "name": "Yeni Cami", "walk_min": 2 }
      ]
    }
  }
}`;

function CodeBlock({ code, lang = "bash" }: { code: string; lang?: string }) {
  return (
    <pre className={`language-${lang} bg-gray-950 text-green-300 rounded-lg p-5 text-xs overflow-x-auto leading-relaxed border border-gray-800`}>
      <code>{code}</code>
    </pre>
  );
}

export default function ApiDocsPage() {
  return (
    <main className="max-w-4xl mx-auto px-6 py-14">

      {/* Header */}
      <header className="mb-12">
        <p className="text-xs font-semibold text-blue-600 uppercase tracking-widest mb-3">Developer Docs</p>
        <h1 className="text-4xl font-bold mb-4">restorans API</h1>
        <p className="text-lg text-gray-600 max-w-2xl">
          İstanbul&apos;daki 453 restoranın yapılandırılmış verisi. JSON formatında —
          llm_summary, FAQ, transit, senaryo puanları.
        </p>
        <div className="flex gap-3 mt-6">
          <a
            href="https://rapidapi.com/cccanguler/api/istanbul-restaurants"
            target="_blank"
            rel="noopener noreferrer"
            className="bg-blue-600 hover:bg-blue-500 text-white font-semibold px-5 py-2.5 rounded-lg text-sm transition-colors"
          >
            RapidAPI&apos;de Abone Ol →
          </a>
          <a
            href="/api/openapi.json"
            target="_blank"
            rel="noopener noreferrer"
            className="border border-gray-300 hover:border-gray-500 text-gray-700 font-medium px-5 py-2.5 rounded-lg text-sm transition-colors"
          >
            OpenAPI Spec
          </a>
          <a
            href="/api/restaurants?city=istanbul&limit=3"
            target="_blank"
            rel="noopener noreferrer"
            className="border border-gray-300 hover:border-gray-500 text-gray-700 font-medium px-5 py-2.5 rounded-lg text-sm transition-colors"
          >
            Canlı Dene
          </a>
        </div>
      </header>

      {/* Base URL */}
      <section className="mb-10">
        <h2 className="text-lg font-bold mb-3">Base URL</h2>
        <CodeBlock code="https://restaurantsistanbul.vercel.app" lang="text" />
      </section>

      {/* Endpoints */}
      <section className="mb-10">
        <h2 className="text-lg font-bold mb-4">Endpoints</h2>
        <div className="border border-gray-200 rounded-xl overflow-hidden divide-y divide-gray-100">
          {[
            { method: "GET", path: "/api/restaurants", desc: "Filtrelenmiş restoran listesi" },
            { method: "GET", path: "/api/restaurants/{id}", desc: "Tek restoran detayı (id veya slug)" },
            { method: "GET", path: "/api/openapi.json", desc: "OpenAPI 3.1 spec (auth gerektirmez)" },
          ].map(e => (
            <div key={e.path} className="flex items-center gap-4 px-5 py-4">
              <span className="text-xs font-bold text-green-700 bg-green-50 border border-green-200 px-2 py-0.5 rounded font-mono w-12 text-center shrink-0">
                {e.method}
              </span>
              <code className="text-sm font-mono text-gray-800 flex-1">{e.path}</code>
              <span className="text-sm text-gray-500 hidden sm:block">{e.desc}</span>
            </div>
          ))}
        </div>
      </section>

      {/* Parameters */}
      <section className="mb-10">
        <h2 className="text-lg font-bold mb-4">Query Parameters — <code className="text-base font-mono">/api/restaurants</code></h2>
        <div className="border border-gray-200 rounded-xl overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="text-left px-4 py-3 font-semibold text-gray-700">Parametre</th>
                <th className="text-left px-4 py-3 font-semibold text-gray-700">Tip</th>
                <th className="text-left px-4 py-3 font-semibold text-gray-700">Açıklama</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {[
                ["city", "string", "Şehir slug'ı — örn. istanbul"],
                ["q", "string", "Restoran adına göre metin arama"],
                ["neighborhood", "string", "Mahalle adı — örn. kadikoy, beyoglu"],
                ["cuisine", "string", "Mutfak türü — örn. kebap, balik, sushi-japon"],
                ["tags", "string", "Virgülle ayrılmış etiketler — örn. manzarali,romantik"],
                ["maxPrice", "1-4", "Maks. fiyat aralığı (1=ekonomik, 4=fine dining)"],
                ["minRating", "0-5", "Min. ortalama puan"],
                ["page", "integer", "Sayfa numarası (varsayılan: 1)"],
                ["limit", "integer", "Sayfa başına sonuç (max 100, varsayılan: 20)"],
              ].map(([p, t, d]) => (
                <tr key={p} className="hover:bg-gray-50">
                  <td className="px-4 py-3 font-mono text-blue-700 text-xs">{p}</td>
                  <td className="px-4 py-3 text-gray-500 text-xs">{t}</td>
                  <td className="px-4 py-3 text-gray-600">{d}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* Example 1 */}
      <section className="mb-10">
        <h2 className="text-lg font-bold mb-2">Örnek 1 — Uygun Fiyatlı, Yüksek Puanlı</h2>
        <p className="text-sm text-gray-500 mb-3">Request:</p>
        <CodeBlock code={CODE_LIST} />
        <p className="text-sm text-gray-500 mt-4 mb-3">Response:</p>
        <CodeBlock code={RESPONSE_LIST} lang="json" />
      </section>

      {/* Example 2 */}
      <section className="mb-10">
        <h2 className="text-lg font-bold mb-2">Örnek 2 — Tek Restoran Detayı</h2>
        <p className="text-sm text-gray-500 mb-3">Request:</p>
        <CodeBlock code={CODE_DETAIL} />
        <p className="text-sm text-gray-500 mt-4 mb-3">Response:</p>
        <CodeBlock code={RESPONSE_DETAIL} lang="json" />
      </section>

      {/* Example 3 */}
      <section className="mb-10">
        <h2 className="text-lg font-bold mb-2">Örnek 3 — Kadıköy&apos;de Balık</h2>
        <p className="text-sm text-gray-500 mb-3">Request:</p>
        <CodeBlock code={CODE_NEIGHBORHOOD} />
      </section>

      {/* Response fields */}
      <section className="mb-10">
        <h2 className="text-lg font-bold mb-4">Her Kayıtta Ne Var</h2>
        <div className="grid sm:grid-cols-2 gap-3">
          {[
            ["llm_summary", "LLM için hazır 2-3 cümlelik Türkçe özet"],
            ["faq", "10-12 soru-cevap (ulaşım, menü, rezervasyon...)"],
            ["nearby.transit", "En yakın metro/tramvay/vapur + yürüme süresi"],
            ["nearby.landmarks", "Yakın müze, tarihi yer, turistik nokta"],
            ["popular_dishes", "Popüler ve imza yemekler listesi"],
            ["contextual_ratings", "businessLunch, romanticDate, familyDining (1-5)"],
            ["scenario_summary", "tourist, romantic, family, budget senaryoları"],
            ["sentiment_summary", "Yorumlardan çıkarılan duygu analizi"],
            ["confidence_score", "Veri güvenilirlik skoru (0.0-1.0)"],
            ["Schema.org/Restaurant", "Makine-okunabilir yapılandırılmış veri"],
          ].map(([k, v]) => (
            <div key={k} className="flex gap-3 bg-gray-50 rounded-lg px-4 py-3">
              <code className="text-xs text-blue-700 font-mono shrink-0 mt-0.5">{k}</code>
              <span className="text-xs text-gray-600">{v}</span>
            </div>
          ))}
        </div>
      </section>

      {/* RapidAPI CTA */}
      <section className="bg-gray-900 rounded-xl p-8 text-center">
        <p className="text-blue-400 text-xs font-semibold uppercase tracking-widest mb-3">API Erişimi</p>
        <h2 className="text-white text-2xl font-bold mb-2">Hemen Başlayın</h2>
        <p className="text-gray-400 mb-6 text-sm">RapidAPI üzerinden abone olun — ücretsiz plan mevcut.</p>
        <a
          href="https://rapidapi.com/cccanguler/api/istanbul-restaurants"
          target="_blank"
          rel="noopener noreferrer"
          className="inline-block bg-blue-500 hover:bg-blue-400 text-white font-bold px-8 py-3 rounded-lg transition-colors"
        >
          RapidAPI&apos;de Abone Ol →
        </a>
        <div className="mt-6 flex justify-center gap-6 text-xs text-gray-500">
          <a href="/api/openapi.json" target="_blank" className="hover:text-gray-300 transition-colors">OpenAPI Spec</a>
          <a href="/llms.txt" target="_blank" className="hover:text-gray-300 transition-colors">llms.txt</a>
          <a href="/.well-known/ai-plugin.json" target="_blank" className="hover:text-gray-300 transition-colors">ai-plugin.json</a>
        </div>
      </section>

    </main>
  );
}
