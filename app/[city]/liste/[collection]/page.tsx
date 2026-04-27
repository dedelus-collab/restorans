import { notFound } from "next/navigation";
import Link from "next/link";
import type { Metadata } from "next";
import { getRestaurantsByCity, weightedScore, getDistrictForRestaurant } from "@/data/restaurants";
import { COLLECTIONS, getCollection } from "@/lib/collections";
import { CollectionList } from "@/components/CollectionList";

type Props = { params: Promise<{ city: string; collection: string }> };

export async function generateStaticParams() {
  return COLLECTIONS.map(c => ({ city: "istanbul", collection: c.slug }));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { city, collection: colSlug } = await params;
  const col = getCollection(colSlug);
  if (!col) return {};
  return {
    title: `${col.title} | Istanbul Restaurants`,
    description: col.description,
    alternates: { canonical: `https://www.restaurantsistanbul.com/${city}/liste/${colSlug}` },
    openGraph: {
      type: "website",
      url: `https://www.restaurantsistanbul.com/${city}/liste/${colSlug}`,
      title: col.title,
      description: col.description,
      siteName: "Istanbul Restaurants",
      locale: "en_US",
    },
    twitter: {
      card: "summary_large_image",
      title: col.title,
      description: col.description,
    },
  };
}

const COLLECTION_PHOTOS: Record<string, { photo: string; color: string }> = {
  "romantik-aksam-yemegi-istanbul": { photo: "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=1200&q=80&auto=format&fit=crop", color: "#9f1239" },
  "is-yemegi-istanbul":             { photo: "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=1200&q=80&auto=format&fit=crop", color: "#1e3a5f" },
  "ozel-gun-istanbul":              { photo: "https://images.unsplash.com/photo-1559339352-11d035aa65de?w=1200&q=80&auto=format&fit=crop", color: "#7e22ce" },
  "gec-acik-istanbul":              { photo: "https://images.unsplash.com/photo-1524231757912-21f4fe3a7200?w=1200&q=80&auto=format&fit=crop", color: "#1e1b4b" },
  "aile-dostu-istanbul":            { photo: "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=1200&q=80&auto=format&fit=crop", color: "#166534" },
  "vejetaryen-vegan-istanbul":      { photo: "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=1200&q=80&auto=format&fit=crop", color: "#15803d" },
  "manzarali-istanbul":             { photo: "https://images.unsplash.com/photo-1541432901042-2d8bd64b4a9b?w=1200&q=80&auto=format&fit=crop", color: "#0369a1" },
  "bogaz-manzarali-istanbul":       { photo: "https://images.unsplash.com/photo-1524231757912-21f4fe3a7200?w=1200&q=80&auto=format&fit=crop", color: "#075985" },
  "uygun-fiyatli-istanbul":         { photo: "https://images.unsplash.com/photo-1547592180-85f173990554?w=1200&q=80&auto=format&fit=crop", color: "#92400e" },
  "fine-dining-istanbul":           { photo: "https://images.unsplash.com/photo-1559339352-11d035aa65de?w=1200&q=80&auto=format&fit=crop", color: "#3b0764" },
  "teras-istanbul":                 { photo: "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=1200&q=80&auto=format&fit=crop", color: "#064e3b" },
  "kebap-istanbul":                 { photo: "https://images.unsplash.com/photo-1529543544282-ea669407fca3?w=1200&q=80&auto=format&fit=crop", color: "#b91c1c" },
  "balik-deniz-urunleri-istanbul":  { photo: "https://images.unsplash.com/photo-1560717845-968823efbee1?w=1200&q=80&auto=format&fit=crop", color: "#0369a1" },
  "pizza-italyan-istanbul":         { photo: "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=1200&q=80&auto=format&fit=crop", color: "#166534" },
  "sushi-japon-istanbul":           { photo: "https://images.unsplash.com/photo-1579584425555-c3ce17fd4351?w=1200&q=80&auto=format&fit=crop", color: "#9f1239" },
  "burger-steak-istanbul":          { photo: "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=1200&q=80&auto=format&fit=crop", color: "#b45309" },
  "kahvalti-istanbul":              { photo: "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=1200&q=80&auto=format&fit=crop", color: "#b45309" },
  "meyhane-istanbul":               { photo: "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=1200&q=80&auto=format&fit=crop", color: "#7e22ce" },
  "lokanta-istanbul":               { photo: "https://images.unsplash.com/photo-1547592180-85f173990554?w=1200&q=80&auto=format&fit=crop", color: "#c2410c" },
  "turk-mutfagi-istanbul":          { photo: "https://images.unsplash.com/photo-1547592180-85f173990554?w=1200&q=80&auto=format&fit=crop", color: "#991b1b" },
  "kafe-istanbul":                  { photo: "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=1200&q=80&auto=format&fit=crop", color: "#92400e" },
  "pide-istanbul":                  { photo: "https://images.unsplash.com/photo-1555507036-ab1f4038808a?w=1200&q=80&auto=format&fit=crop", color: "#d97706" },
  "dunya-mutfagi-istanbul":         { photo: "https://images.unsplash.com/photo-1559339352-11d035aa65de?w=1200&q=80&auto=format&fit=crop", color: "#0e7490" },
};
const DEFAULT_PHOTO = { photo: "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=1200&q=80&auto=format&fit=crop", color: "#334155" };

const RELATED_THUMBS: Record<string, string> = {
  "romantik-aksam-yemegi-istanbul": "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=400&q=70&auto=format&fit=crop",
  "balik-deniz-urunleri-istanbul":  "https://images.unsplash.com/photo-1560717845-968823efbee1?w=400&q=70&auto=format&fit=crop",
  "kebap-istanbul":                 "https://images.unsplash.com/photo-1529543544282-ea669407fca3?w=400&q=70&auto=format&fit=crop",
  "manzarali-istanbul":             "https://images.unsplash.com/photo-1541432901042-2d8bd64b4a9b?w=400&q=70&auto=format&fit=crop",
  "is-yemegi-istanbul":             "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=400&q=70&auto=format&fit=crop",
  "gec-acik-istanbul":              "https://images.unsplash.com/photo-1524231757912-21f4fe3a7200?w=400&q=70&auto=format&fit=crop",
  "kahvalti-istanbul":              "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=400&q=70&auto=format&fit=crop",
  "fine-dining-istanbul":           "https://images.unsplash.com/photo-1559339352-11d035aa65de?w=400&q=70&auto=format&fit=crop",
  "meyhane-istanbul":               "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=400&q=70&auto=format&fit=crop",
  "sushi-japon-istanbul":           "https://images.unsplash.com/photo-1579584425555-c3ce17fd4351?w=400&q=70&auto=format&fit=crop",
  "burger-steak-istanbul":          "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400&q=70&auto=format&fit=crop",
  "pizza-italyan-istanbul":         "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=400&q=70&auto=format&fit=crop",
  "bogaz-manzarali-istanbul":       "https://images.unsplash.com/photo-1524231757912-21f4fe3a7200?w=400&q=70&auto=format&fit=crop",
  "vejetaryen-vegan-istanbul":      "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=400&q=70&auto=format&fit=crop",
};
const DEFAULT_THUMB = "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=400&q=70&auto=format&fit=crop";

export default async function CollectionPage({ params }: Props) {
  const { city, collection: colSlug } = await params;
  const col = getCollection(colSlug);
  if (!col) notFound();

  const allRestaurants = getRestaurantsByCity(city);
  const list = allRestaurants.filter(col.filter).sort((a, b) => weightedScore(b) - weightedScore(a));
  if (!list.length) notFound();

  const cityName = allRestaurants[0]?.city ?? city;

  const districtMap = new Map<string, number>();
  for (const r of list) {
    const d = getDistrictForRestaurant(r);
    if (!d) continue;
    districtMap.set(d, (districtMap.get(d) || 0) + 1);
  }
  const topHoods = Array.from(districtMap.entries()).sort((a, b) => b[1] - a[1]);

  const listWithDistrict = list.map(r => ({
    ...r,
    district: getDistrictForRestaurant(r) || r.neighborhood || "",
  }));

  const avgRating = (list.reduce((s, r) => s + (r.avgRating || 0), 0) / list.length).toFixed(1);
  const totalReviews = list.reduce((s, r) => s + (r.reviewCount || 0), 0);

  const relatedCollections = (col.related ?? [])
    .map(slug => COLLECTIONS.find(c => c.slug === slug))
    .filter((c): c is NonNullable<typeof c> => !!c)
    .map(c => ({ ...c, count: allRestaurants.filter(c.filter).length }))
    .filter(c => c.count > 0);

  const sameCategoryOthers = COLLECTIONS.filter(
    c => c.category === col.category &&
         c.slug !== colSlug &&
         !(col.related ?? []).includes(c.slug)
  ).map(c => ({ ...c, count: allRestaurants.filter(c.filter).length }))
   .filter(c => c.count > 0);

  const heroTheme = COLLECTION_PHOTOS[colSlug] ?? DEFAULT_PHOTO;

  const categoryLabels: Record<string, string> = {
    cuisine: "Cuisine Guide",
    scenario: "Curated List",
    vibe: "Ambiance & Vibe",
  };

  const itemListJsonLd = {
    "@context": "https://schema.org",
    "@type": "ItemList",
    name: col.title,
    description: col.description,
    url: `https://www.restaurantsistanbul.com/${city}/liste/${colSlug}`,
    numberOfItems: list.length,
    itemListElement: list.slice(0, 20).map((r, i) => ({
      "@type": "ListItem",
      position: i + 1,
      name: r.name,
      url: `https://www.restaurantsistanbul.com/${city}/${r.slug}`,
      description: r.llmSummary,
    })),
  };

  const breadcrumbJsonLd = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: [
      { "@type": "ListItem", position: 1, name: cityName, item: `https://www.restaurantsistanbul.com/${city}` },
      { "@type": "ListItem", position: 2, name: col.title, item: `https://www.restaurantsistanbul.com/${city}/liste/${colSlug}` },
    ],
  };

  const collectionPageJsonLd = {
    "@context": "https://schema.org",
    "@type": "CollectionPage",
    "@id": `https://www.restaurantsistanbul.com/${city}/liste/${colSlug}`,
    name: col.title,
    description: col.description,
    url: `https://www.restaurantsistanbul.com/${city}/liste/${colSlug}`,
    about: { "@type": "Restaurant", servesCuisine: col.title },
    provider: { "@type": "Organization", name: "Istanbul Restaurants", url: "https://www.restaurantsistanbul.com" },
  };

  return (
    <>
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(collectionPageJsonLd) }} />
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(itemListJsonLd) }} />
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbJsonLd) }} />

      {/* ── HERO ── */}
      <header className="relative flex flex-col justify-end overflow-hidden" style={{ minHeight: "360px" }}>
        <div
          className="absolute inset-0"
          style={{
            backgroundImage: `url('${heroTheme.photo}')`,
            backgroundSize: "cover",
            backgroundPosition: "center",
          }}
        />
        <div
          className="absolute inset-0"
          style={{ background: `linear-gradient(to top, ${heroTheme.color}f0 0%, ${heroTheme.color}99 40%, transparent 100%)` }}
        />

        <div className="relative max-w-4xl mx-auto px-6 pt-20 pb-10 w-full">
          <nav className="text-xs text-white/50 mb-4 flex items-center gap-1.5">
            <Link href={`/${city}`} className="hover:text-white/80 transition-colors">{cityName}</Link>
            <span>/</span>
            <span className="text-white/80">{categoryLabels[col.category]}</span>
          </nav>
          <span className="inline-block text-xs font-bold text-white/60 uppercase tracking-widest mb-2">
            {categoryLabels[col.category]}
          </span>
          <h1 className="text-4xl sm:text-5xl font-black text-white leading-tight mb-3 drop-shadow-sm">
            {col.title}
          </h1>
          <p className="text-white/75 text-base max-w-xl leading-relaxed">{col.description}</p>
        </div>

        {/* Stats strip */}
        <div className="relative border-t border-white/10 bg-black/40 backdrop-blur-md">
          <div className="max-w-4xl mx-auto px-6 py-4 flex gap-8 sm:gap-12">
            <div>
              <div className="text-xl font-black text-white">{list.length}</div>
              <div className="text-xs text-white/50 mt-0.5">Restaurants</div>
            </div>
            <div>
              <div className="text-xl font-black text-white">{avgRating} ★</div>
              <div className="text-xs text-white/50 mt-0.5">Avg rating</div>
            </div>
            <div>
              <div className="text-xl font-black text-white">{(totalReviews / 1000).toFixed(0)}K+</div>
              <div className="text-xs text-white/50 mt-0.5">Reviews</div>
            </div>
            <div>
              <div className="text-xl font-black text-white">{topHoods.length}</div>
              <div className="text-xs text-white/50 mt-0.5">Districts</div>
            </div>
          </div>
        </div>
      </header>

      <main>
        {/* ── RESTAURANT LIST ── */}
        <section className="py-12">
          <div className="max-w-4xl mx-auto px-6">
            <CollectionList
              city={city}
              list={listWithDistrict}
              topDistricts={topHoods}
            />
          </div>
        </section>

        {/* ── RELATED COLLECTIONS ── */}
        {relatedCollections.length > 0 && (
          <section className="py-10 border-t border-gray-100">
            <div className="max-w-4xl mx-auto px-6">
              <h2 className="text-xl font-black text-gray-900 mb-5">You Might Also Like</h2>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                {relatedCollections.map(c => {
                  const thumb = RELATED_THUMBS[c.slug] ?? DEFAULT_THUMB;
                  const relTheme = COLLECTION_PHOTOS[c.slug] ?? DEFAULT_PHOTO;
                  return (
                    <Link
                      key={c.slug}
                      href={`/${city}/liste/${c.slug}`}
                      className="group rounded-2xl overflow-hidden border border-gray-100 hover:shadow-lg hover:-translate-y-1 transition-all duration-200"
                    >
                      <div
                        className="relative h-20 overflow-hidden"
                        style={{ backgroundImage: `url('${thumb}')`, backgroundSize: "cover", backgroundPosition: "center" }}
                      >
                        <div className="absolute inset-0" style={{ background: `linear-gradient(to top, ${relTheme.color}cc, transparent)` }} />
                      </div>
                      <div className="p-2.5 bg-white">
                        <div className="font-bold text-xs text-gray-900 group-hover:text-blue-600 transition-colors leading-tight line-clamp-2">
                          {c.title.replace(" in Istanbul", "").replace(" Restaurants", "")}
                        </div>
                        <div className="text-xs text-gray-400 mt-0.5">{c.count} places</div>
                      </div>
                    </Link>
                  );
                })}
              </div>
            </div>
          </section>
        )}

        {/* ── SAME CATEGORY ── */}
        {sameCategoryOthers.length > 0 && (
          <section className="py-8 border-t border-gray-100">
            <div className="max-w-4xl mx-auto px-6">
              <h2 className="text-sm font-bold text-gray-500 uppercase tracking-widest mb-3">
                {col.category === "cuisine" ? "Other Cuisines" :
                 col.category === "scenario" ? "More Scenarios" : "More Lists"}
              </h2>
              <div className="flex flex-wrap gap-2">
                {sameCategoryOthers.map(c => (
                  <Link
                    key={c.slug}
                    href={`/${city}/liste/${c.slug}`}
                    className="text-sm border border-gray-200 hover:border-gray-900 hover:bg-gray-900 hover:text-white text-gray-700 font-medium px-4 py-2 rounded-full transition-all"
                  >
                    {c.title.replace(" in Istanbul", "").replace(" Restaurants", "").replace(" Istanbul", "").split(" ").slice(0, 4).join(" ")}
                    <span className="text-gray-400 ml-1.5 text-xs group-hover:text-gray-300">({c.count})</span>
                  </Link>
                ))}
              </div>
            </div>
          </section>
        )}

        <div className="border-t border-gray-100 py-6">
          <div className="max-w-4xl mx-auto px-6 flex items-center justify-between flex-wrap gap-2 text-xs text-gray-400">
            <Link href={`/${city}`} className="text-blue-500 hover:underline font-medium">
              ← All {cityName} restaurants
            </Link>
            <a href={`/api/restaurants?city=${city}`} className="text-blue-500 hover:underline">JSON API</a>
          </div>
        </div>
      </main>
    </>
  );
}
