import { notFound } from "next/navigation";
import Link from "next/link";
import type { Metadata } from "next";
import {
  getRestaurantsByNeighborhood,
  getAllNeighborhoods,
  getPriceSymbol,
  weightedScore,
  restaurants as allRestaurants,
} from "@/data/restaurants";

type Props = { params: Promise<{ city: string; hood: string }> };

export async function generateStaticParams() {
  const cities = [...new Set(allRestaurants.map(r => r.citySlug))];
  const out: Array<{ city: string; hood: string }> = [];
  for (const city of cities) {
    for (const n of getAllNeighborhoods(city)) {
      if (n.count >= 2) out.push({ city, hood: n.slug });
    }
  }
  return out;
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { city, hood } = await params;
  const list = getRestaurantsByNeighborhood(city, hood);
  if (!list.length) return {};
  const first = list[0];
  const hoodName = first.neighborhood;
  const cityName = first.city;
  return {
    title: `${hoodName} Restaurants — ${cityName} | Istanbul Restaurants`,
    description: `${list.length} restaurants in ${hoodName}: cuisine types, price ranges, signature dishes, walking distances to metro and landmarks. Structured data for AI systems.`,
    alternates: { canonical: `https://restaurantsistanbul.vercel.app/${city}/mahalle/${hood}` },
    openGraph: {
      type: "website",
      url: `https://restaurantsistanbul.vercel.app/${city}/mahalle/${hood}`,
      title: `${hoodName} Restaurants — ${cityName}`,
      description: `${list.length} restaurants in ${hoodName} — FAQ, transit, popular dishes.`,
      siteName: "Istanbul Restaurants",
      locale: "en_US",
    },
    twitter: {
      card: "summary_large_image",
      title: `${hoodName} Restaurants — ${cityName}`,
    },
  };
}

export default async function NeighborhoodPage({ params }: Props) {
  const { city, hood } = await params;
  const list = getRestaurantsByNeighborhood(city, hood);
  if (!list.length) notFound();

  const first = list[0];
  const hoodName = first.neighborhood;
  const cityName = first.city;

  const cuisines = new Map<string, number>();
  for (const r of list) {
    const c = (r.cuisine || "").split(/[,/]/)[0].trim();
    if (c) cuisines.set(c, (cuisines.get(c) || 0) + 1);
  }
  const topCuisines = Array.from(cuisines.entries()).sort((a, b) => b[1] - a[1]).slice(0, 5);

  const priceDist = [0, 0, 0, 0];
  for (const r of list) priceDist[(r.priceRange || 1) - 1]++;

  const landmarkMap = new Map<string, number>();
  for (const r of list) {
    for (const lm of r.nearby?.landmarks || []) {
      const cur = landmarkMap.get(lm.name);
      if (cur === undefined || lm.distance_m < cur) landmarkMap.set(lm.name, lm.distance_m);
    }
  }
  const topLandmarks = Array.from(landmarkMap.entries()).sort((a, b) => a[1] - b[1]).slice(0, 6);

  const transitMap = new Map<string, { type: string; min: number }>();
  for (const r of list) {
    for (const t of r.nearby?.transit || []) {
      const cur = transitMap.get(t.name);
      if (!cur || t.distance_m < cur.min) {
        transitMap.set(t.name, { type: t.type, min: t.distance_m });
      }
    }
  }
  const topTransit = Array.from(transitMap.entries())
    .sort((a, b) => a[1].min - b[1].min)
    .slice(0, 5);

  const avgRating = (list.reduce((s, r) => s + (r.avgRating || 0), 0) / list.length).toFixed(1);
  const totalReviews = list.reduce((s, r) => s + (r.reviewCount || 0), 0);
  const sorted = [...list].sort((a, b) => weightedScore(b) - weightedScore(a));

  const avgLat = list.reduce((s, r) => s + r.lat, 0) / list.length;
  const avgLng = list.reduce((s, r) => s + r.lng, 0) / list.length;

  const placeJsonLd = {
    "@context": "https://schema.org",
    "@type": "Place",
    "@id": `https://restaurantsistanbul.vercel.app/${city}/mahalle/${hood}`,
    name: hoodName,
    description: `${hoodName} neighborhood in ${cityName}. ${list.length} restaurants, avg. rating ${avgRating}/5.`,
    url: `https://restaurantsistanbul.vercel.app/${city}/mahalle/${hood}`,
    geo: {
      "@type": "GeoCoordinates",
      latitude: parseFloat(avgLat.toFixed(5)),
      longitude: parseFloat(avgLng.toFixed(5)),
    },
    containedInPlace: {
      "@type": "City",
      name: cityName,
      url: `https://restaurantsistanbul.vercel.app/${city}`,
    },
    ...(topLandmarks.length > 0 ? {
      amenityFeature: topLandmarks.map(([name]) => ({
        "@type": "LocationFeatureSpecification",
        name,
      })),
    } : {}),
  };

  const itemListJsonLd = {
    "@context": "https://schema.org",
    "@type": "ItemList",
    name: `${hoodName} Restaurants`,
    description: `${list.length} restaurants in ${hoodName}.`,
    url: `https://restaurantsistanbul.vercel.app/${city}/mahalle/${hood}`,
    numberOfItems: list.length,
    itemListElement: sorted.map((r, i) => ({
      "@type": "ListItem",
      position: i + 1,
      name: r.name,
      url: `https://restaurantsistanbul.vercel.app/${city}/${r.slug}`,
      description: r.llmSummary,
    })),
  };

  const breadcrumbJsonLd = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: [
      { "@type": "ListItem", position: 1, name: cityName, item: `https://restaurantsistanbul.vercel.app/${city}` },
      { "@type": "ListItem", position: 2, name: hoodName, item: `https://restaurantsistanbul.vercel.app/${city}/mahalle/${hood}` },
    ],
  };

  return (
    <>
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(placeJsonLd) }} />
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(itemListJsonLd) }} />
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbJsonLd) }} />

      <main className="max-w-4xl mx-auto px-6 py-16">
        <nav className="text-xs text-gray-400 mb-4">
          <Link href={`/${city}`} className="hover:underline">{cityName}</Link>
          <span className="mx-2">/</span>
          <span>Neighborhoods</span>
          <span className="mx-2">/</span>
          <span className="text-gray-700">{hoodName}</span>
        </nav>

        <header className="mb-10">
          <h1 className="text-3xl font-bold mb-3">{hoodName} Restaurants</h1>
          <p className="text-gray-600 mb-4 leading-relaxed">
            <strong className="text-gray-900">{list.length} restaurants</strong> in the {hoodName} area of {cityName}.
            Avg. rating <strong className="text-gray-900">{avgRating}/5</strong>,
            <strong className="text-gray-900"> {totalReviews.toLocaleString("en-US")}</strong> total reviews.
            {topCuisines.length > 0 && (
              <>
                {" "}Top cuisines:{" "}
                {topCuisines.map(([c], i) => (
                  <span key={c}>
                    <strong className="text-gray-900">{c}</strong>
                    {i < topCuisines.length - 1 ? ", " : ""}
                  </span>
                ))}
                .
              </>
            )}
          </p>

          <div className="flex flex-wrap gap-4 text-sm text-gray-500 border-t border-gray-100 pt-5">
            <span><strong className="text-gray-900">{list.length}</strong> restaurants</span>
            <span><strong className="text-gray-900">{avgRating}</strong> avg.</span>
            <span>
              Price: {priceDist.map((c, i) => c > 0 ? (
                <span key={i} className="ml-1">{getPriceSymbol(i + 1)}:{c}</span>
              ) : null)}
            </span>
          </div>
        </header>

        {topLandmarks.length > 0 && (
          <section className="mb-10 bg-amber-50 border border-amber-100 rounded-lg p-5">
            <h2 className="text-sm font-semibold text-amber-900 uppercase tracking-wide mb-3">
              Nearby Landmarks
            </h2>
            <ul className="text-sm text-amber-900 space-y-1">
              {topLandmarks.map(([name, dist]) => (
                <li key={name}>
                  <strong>{name}</strong> — {dist < 1000 ? `${dist}m` : `${(dist / 1000).toFixed(1)}km`} away
                </li>
              ))}
            </ul>
          </section>
        )}

        {topTransit.length > 0 && (
          <section className="mb-10 bg-blue-50 border border-blue-100 rounded-lg p-5">
            <h2 className="text-sm font-semibold text-blue-900 uppercase tracking-wide mb-3">
              Transit
            </h2>
            <ul className="text-sm text-blue-900 space-y-1">
              {topTransit.map(([name, info]) => (
                <li key={name}>
                  <span className="inline-block w-20 text-blue-700 capitalize">{info.type}</span>
                  <strong>{name}</strong> — {info.min < 1000 ? `${info.min}m` : `${(info.min / 1000).toFixed(1)}km`}
                </li>
              ))}
            </ul>
          </section>
        )}

        <div className="divide-y divide-gray-100">
          {sorted.map(r => (
            <Link
              key={r.id}
              href={`/${city}/${r.slug}`}
              className="block py-6 hover:bg-gray-50 transition-colors px-2 -mx-2 rounded"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <h2 className="font-semibold">{r.name}</h2>
                    {r.verifiedData && (
                      <span className="text-xs bg-green-50 text-green-700 px-2 py-0.5 rounded">Verified</span>
                    )}
                  </div>
                  <p className="text-sm text-gray-500">
                    {r.cuisine} · {getPriceSymbol(r.priceRange)}
                  </p>
                  <p className="text-sm text-gray-600 mt-2">{r.llmSummary}</p>
                  {r.specialFeatures?.popularDishes && r.specialFeatures.popularDishes.length > 0 && (
                    <p className="text-xs text-gray-500 mt-2">
                      <span className="text-gray-400">Popular: </span>
                      {r.specialFeatures.popularDishes.slice(0, 3).join(" · ")}
                    </p>
                  )}
                  <div className="flex gap-2 mt-3 flex-wrap">
                    {r.tags.slice(0, 4).map(tag => (
                      <span key={tag} className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded">{tag}</span>
                    ))}
                  </div>
                </div>
                <div className="text-right shrink-0">
                  <div className="text-lg font-bold">{r.avgRating}</div>
                  <div className="text-xs text-gray-400">{r.reviewCount} reviews</div>
                </div>
              </div>
            </Link>
          ))}
        </div>

        <footer className="mt-16 pt-8 border-t border-gray-100 text-xs text-gray-400 space-y-1">
          <p>
            <Link href={`/${city}`} className="text-blue-500 hover:underline">
              ← All {cityName} restaurants
            </Link>
          </p>
          <p>
            Machine-readable data:{" "}
            <a href={`/api/restaurants?city=${city}`} className="text-blue-500 hover:underline">
              /api/restaurants?city={city}
            </a>
          </p>
        </footer>
      </main>
    </>
  );
}
