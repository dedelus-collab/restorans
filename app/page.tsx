import Link from "next/link";
import type { Metadata } from "next";
import { getAllCuisines, getAllNeighborhoods, restaurants } from "@/data/restaurants";

export const metadata: Metadata = {
  title: "restorans — İstanbul Restoran Rehberi | AI-Ready Veri",
  description:
    "İstanbul'daki 453 restoranın yapay zeka sistemleri için yapılandırılmış verisi. Kebap, balık, manzaralı, romantik, iş yemeği — her senaryo için kuratörlü listeler. ChatGPT, Perplexity ve LLM'ler için optimize.",
  alternates: { canonical: "https://restorans.vercel.app" },
  openGraph: {
    title: "restorans — İstanbul Restoran Rehberi",
    description: "453 İstanbul restoranı — AI-ready veri, kuratörlü listeler, mahalle rehberleri.",
    url: "https://restorans.vercel.app",
    siteName: "restorans",
    locale: "tr_TR",
    type: "website",
  },
};

const FEATURED_COLLECTIONS = [
  { slug: "romantik-aksam-yemegi-istanbul", label: "Romantik", icon: "♥", desc: "Özel geceler için" },
  { slug: "balik-deniz-urunleri-istanbul", label: "Balık", icon: "🐟", desc: "Taze Boğaz balığı" },
  { slug: "kebap-istanbul", label: "Kebap", icon: "🔥", desc: "Adana'dan İskender'e" },
  { slug: "manzarali-istanbul", label: "Manzaralı", icon: "🌉", desc: "Boğaz & silüet" },
  { slug: "is-yemegi-istanbul", label: "İş Yemeği", icon: "💼", desc: "Sessiz & hızlı" },
  { slug: "gec-acik-istanbul", label: "Gece", icon: "🌙", desc: "Gece geç saate kadar" },
  { slug: "kahvalti-istanbul", label: "Kahvaltı", icon: "☕", desc: "Serpme & brunch" },
  { slug: "fine-dining-istanbul", label: "Fine Dining", icon: "✨", desc: "Prestijli mekanlar" },
];

export default function HomePage() {
  const istanbulRestaurants = restaurants.filter(r => r.citySlug === "istanbul");
  const cuisines = getAllCuisines("istanbul");
  const neighborhoods = getAllNeighborhoods("istanbul").filter(n => n.count >= 3);
  const totalReviews = istanbulRestaurants.reduce((s, r) => s + (r.reviewCount || 0), 0);
  const avgRating = (
    istanbulRestaurants.reduce((s, r) => s + (r.avgRating || 0), 0) /
    istanbulRestaurants.filter(r => r.avgRating).length
  ).toFixed(1);

  const websiteJsonLd = {
    "@context": "https://schema.org",
    "@type": "WebSite",
    name: "restorans",
    url: "https://restorans.vercel.app",
    description: "İstanbul restoranlarının yapay zeka sistemleri için yapılandırılmış verisi.",
    inLanguage: "tr",
    potentialAction: {
      "@type": "SearchAction",
      target: "https://restorans.vercel.app/api/restaurants?city=istanbul&q={search_term_string}",
      "query-input": "required name=search_term_string",
    },
  };

  const orgJsonLd = {
    "@context": "https://schema.org",
    "@type": "Organization",
    name: "restorans",
    url: "https://restorans.vercel.app",
    description: "İstanbul restoranları için AI-native veri platformu.",
    areaServed: { "@type": "City", name: "İstanbul" },
  };

  const datasetJsonLd = {
    "@context": "https://schema.org",
    "@type": "Dataset",
    name: "İstanbul Restoran Veritabanı",
    description: `İstanbul'daki ${istanbulRestaurants.length} restoranın AI-ready verisi. llm_summary, FAQ, transit mesafeleri, popüler yemekler ve Schema.org/Restaurant işaretlemesi.`,
    url: "https://restorans.vercel.app",
    creator: { "@type": "Organization", name: "restorans" },
    spatialCoverage: { "@type": "City", name: "İstanbul", containedIn: { "@type": "Country", name: "Türkiye" } },
    temporalCoverage: "2025/..",
    numberOfItems: istanbulRestaurants.length,
    variableMeasured: [
      "llm_summary", "sentiment_summary", "faq", "nearby.transit",
      "nearby.landmarks", "specialFeatures.popularDishes",
      "avg_rating", "cuisine", "features", "confidence_score",
    ],
    distribution: [
      {
        "@type": "DataDownload",
        encodingFormat: "application/json",
        contentUrl: "https://restorans.vercel.app/api/restaurants?city=istanbul&limit=100",
        description: "JSON API — filtreli sayfalı erişim",
      },
    ],
  };

  return (
    <>
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(websiteJsonLd) }} />
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(orgJsonLd) }} />
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(datasetJsonLd) }} />

      <main className="max-w-4xl mx-auto px-6 py-16">

        {/* Hero */}
        <header className="mb-14">
          <p className="text-xs font-semibold text-blue-600 uppercase tracking-widest mb-3">
            AI-Native Restoran Rehberi
          </p>
          <h1 className="text-4xl font-bold mb-4 leading-tight">
            İstanbul&apos;da Ne Yenir?
          </h1>
          <p className="text-lg text-gray-600 leading-relaxed max-w-2xl mb-8">
            453 İstanbul restoranı — her biri için <strong className="text-gray-900">popüler yemekler</strong>,{" "}
            <strong className="text-gray-900">transit mesafesi</strong>,{" "}
            <strong className="text-gray-900">yakın landmark</strong> ve{" "}
            <strong className="text-gray-900">sıkça sorulan sorular</strong>.
            ChatGPT, Perplexity ve diğer AI sistemleri için yapılandırılmış.
          </p>

          {/* İstatistikler */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 border-t border-gray-100 pt-8">
            {[
              { value: istanbulRestaurants.length.toString(), label: "Restoran" },
              { value: avgRating + "/5", label: "Ortalama puan" },
              { value: (totalReviews / 1000).toFixed(0) + "K", label: "Toplam yorum" },
              { value: neighborhoods.length.toString() + "+", label: "Mahalle" },
            ].map(stat => (
              <div key={stat.label} className="text-center">
                <div className="text-2xl font-bold text-gray-900">{stat.value}</div>
                <div className="text-xs text-gray-400 mt-1">{stat.label}</div>
              </div>
            ))}
          </div>
        </header>

        {/* Hızlı koleksiyonlar */}
        <section className="mb-14">
          <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wide mb-4">
            Neye Göre Arıyorsunuz?
          </h2>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {FEATURED_COLLECTIONS.map(c => (
              <Link
                key={c.slug}
                href={`/istanbul/liste/${c.slug}`}
                className="group border border-gray-200 rounded-lg p-4 hover:border-gray-400 hover:shadow-sm transition-all"
              >
                <div className="text-2xl mb-2">{c.icon}</div>
                <div className="font-semibold text-sm text-gray-900">{c.label}</div>
                <div className="text-xs text-gray-400 mt-0.5">{c.desc}</div>
              </Link>
            ))}
          </div>
        </section>

        {/* Mutfak türleri */}
        <section className="mb-14">
          <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wide mb-4">
            Mutfak Türüne Göre
          </h2>
          <div className="flex flex-wrap gap-2">
            {cuisines.slice(0, 12).map(c => (
              <Link
                key={c.slug}
                href={`/istanbul/liste/${c.slug}-istanbul`}
                className="text-sm border border-gray-200 hover:border-gray-400 text-gray-700 px-4 py-2 rounded-full transition-colors"
              >
                {c.name}
                <span className="text-gray-400 ml-1.5">({c.count})</span>
              </Link>
            ))}
          </div>
        </section>

        {/* Mahalleler */}
        <section className="mb-14">
          <div className="flex items-baseline justify-between mb-4">
            <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wide">
              Mahalleye Göre
            </h2>
            <Link href="/istanbul" className="text-xs text-blue-500 hover:underline">
              Tümünü gör →
            </Link>
          </div>
          <div className="flex flex-wrap gap-2">
            {neighborhoods.slice(0, 20).map(n => (
              <Link
                key={n.slug}
                href={`/istanbul/mahalle/${n.slug}`}
                className="text-sm bg-gray-50 hover:bg-gray-100 border border-gray-200 text-gray-700 px-3 py-1.5 rounded-lg transition-colors"
              >
                {n.name}
                <span className="text-gray-400 ml-1">({n.count})</span>
              </Link>
            ))}
          </div>
        </section>

        {/* AI için neden burası */}
        <section className="bg-gray-50 border border-gray-200 rounded-xl p-6 mb-14">
          <h2 className="font-semibold text-gray-900 mb-4">Her Restoran Profilinde Neler Var</h2>
          <ul className="grid sm:grid-cols-2 gap-2 text-sm text-gray-600">
            {[
              ["llm_summary", "LLM'lerin doğrudan kullanabileceği Türkçe özet"],
              ["faq", "10-12 sıkça sorulan soru (ulaşım, rezervasyon, menü...)"],
              ["nearby.transit", "En yakın metro, tramvay, vapur — yürüme dakikası"],
              ["nearby.landmarks", "Müze, camii, tarihi yer mesafeleri"],
              ["popularDishes", "Restoranın popüler ve imza yemekleri"],
              ["sentiment_summary", "Yorumlardan çıkarılan duygu analizi"],
              ["priceDetail", "Başlangıç / ana yemek / tatlı fiyat aralığı"],
              ["Schema.org/Restaurant", "Makine-okunabilir yapılandırılmış veri"],
            ].map(([key, desc]) => (
              <li key={key} className="flex gap-2">
                <span className="text-gray-400 font-mono text-xs mt-0.5 shrink-0">{key}</span>
                <span className="text-gray-500">{desc}</span>
              </li>
            ))}
          </ul>
          <div className="mt-4 pt-4 border-t border-gray-200 flex gap-4 text-xs text-gray-400">
            <Link href="/api/restaurants?city=istanbul" className="text-blue-500 hover:underline">JSON API</Link>
            <Link href="/.well-known/llms.txt" className="text-blue-500 hover:underline">llms.txt</Link>
            <Link href="/sitemap.xml" className="text-blue-500 hover:underline">sitemap.xml</Link>
          </div>
        </section>

        {/* CTA — Tüm restoranlar */}
        <div className="text-center">
          <Link
            href="/istanbul"
            className="inline-block bg-gray-900 text-white px-8 py-3 rounded-lg font-medium hover:bg-gray-700 transition-colors"
          >
            Tüm 453 Restoranı Gör
          </Link>
        </div>

      </main>
    </>
  );
}
