import { notFound } from "next/navigation";
import Link from "next/link";
import type { Metadata } from "next";
import {
  getRestaurantsByDistrict,
  getAllDistricts,
  getPriceSymbol,
  slugifyDistrict,
  restaurants as allRestaurants,
} from "@/data/restaurants";

type Props = { params: Promise<{ city: string; district: string }> };

export async function generateStaticParams() {
  const cities = [...new Set(allRestaurants.map(r => r.citySlug))];
  const out: Array<{ city: string; district: string }> = [];
  for (const city of cities) {
    for (const d of getAllDistricts(city)) {
      out.push({ city, district: d.slug });
    }
  }
  return out;
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { city, district } = await params;
  const list = getRestaurantsByDistrict(city, district);
  if (!list.length) return {};
  const districtName = getAllDistricts(city).find(d => d.slug === district)?.name ?? district;
  return {
    title: `${districtName} Restaurants — Istanbul | Istanbul Restaurants`,
    description: `${list.length} restaurants in ${districtName}, Istanbul — cuisine types, price ranges, popular dishes and transit info.`,
    alternates: { canonical: `https://restaurantsistanbul.vercel.app/${city}/ilce/${district}` },
    openGraph: {
      type: "website",
      url: `https://restaurantsistanbul.vercel.app/${city}/ilce/${district}`,
      title: `${districtName} Restaurants — Istanbul`,
      description: `${list.length} restaurants in ${districtName}.`,
      siteName: "Istanbul Restaurants",
      locale: "en_US",
    },
  };
}

export default async function DistrictPage({ params }: Props) {
  const { city, district } = await params;
  const list = getRestaurantsByDistrict(city, district);
  if (!list.length) notFound();

  const districtName = getAllDistricts(city).find(d => d.slug === district)?.name ?? district;
  const cityName = list[0].city;
  const sorted = [...list].sort((a, b) => (b.avgRating || 0) - (a.avgRating || 0));
  const avgRating = (list.reduce((s, r) => s + (r.avgRating || 0), 0) / list.length).toFixed(1);
  const totalReviews = list.reduce((s, r) => s + (r.reviewCount || 0), 0);

  const cuisines = new Map<string, number>();
  for (const r of list) {
    const c = (r.cuisine || "").split(/[,/]/)[0].trim();
    if (c) cuisines.set(c, (cuisines.get(c) || 0) + 1);
  }
  const topCuisines = Array.from(cuisines.entries()).sort((a, b) => b[1] - a[1]).slice(0, 5);

  const breadcrumbJsonLd = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: [
      { "@type": "ListItem", position: 1, name: cityName, item: `https://restaurantsistanbul.vercel.app/${city}` },
      { "@type": "ListItem", position: 2, name: "Districts", item: `https://restaurantsistanbul.vercel.app/${city}` },
      { "@type": "ListItem", position: 3, name: districtName, item: `https://restaurantsistanbul.vercel.app/${city}/ilce/${district}` },
    ],
  };

  const itemListJsonLd = {
    "@context": "https://schema.org",
    "@type": "ItemList",
    name: `${districtName} Restaurants`,
    numberOfItems: list.length,
    itemListElement: sorted.map((r, i) => ({
      "@type": "ListItem",
      position: i + 1,
      name: r.name,
      url: `https://restaurantsistanbul.vercel.app/${city}/${r.slug}`,
    })),
  };

  return (
    <>
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbJsonLd) }} />
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(itemListJsonLd) }} />

      <main className="max-w-4xl mx-auto px-6 py-16">
        <nav className="text-xs text-gray-400 mb-4 flex items-center gap-1.5">
          <Link href={`/${city}`} className="hover:underline">{cityName}</Link>
          <span>/</span>
          <Link href={`/${city}`} className="hover:underline">Districts</Link>
          <span>/</span>
          <span className="text-gray-700">{districtName}</span>
        </nav>

        <header className="mb-10">
          <h1 className="text-3xl font-bold mb-3">{districtName} Restaurants</h1>
          <p className="text-gray-600 mb-4 leading-relaxed">
            <strong className="text-gray-900">{list.length} restaurants</strong> in {districtName} district of {cityName}.
            Avg. rating <strong className="text-gray-900">{avgRating}/5</strong>,{" "}
            <strong className="text-gray-900">{totalReviews.toLocaleString("en-US")}</strong> total reviews.
            {topCuisines.length > 0 && (
              <> Top cuisines: {topCuisines.map(([c], i) => (
                <span key={c}><strong className="text-gray-900">{c}</strong>{i < topCuisines.length - 1 ? ", " : "."}</span>
              ))}</>
            )}
          </p>
        </header>

        <div className="divide-y divide-gray-100">
          {sorted.map(r => (
            <Link
              key={r.id}
              href={`/${city}/${r.slug}`}
              className="block py-5 hover:bg-gray-50 transition-colors px-2 -mx-2 rounded"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <h2 className="font-semibold">{r.name}</h2>
                  </div>
                  <p className="text-xs text-gray-400">{r.neighborhood} · {r.cuisine} · {getPriceSymbol(r.priceRange)}</p>
                  <p className="text-sm text-gray-600 mt-1.5 line-clamp-2">{r.llmSummary}</p>
                  {r.specialFeatures?.popularDishes && r.specialFeatures.popularDishes.length > 0 && (
                    <p className="text-xs text-gray-400 mt-1.5">
                      {r.specialFeatures.popularDishes.slice(0, 3).join(" · ")}
                    </p>
                  )}
                </div>
                <div className="text-right shrink-0">
                  <div className="text-lg font-bold">{r.avgRating}</div>
                  <div className="text-xs text-gray-400">{r.reviewCount} reviews</div>
                </div>
              </div>
            </Link>
          ))}
        </div>

        <footer className="mt-16 pt-8 border-t border-gray-100 text-xs text-gray-400">
          <Link href={`/${city}`} className="text-blue-500 hover:underline">← All Istanbul restaurants</Link>
        </footer>
      </main>
    </>
  );
}
