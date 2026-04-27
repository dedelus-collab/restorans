import { notFound } from "next/navigation";
import Link from "next/link";
import { getRestaurantBySlug, getPriceSymbol, getAllSlugs } from "@/data/restaurants";
import type { Metadata } from "next";

type Props = { params: Promise<{ city: string; slug: string }> };

export function generateStaticParams() {
  return getAllSlugs();
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { city, slug } = await params;
  const r = getRestaurantBySlug(city, slug);
  if (!r) return {};
  return {
    title: `${r.name} — ${r.neighborhood}, ${r.city} | Istanbul Restaurants`,
    description: r.llmSummary,
    alternates: { canonical: `https://www.restaurantsistanbul.com/${city}/${slug}` },
    openGraph: {
      type: "website",
      url: `https://www.restaurantsistanbul.com/${city}/${slug}`,
      title: `${r.name} — ${r.neighborhood}, ${r.city}`,
      description: r.llmSummary ?? undefined,
      siteName: "Istanbul Restaurants",
      locale: "en_US",
    },
    twitter: {
      card: "summary_large_image",
      title: `${r.name} — ${r.neighborhood}, ${r.city}`,
      description: r.llmSummary ?? undefined,
    },
  };
}

const CUISINE_PHOTOS: Record<string, { photo: string; color: string }> = {
  kebap:           { photo: "https://images.unsplash.com/photo-1529543544282-ea669407fca3?w=1200&q=80&auto=format&fit=crop", color: "#7f1d1d" },
  balik:           { photo: "https://images.unsplash.com/photo-1560717845-968823efbee1?w=1200&q=80&auto=format&fit=crop", color: "#0c4a6e" },
  "pizza-italyan": { photo: "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=1200&q=80&auto=format&fit=crop", color: "#14532d" },
  "sushi-japon":   { photo: "https://images.unsplash.com/photo-1579584425555-c3ce17fd4351?w=1200&q=80&auto=format&fit=crop", color: "#4c0519" },
  "burger-steak":  { photo: "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=1200&q=80&auto=format&fit=crop", color: "#78350f" },
  kahvalti:        { photo: "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=1200&q=80&auto=format&fit=crop", color: "#78350f" },
  meyhane:         { photo: "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=1200&q=80&auto=format&fit=crop", color: "#3b0764" },
  vegan:           { photo: "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=1200&q=80&auto=format&fit=crop", color: "#14532d" },
  lokanta:         { photo: "https://images.unsplash.com/photo-1547592180-85f173990554?w=1200&q=80&auto=format&fit=crop", color: "#7c2d12" },
  kafe:            { photo: "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=1200&q=80&auto=format&fit=crop", color: "#451a03" },
  pide:            { photo: "https://images.unsplash.com/photo-1555507036-ab1f4038808a?w=1200&q=80&auto=format&fit=crop", color: "#78350f" },
  "turk-mutfagi":  { photo: "https://images.unsplash.com/photo-1547592180-85f173990554?w=1200&q=80&auto=format&fit=crop", color: "#7f1d1d" },
  "dunya-mutfagi": { photo: "https://images.unsplash.com/photo-1559339352-11d035aa65de?w=1200&q=80&auto=format&fit=crop", color: "#0c4a6e" },
  italyan:         { photo: "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=1200&q=80&auto=format&fit=crop", color: "#14532d" },
  seafood:         { photo: "https://images.unsplash.com/photo-1560717845-968823efbee1?w=1200&q=80&auto=format&fit=crop", color: "#0c4a6e" },
};
const DEFAULT_PHOTO = { photo: "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=1200&q=80&auto=format&fit=crop", color: "#1c1917" };

const TRANSIT_ICONS: Record<string, string> = {
  metro: "🚇", tramvay: "🚊", vapur: "⛴️", marmaray: "🚆", metrobus: "🚌",
};

const FALSY = new Set([
  "false", "False", "hayır", "yanlış", "yanlıs", "yanlis", "yanıtsız",
  "no", "0", "", "değil", "Hayır", "olmaz", "uygun degil", "devam",
  "olay", "none", "Hemse",
]);
const SCENARIO_MAP: Record<string, string> = {
  // affirmative
  evet: "Yes", Evet: "Yes", true: "Yes", True: "Yes",
  doğru: "Yes", uygun: "Suitable", Uygun: "Suitable", olabilir: "Possibly suitable",
  // budget
  orta: "Mid-range", ortada: "Mid-range", ortalama: "Mid-range", Orta: "Mid-range",
  "ortaya yakın": "Mid-range",
  // birthday
  birthday: "Great for birthdays",
  "birthday için uygun": "Suitable for birthdays",
  "birthday için ideal": "Ideal for birthdays",
  "birthdayne uygun": "Suitable for birthdays",
  "birthday kutlama sunar": "Offers birthday celebrations",
  "special occasion için uygun": "Suitable for special occasions",
  "special occasion": "Great for special occasions",
  önerilir: "Recommended",
  dogum: "Great for birthdays",
  "dogum gunu": "Great for birthdays",
  // romantic
  romantic: "Romantic setting",
  // tourist
  scenic: "Scenic location", manzarali: "Scenic views",
  "Bosphorus view": "Bosphorus view",
  seyyah: "Tourist friendly", seyahatçi: "Tourist friendly", tourist: "Tourist friendly",
  // group / family
  "iş yemeği": "Great for business meals",
  "iş yemeği, büyük grup": "Great for business meals & large groups",
  "iş yemeği/büyük grup": "Great for business meals & large groups",
  "büyük grup": "Great for large groups", buyuk: "Large groups welcome",
  "buyuk grup": "Great for large groups",
  family: "Family friendly", "family dostu": "Family friendly",
  "arkadaşları ile akşam yemeği için uygun": "Great for group dinners with friends",
  // late night
  gece: "Great for evenings",
  "gec acik": "Open late", "gec açik": "Open late", "geç açık": "Open late",
  "geç acik": "Open late", "Geç açıklık": "Open late",
  "until late hours açık": "Open until late hours",
  // quick lunch
  "quick öğün": "Quick meal", "quick kahvaltı": "Quick breakfast",
  "özellikle öğle arası": "Especially good for lunch",
  "Tercih edilen": "Popular choice", kahvaltı: "Breakfast available",
  "sahur kahvaltısı": "Early morning breakfast available",
  // vegetarian
  vegan: "Vegan-friendly",
};

function normalizeScenario(val: string | undefined): string | null {
  if (!val || FALSY.has(val)) return null;
  return SCENARIO_MAP[val] ?? val;
}

function Stars({ rating }: { rating: number }) {
  const full = Math.floor(rating);
  const half = rating % 1 >= 0.3 && rating % 1 < 0.8;
  const empty = 5 - full - (half ? 1 : 0);
  return (
    <span className="text-amber-400 tracking-tight">
      {"★".repeat(full)}{half ? "½" : ""}<span className="text-gray-300">{"★".repeat(empty)}</span>
    </span>
  );
}

export default async function RestaurantPage({ params }: Props) {
  const { city, slug } = await params;
  const r = getRestaurantBySlug(city, slug);
  if (!r) notFound();

  const theme = CUISINE_PHOTOS[r.cuisineSlug?.toLowerCase().trim() ?? ""] ?? DEFAULT_PHOTO;
  const dishes = [
    ...(r.specialFeatures?.popularDishes ?? []),
    ...(r.specialFeatures?.signatureDishes ?? []),
  ].filter((v, i, a) => a.indexOf(v) === i);
  const avgCost = r.specialFeatures?.avgMealCost
    ? `~${r.specialFeatures.avgMealCost} TL`
    : r.priceDetail?.avgPerPerson ?? null;
  const hasTerrace = r.features?.terrace || r.features?.teras;
  const hasReservation = r.features?.reservation || r.features?.rezervasyon;

  const restaurantJsonLd = {
    "@context": "https://schema.org",
    "@type": "Restaurant",
    "@id": `https://www.restaurantsistanbul.com/${city}/${slug}`,
    name: r.name,
    description: r.llmSummary,
    servesCuisine: r.cuisine,
    priceRange: getPriceSymbol(r.priceRange),
    address: { "@type": "PostalAddress", streetAddress: r.address, addressLocality: r.neighborhood, addressRegion: r.city, addressCountry: "TR" },
    geo: { "@type": "GeoCoordinates", latitude: r.lat, longitude: r.lng },
    ...(r.avgRating != null ? { aggregateRating: { "@type": "AggregateRating", ratingValue: r.avgRating.toString(), reviewCount: (r.reviewCount ?? 0).toString(), bestRating: "5", worstRating: "1" } } : {}),
    openingHours: r.hoursEstimated ? undefined : r.openingHours,
    telephone: r.phone || undefined,
    url: r.website || `https://www.restaurantsistanbul.com/${city}/${slug}`,
    ...(r.reservationLinks?.googleMaps ? { sameAs: [r.reservationLinks.googleMaps], hasMap: r.reservationLinks.googleMaps } : {}),
    amenityFeature: [
      ...(r.features?.wifi ? [{ "@type": "LocationFeatureSpecification", name: "Wi-Fi", value: true }] : []),
      ...(hasTerrace ? [{ "@type": "LocationFeatureSpecification", name: "Terrace / Outdoor Seating", value: true }] : []),
      ...(hasReservation ? [{ "@type": "LocationFeatureSpecification", name: "Reservation Available", value: true }] : []),
      ...(r.features?.vegan ? [{ "@type": "LocationFeatureSpecification", name: "Vegan Options", value: true }] : []),
      ...(r.features?.seaView ? [{ "@type": "LocationFeatureSpecification", name: "Sea View", value: true }] : []),
      ...(r.features?.liveMusic ? [{ "@type": "LocationFeatureSpecification", name: "Live Music", value: true }] : []),
      ...(r.features?.parking ? [{ "@type": "LocationFeatureSpecification", name: "Parking", value: true }] : []),
    ],
    ...(r.nearby?.transit?.length ? {
      containsPlace: r.nearby.transit.map(t => ({
        "@type": "Place", name: t.name,
        additionalProperty: [
          { "@type": "PropertyValue", name: "transit_type", value: t.type },
          { "@type": "PropertyValue", name: "distance_m", value: t.distance_m.toString() },
          { "@type": "PropertyValue", name: "walk_minutes", value: t.walk_min.toString() },
        ],
      })),
    } : {}),
    additionalProperty: [
      { "@type": "PropertyValue", name: "llm_summary", value: r.llmSummary },
      { "@type": "PropertyValue", name: "sentiment_summary", value: r.sentimentSummary },
      ...(r.confidenceScore != null ? [{ "@type": "PropertyValue", name: "confidence_score", value: r.confidenceScore.toString() }] : []),
      { "@type": "PropertyValue", name: "last_updated", value: r.lastUpdated },
      { "@type": "PropertyValue", name: "tags", value: r.tags.join(", ") },
      ...(r.specialFeatures?.avgMealCost ? [{ "@type": "PropertyValue", name: "avg_meal_cost_try", value: r.specialFeatures.avgMealCost.toString() }] : []),
      ...(r.specialFeatures?.standoutPlus ? [{ "@type": "PropertyValue", name: "standout_plus", value: r.specialFeatures.standoutPlus }] : []),
      ...(r.specialFeatures?.criticalMinus ? [{ "@type": "PropertyValue", name: "critical_minus", value: r.specialFeatures.criticalMinus }] : []),
      ...(r.faq?.length ? [{ "@type": "PropertyValue", name: "faq", value: JSON.stringify(r.faq) }] : []),
    ],
  };

  const faqJsonLd = r.faq?.length ? {
    "@context": "https://schema.org", "@type": "FAQPage",
    mainEntity: r.faq.map(item => ({
      "@type": "Question", name: item.question,
      acceptedAnswer: { "@type": "Answer", text: item.answer },
    })),
  } : null;

  const breadcrumbJsonLd = {
    "@context": "https://schema.org", "@type": "BreadcrumbList",
    itemListElement: [
      { "@type": "ListItem", position: 1, name: "Istanbul Restaurants", item: "https://www.restaurantsistanbul.com" },
      { "@type": "ListItem", position: 2, name: r.city, item: `https://www.restaurantsistanbul.com/${city}` },
      { "@type": "ListItem", position: 3, name: r.name, item: `https://www.restaurantsistanbul.com/${city}/${slug}` },
    ],
  };

  return (
    <>
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(restaurantJsonLd) }} />
      {faqJsonLd && <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(faqJsonLd) }} />}
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbJsonLd) }} />

      {/* ── HERO ── */}
      <header className="relative flex flex-col justify-end overflow-hidden" style={{ minHeight: "400px" }}>
        <div className="absolute inset-0" style={{ backgroundImage: `url('${theme.photo}')`, backgroundSize: "cover", backgroundPosition: "center" }} />
        <div className="absolute inset-0" style={{ background: `linear-gradient(to top, ${theme.color}f5 0%, ${theme.color}bb 40%, ${theme.color}44 75%, transparent 100%)` }} />

        <div className="relative max-w-4xl mx-auto px-6 pt-24 pb-10 w-full">
          <nav className="text-xs text-white/50 mb-4 flex items-center gap-1.5">
            <Link href={`/${city}`} className="hover:text-white/80 transition-colors">{r.city}</Link>
            <span>/</span>
            <span className="text-white/80 truncate">{r.name}</span>
          </nav>

          <div className="flex items-end justify-between gap-4 flex-wrap">
            <div>
              <p className="text-white/60 text-sm font-medium mb-1">{r.neighborhood} · {r.cuisine}</p>
              <h1 className="text-4xl sm:text-5xl font-black text-white leading-tight drop-shadow-sm mb-3">
                {r.name}
              </h1>
              {r.avgRating != null && (
                <div className="flex items-center gap-2">
                  <Stars rating={r.avgRating} />
                  <span className="text-white font-black text-lg">{r.avgRating}</span>
                  <span className="text-white/50 text-sm">({r.reviewCount?.toLocaleString("en-US")} reviews)</span>
                </div>
              )}
            </div>
            <div className="flex flex-col items-end gap-2 shrink-0">
              {r.verifiedData && (
                <span className="text-xs bg-white/15 backdrop-blur-sm border border-white/25 text-white font-semibold px-3 py-1 rounded-full">
                  ✓ Verified Data
                </span>
              )}
              <span className="text-2xl font-black text-white">{getPriceSymbol(r.priceRange)}</span>
            </div>
          </div>
        </div>

        {/* Quick action strip */}
        <div className="relative border-t border-white/10 bg-black/40 backdrop-blur-md">
          <div className="max-w-4xl mx-auto px-6 py-3 flex flex-wrap items-center gap-4 sm:gap-8 text-sm">
            {r.openingHours && (
              <span className="text-white/70 flex items-center gap-1.5">
                <span className="text-white/40">🕐</span>
                <span>{r.openingHours}{r.hoursEstimated && <span className="text-white/40 ml-1 text-xs">(est.)</span>}</span>
              </span>
            )}
            {avgCost && (
              <span className="text-white/70 flex items-center gap-1.5">
                <span className="text-white/40">💰</span>
                {avgCost} <span className="text-white/40">avg/person</span>
              </span>
            )}
            {r.lat && r.lng && (
              <a
                href={`https://www.google.com/maps/search/?api=1&query=${r.lat},${r.lng}`}
                target="_blank"
                rel="noopener noreferrer"
                className="text-white font-semibold flex items-center gap-1.5 hover:text-white/80 transition-colors"
              >
                <span>📍</span> Google Maps →
              </a>
            )}
            {r.website && (
              <a href={r.website} target="_blank" rel="noopener noreferrer"
                className="text-white/70 hover:text-white transition-colors flex items-center gap-1">
                🌐 Website
              </a>
            )}
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-6 py-12 space-y-12">

        {/* ── AI SUMMARY ── */}
        <section>
          <h2 className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-3">AI Summary</h2>
          <p className="text-gray-800 text-base leading-relaxed">{r.llmSummary}</p>
        </section>

        {/* ── POPULAR DISHES ── */}
        {dishes.length > 0 && (
          <section>
            <h2 className="text-xl font-black text-gray-900 mb-4">Popular Dishes</h2>
            <div className="flex flex-wrap gap-2">
              {dishes.map(d => (
                <span key={d} className="text-sm bg-amber-50 border border-amber-200 text-amber-800 px-4 py-2 rounded-full font-semibold">
                  {d}
                </span>
              ))}
            </div>
          </section>
        )}

        {/* ── REVIEW ANALYSIS ── */}
        {(r.sentimentSummary || r.specialFeatures?.standoutPlus || r.specialFeatures?.criticalMinus) && (
          <section>
            <h2 className="text-xl font-black text-gray-900 mb-4">Review Analysis</h2>
            <div className="space-y-3">
              {r.sentimentSummary && (
                <div className="p-4 bg-gray-50 border border-gray-200 rounded-2xl">
                  <p className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">Sentiment</p>
                  <p className="text-gray-700 leading-relaxed">{r.sentimentSummary}</p>
                </div>
              )}
              {r.specialFeatures?.standoutPlus && (
                <div className="flex items-start gap-3 p-4 bg-green-50 border border-green-200 rounded-2xl">
                  <span className="text-green-600 font-black text-lg shrink-0">✦</span>
                  <p className="text-green-800 font-medium leading-relaxed">{r.specialFeatures.standoutPlus}</p>
                </div>
              )}
              {r.specialFeatures?.criticalMinus && (
                <div className="flex items-start gap-3 p-4 bg-red-50 border border-red-200 rounded-2xl">
                  <span className="text-red-500 font-black text-lg shrink-0">✗</span>
                  <p className="text-red-800 leading-relaxed">{r.specialFeatures.criticalMinus}</p>
                </div>
              )}
            </div>
          </section>
        )}

        {/* ── CONTEXTUAL RATINGS ── */}
        {r.specialFeatures?.contextualRatings && Object.values(r.specialFeatures.contextualRatings).some(Boolean) && (
          <section>
            <h2 className="text-xl font-black text-gray-900 mb-4">Rated By Occasion</h2>
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
              {([
                { key: "businessLunch",  label: "Business Lunch", icon: "💼" },
                { key: "romanticDate",   label: "Romantic Date",  icon: "🌹" },
                { key: "familyDining",  label: "Family Dining",  icon: "👨‍👩‍👧" },
                { key: "soloVisit",      label: "Solo Visit",     icon: "👤" },
                { key: "groupDining",    label: "Group Dining",   icon: "👥" },
              ] as const).map(({ key, label, icon }) => {
                const val = r.specialFeatures?.contextualRatings?.[key];
                if (!val) return null;
                return (
                  <div key={key} className="bg-gray-50 border border-gray-200 rounded-2xl p-4 text-center">
                    <div className="text-2xl mb-1">{icon}</div>
                    <div className="text-2xl font-black text-gray-900">{val}<span className="text-sm text-gray-400">/5</span></div>
                    <div className="text-xs text-gray-500 mt-1 font-medium">{label}</div>
                  </div>
                );
              })}
            </div>
          </section>
        )}

        {/* ── GETTING HERE ── */}
        {r.nearby?.transit && r.nearby.transit.length > 0 && (
          <section>
            <h2 className="text-xl font-black text-gray-900 mb-4">Getting Here</h2>
            <div className="grid sm:grid-cols-2 gap-3 mb-4">
              {r.nearby.transit.map((t, i) => (
                <div key={i} className="flex items-center gap-3 p-4 bg-blue-50 border border-blue-100 rounded-2xl">
                  <span className="text-2xl shrink-0">{TRANSIT_ICONS[t.type] ?? "🚏"}</span>
                  <div>
                    <div className="font-bold text-gray-900 text-sm">{t.name}</div>
                    <div className="text-xs text-gray-500 mt-0.5 capitalize">{t.type} · {t.walk_min} min walk · {t.distance_m}m</div>
                  </div>
                </div>
              ))}
            </div>
            {r.nearby.landmarks && r.nearby.landmarks.length > 0 && (
              <div className="p-4 bg-gray-50 border border-gray-100 rounded-2xl">
                <p className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-3">Nearby Landmarks</p>
                <div className="space-y-1.5">
                  {r.nearby.landmarks.slice(0, 5).map((l, i) => (
                    <div key={i} className="flex items-center justify-between text-sm">
                      <span className="text-gray-700 font-medium">{l.name}</span>
                      <span className="text-gray-400">{l.walk_min} min walk</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </section>
        )}

        {/* ── MENU & PRICES ── */}
        {(r.priceDetail || r.menuItems?.length) && (
          <section>
            <h2 className="text-xl font-black text-gray-900 mb-4">Menu & Prices</h2>
            {r.priceDetail && (
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-4">
                {[
                  { label: "Starter",     val: r.priceDetail.starterRange },
                  { label: "Main Course", val: r.priceDetail.mainCourseRange },
                  { label: "Dessert",     val: r.priceDetail.dessertRange },
                  { label: "Drinks",      val: r.priceDetail.drinkRange },
                ].filter(x => x.val).map(({ label, val }) => (
                  <div key={label} className="bg-gray-50 border border-gray-200 rounded-2xl p-4">
                    <p className="text-xs text-gray-400 font-bold uppercase tracking-wide mb-1">{label}</p>
                    <p className="font-bold text-gray-900">{val}</p>
                  </div>
                ))}
              </div>
            )}
            {r.menuItems?.length ? (
              <div className="flex flex-wrap gap-2">
                {r.menuItems.map((item, i) => (
                  <span key={i} className="text-sm bg-orange-50 text-orange-800 border border-orange-100 px-3 py-1.5 rounded-full font-medium">{item}</span>
                ))}
              </div>
            ) : null}
          </section>
        )}

        {/* ── FEATURES ── */}
        {(r.features && Object.values(r.features).some(Boolean)) && (
          <section>
            <h2 className="text-xl font-black text-gray-900 mb-4">Features & Amenities</h2>
            <div className="flex flex-wrap gap-2">
              {([
                { key: "terrace",     label: "🌿 Terrace" },
                { key: "teras",       label: "🌿 Terrace" },
                { key: "seaView",     label: "🌊 Sea View" },
                { key: "wifi",        label: "📶 Wi-Fi" },
                { key: "reservation", label: "📅 Reservations" },
                { key: "rezervasyon", label: "📅 Reservations" },
                { key: "parking",     label: "🅿️ Parking" },
                { key: "liveMusic",   label: "🎵 Live Music" },
                { key: "romantic",    label: "🌹 Romantic Setting" },
                { key: "vegan",       label: "🥗 Vegan Options" },
              ] as const).filter(({ key }) => r.features?.[key]).map(({ key, label }) => (
                <span key={key} className="text-sm bg-white border border-gray-200 text-gray-700 font-medium px-4 py-2 rounded-full">
                  {label}
                </span>
              ))}
              {r.specialFeatures?.noiseLevel && (
                <span className="text-sm bg-white border border-gray-200 text-gray-700 font-medium px-4 py-2 rounded-full capitalize">
                  🔊 Noise: {r.specialFeatures.noiseLevel}
                </span>
              )}
              {r.specialFeatures?.laptopFriendly && (
                <span className="text-sm bg-white border border-gray-200 text-gray-700 font-medium px-4 py-2 rounded-full">
                  💻 Laptop Friendly
                </span>
              )}
            </div>
          </section>
        )}

        {/* ── BEST FOR ── */}
        {r.scenarioSummary && Object.keys(r.scenarioSummary).length > 0 && (
          <section>
            <h2 className="text-xl font-black text-gray-900 mb-4">Best For</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {([
                { key: "birthday",   label: "🎂 Birthday" },
                { key: "budget",     label: "💰 Budget" },
                { key: "vegetarian", label: "🥗 Vegetarian" },
                { key: "quickLunch", label: "⚡ Quick Lunch" },
                { key: "tourist",    label: "🗺️ Tourists" },
                { key: "romantic",   label: "❤️ Romantic" },
                { key: "family",     label: "👨‍👩‍👧 Family" },
                { key: "lateNight",  label: "🌙 Late Night" },
              ] as const).map(({ key, label }) => {
                const raw = r.scenarioSummary?.[key as keyof typeof r.scenarioSummary];
                const val = normalizeScenario(raw);
                return val ? (
                  <div key={key} className="flex gap-3 p-4 bg-gray-50 border border-gray-200 rounded-2xl text-sm">
                    <span className="font-bold text-gray-600 shrink-0">{label}</span>
                    <span className="text-gray-700 leading-relaxed">{val}</span>
                  </div>
                ) : null;
              })}
            </div>
          </section>
        )}

        {/* ── FAQ ── */}
        {r.faq?.length ? (
          <section>
            <h2 className="text-xl font-black text-gray-900 mb-4">Frequently Asked Questions</h2>
            <div className="space-y-3">
              {r.faq.map((item, i) => (
                <div key={i} className="border border-gray-200 rounded-2xl overflow-hidden">
                  <div className="px-5 py-4 bg-gray-50 border-b border-gray-100 flex items-start gap-3">
                    <span className="text-xs font-black text-gray-400 shrink-0 mt-0.5 w-5 text-center">{i + 1}</span>
                    <p className="font-bold text-gray-900 text-sm leading-snug">{item.question}</p>
                  </div>
                  <div className="px-5 py-4 flex items-start gap-3">
                    <span className="w-5 shrink-0" />
                    <p className="text-gray-700 text-sm leading-relaxed">{item.answer}</p>
                  </div>
                </div>
              ))}
            </div>
          </section>
        ) : null}

        {/* ── RESERVATION & LINKS ── */}
        {(r.reservationLinks || r.lat) && (
          <section>
            <h2 className="text-xl font-black text-gray-900 mb-4">Reservation & Directions</h2>
            <div className="flex flex-wrap gap-3">
              {r.reservationLinks?.googleMaps && (
                <a href={r.reservationLinks.googleMaps} target="_blank" rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 px-6 py-3 bg-gray-900 hover:bg-gray-700 text-white font-semibold text-sm rounded-2xl transition-colors">
                  📍 View on Google Maps
                </a>
              )}
              {r.reservationLinks?.website && (
                <a href={r.reservationLinks.website} target="_blank" rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 px-6 py-3 border border-gray-300 text-gray-700 font-semibold text-sm rounded-2xl hover:bg-gray-50 transition-colors">
                  🌐 Official Website
                </a>
              )}
            </div>
            {r.address && (
              <p className="text-sm text-gray-500 mt-3 flex items-center gap-1.5">
                <span className="text-gray-400">📌</span> {r.address}
              </p>
            )}
          </section>
        )}

        {/* ── TAGS ── */}
        {r.tags.length > 0 && (
          <section className="pt-6 border-t border-gray-100">
            <p className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-3">Tags</p>
            <div className="flex flex-wrap gap-2">
              {r.tags.map(tag => (
                <span key={tag} className="text-xs bg-gray-100 text-gray-600 px-3 py-1.5 rounded-full font-medium">
                  {tag}
                </span>
              ))}
            </div>
          </section>
        )}

        {/* ── DATA TRUST ── */}
        <section className="pt-6 border-t border-gray-100">
          <p className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-3">Data Quality</p>
          <div className="flex flex-wrap gap-x-6 gap-y-1.5 text-xs text-gray-500">
            <span>Confidence: <strong className="text-gray-700">{(r.confidenceScore * 100).toFixed(0)}%</strong></span>
            <span>Last updated: <strong className="text-gray-700">{r.lastUpdated}</strong></span>
            <span>Verified: <strong className="text-gray-700">{r.verifiedData ? "Yes" : "No"}</strong></span>
            {r.dataFreshness?.source && <span>Source: <strong className="text-gray-700">{r.dataFreshness.source}</strong></span>}
            <a href={`/api/restaurants/${r.id}`} className="text-blue-500 hover:underline">JSON →</a>
          </div>
        </section>

      </main>
    </>
  );
}
