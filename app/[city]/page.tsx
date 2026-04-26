import { notFound } from "next/navigation";
import Link from "next/link";
import { AniHead, AniChibi } from "@/components/AniMascot";
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
  const districts = getAllDistricts(city);
  const cuisines = getAllCuisines(city);

  const listWithDistrict = restaurants.map(r => ({
    ...r,
    district: getDistrictForRestaurant(r),
  }));
  const topDistricts: [string, number][] = districts
    .slice(0, 15)
    .map(d => [d.name, d.count]);

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
              { value: districts.length.toString(), label: "Districts" },
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
            <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wide mb-4 flex items-center gap-2">
              <AniHead variant="star" className="w-7 h-7 shrink-0" />
              What Are You Looking For?
            </h2>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
              {scenarioCollections.map((c, i) => {
                const count = restaurants.filter(c.filter).length;
                const slugVariant: Record<string, "chef"|"reviewer"|"foodie"|"explorer"|"star"> = {
                  "romantik-aksam-yemegi-istanbul": "star",
                  "is-yemegi-istanbul": "reviewer",
                  "ozel-gun-istanbul": "star",
                  "gec-acik-istanbul": "explorer",
                  "aile-dostu-istanbul": "foodie",
                  "vejetaryen-vegan-istanbul": "foodie",
                };
                const variant = slugVariant[c.slug] ?? (["chef","reviewer","foodie","explorer","star"] as const)[i % 5];
                return (
                  <Link
                    key={c.slug}
                    href={`/${city}/liste/${c.slug}`}
                    className="border border-gray-200 rounded-xl px-3 py-4 hover:border-gray-300 hover:shadow-md transition-all group flex flex-col items-center text-center"
                  >
                    <AniChibi variant={variant} className="w-20 h-auto mb-2 group-hover:scale-105 transition-transform duration-200" />
                    <div className="font-medium text-sm text-gray-900 leading-tight">{c.title.replace(`${cityName}&apos;da `, "").replace(`${cityName}'da `, "").split(" ").slice(0, 4).join(" ")}</div>
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
            <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wide mb-4 flex items-center gap-2">
              <AniHead variant="foodie" className="w-7 h-7 shrink-0" />
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
            <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wide mb-4 flex items-center gap-2">
              <AniHead variant="explorer" className="w-7 h-7 shrink-0" />
              Ambiance & Vibe
            </h2>
            <div className="flex flex-wrap gap-2">
              {vibeCollections.map((c, i) => {
                const count = restaurants.filter(c.filter).length;
                const vibeVariant: Record<string, "chef"|"reviewer"|"foodie"|"explorer"|"star"> = {
                  "manzarali-istanbul": "explorer",
                  "bogaz-manzarali-istanbul": "explorer",
                  "uygun-fiyatli-istanbul": "reviewer",
                  "fine-dining-istanbul": "star",
                  "teras-istanbul": "foodie",
                };
                const variant = vibeVariant[c.slug] ?? (["explorer","star","foodie","reviewer","chef"] as const)[i % 5];
                return (
                  <Link
                    key={c.slug}
                    href={`/${city}/liste/${c.slug}`}
                    className="text-sm bg-gray-50 hover:bg-gray-100 border border-gray-200 text-gray-700 px-3 py-1.5 rounded-lg transition-colors flex items-center gap-1.5"
                  >
                    <AniHead variant={variant} className="w-5 h-5 shrink-0" />
                    {c.title.replace(`${cityName}&apos;da `, "").replace(`${cityName}'da `, "").split(" ").slice(0, 3).join(" ")}
                    <span className="text-gray-400 ml-1.5">({count})</span>
                  </Link>
                );
              })}
            </div>
          </section>
        )}

        {/* By District */}
        {districts.length > 1 && (
          <section className="mb-12">
            <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wide mb-4 flex items-center gap-2">
              <AniHead variant="reviewer" className="w-7 h-7 shrink-0" />
              By District
            </h2>
            <div className="flex flex-wrap gap-2">
              {districts.filter(d => d.count >= 2).map(d => (
                <Link
                  key={d.slug}
                  href={`/${city}/ilce/${d.slug}`}
                  className="text-sm bg-gray-50 hover:bg-gray-100 border border-gray-200 text-gray-700 px-3 py-1 rounded transition-colors"
                >
                  {d.name} <span className="text-gray-400">({d.count})</span>
                </Link>
              ))}
            </div>
          </section>
        )}

        {/* All restaurants */}
        <section>
          <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wide mb-4 flex items-center gap-2">
            <AniHead variant="chef" className="w-7 h-7 shrink-0" />
            All Restaurants
          </h2>
          <CityRestaurantList city={city} list={listWithDistrict} topDistricts={topDistricts} />
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
