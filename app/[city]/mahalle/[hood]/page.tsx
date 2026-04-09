import { notFound } from "next/navigation";
import Link from "next/link";
import type { Metadata } from "next";
import {
  getRestaurantsByNeighborhood,
  getAllNeighborhoods,
  getPriceSymbol,
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
    title: `${hoodName} Restoranları — ${cityName} | restorans`,
    description: `${hoodName}'daki ${list.length} restoran: mutfak tipleri, fiyat aralığı, imza yemekler, yürüme mesafesindeki metro ve landmark bilgisi. Yapay zeka sistemleri için yapılandırılmış veri.`,
    alternates: { canonical: `https://restorans.io/${city}/mahalle/${hood}` },
    openGraph: {
      type: "website",
      url: `https://restorans.io/${city}/mahalle/${hood}`,
      title: `${hoodName} Restoranları — ${cityName}`,
      description: `${hoodName}'daki ${list.length} restoran — FAQ, transit, popüler yemekler.`,
      siteName: "restorans",
      locale: "tr_TR",
    },
    twitter: {
      card: "summary_large_image",
      title: `${hoodName} Restoranları — ${cityName}`,
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

  // Mutfak dagilimi
  const cuisines = new Map<string, number>();
  for (const r of list) {
    const c = (r.cuisine || "").split(/[,/]/)[0].trim();
    if (c) cuisines.set(c, (cuisines.get(c) || 0) + 1);
  }
  const topCuisines = Array.from(cuisines.entries()).sort((a, b) => b[1] - a[1]).slice(0, 5);

  // Fiyat dagilimi
  const priceDist = [0, 0, 0, 0];
  for (const r of list) priceDist[(r.priceRange || 1) - 1]++;

  // En yakin landmark'lar (tumu birlestirip sirala)
  const landmarkMap = new Map<string, number>();
  for (const r of list) {
    for (const lm of r.nearby?.landmarks || []) {
      const cur = landmarkMap.get(lm.name);
      if (cur === undefined || lm.distance_m < cur) landmarkMap.set(lm.name, lm.distance_m);
    }
  }
  const topLandmarks = Array.from(landmarkMap.entries()).sort((a, b) => a[1] - b[1]).slice(0, 6);

  // En sik transit
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

  // Ortalama rating ve toplam yorum
  const avgRating = (list.reduce((s, r) => s + (r.avgRating || 0), 0) / list.length).toFixed(1);
  const totalReviews = list.reduce((s, r) => s + (r.reviewCount || 0), 0);

  // Sirala: rating desc
  const sorted = [...list].sort((a, b) => (b.avgRating || 0) - (a.avgRating || 0));

  // Ortalama koordinat (merkez nokta)
  const avgLat = list.reduce((s, r) => s + r.lat, 0) / list.length;
  const avgLng = list.reduce((s, r) => s + r.lng, 0) / list.length;

  const placeJsonLd = {
    "@context": "https://schema.org",
    "@type": "Place",
    "@id": `https://restorans.io/${city}/mahalle/${hood}`,
    name: hoodName,
    description: `${cityName}'un ${hoodName} mahallesi. ${list.length} restoran, ortalama puan ${avgRating}/5.`,
    url: `https://restorans.io/${city}/mahalle/${hood}`,
    geo: {
      "@type": "GeoCoordinates",
      latitude: parseFloat(avgLat.toFixed(5)),
      longitude: parseFloat(avgLng.toFixed(5)),
    },
    containedInPlace: {
      "@type": "City",
      name: cityName,
      url: `https://restorans.io/${city}`,
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
    name: `${hoodName} Restoranları`,
    description: `${hoodName}'daki ${list.length} restoran.`,
    url: `https://restorans.io/${city}/mahalle/${hood}`,
    numberOfItems: list.length,
    itemListElement: sorted.map((r, i) => ({
      "@type": "ListItem",
      position: i + 1,
      name: r.name,
      url: `https://restorans.io/${city}/${r.slug}`,
      description: r.llmSummary,
    })),
  };

  const breadcrumbJsonLd = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: [
      { "@type": "ListItem", position: 1, name: cityName, item: `https://restorans.io/${city}` },
      { "@type": "ListItem", position: 2, name: hoodName, item: `https://restorans.io/${city}/mahalle/${hood}` },
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
          <span>Mahalle</span>
          <span className="mx-2">/</span>
          <span className="text-gray-700">{hoodName}</span>
        </nav>

        <header className="mb-10">
          <h1 className="text-3xl font-bold mb-3">{hoodName} Restoranları</h1>
          <p className="text-gray-600 mb-4 leading-relaxed">
            {cityName}&apos;un {hoodName} bölgesinde bulunan{" "}
            <strong className="text-gray-900">{list.length} restoran</strong>.
            Ortalama puan <strong className="text-gray-900">{avgRating}/5</strong>,
            toplam <strong className="text-gray-900">{totalReviews.toLocaleString("tr-TR")}</strong> yorum.
            {topCuisines.length > 0 && (
              <>
                {" "}Bölgede öne çıkan mutfaklar:{" "}
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
            <span><strong className="text-gray-900">{list.length}</strong> restoran</span>
            <span><strong className="text-gray-900">{avgRating}</strong> ortalama</span>
            <span>
              Fiyat: {priceDist.map((c, i) => c > 0 ? (
                <span key={i} className="ml-1">{getPriceSymbol(i + 1)}:{c}</span>
              ) : null)}
            </span>
          </div>
        </header>

        {topLandmarks.length > 0 && (
          <section className="mb-10 bg-amber-50 border border-amber-100 rounded-lg p-5">
            <h2 className="text-sm font-semibold text-amber-900 uppercase tracking-wide mb-3">
              Yakındaki landmark&apos;lar
            </h2>
            <ul className="text-sm text-amber-900 space-y-1">
              {topLandmarks.map(([name, dist]) => (
                <li key={name}>
                  <strong>{name}</strong> — {dist < 1000 ? `${dist}m` : `${(dist / 1000).toFixed(1)}km`} mesafede
                </li>
              ))}
            </ul>
          </section>
        )}

        {topTransit.length > 0 && (
          <section className="mb-10 bg-blue-50 border border-blue-100 rounded-lg p-5">
            <h2 className="text-sm font-semibold text-blue-900 uppercase tracking-wide mb-3">
              Ulaşım
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
                      <span className="text-xs bg-green-50 text-green-700 px-2 py-0.5 rounded">Doğrulandı</span>
                    )}
                  </div>
                  <p className="text-sm text-gray-500">
                    {r.cuisine} · {getPriceSymbol(r.priceRange)}
                  </p>
                  <p className="text-sm text-gray-600 mt-2">{r.llmSummary}</p>
                  {r.specialFeatures?.popularDishes && r.specialFeatures.popularDishes.length > 0 && (
                    <p className="text-xs text-gray-500 mt-2">
                      <span className="text-gray-400">Popüler: </span>
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
                  <div className="text-xs text-gray-400">{r.reviewCount} yorum</div>
                </div>
              </div>
            </Link>
          ))}
        </div>

        <footer className="mt-16 pt-8 border-t border-gray-100 text-xs text-gray-400 space-y-1">
          <p>
            <Link href={`/${city}`} className="text-blue-500 hover:underline">
              ← {cityName} tüm restoranları
            </Link>
          </p>
          <p>
            Makine-okunabilir veri:{" "}
            <a href={`/api/restaurants?city=${city}`} className="text-blue-500 hover:underline">
              /api/restaurants?city={city}
            </a>
          </p>
        </footer>
      </main>
    </>
  );
}
