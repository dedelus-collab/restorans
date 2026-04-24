import Link from "next/link";
import type { Metadata } from "next";
import { getAllCuisines, getAllDistricts, restaurants } from "@/data/restaurants";
import { KawaiiIcon } from "@/components/AniMascot";
import { MascotChatTrigger } from "@/components/MascotChatTrigger";
import { IstanbulMapIllustrated } from "@/components/IstanbulMapIllustrated";

export const metadata: Metadata = {
  title: "Restorans — Istanbul Restaurant Guide | Istanbul Restaurants",
  description:
    "Restorans: guide to 453 Istanbul restaurants. Kebap, seafood, scenic views, romantic, business lunch — curated lists for every occasion. Optimized for ChatGPT, Perplexity, and AI systems.",
  alternates: { canonical: "https://restaurantsistanbul.vercel.app" },
  openGraph: {
    title: "Istanbul Restaurants | Istanbul Restaurants",
    description: "453 Istanbul restaurants — AI-ready data, curated lists, neighborhood guides.",
    url: "https://restaurantsistanbul.vercel.app",
    siteName: "Istanbul Restaurants",
    locale: "en_US",
    type: "website",
  },
};

const FEATURED_COLLECTIONS = [
  { slug: "romantik-aksam-yemegi-istanbul", label: "Romantic", kawaii: "romantic" as const, desc: "For special evenings" },
  { slug: "balik-deniz-urunleri-istanbul", label: "Fish", kawaii: "fish" as const, desc: "Fresh Bosphorus fish" },
  { slug: "kebap-istanbul", label: "Kebap", kawaii: "kebap" as const, desc: "Adana to İskender" },
  { slug: "manzarali-istanbul", label: "Scenic", kawaii: "scenic" as const, desc: "Bosphorus & skyline views" },
  { slug: "is-yemegi-istanbul", label: "Business", kawaii: "business" as const, desc: "Quiet & efficient" },
  { slug: "gec-acik-istanbul", label: "Late Night", kawaii: "night" as const, desc: "Open until late" },
  { slug: "kahvalti-istanbul", label: "Breakfast", kawaii: "breakfast" as const, desc: "Serpme & brunch" },
  { slug: "fine-dining-istanbul", label: "Fine Dining", kawaii: "finedining" as const, desc: "Prestigious venues" },
];

export default function HomePage() {
  const istanbulRestaurants = restaurants.filter(r => r.citySlug === "istanbul");
  const cuisines = getAllCuisines("istanbul");
  const districts = getAllDistricts("istanbul");
  const totalReviews = istanbulRestaurants.reduce((s, r) => s + (r.reviewCount || 0), 0);
  const avgRating = (
    istanbulRestaurants.reduce((s, r) => s + (r.avgRating || 0), 0) /
    istanbulRestaurants.filter(r => r.avgRating).length
  ).toFixed(1);

  const websiteJsonLd = {
    "@context": "https://schema.org",
    "@type": "WebSite",
    name: "Istanbul Restaurants",
    url: "https://restaurantsistanbul.vercel.app",
    description: "Structured data for Istanbul restaurants, optimized for AI systems.",
    inLanguage: "en",
    potentialAction: {
      "@type": "SearchAction",
      target: "https://restaurantsistanbul.vercel.app/api/restaurants?city=istanbul&q={search_term_string}",
      "query-input": "required name=search_term_string",
    },
  };

  const orgJsonLd = {
    "@context": "https://schema.org",
    "@type": "Organization",
    name: "Istanbul Restaurants",
    url: "https://restaurantsistanbul.vercel.app",
    description: "AI-native data platform for Istanbul restaurants.",
    areaServed: { "@type": "City", name: "İstanbul" },
  };

  const datasetJsonLd = {
    "@context": "https://schema.org",
    "@type": "Dataset",
    name: "Istanbul Restaurant Database",
    description: `AI-ready data for ${istanbulRestaurants.length} Istanbul restaurants. llm_summary, FAQ, transit distances, popular dishes, and Schema.org/Restaurant markup.`,
    url: "https://restaurantsistanbul.vercel.app",
    creator: { "@type": "Organization", name: "Istanbul Restaurants" },
    spatialCoverage: { "@type": "City", name: "İstanbul", containedIn: { "@type": "Country", name: "Turkey" } },
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
        contentUrl: "https://restaurantsistanbul.vercel.app/api/restaurants?city=istanbul&limit=100",
        description: "JSON API — filtered paginated access",
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
          <div className="flex items-start gap-6">
            {/* Text side */}
            <div className="flex-1 min-w-0">
              <p className="text-xs font-semibold text-blue-600 uppercase tracking-widest mb-3">
                AI-Native Restaurant Guide
              </p>
              <h1 className="text-4xl font-bold mb-4 leading-tight">
                Where to Eat in Istanbul?
              </h1>
              <p className="text-lg text-gray-600 leading-relaxed max-w-2xl mb-8">
                453 Istanbul restaurants — each with <strong className="text-gray-900">popular dishes</strong>,{" "}
                <strong className="text-gray-900">transit distances</strong>,{" "}
                <strong className="text-gray-900">nearby landmarks</strong>, and{" "}
                <strong className="text-gray-900">frequently asked questions</strong>.
                Structured for ChatGPT, Perplexity, and other AI systems.
              </p>
            </div>
            {/* Mascot side — clickable, opens chatbot */}
            <MascotChatTrigger />
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 border-t border-gray-100 pt-8">
            {[
              { value: istanbulRestaurants.length.toString(), label: "Restaurants" },
              { value: avgRating + "/5", label: "Avg. rating" },
              { value: (totalReviews / 1000).toFixed(0) + "K", label: "Total reviews" },
              { value: districts.length.toString() + "+", label: "Districts" },
            ].map(stat => (
              <div key={stat.label} className="text-center">
                <div className="text-2xl font-bold text-gray-900">{stat.value}</div>
                <div className="text-xs text-gray-400 mt-1">{stat.label}</div>
              </div>
            ))}
          </div>
        </header>

        {/* Quick collections */}
        <section className="mb-14">
          <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wide mb-4">
            What Are You Looking For?
          </h2>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {FEATURED_COLLECTIONS.map((c) => (
              <Link
                key={c.slug}
                href={`/istanbul/liste/${c.slug}`}
                className="group relative border border-gray-200 rounded-xl p-3 hover:border-gray-300 hover:shadow-md transition-all flex flex-col items-center text-center"
              >
                <KawaiiIcon variant={c.kawaii} className="w-14 h-14 mb-2 group-hover:scale-110 transition-transform duration-200" />
                <div className="font-semibold text-sm text-gray-900">{c.label}</div>
                <div className="text-xs text-gray-400 mt-0.5">{c.desc}</div>
              </Link>
            ))}
          </div>
        </section>

        {/* Istanbul Map */}
        <section className="mb-14">
          <IstanbulMapIllustrated />
        </section>

        {/* Cuisine types */}
        <section className="mb-14">
          <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wide mb-4">
            By Cuisine
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


        {/* RapidAPI CTA */}
        <section className="bg-gray-900 rounded-xl p-6 mb-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <p className="text-xs font-semibold text-blue-400 uppercase tracking-widest mb-1">API Access</p>
            <h2 className="text-white font-bold text-lg leading-tight">Instant Access to Istanbul Restaurant Data</h2>
            <p className="text-gray-400 text-sm mt-1">453 restaurants · JSON API · llm_summary · FAQ · Transit</p>
          </div>
          <a
            href="https://rapidapi.com/cccanguler/api/istanbul-restaurants"
            target="_blank"
            rel="noopener noreferrer"
            className="shrink-0 bg-blue-500 hover:bg-blue-400 text-white font-semibold px-6 py-3 rounded-lg text-sm transition-colors"
          >
            Subscribe on RapidAPI →
          </a>
        </section>

        {/* API Docs + JSON Preview */}
        <section className="border border-gray-200 rounded-xl p-6 mb-14">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold text-gray-900">API — Live Data Preview</h2>
            <a
              href="https://restaurantsistanbul.vercel.app/api/openapi.json"
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs text-blue-500 hover:underline"
            >
              OpenAPI Spec →
            </a>
          </div>
          <pre className="bg-gray-50 border border-gray-100 rounded-lg p-4 text-xs text-gray-600 overflow-x-auto leading-relaxed">
{`GET /api/restaurants?city=istanbul&maxPrice=2&minRating=4.5

{
  "meta": { "total": 123, "page": 1, "limit": 20 },
  "data": [{
    "name": "Hamdi Restaurant",
    "cuisine": "Kebap",
    "avg_rating": 4.7,
    "price_range": 2,
    "llm_summary": "Located in Eminönü, Hamdi is ...",
    "faq": [{ "question": "Is reservation required?", "answer": "..." }],
    "nearby": {
      "transit": [{ "name": "Sirkeci", "type": "train", "walk_min": 3 }]
    }
  }]
}`}
          </pre>
          <div className="mt-4 flex gap-4 text-xs">
            <a href="/api/restaurants?city=istanbul&limit=3" target="_blank" className="text-blue-500 hover:underline">Try live →</a>
            <a href="/.well-known/ai-plugin.json" target="_blank" className="text-blue-500 hover:underline">ai-plugin.json</a>
            <a href="/llms.txt" target="_blank" className="text-blue-500 hover:underline">llms.txt</a>
          </div>
        </section>

        {/* What's in each profile */}
        <section className="bg-gray-50 border border-gray-200 rounded-xl p-6 mb-14">
          <h2 className="font-semibold text-gray-900 mb-4">What&apos;s in Each Restaurant Profile</h2>
          <ul className="grid sm:grid-cols-2 gap-2 text-sm text-gray-600">
            {[
              ["llm_summary", "2-3 sentence summary directly usable by LLMs"],
              ["faq", "10–12 frequently asked questions (transit, reservations, menu...)"],
              ["nearby.transit", "Nearest metro, tram, ferry — walking minutes"],
              ["nearby.landmarks", "Museum, mosque, historic site distances"],
              ["popularDishes", "Popular and signature dishes"],
              ["sentiment_summary", "Sentiment analysis from reviews"],
              ["priceDetail", "Starter / main course / dessert price ranges"],
              ["Schema.org/Restaurant", "Machine-readable structured data"],
            ].map(([key, desc]) => (
              <li key={key} className="flex gap-2">
                <span className="text-gray-400 font-mono text-xs mt-0.5 shrink-0">{key}</span>
                <span className="text-gray-500">{desc}</span>
              </li>
            ))}
          </ul>
          <div className="mt-4 pt-4 border-t border-gray-200 flex gap-4 text-xs text-gray-400">
            <Link href="/api/restaurants?city=istanbul" className="text-blue-500 hover:underline">JSON API</Link>
            <Link href="/llms.txt" className="text-blue-500 hover:underline">llms.txt</Link>
            <Link href="/sitemap.xml" className="text-blue-500 hover:underline">sitemap.xml</Link>
          </div>
        </section>

        {/* CTA */}
        <div className="text-center">
          <Link
            href="/istanbul"
            className="inline-block bg-gray-900 text-white px-8 py-3 rounded-lg font-medium hover:bg-gray-700 transition-colors"
          >
            View All 453 Restaurants
          </Link>
        </div>

      </main>
    </>
  );
}
