import Link from "next/link";
import type { Metadata } from "next";
import { getAllCuisines, getAllDistricts, restaurants, weightedScore } from "@/data/restaurants";
import { IstanbulMapIllustrated } from "@/components/IstanbulMapIllustrated";
import { SearchBar } from "@/components/SearchBar";
import { RestaurantCard } from "@/components/RestaurantCard";

const ISTANBUL_COUNT = restaurants.filter(r => r.citySlug === "istanbul").length;

export const metadata: Metadata = {
  title: "Restorans — Istanbul Restaurant Guide | Istanbul Restaurants",
  description:
    `Restorans: guide to ${ISTANBUL_COUNT} Istanbul restaurants. Kebap, seafood, scenic views, romantic, business lunch — curated lists for every occasion. Optimized for ChatGPT, Perplexity, and AI systems.`,
  alternates: { canonical: "https://www.restaurantsistanbul.com" },
  openGraph: {
    title: "Istanbul Restaurants | Istanbul Restaurants",
    description: `${ISTANBUL_COUNT} Istanbul restaurants — AI-ready data, curated lists, neighborhood guides.`,
    url: "https://www.restaurantsistanbul.com",
    siteName: "Istanbul Restaurants",
    locale: "en_US",
    type: "website",
  },
};

const FEATURED_COLLECTIONS = [
  { slug: "romantik-aksam-yemegi-istanbul", label: "Romantic",    emoji: "🌹", desc: "For special evenings",      photo: "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=600&q=75&auto=format&fit=crop", color: "#9f1239" },
  { slug: "balik-deniz-urunleri-istanbul",  label: "Fish",        emoji: "🐟", desc: "Fresh Bosphorus fish",      photo: "https://images.unsplash.com/photo-1560717845-968823efbee1?w=600&q=75&auto=format&fit=crop", color: "#0369a1" },
  { slug: "kebap-istanbul",                 label: "Kebap",       emoji: "🥩", desc: "Adana to İskender",         photo: "https://images.unsplash.com/photo-1529543544282-ea669407fca3?w=600&q=75&auto=format&fit=crop", color: "#dc2626" },
  { slug: "manzarali-istanbul",             label: "Scenic",      emoji: "🌉", desc: "Bosphorus & skyline",       photo: "https://images.unsplash.com/photo-1541432901042-2d8bd64b4a9b?w=600&q=75&auto=format&fit=crop", color: "#0369a1" },
  { slug: "is-yemegi-istanbul",             label: "Business",    emoji: "💼", desc: "Quiet & efficient",         photo: "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=600&q=75&auto=format&fit=crop", color: "#334155" },
  { slug: "gec-acik-istanbul",              label: "Late Night",  emoji: "🌙", desc: "Open until late",           photo: "https://images.unsplash.com/photo-1524231757912-21f4fe3a7200?w=600&q=75&auto=format&fit=crop&crop=bottom", color: "#3730a3" },
  { slug: "kahvalti-istanbul",              label: "Breakfast",   emoji: "🍳", desc: "Serpme & brunch",           photo: "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=600&q=75&auto=format&fit=crop", color: "#b45309" },
  { slug: "fine-dining-istanbul",           label: "Fine Dining", emoji: "✨", desc: "Prestigious venues",        photo: "https://images.unsplash.com/photo-1559339352-11d035aa65de?w=600&q=75&auto=format&fit=crop", color: "#7e22ce" },
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
    url: "https://www.restaurantsistanbul.com",
    description: "Structured data for Istanbul restaurants, optimized for AI systems.",
    inLanguage: "en",
    potentialAction: {
      "@type": "SearchAction",
      target: "https://www.restaurantsistanbul.com/api/restaurants?city=istanbul&q={search_term_string}",
      "query-input": "required name=search_term_string",
    },
  };

  const orgJsonLd = {
    "@context": "https://schema.org",
    "@type": "Organization",
    name: "Istanbul Restaurants",
    url: "https://www.restaurantsistanbul.com",
    description: "AI-native data platform for Istanbul restaurants.",
    areaServed: { "@type": "City", name: "İstanbul" },
  };

  const datasetJsonLd = {
    "@context": "https://schema.org",
    "@type": "Dataset",
    name: "Istanbul Restaurant Database",
    description: `AI-ready data for ${istanbulRestaurants.length} Istanbul restaurants. llm_summary, FAQ, transit distances, popular dishes, and Schema.org/Restaurant markup.`,
    url: "https://www.restaurantsistanbul.com",
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
        contentUrl: "https://www.restaurantsistanbul.com/api/restaurants?city=istanbul&limit=100",
        description: "JSON API — filtered paginated access",
      },
    ],
  };

  return (
    <>
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(websiteJsonLd) }} />
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(orgJsonLd) }} />
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(datasetJsonLd) }} />

      {/* ── HERO ── */}
      <header className="relative flex flex-col justify-end overflow-hidden" style={{ minHeight: "600px" }}>
        {/* Istanbul background image */}
        <div
          className="absolute inset-0"
          style={{
            backgroundImage: "url('https://images.unsplash.com/photo-1524231757912-21f4fe3a7200?w=1400&q=80&auto=format&fit=crop')",
            backgroundSize: "cover",
            backgroundPosition: "center 40%",
          }}
        />
        {/* Gradient overlay */}
        <div className="absolute inset-0 bg-gradient-to-t from-gray-950 via-gray-900/75 to-gray-800/30" />

        {/* Content */}
        <div className="relative max-w-4xl mx-auto px-6 pt-24 pb-10 w-full">
          <div className="inline-flex items-center gap-1.5 bg-white/10 backdrop-blur-sm border border-white/20 rounded-full px-3 py-1 text-xs font-semibold text-white/90 mb-5">
            <span className="w-1.5 h-1.5 rounded-full bg-green-400"></span>
            {istanbulRestaurants.length} restaurants · Istanbul
          </div>
          <h1 className="text-5xl sm:text-7xl font-black text-white leading-none tracking-tight mb-4 drop-shadow-sm">
            Where to Eat<br />in Istanbul
          </h1>
          <p className="text-base sm:text-lg text-white/70 leading-relaxed max-w-lg mb-8">
            Every neighborhood, every cuisine, every occasion — curated and rated.
          </p>
          <div className="max-w-xl">
            <SearchBar entries={searchEntries} />
          </div>
        </div>

        {/* Stats strip */}
        <div className="relative border-t border-white/10 bg-black/50 backdrop-blur-md">
          <div className="max-w-4xl mx-auto px-6 py-5 flex gap-8 sm:gap-14 overflow-x-auto">
            {[
              { value: istanbulRestaurants.length.toLocaleString(), label: "Restaurants" },
              { value: avgRating + " ★", label: "Average rating" },
              { value: (totalReviews / 1000).toFixed(0) + "K+", label: "Reviews" },
              { value: districts.length + "+", label: "Districts" },
              { value: "25+", label: "Curated lists" },
            ].map(s => (
              <div key={s.label} className="shrink-0">
                <div className="text-2xl font-black text-white leading-none">{s.value}</div>
                <div className="text-xs text-white/50 mt-1">{s.label}</div>
              </div>
            ))}
          </div>
        </div>
      </header>

      <main>

        {/* ── BROWSE BY OCCASION ── */}
        <section className="py-14 border-b border-gray-100">
          <div className="max-w-4xl mx-auto px-6">
            <h2 className="text-2xl font-black text-gray-900 mb-2">Browse by Occasion</h2>
            <p className="text-gray-500 mb-6 text-sm">Handpicked lists for every kind of evening</p>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {FEATURED_COLLECTIONS.map((c) => (
                <Link
                  key={c.slug}
                  href={`/istanbul/liste/${c.slug}`}
                  className="group relative rounded-2xl overflow-hidden border border-gray-100 hover:shadow-lg hover:-translate-y-1 transition-all duration-200"
                >
                  <div
                    className="relative h-28 flex items-end justify-start overflow-hidden"
                    style={{ backgroundImage: `url('${c.photo}')`, backgroundSize: "cover", backgroundPosition: "center" }}
                  >
                    <div className="absolute inset-0" style={{ background: `linear-gradient(to top, ${c.color}ee, ${c.color}55 50%, transparent)` }} />
                    <span className="relative text-2xl px-3 pb-2">{c.emoji}</span>
                  </div>
                  <div className="p-3 bg-white">
                    <div className="font-bold text-sm text-gray-900 group-hover:text-blue-600 transition-colors">{c.label}</div>
                    <div className="text-xs text-gray-500 mt-0.5">{c.desc}</div>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        </section>

        {/* ── TOP RATED ── */}
        <section className="py-14 border-b border-gray-100">
          <div className="max-w-4xl mx-auto px-6">
            <div className="flex items-end justify-between mb-6">
              <div>
                <h2 className="text-2xl font-black text-gray-900">Top Rated Restaurants</h2>
                <p className="text-sm text-gray-500 mt-1">Ranked by rating and review volume</p>
              </div>
              <Link href="/istanbul" className="text-sm font-semibold text-blue-600 hover:text-blue-700 flex items-center gap-1">
                View all <span>→</span>
              </Link>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {topRated.map((r, i) => (
                <div key={r.slug} className="relative">
                  {i < 3 && (
                    <span className="absolute top-3 left-3 z-10 text-xs font-black bg-amber-400 text-white px-2 py-0.5 rounded-full shadow">
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
          </div>
        </section>

        {/* ── EXPLORE ISTANBUL ── Bosphorus image banner */}
        <section className="relative overflow-hidden" style={{ height: "220px" }}>
          <div
            className="absolute inset-0"
            style={{
              backgroundImage: "url('https://images.unsplash.com/photo-1541432901042-2d8bd64b4a9b?w=1200&q=80&auto=format&fit=crop')",
              backgroundSize: "cover",
              backgroundPosition: "center 60%",
            }}
          />
          <div className="absolute inset-0 bg-gradient-to-r from-gray-950/90 via-gray-900/60 to-transparent" />
          <div className="relative h-full max-w-4xl mx-auto px-6 flex flex-col justify-center">
            <p className="text-xs font-semibold text-white/50 uppercase tracking-widest mb-2">Explore the City</p>
            <h2 className="text-3xl sm:text-4xl font-black text-white leading-tight mb-4">
              Istanbul&apos;s Best by District
            </h2>
            <Link
              href="/istanbul"
              className="inline-flex items-center gap-2 bg-white text-gray-900 font-semibold text-sm px-5 py-2.5 rounded-xl hover:bg-gray-100 transition-colors w-fit"
            >
              Browse all neighborhoods →
            </Link>
          </div>
        </section>

        {/* ── DISTRICTS + CUISINES ── */}
        <section className="py-14 border-b border-gray-100">
          <div className="max-w-4xl mx-auto px-6 grid sm:grid-cols-2 gap-10">
            <div>
              <div className="flex items-center justify-between mb-5">
                <h2 className="text-xl font-black text-gray-900">By District</h2>
                <Link href="/istanbul" className="text-xs text-blue-600 hover:underline font-semibold">All →</Link>
              </div>
              <div className="flex flex-col gap-2">
                {districts.slice(0, 9).map(d => (
                  <Link
                    key={d.slug}
                    href={`/istanbul/ilce/${d.slug}`}
                    className="flex items-center justify-between bg-white hover:bg-gray-50 border border-gray-200 hover:border-gray-300 text-gray-800 px-4 py-3 rounded-xl transition-colors group"
                  >
                    <span className="font-semibold text-sm group-hover:text-blue-600 transition-colors">{d.name}</span>
                    <span className="text-xs bg-gray-100 text-gray-600 font-semibold px-2.5 py-1 rounded-full">{d.count}</span>
                  </Link>
                ))}
              </div>
            </div>

            <div>
              <h2 className="text-xl font-black text-gray-900 mb-5">By Cuisine</h2>
              <div className="flex flex-wrap gap-2">
                {cuisines.slice(0, 14).map(c => (
                  <Link
                    key={c.slug}
                    href={`/istanbul/liste/${c.slug}-istanbul`}
                    className="inline-flex items-center gap-1.5 text-sm bg-white border border-gray-200 hover:border-gray-900 hover:bg-gray-900 hover:text-white text-gray-800 font-medium px-4 py-2 rounded-full transition-all"
                  >
                    {c.name}
                    <span className="text-gray-400 text-xs">({c.count})</span>
                  </Link>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* ── MAP ── */}
        <section className="py-10 border-b border-gray-100">
          <div className="max-w-4xl mx-auto px-6">
            <IstanbulMapIllustrated />
          </div>
        </section>

        {/* ── RECENTLY ADDED ── */}
        <section className="py-14 border-b border-gray-100">
          <div className="max-w-4xl mx-auto px-6">
            <h2 className="text-xl font-black text-gray-900 mb-5 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-green-500 inline-block animate-pulse"></span>
              Recently Added
            </h2>
            <div className="flex flex-col divide-y divide-gray-100">
              {recentlyAdded.map(r => (
                <Link
                  key={r.slug}
                  href={`/istanbul/${r.slug}`}
                  className="flex items-center justify-between py-3.5 hover:bg-gray-50 -mx-3 px-3 rounded-xl transition-colors group"
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <div className="w-8 h-8 rounded-lg bg-gray-100 flex items-center justify-center text-base shrink-0">🍽️</div>
                    <div className="min-w-0">
                      <div className="text-sm font-bold text-gray-900 group-hover:text-blue-600 transition-colors leading-tight">{r.name}</div>
                      <div className="text-xs text-gray-500 mt-0.5">{r.cuisine} · {r.neighborhood}</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 shrink-0 ml-4">
                    {r.avgRating != null && (
                      <span className="text-xs font-bold text-amber-500">★ {r.avgRating}</span>
                    )}
                    <span className="text-xs text-gray-400">
                      {r.lastUpdated ? new Date(r.lastUpdated).toLocaleDateString("en-GB", { day: "numeric", month: "short" }) : ""}
                    </span>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        </section>

        {/* ── TIPS ── */}
        <section className="py-14 border-b border-gray-100">
          <div className="max-w-4xl mx-auto px-6">
            <h2 className="text-xl font-black text-gray-900 mb-6">Dining in Istanbul — Tips</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {[
                { icon: "🗺️", title: "Where to Eat by Area", body: "Beyoğlu & Karaköy for trendy bistros. Eminönü & Fatih for traditional Turkish. Beşiktaş & Kadıköy for local neighbourhood spots. Bosphorus villages (Bebek, Arnavutköy) for scenic seafood." },
                { icon: "💰", title: "Tipping Culture", body: "Tipping is expected. 10–15% is standard for sit-down restaurants. Many places add a service charge — check the bill. Card payments widely accepted in most mid-range and above venues." },
                { icon: "📅", title: "Reservations", body: "Popular spots fill fast on Friday–Saturday evenings. Book at least 2–3 days ahead for fine dining. Casual lokantas and pide salons rarely need reservations." },
                { icon: "🕐", title: "Meal Times", body: "Lunch runs 12:00–15:00, dinner from 19:00 onwards. Many restaurants close between meals. Breakfast (kahvaltı) culture is strong — weekend brunch tables often need booking." },
              ].map(tip => (
                <div key={tip.title} className="p-5 bg-gray-50 border border-gray-200 rounded-2xl hover:border-gray-300 transition-colors">
                  <div className="flex items-start gap-3">
                    <span className="text-2xl shrink-0">{tip.icon}</span>
                    <div>
                      <h3 className="font-bold text-gray-900 mb-1">{tip.title}</h3>
                      <p className="text-sm text-gray-600 leading-relaxed">{tip.body}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ── API CTA ── */}
        <section className="relative overflow-hidden bg-gray-950 py-14">
          <div className="absolute inset-0 bg-gradient-to-br from-blue-600/15 via-transparent to-indigo-600/10 pointer-events-none" />
          <div className="relative max-w-4xl mx-auto px-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6">
            <div>
              <div className="inline-flex items-center gap-1.5 bg-blue-500/20 border border-blue-400/30 rounded-full px-3 py-0.5 text-xs font-semibold text-blue-300 mb-4">
                <span className="w-1.5 h-1.5 rounded-full bg-blue-400"></span>
                API Access
              </div>
              <h2 className="text-white font-black text-2xl leading-tight mb-2">Build with Istanbul Restaurant Data</h2>
              <p className="text-gray-400 text-sm max-w-md">
                {istanbulRestaurants.length} restaurants · JSON API · llm_summary · FAQ · Transit distances · Schema.org
              </p>
              <div className="flex flex-wrap gap-4 mt-4 text-xs text-gray-500">
                <span>✓ Schema.org markup</span>
                <span>✓ OpenAPI spec</span>
                <span>✓ AI-optimized</span>
                <span>✓ Updated daily</span>
              </div>
            </div>
            <a
              href="https://rapidapi.com/cccanguler/api/istanbul-restaurants"
              target="_blank"
              rel="noopener noreferrer"
              className="shrink-0 bg-white hover:bg-blue-50 text-gray-900 font-bold px-7 py-3.5 rounded-2xl text-sm transition-colors flex items-center gap-2 shadow-lg"
            >
              Subscribe on RapidAPI →
            </a>
          </div>
        </section>

        {/* ── FOOTER CTA ── */}
        <section className="py-16 text-center bg-white border-b border-gray-100">
          <div className="max-w-4xl mx-auto px-6">
            <h2 className="text-3xl font-black text-gray-900 mb-3">Ready to explore?</h2>
            <p className="text-gray-500 mb-8 max-w-md mx-auto">Browse every restaurant in Istanbul — filter by district, cuisine, rating, and more.</p>
            <Link
              href="/istanbul"
              className="inline-flex items-center gap-2 bg-gray-900 hover:bg-gray-700 text-white px-10 py-4 rounded-2xl font-bold text-base transition-colors shadow-sm"
            >
              Browse {istanbulRestaurants.length.toLocaleString()} Restaurants →
            </Link>
            <p className="text-xs text-gray-400 mt-4">Updated daily · Free to browse · API available</p>
          </div>
        </section>

      </main>
    </>
  );
}
