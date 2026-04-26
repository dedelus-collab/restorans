import Link from "next/link";
import type { Metadata } from "next";
import { getAllCuisines, getAllDistricts, restaurants, weightedScore } from "@/data/restaurants";
import { KawaiiIcon, AniHead } from "@/components/AniMascot";
import { MascotChatTrigger } from "@/components/MascotChatTrigger";
import { IstanbulMapIllustrated } from "@/components/IstanbulMapIllustrated";
import { SearchBar } from "@/components/SearchBar";
import { RestaurantCard } from "@/components/RestaurantCard";

const ISTANBUL_COUNT = restaurants.filter(r => r.citySlug === "istanbul").length;

export const metadata: Metadata = {
  title: "Restorans — Istanbul Restaurant Guide | Istanbul Restaurants",
  description:
    `Restorans: guide to ${ISTANBUL_COUNT} Istanbul restaurants. Kebap, seafood, scenic views, romantic, business lunch — curated lists for every occasion. Optimized for ChatGPT, Perplexity, and AI systems.`,
  alternates: { canonical: "https://restaurantsistanbul.vercel.app" },
  openGraph: {
    title: "Istanbul Restaurants | Istanbul Restaurants",
    description: `${ISTANBUL_COUNT} Istanbul restaurants — AI-ready data, curated lists, neighborhood guides.`,
    url: "https://restaurantsistanbul.vercel.app",
    siteName: "Istanbul Restaurants",
    locale: "en_US",
    type: "website",
  },
};

const FEATURED_COLLECTIONS = [
  { slug: "romantik-aksam-yemegi-istanbul", label: "Romantic",    kawaii: "romantic"   as const, desc: "For special evenings",        color: "bg-rose-50 border-rose-100 group-hover:bg-rose-50/80 group-hover:border-rose-200",    iconBg: "bg-rose-100/70" },
  { slug: "balik-deniz-urunleri-istanbul",  label: "Fish",        kawaii: "fish"        as const, desc: "Fresh Bosphorus fish",         color: "bg-cyan-50 border-cyan-100 group-hover:bg-cyan-50/80 group-hover:border-cyan-200",     iconBg: "bg-cyan-100/70" },
  { slug: "kebap-istanbul",                 label: "Kebap",       kawaii: "kebap"       as const, desc: "Adana to İskender",            color: "bg-orange-50 border-orange-100 group-hover:bg-orange-50/80 group-hover:border-orange-200", iconBg: "bg-orange-100/70" },
  { slug: "manzarali-istanbul",             label: "Scenic",      kawaii: "scenic"      as const, desc: "Bosphorus & skyline views",    color: "bg-sky-50 border-sky-100 group-hover:bg-sky-50/80 group-hover:border-sky-200",        iconBg: "bg-sky-100/70" },
  { slug: "is-yemegi-istanbul",             label: "Business",    kawaii: "business"    as const, desc: "Quiet & efficient",            color: "bg-slate-50 border-slate-200 group-hover:bg-slate-100/60 group-hover:border-slate-300", iconBg: "bg-slate-200/60" },
  { slug: "gec-acik-istanbul",              label: "Late Night",  kawaii: "night"       as const, desc: "Open until late",              color: "bg-indigo-50 border-indigo-100 group-hover:bg-indigo-50/80 group-hover:border-indigo-200", iconBg: "bg-indigo-100/70" },
  { slug: "kahvalti-istanbul",              label: "Breakfast",   kawaii: "breakfast"   as const, desc: "Serpme & brunch",              color: "bg-yellow-50 border-yellow-100 group-hover:bg-yellow-50/80 group-hover:border-yellow-200", iconBg: "bg-yellow-100/70" },
  { slug: "fine-dining-istanbul",           label: "Fine Dining", kawaii: "finedining"  as const, desc: "Prestigious venues",           color: "bg-purple-50 border-purple-100 group-hover:bg-purple-50/80 group-hover:border-purple-200", iconBg: "bg-purple-100/70" },
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

  // Top rated (min 50 reviews, sorted by weighted score)
  const topRated = [...istanbulRestaurants]
    .filter(r => (r.reviewCount ?? 0) >= 50 && r.avgRating != null)
    .sort((a, b) => weightedScore(b) - weightedScore(a))
    .slice(0, 6);

  // Recently added (last 5 by lastUpdated)
  const recentlyAdded = [...istanbulRestaurants]
    .filter(r => r.lastUpdated)
    .sort((a, b) => (b.lastUpdated ?? "").localeCompare(a.lastUpdated ?? ""))
    .slice(0, 5);

  // Search entries
  const searchEntries = istanbulRestaurants.map(r => ({
    slug: r.slug,
    name: r.name,
    cuisine: r.cuisine ?? "",
    neighborhood: r.neighborhood ?? "",
    avgRating: r.avgRating ?? null,
    priceRange: r.priceRange ?? "",
  }));

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
          <div className="rounded-2xl bg-gradient-to-br from-slate-50 via-white to-blue-50/40 border border-gray-200/80 px-8 py-10 mb-6">
            <div className="flex items-start gap-6">
              <div className="flex-1 min-w-0">
                <div className="inline-flex items-center gap-1.5 bg-white border border-gray-200 rounded-full px-3 py-1 text-xs font-medium text-gray-500 mb-5 shadow-sm">
                  <span className="w-1.5 h-1.5 rounded-full bg-green-400"></span>
                  AI-Native · {istanbulRestaurants.length} restaurants · Updated daily
                </div>
                <h1 className="text-4xl sm:text-5xl font-bold mb-4 leading-tight tracking-tight">
                  Where to Eat<br className="hidden sm:block" /> in Istanbul?
                </h1>
                <p className="text-base text-gray-500 leading-relaxed max-w-xl mb-0">
                  Curated restaurant data with <span className="text-gray-800 font-medium">popular dishes</span>,{" "}
                  <span className="text-gray-800 font-medium">transit distances</span>, and{" "}
                  <span className="text-gray-800 font-medium">AI-ready summaries</span>.
                  Structured for ChatGPT, Perplexity, and beyond.
                </p>
              </div>
              <MascotChatTrigger />
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {[
              { value: istanbulRestaurants.length.toLocaleString(), label: "Restaurants", icon: "🍽️", bg: "bg-blue-50 border-blue-100" },
              { value: avgRating + " / 5",                          label: "Avg. rating",       icon: "★",  bg: "bg-amber-50 border-amber-100" },
              { value: (totalReviews / 1000).toFixed(0) + "K+",     label: "Total reviews",     icon: "💬", bg: "bg-violet-50 border-violet-100" },
              { value: districts.length + "+ areas",                 label: "Districts covered", icon: "📍", bg: "bg-emerald-50 border-emerald-100" },
            ].map(stat => (
              <div key={stat.label} className={`${stat.bg} border rounded-xl px-4 py-4`}>
                <div className="text-lg mb-0.5">{stat.icon}</div>
                <div className="text-xl font-bold text-gray-900 leading-tight">{stat.value}</div>
                <div className="text-xs text-gray-500 mt-0.5">{stat.label}</div>
              </div>
            ))}
          </div>
        </header>

        {/* Search */}
        <section className="mb-14">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-sm font-semibold text-gray-900 flex items-center gap-2">
              <span className="w-0.5 h-4 bg-blue-400 rounded-full inline-block"></span>
              Find the perfect place to eat
            </h2>
            <div className="hidden sm:flex items-end gap-2">
              {(["kebap","fish","scenic","breakfast","romantic","night"] as const).map((v, i) => (
                <div key={v} className="animate-bounce" style={{ animationDelay: `${i * 100}ms`, animationDuration: "1.8s" }}>
                  <KawaiiIcon variant={v} className="w-7 h-7" />
                </div>
              ))}
            </div>
          </div>

          <SearchBar entries={searchEntries} />

          {/* Quick collections */}
          <div className="mt-4 grid grid-cols-2 sm:grid-cols-4 gap-2.5">
            {FEATURED_COLLECTIONS.map((c) => (
              <Link
                key={c.slug}
                href={`/istanbul/liste/${c.slug}`}
                className={`group relative border rounded-xl p-3.5 hover:shadow-md transition-all flex gap-3 items-center ${c.color}`}
              >
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center shrink-0 transition-colors ${c.iconBg}`}>
                  <KawaiiIcon variant={c.kawaii} className="w-8 h-8 group-hover:scale-110 transition-transform duration-200" />
                </div>
                <div className="min-w-0">
                  <div className="font-semibold text-sm text-gray-900 leading-tight">{c.label}</div>
                  <div className="text-xs text-gray-500 mt-0.5 truncate">{c.desc}</div>
                </div>
              </Link>
            ))}
          </div>
        </section>

        {/* Top Rated */}
        <section className="mb-14">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-semibold text-gray-900 flex items-center gap-2">
              <span className="w-0.5 h-4 bg-amber-400 rounded-full inline-block"></span>
              Top Rated Restaurants
              <AniHead variant="star" className="w-7 h-7" />
            </h2>
            <Link href="/istanbul" className="text-xs text-blue-500 hover:underline font-medium">View all →</Link>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {topRated.map((r, i) => (
              <div key={r.slug} className="relative">
                {i < 3 && (
                  <span className="absolute top-3 left-3 z-10 text-xs font-bold bg-amber-400 text-white px-2 py-0.5 rounded-full shadow">
                    #{i + 1}
                  </span>
                )}
                <RestaurantCard
                  city="istanbul"
                  slug={r.slug}
                  name={r.name}
                  neighborhood={r.neighborhood}
                  cuisine={r.cuisine}
                  cuisineSlug={r.cuisineSlug}
                  priceRange={r.priceRange}
                  avgRating={r.avgRating}
                  reviewCount={r.reviewCount}
                  llmSummary={r.llmSummary}
                  verifiedData={r.verifiedData}
                  popularDishes={r.specialFeatures?.popularDishes ?? []}
                  variant="featured"
                />
              </div>
            ))}
          </div>
        </section>

        {/* Istanbul Map */}
        <section className="mb-6">
          <IstanbulMapIllustrated />
        </section>

        {/* Districts + Cuisine side by side */}
        <section className="mb-14 grid sm:grid-cols-2 gap-8">
          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-sm font-semibold text-gray-900 flex items-center gap-2">
                <span className="w-0.5 h-4 bg-indigo-400 rounded-full inline-block"></span>
                By District
              </h2>
              <Link href="/istanbul" className="text-xs text-blue-500 hover:underline font-medium">All →</Link>
            </div>
            <div className="flex flex-col gap-1.5">
              {districts.slice(0, 8).map(d => (
                <Link
                  key={d.slug}
                  href={`/istanbul/ilce/${d.slug}`}
                  className="flex items-center justify-between text-sm bg-white hover:bg-gray-50 border border-gray-200 hover:border-gray-300 text-gray-700 px-3.5 py-2.5 rounded-lg transition-colors group"
                >
                  <span className="font-medium group-hover:text-gray-900">{d.name}</span>
                  <span className="text-xs bg-gray-100 text-gray-500 px-2 py-0.5 rounded-full">{d.count}</span>
                </Link>
              ))}
            </div>
          </div>

          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-sm font-semibold text-gray-900 flex items-center gap-2">
                <span className="w-0.5 h-4 bg-rose-400 rounded-full inline-block"></span>
                By Cuisine
              </h2>
            </div>
            <div className="flex flex-wrap gap-2">
              {cuisines.slice(0, 12).map(c => (
                <Link
                  key={c.slug}
                  href={`/istanbul/liste/${c.slug}-istanbul`}
                  className="text-sm bg-white border border-gray-200 hover:border-gray-300 hover:bg-gray-50 text-gray-700 px-3.5 py-1.5 rounded-full transition-colors"
                >
                  {c.name}
                  <span className="text-gray-400 ml-1.5 text-xs">({c.count})</span>
                </Link>
              ))}
            </div>
          </div>
        </section>


        {/* Recently Added */}
        <section className="mb-14">
          <h2 className="text-sm font-semibold text-gray-900 flex items-center gap-2 mb-4">
            <span className="w-0.5 h-4 bg-green-400 rounded-full inline-block"></span>
            Recently Added
          </h2>
          <div className="flex flex-col gap-2">
            {recentlyAdded.map(r => (
              <Link
                key={r.slug}
                href={`/istanbul/${r.slug}`}
                className="flex items-center justify-between px-4 py-3 border border-gray-200 rounded-xl hover:border-gray-300 hover:bg-gray-50 transition-all group"
              >
                <div className="flex items-center gap-3 min-w-0">
                  <span className="w-1.5 h-1.5 rounded-full bg-green-400 shrink-0" />
                  <div className="min-w-0">
                    <span className="text-sm font-medium text-gray-900 group-hover:text-blue-600 transition-colors">{r.name}</span>
                    <span className="text-xs text-gray-400 ml-2">{r.cuisine} · {r.neighborhood}</span>
                  </div>
                </div>
                <div className="flex items-center gap-3 shrink-0 ml-4">
                  {r.avgRating != null && (
                    <span className="text-xs font-semibold text-gray-600">★ {r.avgRating}</span>
                  )}
                  <span className="text-xs text-gray-400">
                    {r.lastUpdated ? new Date(r.lastUpdated).toLocaleDateString("en-GB", { day: "numeric", month: "short" }) : ""}
                  </span>
                </div>
              </Link>
            ))}
          </div>
        </section>

        {/* Travel Tips */}
        <section className="mb-14">
          <h2 className="text-sm font-semibold text-gray-900 flex items-center gap-2 mb-4">
            <span className="w-0.5 h-4 bg-violet-400 rounded-full inline-block"></span>
            Dining in Istanbul — Tips
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {[
              { icon: "🗺️", title: "Where to Eat by Area", body: "Beyoğlu & Karaköy for trendy bistros. Eminönü & Fatih for traditional Turkish. Beşiktaş & Kadıköy for local neighbourhood spots. Bosphorus villages (Bebek, Arnavutköy) for scenic seafood." },
              { icon: "💰", title: "Tipping Culture", body: "Tipping is expected. 10–15% is standard for sit-down restaurants. Many places add a service charge — check the bill. Card payments widely accepted in most mid-range and above venues." },
              { icon: "📅", title: "Reservations", body: "Popular spots fill fast on Friday–Saturday evenings. Book at least 2–3 days ahead for fine dining. Casual lokantas and pide salons rarely need reservations." },
              { icon: "🕐", title: "Meal Times", body: "Lunch runs 12:00–15:00, dinner from 19:00 onwards. Many restaurants close between meals. Breakfast (kahvaltı) culture is strong — weekend brunch tables often need booking." },
            ].map(tip => (
              <div key={tip.title} className="p-5 bg-white border border-gray-200 rounded-xl hover:border-gray-300 hover:shadow-sm transition-all">
                <div className="flex items-start gap-3">
                  <span className="text-xl shrink-0">{tip.icon}</span>
                  <div>
                    <h3 className="font-semibold text-sm text-gray-900 mb-1">{tip.title}</h3>
                    <p className="text-sm text-gray-500 leading-relaxed">{tip.body}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* RapidAPI CTA */}
        <section className="relative overflow-hidden bg-gray-950 rounded-2xl p-7 mb-6">
          <div className="absolute inset-0 bg-gradient-to-br from-blue-600/20 via-transparent to-indigo-600/10 pointer-events-none" />
          <div className="relative flex flex-col sm:flex-row items-start sm:items-center justify-between gap-5">
            <div>
              <div className="inline-flex items-center gap-1.5 bg-blue-500/20 border border-blue-400/30 rounded-full px-3 py-0.5 text-xs font-medium text-blue-300 mb-3">
                <span className="w-1.5 h-1.5 rounded-full bg-blue-400"></span>
                API Access
              </div>
              <h2 className="text-white font-bold text-xl leading-tight mb-1.5">Build with Istanbul Restaurant Data</h2>
              <p className="text-gray-400 text-sm">
                {istanbulRestaurants.length} restaurants · JSON API · llm_summary · FAQ · Transit distances
              </p>
              <div className="flex gap-3 mt-3 text-xs text-gray-500">
                <span className="flex items-center gap-1">✓ Schema.org markup</span>
                <span className="flex items-center gap-1">✓ OpenAPI spec</span>
                <span className="flex items-center gap-1">✓ AI-optimized</span>
              </div>
            </div>
            <a
              href="https://rapidapi.com/cccanguler/api/istanbul-restaurants"
              target="_blank"
              rel="noopener noreferrer"
              className="shrink-0 bg-white hover:bg-blue-50 text-gray-900 font-semibold px-6 py-3 rounded-xl text-sm transition-colors flex items-center gap-2"
            >
              Subscribe on RapidAPI
              <span className="text-gray-400">→</span>
            </a>
          </div>
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
        <div className="text-center pt-2">
          <Link
            href="/istanbul"
            className="inline-flex items-center gap-2 bg-gray-900 hover:bg-gray-700 text-white px-8 py-3.5 rounded-xl font-semibold text-sm transition-colors shadow-sm"
          >
            Browse All {istanbulRestaurants.length.toLocaleString()} Restaurants
            <span className="text-gray-400">→</span>
          </Link>
          <p className="text-xs text-gray-400 mt-3">Updated daily · Free to browse · API available</p>
        </div>

      </main>
    </>
  );
}
