import { notFound } from "next/navigation";
import Link from "next/link";
import type { Metadata } from "next";
import { getRestaurantsByCity, weightedScore, getDistrictForRestaurant } from "@/data/restaurants";
import { COLLECTIONS, getCollection } from "@/lib/collections";
import { AniHead, SpeechBubble } from "@/components/AniMascot";
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
    alternates: { canonical: `https://restaurantsistanbul.vercel.app/${city}/liste/${colSlug}` },
    openGraph: {
      type: "website",
      url: `https://restaurantsistanbul.vercel.app/${city}/liste/${colSlug}`,
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

  // Listeye district alanı ekle (CollectionList client component için)
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

  const itemListJsonLd = {
    "@context": "https://schema.org",
    "@type": "ItemList",
    name: col.title,
    description: col.description,
    url: `https://restaurantsistanbul.vercel.app/${city}/liste/${colSlug}`,
    numberOfItems: list.length,
    itemListElement: list.slice(0, 20).map((r, i) => ({
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
      { "@type": "ListItem", position: 2, name: col.title, item: `https://restaurantsistanbul.vercel.app/${city}/liste/${colSlug}` },
    ],
  };

  const collectionPageJsonLd = {
    "@context": "https://schema.org",
    "@type": "CollectionPage",
    "@id": `https://restaurantsistanbul.vercel.app/${city}/liste/${colSlug}`,
    name: col.title,
    description: col.description,
    url: `https://restaurantsistanbul.vercel.app/${city}/liste/${colSlug}`,
    about: { "@type": "Restaurant", servesCuisine: col.title },
    provider: { "@type": "Organization", name: "Istanbul Restaurants", url: "https://restaurantsistanbul.vercel.app" },
  };

  const categoryLabels: Record<string, string> = {
    cuisine: "Cuisine",
    scenario: "Scenario",
    vibe: "Ambiance & Vibe",
  };

  type AniVariant = "chef" | "reviewer" | "foodie" | "explorer" | "star";
  const slugVariantMap: Record<string, AniVariant> = {
    // scenario
    "romantik-aksam-yemegi-istanbul": "star",
    "is-yemegi-istanbul": "reviewer",
    "ozel-gun-istanbul": "star",
    "gec-acik-istanbul": "explorer",
    "aile-dostu-istanbul": "foodie",
    "vejetaryen-vegan-istanbul": "foodie",
    // vibe
    "manzarali-istanbul": "explorer",
    "bogaz-manzarali-istanbul": "explorer",
    "uygun-fiyatli-istanbul": "reviewer",
    "fine-dining-istanbul": "star",
    "teras-istanbul": "foodie",
  };
  const categoryFallback: Record<string, AniVariant> = {
    cuisine: "chef",
    scenario: "star",
    vibe: "explorer",
  };
  const aniVariant: AniVariant = slugVariantMap[colSlug] ?? categoryFallback[col.category] ?? "chef";

  const slugSpeech: Record<string, string> = {
    "romantik-aksam-yemegi-istanbul": "Perfect for date night! ♥",
    "is-yemegi-istanbul": "Client approved! ✓",
    "ozel-gun-istanbul": "Make it special! ★",
    "gec-acik-istanbul": "Still open! 🌙",
    "aile-dostu-istanbul": "Kids welcome! ☺",
    "vejetaryen-vegan-istanbul": "Plant-powered! ✿",
    "manzarali-istanbul": "What a view! ✦",
    "bogaz-manzarali-istanbul": "Bosphorus! ⛵",
    "uygun-fiyatli-istanbul": "Great value! ✓",
    "fine-dining-istanbul": "Exquisite! ✦",
    "teras-istanbul": "Fresh air dining! ✿",
    "kebap-istanbul": "Best kebap! 🔥",
    "balik-deniz-urunleri-istanbul": "Fresh catch! ✦",
    "kahvalti-istanbul": "Breakfast time! ☀",
    "meyhane-istanbul": "Rakı & meze! ♪",
  };
  const speech = slugSpeech[colSlug] ?? `${list.length} top picks! ★`;

  return (
    <>
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(collectionPageJsonLd) }} />
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(itemListJsonLd) }} />
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbJsonLd) }} />

      <main className="max-w-4xl mx-auto px-6 py-16">
        <nav className="text-xs text-gray-400 mb-4 flex gap-2">
          <Link href={`/${city}`} className="hover:underline">{cityName}</Link>
          <span>/</span>
          <Link href={`/${city}#listeler`} className="hover:underline">Lists</Link>
          <span>/</span>
          <span className="text-gray-700">{col.title}</span>
        </nav>

        <header className="mb-10 flex items-start gap-6">
          <div className="flex-1 min-w-0">
            <span className="text-xs font-semibold text-blue-600 uppercase tracking-wide">
              {categoryLabels[col.category]}
            </span>
            <h1 className="text-3xl font-bold mt-1 mb-3">{col.title}</h1>
            <p className="text-gray-600 leading-relaxed mb-5">{col.description}</p>
            <div className="flex flex-wrap gap-5 text-sm text-gray-500 border-t border-gray-100 pt-5">
              <span><strong className="text-gray-900">{list.length}</strong> restaurants</span>
              <span><strong className="text-gray-900">{avgRating}</strong> avg. rating</span>
              <span><strong className="text-gray-900">{totalReviews.toLocaleString("en-US")}</strong> reviews</span>
            </div>
          </div>
          <div className="hidden sm:flex flex-col items-center gap-2 shrink-0 pt-4">
            <SpeechBubble text={speech} />
            <AniHead variant={aniVariant} className="w-24 h-24 drop-shadow-sm" />
          </div>
        </header>

        <CollectionList
          city={city}
          list={listWithDistrict}
          topDistricts={topHoods}
        />

        {/* Related collections */}
        {relatedCollections.length > 0 && (
          <section className="mt-16 pt-8 border-t border-gray-100">
            <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wide mb-5">
              You Might Also Like
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
                      <div className="text-xs text-gray-400 mt-0.5">{c.count} restaurants</div>
                    </div>
                    <span className="text-gray-300 group-hover:text-gray-500 text-lg">→</span>
                  </div>
                </Link>
              ))}
            </div>
          </section>
        )}

        {/* Same category others */}
        {sameCategoryOthers.length > 0 && (
          <section className="mt-8">
            <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wide mb-3">
              {col.category === "cuisine" ? "Other Cuisines" :
               col.category === "scenario" ? "Other Scenarios" : "Other Lists"}
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
              ← All {cityName} restaurants
            </Link>
          </p>
          <p>
            Machine-readable:{" "}
            <a href={`/api/restaurants?city=${city}`} className="text-blue-500 hover:underline">
              JSON API
            </a>
          </p>
        </footer>
      </main>
    </>
  );
}
