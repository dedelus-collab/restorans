import { notFound } from "next/navigation";
import Link from "next/link";
import {
  getRestaurantsByCity,
  getAllDistricts,
  getDistrictForRestaurant,
  getAllCuisines,
  restaurants as allRestaurants,
} from "@/data/restaurants";
import { COLLECTIONS } from "@/lib/collections";
import { CityRestaurantList } from "@/components/CityRestaurantList";
import type { Metadata } from "next";

type Props = { params: Promise<{ city: string }> };

export function generateStaticParams() {
  const cities = [...new Set(allRestaurants.map(r => r.citySlug))];
  return cities.map(city => ({ city }));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { city } = await params;
  const restaurants = getRestaurantsByCity(city);
  if (!restaurants.length) return {};
  const cityName = restaurants[0].city;
  return {
    title: `${cityName} Restaurants — ${restaurants.length} Places | Istanbul Restaurants`,
    description: `Structured data for ${restaurants.length} ${cityName} restaurants. Kebap, seafood, scenic views, romantic and more. With FAQ, transit distances and popular dishes.`,
    alternates: { canonical: `https://www.restaurantsistanbul.com/${city}` },
    openGraph: {
      type: "website",
      url: `https://www.restaurantsistanbul.com/${city}`,
      title: `${cityName} Restaurants — ${restaurants.length} Places`,
      description: `${restaurants.length} ${cityName} restaurants — AI-ready data, curated lists, neighborhood guides.`,
      siteName: "Istanbul Restaurants",
      locale: "en_US",
    },
    twitter: {
      card: "summary_large_image",
      title: `${cityName} Restaurants — ${restaurants.length} Places`,
    },
  };
}

// Photo + color per collection slug
const COLLECTION_PHOTOS: Record<string, { photo: string; color: string; emoji: string }> = {
  "romantik-aksam-yemegi-istanbul": { photo: "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=600&q=75&auto=format&fit=crop", color: "#9f1239", emoji: "🌹" },
  "is-yemegi-istanbul":             { photo: "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=600&q=75&auto=format&fit=crop", color: "#1e3a5f", emoji: "💼" },
  "ozel-gun-istanbul":              { photo: "https://images.unsplash.com/photo-1559339352-11d035aa65de?w=600&q=75&auto=format&fit=crop", color: "#7e22ce", emoji: "🎉" },
  "gec-acik-istanbul":              { photo: "https://images.unsplash.com/photo-1524231757912-21f4fe3a7200?w=600&q=75&auto=format&fit=crop&crop=bottom", color: "#1e1b4b", emoji: "🌙" },
  "aile-dostu-istanbul":            { photo: "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=600&q=75&auto=format&fit=crop", color: "#166534", emoji: "👨‍👩‍👧" },
  "vejetaryen-vegan-istanbul":      { photo: "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=600&q=75&auto=format&fit=crop", color: "#15803d", emoji: "🥗" },
  "manzarali-istanbul":             { photo: "https://images.unsplash.com/photo-1541432901042-2d8bd64b4a9b?w=600&q=75&auto=format&fit=crop", color: "#0369a1", emoji: "🌉" },
  "bogaz-manzarali-istanbul":       { photo: "https://images.unsplash.com/photo-1524231757912-21f4fe3a7200?w=600&q=75&auto=format&fit=crop", color: "#075985", emoji: "🚢" },
  "uygun-fiyatli-istanbul":         { photo: "https://images.unsplash.com/photo-1547592180-85f173990554?w=600&q=75&auto=format&fit=crop", color: "#92400e", emoji: "₺" },
  "fine-dining-istanbul":           { photo: "https://images.unsplash.com/photo-1559339352-11d035aa65de?w=600&q=75&auto=format&fit=crop", color: "#3b0764", emoji: "✨" },
  "teras-istanbul":                 { photo: "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=600&q=75&auto=format&fit=crop", color: "#064e3b", emoji: "🌿" },
  "kebap-istanbul":                 { photo: "https://images.unsplash.com/photo-1529543544282-ea669407fca3?w=600&q=75&auto=format&fit=crop", color: "#dc2626", emoji: "🥩" },
  "balik-deniz-urunleri-istanbul":  { photo: "https://images.unsplash.com/photo-1560717845-968823efbee1?w=600&q=75&auto=format&fit=crop", color: "#0369a1", emoji: "🐟" },
  "pizza-italyan-istanbul":         { photo: "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=600&q=75&auto=format&fit=crop", color: "#166534", emoji: "🍕" },
  "sushi-japon-istanbul":           { photo: "https://images.unsplash.com/photo-1579584425555-c3ce17fd4351?w=600&q=75&auto=format&fit=crop", color: "#9f1239", emoji: "🍣" },
  "burger-steak-istanbul":          { photo: "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=600&q=75&auto=format&fit=crop", color: "#b45309", emoji: "🍔" },
  "kahvalti-istanbul":              { photo: "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=600&q=75&auto=format&fit=crop", color: "#b45309", emoji: "🍳" },
  "meyhane-istanbul":               { photo: "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=600&q=75&auto=format&fit=crop", color: "#7e22ce", emoji: "🍷" },
  "lokanta-istanbul":               { photo: "https://images.unsplash.com/photo-1547592180-85f173990554?w=600&q=75&auto=format&fit=crop", color: "#c2410c", emoji: "🫕" },
  "turk-mutfagi-istanbul":          { photo: "https://images.unsplash.com/photo-1547592180-85f173990554?w=600&q=75&auto=format&fit=crop", color: "#991b1b", emoji: "🍲" },
  "kafe-istanbul":                  { photo: "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=600&q=75&auto=format&fit=crop", color: "#92400e", emoji: "☕" },
  "pide-istanbul":                  { photo: "https://images.unsplash.com/photo-1555507036-ab1f4038808a?w=600&q=75&auto=format&fit=crop", color: "#d97706", emoji: "🫓" },
  "dunya-mutfagi-istanbul":         { photo: "https://images.unsplash.com/photo-1559339352-11d035aa65de?w=600&q=75&auto=format&fit=crop", color: "#0e7490", emoji: "🌍" },
};

const DEFAULT_COLLECTION = { photo: "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=600&q=75&auto=format&fit=crop", color: "#334155", emoji: "🍽️" };

export default async function CityPage({ params }: Props) {
  const { city } = await params;
  const restaurants = getRestaurantsByCity(city);
  if (!restaurants.length) notFound();

  const cityName = restaurants[0].city;
  const districts = getAllDistricts(city);
  const cuisines = getAllCuisines(city);

  const listWithDistrict = restaurants.map(r => ({
    ...r,
    district: getDistrictForRestaurant(r),
  }));
  const topDistricts: [string, number][] = districts.map(d => [d.name, d.count]);

  const totalReviews = restaurants.reduce((s, r) => s + (r.reviewCount || 0), 0);
  const avgRating = (
    restaurants.reduce((s, r) => s + (r.avgRating || 0), 0) /
    restaurants.filter(r => r.avgRating).length
  ).toFixed(1);

  const lastUpdated = restaurants
    .map(r => r.lastUpdated)
    .filter(Boolean)
    .sort()
    .reverse()[0] ?? "—";

  const cityCollections = COLLECTIONS.filter(c => {
    const count = restaurants.filter(c.filter).length;
    return count >= 3;
  });

  const cuisineCollections = cityCollections.filter(c => c.category === "cuisine");
  const scenarioCollections = cityCollections.filter(c => c.category === "scenario");
  const vibeCollections = cityCollections.filter(c => c.category === "vibe");

  const itemListJsonLd = {
    "@context": "https://schema.org",
    "@type": "ItemList",
    name: `${cityName} Restaurants`,
    description: `${restaurants.length} ${cityName} restaurants with llm_summary, FAQ, transit distances, popular dishes and Schema.org/Restaurant markup.`,
    url: `https://www.restaurantsistanbul.com/${city}`,
    numberOfItems: restaurants.length,
    itemListElement: restaurants.slice(0, 30).map((r, i) => ({
      "@type": "ListItem",
      position: i + 1,
      name: r.name,
      url: `https://www.restaurantsistanbul.com/${city}/${r.slug}`,
      description: r.llmSummary,
    })),
  };

  const datasetJsonLd = {
    "@context": "https://schema.org",
    "@type": "Dataset",
    name: `${cityName} Restaurant Database`,
    description: `AI-ready, Schema.org-compliant restaurant data for ${cityName}.`,
    url: `https://www.restaurantsistanbul.com/${city}`,
    creator: { "@type": "Organization", name: "Istanbul Restaurants" },
    spatialCoverage: {
      "@type": "City",
      name: cityName,
      containedIn: { "@type": "Country", name: "Turkey" },
    },
    temporalCoverage: "2025/..",
    variableMeasured: [
      "llm_summary", "faq", "nearby", "popularDishes",
      "sentiment_summary", "avg_rating", "cuisine", "confidence_score",
    ],
  };

  const breadcrumbJsonLd = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: [
      { "@type": "ListItem", position: 1, name: "Istanbul Restaurants", item: "https://www.restaurantsistanbul.com" },
      { "@type": "ListItem", position: 2, name: cityName, item: `https://www.restaurantsistanbul.com/${city}` },
    ],
  };

  return (
    <>
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbJsonLd) }} />
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(itemListJsonLd) }} />
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(datasetJsonLd) }} />

      {/* ── HERO ── */}
      <header className="relative flex flex-col justify-end overflow-hidden" style={{ minHeight: "420px" }}>
        <div
          className="absolute inset-0"
          style={{
            backgroundImage: "url('https://images.unsplash.com/photo-1527838832700-5059252407fa?w=1400&q=80&auto=format&fit=crop')",
            backgroundSize: "cover",
            backgroundPosition: "center 55%",
          }}
        />
        <div className="absolute inset-0 bg-gradient-to-t from-gray-950 via-gray-900/70 to-gray-800/20" />

        <div className="relative max-w-4xl mx-auto px-6 pt-20 pb-10 w-full">
          <nav className="text-xs text-white/50 mb-5 flex items-center gap-1.5">
            <Link href="/" className="hover:text-white/80 transition-colors">restorans</Link>
            <span>/</span>
            <span className="text-white/80 font-medium">{cityName}</span>
          </nav>
          <div className="inline-flex items-center gap-1.5 bg-white/10 backdrop-blur-sm border border-white/20 rounded-full px-3 py-1 text-xs font-semibold text-white/90 mb-4">
            <span className="w-1.5 h-1.5 rounded-full bg-green-400" />
            {restaurants.length} restaurants · Updated daily
          </div>
          <h1 className="text-5xl sm:text-6xl font-black text-white leading-none tracking-tight mb-3 drop-shadow-sm">
            {cityName}<br />Restaurants
          </h1>
          <p className="text-white/70 text-base max-w-lg leading-relaxed">
            Every neighborhood, every cuisine — curated, rated, and AI-ready.
          </p>
        </div>

        {/* Stats strip */}
        <div className="relative border-t border-white/10 bg-black/50 backdrop-blur-md">
          <div className="max-w-4xl mx-auto px-6 py-4 flex gap-8 sm:gap-14 overflow-x-auto">
            {[
              { value: restaurants.length.toLocaleString(), label: "Restaurants" },
              { value: avgRating + " ★", label: "Average rating" },
              { value: (totalReviews / 1000).toFixed(0) + "K+", label: "Reviews" },
              { value: districts.length + "+", label: "Districts" },
            ].map(s => (
              <div key={s.label} className="shrink-0">
                <div className="text-xl font-black text-white leading-none">{s.value}</div>
                <div className="text-xs text-white/50 mt-1">{s.label}</div>
              </div>
            ))}
          </div>
        </div>
      </header>

      <main>

        {/* ── SCENARIO COLLECTIONS ── */}
        {scenarioCollections.length > 0 && (
          <section className="py-12 border-b border-gray-100">
            <div className="max-w-4xl mx-auto px-6">
              <h2 className="text-2xl font-black text-gray-900 mb-1">What Are You Looking For?</h2>
              <p className="text-sm text-gray-500 mb-6">Browse by occasion</p>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                {scenarioCollections.map(c => {
                  const count = restaurants.filter(c.filter).length;
                  const theme = COLLECTION_PHOTOS[c.slug] ?? DEFAULT_COLLECTION;
                  const shortTitle = c.title.split(" ").slice(0, 3).join(" ");
                  return (
                    <Link
                      key={c.slug}
                      href={`/${city}/liste/${c.slug}`}
                      className="group rounded-2xl overflow-hidden border border-gray-100 hover:shadow-lg hover:-translate-y-1 transition-all duration-200"
                    >
                      <div
                        className="relative h-28 overflow-hidden"
                        style={{ backgroundImage: `url('${theme.photo}')`, backgroundSize: "cover", backgroundPosition: "center" }}
                      >
                        <div className="absolute inset-0" style={{ background: `linear-gradient(to top, ${theme.color}ee, ${theme.color}44 55%, transparent)` }} />
                        <span className="absolute bottom-2 left-3 text-2xl">{theme.emoji}</span>
                      </div>
                      <div className="p-3 bg-white">
                        <div className="font-bold text-sm text-gray-900 group-hover:text-blue-600 transition-colors leading-tight">{shortTitle}</div>
                        <div className="text-xs text-gray-500 mt-0.5">{count} restaurants</div>
                      </div>
                    </Link>
                  );
                })}
              </div>
            </div>
          </section>
        )}

        {/* ── CUISINE COLLECTIONS ── */}
        {cuisineCollections.length > 0 && (
          <section className="py-12 border-b border-gray-100">
            <div className="max-w-4xl mx-auto px-6">
              <h2 className="text-2xl font-black text-gray-900 mb-1">Browse by Cuisine</h2>
              <p className="text-sm text-gray-500 mb-6">All food types available in {cityName}</p>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                {cuisineCollections.map(c => {
                  const count = restaurants.filter(c.filter).length;
                  const theme = COLLECTION_PHOTOS[c.slug] ?? DEFAULT_COLLECTION;
                  const name = cuisines.find(cu => c.slug.startsWith(cu.slug))?.name ?? c.title.split(" ")[0];
                  return (
                    <Link
                      key={c.slug}
                      href={`/${city}/liste/${c.slug}`}
                      className="group rounded-2xl overflow-hidden border border-gray-100 hover:shadow-lg hover:-translate-y-1 transition-all duration-200"
                    >
                      <div
                        className="relative h-24 overflow-hidden"
                        style={{ backgroundImage: `url('${theme.photo}')`, backgroundSize: "cover", backgroundPosition: "center" }}
                      >
                        <div className="absolute inset-0" style={{ background: `linear-gradient(to top, ${theme.color}dd, ${theme.color}33 60%, transparent)` }} />
                        <span className="absolute bottom-2 left-3 text-xl">{theme.emoji}</span>
                      </div>
                      <div className="p-3 bg-white">
                        <div className="font-bold text-sm text-gray-900 group-hover:text-blue-600 transition-colors">{name}</div>
                        <div className="text-xs text-gray-500 mt-0.5">{count} restaurants</div>
                      </div>
                    </Link>
                  );
                })}
              </div>
            </div>
          </section>
        )}

        {/* ── VIBE COLLECTIONS ── */}
        {vibeCollections.length > 0 && (
          <section className="py-12 border-b border-gray-100">
            <div className="max-w-4xl mx-auto px-6">
              <h2 className="text-2xl font-black text-gray-900 mb-1">Ambiance & Vibe</h2>
              <p className="text-sm text-gray-500 mb-6">Filter by experience</p>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                {vibeCollections.map(c => {
                  const count = restaurants.filter(c.filter).length;
                  const theme = COLLECTION_PHOTOS[c.slug] ?? DEFAULT_COLLECTION;
                  const shortTitle = c.title.split(" ").slice(0, 4).join(" ");
                  return (
                    <Link
                      key={c.slug}
                      href={`/${city}/liste/${c.slug}`}
                      className="group rounded-2xl overflow-hidden border border-gray-100 hover:shadow-lg hover:-translate-y-1 transition-all duration-200"
                    >
                      <div
                        className="relative h-28 overflow-hidden"
                        style={{ backgroundImage: `url('${theme.photo}')`, backgroundSize: "cover", backgroundPosition: "center" }}
                      >
                        <div className="absolute inset-0" style={{ background: `linear-gradient(to top, ${theme.color}ee, ${theme.color}44 55%, transparent)` }} />
                        <span className="absolute bottom-2 left-3 text-2xl">{theme.emoji}</span>
                      </div>
                      <div className="p-3 bg-white">
                        <div className="font-bold text-sm text-gray-900 group-hover:text-blue-600 transition-colors leading-tight">{shortTitle}</div>
                        <div className="text-xs text-gray-500 mt-0.5">{count} restaurants</div>
                      </div>
                    </Link>
                  );
                })}
              </div>
            </div>
          </section>
        )}

        {/* ── ALL RESTAURANTS ── */}
        <section className="py-12">
          <div className="max-w-4xl mx-auto px-6">
            <div className="flex items-end justify-between mb-6">
              <div>
                <h2 className="text-2xl font-black text-gray-900">All Restaurants</h2>
                <p className="text-sm text-gray-500 mt-1">Filter by district · {restaurants.length} total</p>
              </div>
              <span className="text-xs text-gray-400">
                Updated: <strong className="text-gray-600">{lastUpdated}</strong>
              </span>
            </div>
            <CityRestaurantList city={city} list={listWithDistrict} topDistricts={topDistricts} />
          </div>
        </section>

        {/* ── FOOTER LINKS ── */}
        <div className="border-t border-gray-100 py-6">
          <div className="max-w-4xl mx-auto px-6 flex items-center justify-between flex-wrap gap-2 text-xs text-gray-400">
            <span>Data: OpenStreetMap + LLM enrichment</span>
            <span className="flex gap-3">
              <a href={`/api/restaurants?city=${city}`} className="text-blue-500 hover:underline">JSON API</a>
              <a href="/sitemap.xml" className="text-blue-500 hover:underline">sitemap.xml</a>
              <a href="/llms.txt" className="text-blue-500 hover:underline">llms.txt</a>
            </span>
          </div>
        </div>

      </main>
    </>
  );
}
