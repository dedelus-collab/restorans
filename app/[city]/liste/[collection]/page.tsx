import { notFound } from "next/navigation";
import Link from "next/link";
import type { Metadata } from "next";
import { getRestaurantsByCity, getPriceSymbol } from "@/data/restaurants";
import { COLLECTIONS, getCollection } from "@/lib/collections";

type Props = { params: Promise<{ city: string; collection: string }> };

export async function generateStaticParams() {
  return COLLECTIONS.map(c => ({ city: "istanbul", collection: c.slug }));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { city, collection: colSlug } = await params;
  const col = getCollection(colSlug);
  if (!col) return {};
  return {
    title: `${col.title} | restorans`,
    description: col.description,
    alternates: { canonical: `https://restorans.vercel.app/${city}/liste/${colSlug}` },
    openGraph: {
      type: "website",
      url: `https://restorans.vercel.app/${city}/liste/${colSlug}`,
      title: col.title,
      description: col.description,
      siteName: "Istanbul Restaurants",
      locale: "tr_TR",
    },
    twitter: {
      card: "summary_large_image",
      title: col.title,
      description: col.description,
    },
  };
}

export default async function CollectionPage({ params }: Props) {
  const { city, collection: colSlug } = await params;
  const col = getCollection(colSlug);
  if (!col) notFound();

  const allRestaurants = getRestaurantsByCity(city);
  const list = allRestaurants.filter(col.filter).sort((a, b) => (b.avgRating || 0) - (a.avgRating || 0));
  if (!list.length) notFound();

  const cityName = allRestaurants[0]?.city ?? city;

  // Yan panel: mahalleler içinde kaçı var
  const hoodMap = new Map<string, number>();
  for (const r of list) {
    if (!r.neighborhood) continue;
    hoodMap.set(r.neighborhood, (hoodMap.get(r.neighborhood) || 0) + 1);
  }
  const topHoods = Array.from(hoodMap.entries()).sort((a, b) => b[1] - a[1]).slice(0, 8);

  const avgRating = (list.reduce((s, r) => s + (r.avgRating || 0), 0) / list.length).toFixed(1);
  const totalReviews = list.reduce((s, r) => s + (r.reviewCount || 0), 0);

  // Cross-link: related koleksiyonlar
  const relatedCollections = (col.related ?? [])
    .map(slug => COLLECTIONS.find(c => c.slug === slug))
    .filter((c): c is NonNullable<typeof c> => !!c)
    .map(c => ({
      ...c,
      count: allRestaurants.filter(c.filter).length,
    }))
    .filter(c => c.count > 0);

  // Diğer aynı kategori koleksiyonları (related'da olmayanlar)
  const sameCategoryOthers = COLLECTIONS.filter(
    c => c.category === col.category &&
         c.slug !== colSlug &&
         !(col.related ?? []).includes(c.slug)
  ).map(c => ({ ...c, count: allRestaurants.filter(c.filter).length }))
   .filter(c => c.count > 0);

  const itemListJsonLd = {
    "@context": "https://schema.org",
    "@type": "ItemList",
    name: col.title,
    description: col.description,
    url: `https://restorans.vercel.app/${city}/liste/${colSlug}`,
    numberOfItems: list.length,
    itemListElement: list.slice(0, 20).map((r, i) => ({
      "@type": "ListItem",
      position: i + 1,
      name: r.name,
      url: `https://restorans.vercel.app/${city}/${r.slug}`,
      description: r.llmSummary,
    })),
  };

  const breadcrumbJsonLd = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: [
      { "@type": "ListItem", position: 1, name: cityName, item: `https://restorans.vercel.app/${city}` },
      { "@type": "ListItem", position: 2, name: col.title, item: `https://restorans.vercel.app/${city}/liste/${colSlug}` },
    ],
  };

  const collectionPageJsonLd = {
    "@context": "https://schema.org",
    "@type": "CollectionPage",
    "@id": `https://restorans.vercel.app/${city}/liste/${colSlug}`,
    name: col.title,
    description: col.description,
    url: `https://restorans.vercel.app/${city}/liste/${colSlug}`,
    about: { "@type": "Restaurant", servesCuisine: col.title },
    provider: { "@type": "Organization", name: "Istanbul Restaurants", url: "https://restorans.vercel.app" },
  };

  const categoryLabels: Record<string, string> = {
    cuisine: "Mutfak",
    scenario: "Senaryo",
    vibe: "Ortam & Vibe",
  };

  return (
    <>
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(collectionPageJsonLd) }} />
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(itemListJsonLd) }} />
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbJsonLd) }} />

      <main className="max-w-4xl mx-auto px-6 py-16">
        <nav className="text-xs text-gray-400 mb-4 flex gap-2">
          <Link href={`/${city}`} className="hover:underline">{cityName}</Link>
          <span>/</span>
          <Link href={`/${city}#listeler`} className="hover:underline">Listeler</Link>
          <span>/</span>
          <span className="text-gray-700">{col.title}</span>
        </nav>

        <header className="mb-10">
          <span className="text-xs font-semibold text-blue-600 uppercase tracking-wide">
            {categoryLabels[col.category]}
          </span>
          <h1 className="text-3xl font-bold mt-1 mb-3">{col.title}</h1>
          <p className="text-gray-600 leading-relaxed mb-5">{col.description}</p>
          <div className="flex flex-wrap gap-5 text-sm text-gray-500 border-t border-gray-100 pt-5">
            <span><strong className="text-gray-900">{list.length}</strong> restoran</span>
            <span><strong className="text-gray-900">{avgRating}</strong> ortalama puan</span>
            <span><strong className="text-gray-900">{totalReviews.toLocaleString("tr-TR")}</strong> yorum</span>
          </div>
        </header>

        {/* Mahalle dağılımı */}
        {topHoods.length > 1 && (
          <section className="mb-8">
            <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">Mahalleler</h2>
            <div className="flex flex-wrap gap-2">
              {topHoods.map(([name, count]) => (
                <span key={name} className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded">
                  {name} <span className="text-gray-400">({count})</span>
                </span>
              ))}
            </div>
          </section>
        )}

        {/* Restoran listesi */}
        <div className="divide-y divide-gray-100">
          {list.map((r, idx) => (
            <Link
              key={r.id}
              href={`/${city}/${r.slug}`}
              className="block py-6 hover:bg-gray-50 transition-colors px-2 -mx-2 rounded"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    {idx < 3 && (
                      <span className="text-xs font-bold text-amber-600 bg-amber-50 px-1.5 py-0.5 rounded">
                        #{idx + 1}
                      </span>
                    )}
                    <h2 className="font-semibold">{r.name}</h2>
                    {r.verifiedData && (
                      <span className="text-xs bg-green-50 text-green-700 px-2 py-0.5 rounded">Doğrulandı</span>
                    )}
                  </div>
                  <p className="text-sm text-gray-500">
                    {r.neighborhood} · {r.cuisine} · {getPriceSymbol(r.priceRange)}
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
                  <div className="text-xs text-gray-400 mt-0.5">{getPriceSymbol(r.priceRange)}</div>
                </div>
              </div>
            </Link>
          ))}
        </div>

        {/* Cross-link: İlgili koleksiyonlar */}
        {relatedCollections.length > 0 && (
          <section className="mt-16 pt-8 border-t border-gray-100">
            <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wide mb-5">
              Bunlar da İlginizi Çekebilir
            </h2>
            <div className="grid sm:grid-cols-2 gap-3">
              {relatedCollections.map(c => (
                <Link
                  key={c.slug}
                  href={`/${city}/liste/${c.slug}`}
                  className="group border border-gray-200 rounded-lg px-4 py-3 hover:border-gray-400 hover:shadow-sm transition-all"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-medium text-sm text-gray-900 group-hover:text-gray-700">
                        {c.title}
                      </div>
                      <div className="text-xs text-gray-400 mt-0.5">{c.count} restoran</div>
                    </div>
                    <span className="text-gray-300 group-hover:text-gray-500 text-lg">→</span>
                  </div>
                </Link>
              ))}
            </div>
          </section>
        )}

        {/* Aynı kategori — diğerleri */}
        {sameCategoryOthers.length > 0 && (
          <section className="mt-8">
            <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wide mb-3">
              {col.category === "cuisine" ? "Diğer Mutfaklar" :
               col.category === "scenario" ? "Diğer Senaryolar" : "Diğer Listeler"}
            </h2>
            <div className="flex flex-wrap gap-2">
              {sameCategoryOthers.map(c => (
                <Link
                  key={c.slug}
                  href={`/${city}/liste/${c.slug}`}
                  className="text-sm border border-gray-200 hover:border-gray-400 text-gray-600 px-3 py-1.5 rounded-lg transition-colors"
                >
                  {c.title.replace(/İstanbul'(da|un|daki)\s/i, "").split(" ").slice(0, 4).join(" ")}
                  <span className="text-gray-400 ml-1">({c.count})</span>
                </Link>
              ))}
            </div>
          </section>
        )}

        <footer className="mt-8 text-xs text-gray-400 space-y-1">
          <p>
            <Link href={`/${city}`} className="text-blue-500 hover:underline">
              ← {cityName} tüm restoranları
            </Link>
          </p>
          <p>
            Makine-okunabilir:{" "}
            <a href={`/api/restaurants?city=${city}`} className="text-blue-500 hover:underline">
              JSON API
            </a>
          </p>
        </footer>
      </main>
    </>
  );
}
