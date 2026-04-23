import { notFound } from "next/navigation";
import Link from "next/link";
import {
  getRestaurantsByCity,
  getPriceSymbol,
  getAllNeighborhoods,
  getAllCuisines,
  restaurants as allRestaurants,
} from "@/data/restaurants";
import { COLLECTIONS } from "@/lib/collections";
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
    alternates: { canonical: `https://restaurantsistanbul.vercel.app/${city}` },
    openGraph: {
      type: "website",
      url: `https://restaurantsistanbul.vercel.app/${city}`,
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

export default async function CityPage({ params }: Props) {
  const { city } = await params;
  const restaurants = getRestaurantsByCity(city);
  if (!restaurants.length) notFound();

  const cityName = restaurants[0].city;
  const neighborhoods = getAllNeighborhoods(city);
  const cuisines = getAllCuisines(city);

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
    url: `https://restaurantsistanbul.vercel.app/${city}`,
    numberOfItems: restaurants.length,
    itemListElement: restaurants.slice(0, 30).map((r, i) => ({
      "@type": "ListItem",
      position: i + 1,
      name: r.name,
      url: `https://restaurantsistanbul.vercel.app/${city}/${r.slug}`,
      description: r.llmSummary,
    })),
  };

  const datasetJsonLd = {
    "@context": "https://schema.org",
    "@type": "Dataset",
    name: `${cityName} Restaurant Database`,
    description: `AI-ready, Schema.org-compliant restaurant data for ${cityName}.`,
    url: `https://restaurantsistanbul.vercel.app/${city}`,
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
      { "@type": "ListItem", position: 1, name: "Istanbul Restaurants", item: "https://restaurantsistanbul.vercel.app" },
      { "@type": "ListItem", position: 2, name: cityName, item: `https://restaurantsistanbul.vercel.app/${city}` },
    ],
  };

  return (
    <>
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbJsonLd) }} />
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(itemListJsonLd) }} />
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(datasetJsonLd) }} />

      <main className="max-w-4xl mx-auto px-6 py-16">

        {/* Breadcrumb */}
        <nav className="text-xs text-gray-400 mb-6">
          <Link href="/" className="hover:underline">restorans</Link>
          <span className="mx-2">/</span>
          <span className="text-gray-700">{cityName}</span>
        </nav>

        {/* Header */}
        <header className="mb-12">
          <h1 className="text-3xl font-bold mb-3">{cityName} Restaurants</h1>
          <p className="text-gray-600 mb-6 leading-relaxed">
            Structured data for <strong className="text-gray-900">{restaurants.length} restaurants</strong> in {cityName}{" "}
            — each profile includes FAQ, transit distances, nearby landmarks, and popular dishes.
          </p>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 border-t border-gray-100 pt-6">
            {[
              { value: restaurants.length.toString(), label: "Restaurants" },
              { value: avgRating + "/5", label: "Avg. rating" },
              { value: (totalReviews / 1000).toFixed(0) + "K", label: "Total reviews" },
              { value: neighborhoods.length.toString(), label: "Neighborhoods" },
            ].map(stat => (
              <div key={stat.label} className="text-center">
                <div className="text-xl font-bold text-gray-900">{stat.value}</div>
                <div className="text-xs text-gray-400 mt-0.5">{stat.label}</div>
              </div>
            ))}
          </div>
        </header>

        {/* Scenario collections */}
        {scenarioCollections.length > 0 && (
          <section className="mb-12">
            <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wide mb-4">
              What Are You Looking For?
            </h2>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
              {scenarioCollections.map(c => {
                const count = restaurants.filter(c.filter).length;
                return (
                  <Link
                    key={c.slug}
                    href={`/${city}/liste/${c.slug}`}
                    className="border border-gray-200 rounded-lg px-4 py-3 hover:border-gray-400 hover:shadow-sm transition-all"
                  >
                    <div className="font-medium text-sm text-gray-900">{c.title.replace(`${cityName}&apos;da `, "").replace(`${cityName}'da `, "").split(" ").slice(0, 4).join(" ")}</div>
                    <div className="text-xs text-gray-400 mt-0.5">{count} restaurants</div>
                  </Link>
                );
              })}
            </div>
          </section>
        )}

        {/* Cuisine collections */}
        {cuisineCollections.length > 0 && (
          <section className="mb-12">
            <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wide mb-4">
              By Cuisine
            </h2>
            <div className="flex flex-wrap gap-2">
              {cuisineCollections.map(c => {
                const count = restaurants.filter(c.filter).length;
                return (
                  <Link
                    key={c.slug}
                    href={`/${city}/liste/${c.slug}`}
                    className="text-sm border border-gray-200 hover:border-gray-400 text-gray-700 px-4 py-2 rounded-full transition-colors"
                  >
                    {cuisines.find(cu => c.slug.startsWith(cu.slug))?.name ?? c.title.split(" ").pop()}
                    <span className="text-gray-400 ml-1.5">({count})</span>
                  </Link>
                );
              })}
            </div>
          </section>
        )}

        {/* Vibe collections */}
        {vibeCollections.length > 0 && (
          <section className="mb-12">
            <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wide mb-4">
              Ambiance & Vibe
            </h2>
            <div className="flex flex-wrap gap-2">
              {vibeCollections.map(c => {
                const count = restaurants.filter(c.filter).length;
                return (
                  <Link
                    key={c.slug}
                    href={`/${city}/liste/${c.slug}`}
                    className="text-sm bg-gray-50 hover:bg-gray-100 border border-gray-200 text-gray-700 px-3 py-1.5 rounded-lg transition-colors"
                  >
                    {c.title.replace(`${cityName}&apos;da `, "").replace(`${cityName}'da `, "").split(" ").slice(0, 3).join(" ")}
                    <span className="text-gray-400 ml-1.5">({count})</span>
                  </Link>
                );
              })}
            </div>
          </section>
        )}

        {/* Neighborhoods */}
        {neighborhoods.length > 1 && (
          <section className="mb-12">
            <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wide mb-4">
              By Neighborhood
            </h2>
            <div className="flex flex-wrap gap-2">
              {neighborhoods.filter(n => n.count >= 2).map(n => (
                <Link
                  key={n.slug}
                  href={`/${city}/mahalle/${n.slug}`}
                  className="text-sm bg-gray-50 hover:bg-gray-100 border border-gray-200 text-gray-700 px-3 py-1 rounded transition-colors"
                >
                  {n.name} <span className="text-gray-400">({n.count})</span>
                </Link>
              ))}
            </div>
          </section>
        )}

        {/* All restaurants */}
        <section>
          <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wide mb-4">
            All Restaurants
          </h2>
          <div className="divide-y divide-gray-100">
            {restaurants.map(r => (
              <Link
                key={r.id}
                href={`/${city}/${r.slug}`}
                className="block py-5 hover:bg-gray-50 transition-colors px-2 -mx-2 rounded"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="font-semibold">{r.name}</h3>
                      {r.verifiedData && (
                        <span className="text-xs bg-green-50 text-green-700 px-2 py-0.5 rounded">Verified</span>
                      )}
                    </div>
                    <p className="text-sm text-gray-500">
                      {r.neighborhood} · {r.cuisine} · {getPriceSymbol(r.priceRange)}
                    </p>
                    <p className="text-sm text-gray-600 mt-1.5 line-clamp-2">{r.llmSummary}</p>
                    {r.specialFeatures?.popularDishes && r.specialFeatures.popularDishes.length > 0 && (
                      <p className="text-xs text-gray-400 mt-1.5">
                        {r.specialFeatures.popularDishes.slice(0, 3).join(" · ")}
                      </p>
                    )}
                    <div className="flex gap-2 mt-2 flex-wrap">
                      {r.tags.slice(0, 3).map(tag => (
                        <span key={tag} className="text-xs bg-gray-100 text-gray-500 px-2 py-0.5 rounded">
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>
                  <div className="text-right shrink-0">
                    <div className="text-base font-bold">{r.avgRating}</div>
                    <div className="text-xs text-gray-400">{r.reviewCount} reviews</div>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </section>

        {/* Footer */}
        <footer className="mt-16 pt-8 border-t border-gray-100 text-xs text-gray-400 space-y-1">
          <p>Last updated: <strong className="text-gray-600">{lastUpdated}</strong></p>
          <p>
            <a href={`/api/restaurants?city=${city}`} className="text-blue-500 hover:underline">JSON API</a>
            {" · "}
            <a href="/sitemap.xml" className="text-blue-500 hover:underline">sitemap.xml</a>
            {" · "}
            <a href="/llms.txt" className="text-blue-500 hover:underline">llms.txt</a>
          </p>
        </footer>
      </main>
    </>
  );
}
