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
    title: `${r.name} — ${r.neighborhood}, ${r.city} | restorans`,
    description: r.llmSummary,
    alternates: { canonical: `https://restorans.io/${city}/${slug}` },
    openGraph: {
      type: "website",
      url: `https://restorans.io/${city}/${slug}`,
      title: `${r.name} — ${r.neighborhood}, ${r.city}`,
      description: r.llmSummary ?? undefined,
      siteName: "restorans",
      locale: "tr_TR",
    },
    twitter: {
      card: "summary_large_image",
      title: `${r.name} — ${r.neighborhood}, ${r.city}`,
      description: r.llmSummary ?? undefined,
    },
  };
}

export default async function RestaurantPage({ params }: Props) {
  const { city, slug } = await params;
  const r = getRestaurantBySlug(city, slug);
  if (!r) notFound();

  const restaurantJsonLd = {
    "@context": "https://schema.org",
    "@type": "Restaurant",
    "@id": `https://restorans.io/${city}/${slug}`,
    name: r.name,
    description: r.llmSummary,
    servesCuisine: r.cuisine,
    priceRange: getPriceSymbol(r.priceRange),
    address: {
      "@type": "PostalAddress",
      streetAddress: r.address,
      addressLocality: r.neighborhood,
      addressRegion: r.city,
      addressCountry: "TR",
    },
    geo: {
      "@type": "GeoCoordinates",
      latitude: r.lat,
      longitude: r.lng,
    },
    aggregateRating: {
      "@type": "AggregateRating",
      ratingValue: r.avgRating.toString(),
      reviewCount: r.reviewCount.toString(),
      bestRating: "5",
      worstRating: "1",
    },
    openingHours: r.hoursEstimated ? undefined : r.openingHours,
    telephone: r.phone || undefined,
    url: r.website || `https://restorans.io/${city}/${slug}`,
    ...(r.reservationLinks?.googleMaps ? {
      sameAs: [r.reservationLinks.googleMaps],
      hasMap: r.reservationLinks.googleMaps,
    } : {}),
    ...(r.photoUrl ? { image: r.photoUrl } : {}),
    // AI-specific extensions
    additionalProperty: [
      {
        "@type": "PropertyValue",
        name: "llm_summary",
        value: r.llmSummary,
      },
      {
        "@type": "PropertyValue",
        name: "sentiment_summary",
        value: r.sentimentSummary,
      },
      {
        "@type": "PropertyValue",
        name: "confidence_score",
        value: r.confidenceScore.toString(),
      },
      {
        "@type": "PropertyValue",
        name: "last_updated",
        value: r.lastUpdated,
      },
      {
        "@type": "PropertyValue",
        name: "verified_data",
        value: r.verifiedData.toString(),
      },
      {
        "@type": "PropertyValue",
        name: "tags",
        value: r.tags.join(", "),
      },
      ...(r.highlights ? [{
        "@type": "PropertyValue",
        name: "highlights",
        value: r.highlights.join(", "),
      }] : []),
      ...(r.specialFeatures?.signatureDish ? [{
        "@type": "PropertyValue",
        name: "signature_dish",
        value: r.specialFeatures.signatureDish,
      }] : []),
      ...(r.specialFeatures?.dietaryOptions?.length ? [{
        "@type": "PropertyValue",
        name: "dietary_options",
        value: r.specialFeatures.dietaryOptions.join(", "),
      }] : []),
      ...(r.specialFeatures?.noiseLevel ? [{
        "@type": "PropertyValue",
        name: "noise_level",
        value: r.specialFeatures.noiseLevel,
      }] : []),
      ...(r.specialFeatures?.avgMealCost ? [{
        "@type": "PropertyValue",
        name: "avg_meal_cost_try",
        value: r.specialFeatures.avgMealCost.toString(),
      }] : []),
      ...(r.specialFeatures?.criticalMinus ? [{
        "@type": "PropertyValue",
        name: "critical_minus",
        value: r.specialFeatures.criticalMinus,
      }] : []),
      ...(r.specialFeatures?.standoutPlus ? [{
        "@type": "PropertyValue",
        name: "standout_plus",
        value: r.specialFeatures.standoutPlus,
      }] : []),
      ...(r.specialFeatures?.contextualRatings ? [{
        "@type": "PropertyValue",
        name: "contextual_ratings",
        value: JSON.stringify(r.specialFeatures.contextualRatings),
      }] : []),
      ...(r.scenarioSummary ? [{
        "@type": "PropertyValue",
        name: "scenario_summary",
        value: JSON.stringify(r.scenarioSummary),
      }] : []),
      ...(r.faq?.length ? [{
        "@type": "PropertyValue",
        name: "faq",
        value: JSON.stringify(r.faq),
      }] : []),
      ...(r.dataFreshness ? [{
        "@type": "PropertyValue",
        name: "data_freshness",
        value: JSON.stringify(r.dataFreshness),
      }] : []),
    ],
  };

  const faqJsonLd = r.faq?.length ? {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    mainEntity: r.faq.map(item => ({
      "@type": "Question",
      name: item.question,
      acceptedAnswer: {
        "@type": "Answer",
        text: item.answer,
      },
    })),
  } : null;

  const breadcrumbJsonLd = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: [
      { "@type": "ListItem", position: 1, name: "restorans", item: "https://restorans.io" },
      { "@type": "ListItem", position: 2, name: r.city, item: `https://restorans.io/${city}` },
      { "@type": "ListItem", position: 3, name: r.name, item: `https://restorans.io/${city}/${slug}` },
    ],
  };

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(restaurantJsonLd) }}
      />
      {faqJsonLd && (
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(faqJsonLd) }}
        />
      )}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbJsonLd) }}
      />

      <main className="max-w-3xl mx-auto px-6 py-16">
        {/* Breadcrumb */}
        <nav className="text-sm text-gray-500 mb-8">
          <Link href="/" className="hover:underline">restorans</Link>
          {" / "}
          <Link href={`/${city}`} className="hover:underline">{r.city}</Link>
          {" / "}
          <span>{r.name}</span>
        </nav>

        {/* Başlık */}
        <header className="mb-10">
          <div className="flex items-start justify-between gap-4 mb-3">
            <h1 className="text-3xl font-bold">{r.name}</h1>
            {r.verifiedData && (
              <span className="text-sm bg-green-50 text-green-700 px-3 py-1 rounded shrink-0">
                Doğrulanmış Veri
              </span>
            )}
          </div>
          <p className="text-gray-500">
            {r.neighborhood}, {r.city} · {r.cuisine} · {getPriceSymbol(r.priceRange)}
          </p>
          {r.lat && r.lng && (
            <a
              href={`https://www.google.com/maps/search/?api=1&query=${r.lat},${r.lng}`}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-block mt-3 text-sm text-blue-600 hover:underline"
            >
              Google Maps&apos;te Gör
            </a>
          )}
        </header>

        {/* LLM Summary — AI için en önemli alan */}
        <section className="mb-10 p-6 bg-gray-50 rounded-lg border border-gray-200">
          <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-3">
            AI Özeti (llm_summary)
          </h2>
          <p className="text-gray-800 leading-relaxed">{r.llmSummary}</p>
        </section>

        {/* Temel Veriler */}
        <section className="mb-10">
          <h2 className="text-lg font-semibold mb-4">Temel Bilgiler</h2>
          <dl className="grid grid-cols-2 gap-y-4 gap-x-8 text-sm">
            <div>
              <dt className="text-gray-500">Puan</dt>
              <dd className="font-semibold mt-0.5">{r.avgRating} / 5 ({r.reviewCount} yorum)</dd>
            </div>
            <div>
              <dt className="text-gray-500">Fiyat Aralığı</dt>
              <dd className="font-semibold mt-0.5">{getPriceSymbol(r.priceRange)}</dd>
            </div>
            <div>
              <dt className="text-gray-500">Mutfak</dt>
              <dd className="font-semibold mt-0.5">{r.cuisine}</dd>
            </div>
            <div>
              <dt className="text-gray-500">Mahalle</dt>
              <dd className="font-semibold mt-0.5">{r.neighborhood}</dd>
            </div>
            <div>
              <dt className="text-gray-500">Çalışma Saatleri</dt>
              <dd className="font-semibold mt-0.5">
                {r.openingHours}
                {r.hoursEstimated && (
                  <span className="ml-2 text-xs font-normal text-amber-600">(tahmini)</span>
                )}
              </dd>
            </div>
            {r.phone && (
              <div>
                <dt className="text-gray-500">Telefon</dt>
                <dd className="font-semibold mt-0.5">{r.phone}</dd>
              </div>
            )}
            <div>
              <dt className="text-gray-500">Adres</dt>
              <dd className="font-semibold mt-0.5">{r.address}</dd>
            </div>
            {r.website && (
              <div>
                <dt className="text-gray-500">Web Sitesi</dt>
                <dd className="font-semibold mt-0.5">
                  <a href={r.website} className="text-blue-600 hover:underline" target="_blank" rel="noopener noreferrer">
                    {r.website.replace("https://", "")}
                  </a>
                </dd>
              </div>
            )}
          </dl>
        </section>

        {/* Bağlamsal Puanlar */}
        {r.specialFeatures?.contextualRatings && (
          <section className="mb-10">
            <h2 className="text-lg font-semibold mb-4">Bağlamsal Puanlar</h2>
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
              {Object.entries(r.specialFeatures.contextualRatings).map(([key, val]) => {
                const labels: Record<string, string> = {
                  businessLunch: "İş Yemeği",
                  romanticDate: "Romantik Buluşma",
                  familyDining: "Aile Yemeği",
                  soloVisit: "Yalnız Ziyaret",
                  groupDining: "Grup Yemeği",
                };
                return val ? (
                  <div key={key} className="p-3 bg-gray-50 rounded-lg text-center">
                    <div className="text-lg font-bold">{val}/5</div>
                    <div className="text-xs text-gray-500 mt-0.5">{labels[key] || key}</div>
                  </div>
                ) : null;
              })}
            </div>
          </section>
        )}

        {/* İmza Yemekler */}
        {r.specialFeatures?.signatureDishes?.length ? (
          <section className="mb-10">
            <h2 className="text-lg font-semibold mb-3">İmza Yemekler</h2>
            <div className="flex flex-wrap gap-2">
              {r.specialFeatures.signatureDishes.map(dish => (
                <span key={dish} className="text-sm bg-orange-50 border border-orange-200 text-orange-800 px-3 py-1.5 rounded">
                  {dish}
                </span>
              ))}
            </div>
          </section>
        ) : null}

        {/* Yorum Analizi */}
        <section className="mb-10">
          <h2 className="text-lg font-semibold mb-3">Yorum Analizi</h2>
          <p className="text-gray-700 leading-relaxed text-sm bg-blue-50 p-4 rounded-lg border border-blue-100 mb-3">
            {r.sentimentSummary}
          </p>
          {r.specialFeatures?.standoutPlus && (
            <p className="text-sm text-green-700 bg-green-50 px-4 py-2 rounded border border-green-100">
              ✓ {r.specialFeatures.standoutPlus}
            </p>
          )}
          {r.specialFeatures?.criticalMinus && (
            <p className="text-sm text-red-700 bg-red-50 px-4 py-2 rounded border border-red-100 mt-2">
              ✗ {r.specialFeatures.criticalMinus}
            </p>
          )}
        </section>

        {/* Highlights */}
        {r.highlights?.length ? (
          <section className="mb-10">
            <h2 className="text-lg font-semibold mb-3">Öne Çıkanlar</h2>
            <ul className="space-y-1">
              {r.highlights.map(h => (
                <li key={h} className="text-sm text-gray-700 flex items-start gap-2">
                  <span className="text-gray-400 mt-0.5">—</span> {h}
                </li>
              ))}
            </ul>
          </section>
        ) : null}

        {/* Özellikler */}
        <section className="mb-10">
          <h2 className="text-lg font-semibold mb-4">Özellikler</h2>
          <div className="flex flex-wrap gap-2">
            {Object.entries(r.features).filter(([, v]) => v).map(([key]) => {
              const labels: Record<string, string> = {
                terrace: "Teras", teras: "Teras", parking: "Otopark", wifi: "Wi-Fi",
                reservation: "Rezervasyon", rezervasyon: "Rezervasyon", romantic: "Romantik",
                seaView: "Deniz Manzarası", liveMusic: "Canlı Müzik", vegan: "Vegan Seçenek",
                laptopFriendly: "Laptop Dostu", outdoorHeating: "Dış Mekan Isıtması",
              };
              return (
                <span key={key} className="text-sm bg-white border border-gray-200 text-gray-700 px-3 py-1.5 rounded">
                  {labels[key] || key}
                </span>
              );
            })}
            {r.specialFeatures?.laptopFriendly && (
              <span className="text-sm bg-white border border-gray-200 text-gray-700 px-3 py-1.5 rounded">Laptop Dostu</span>
            )}
            {r.specialFeatures?.noiseLevel && (
              <span className="text-sm bg-white border border-gray-200 text-gray-700 px-3 py-1.5 rounded">
                Gürültü: {r.specialFeatures.noiseLevel}
              </span>
            )}
          </div>
        </section>

        {/* Diyet Seçenekleri */}
        {r.specialFeatures?.dietaryOptions?.length ? (
          <section className="mb-10">
            <h2 className="text-lg font-semibold mb-3">Diyet Seçenekleri</h2>
            <div className="flex flex-wrap gap-2">
              {r.specialFeatures.dietaryOptions.map(opt => (
                <span key={opt} className="text-sm bg-green-50 border border-green-200 text-green-700 px-3 py-1.5 rounded">
                  {opt}
                </span>
              ))}
            </div>
          </section>
        ) : null}

        {/* Menü & Fiyat */}
        {(r.menuItems?.length || r.priceDetail) && (
          <section className="mb-10">
            <h2 className="text-lg font-semibold mb-4">Menü & Fiyatlar</h2>
            {r.priceDetail && (
              <div className="grid grid-cols-2 gap-2 mb-4 sm:grid-cols-4">
                {r.priceDetail.starterRange && (
                  <div className="bg-gray-50 rounded-lg p-3 text-sm">
                    <p className="text-gray-500 text-xs mb-1">Başlangıç</p>
                    <p className="font-medium">{r.priceDetail.starterRange}</p>
                  </div>
                )}
                {r.priceDetail.mainCourseRange && (
                  <div className="bg-gray-50 rounded-lg p-3 text-sm">
                    <p className="text-gray-500 text-xs mb-1">Ana Yemek</p>
                    <p className="font-medium">{r.priceDetail.mainCourseRange}</p>
                  </div>
                )}
                {r.priceDetail.dessertRange && (
                  <div className="bg-gray-50 rounded-lg p-3 text-sm">
                    <p className="text-gray-500 text-xs mb-1">Tatlı</p>
                    <p className="font-medium">{r.priceDetail.dessertRange}</p>
                  </div>
                )}
                {r.priceDetail.drinkRange && (
                  <div className="bg-gray-50 rounded-lg p-3 text-sm">
                    <p className="text-gray-500 text-xs mb-1">İçecek</p>
                    <p className="font-medium">{r.priceDetail.drinkRange}</p>
                  </div>
                )}
              </div>
            )}
            {r.menuItems?.length ? (
              <div className="flex flex-wrap gap-2">
                {r.menuItems.map((item, i) => (
                  <span key={i} className="text-sm bg-orange-50 text-orange-700 px-3 py-1 rounded-full border border-orange-100">
                    {item}
                  </span>
                ))}
              </div>
            ) : null}
          </section>
        )}

        {/* Rezervasyon */}
        {r.reservationLinks && (
          <section className="mb-10">
            <h2 className="text-lg font-semibold mb-3">Rezervasyon & Yol Tarifi</h2>
            <div className="flex flex-wrap gap-3">
              {r.reservationLinks.googleMaps && (
                <a href={r.reservationLinks.googleMaps} target="_blank" rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700">
                  Google Maps&apos;te Gör
                </a>
              )}
              {r.reservationLinks.website && (
                <a href={r.reservationLinks.website} target="_blank" rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 px-4 py-2 border border-gray-300 text-gray-700 text-sm rounded-lg hover:bg-gray-50">
                  Resmi Web Sitesi
                </a>
              )}
            </div>
          </section>
        )}

        {/* Senaryo Önerileri */}
        {r.scenarioSummary && Object.keys(r.scenarioSummary).length > 0 && (
          <section className="mb-10">
            <h2 className="text-lg font-semibold mb-4">Kim İçin Uygun?</h2>
            <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
              {[
                { key: "birthday", label: "🎂 Doğum Günü" },
                { key: "budget", label: "💰 Bütçe Dostu" },
                { key: "vegetarian", label: "🥗 Vejetaryen" },
                { key: "quickLunch", label: "⚡ Hızlı Öğle" },
                { key: "tourist", label: "🗺️ Turistler" },
                { key: "romantic", label: "❤️ Romantik" },
                { key: "family", label: "👨‍👩‍👧 Aile" },
                { key: "lateNight", label: "🌙 Gece Geç" },
              ].map(({ key, label }) => {
                const val = r.scenarioSummary?.[key as keyof typeof r.scenarioSummary];
                return val ? (
                  <div key={key} className="flex gap-3 p-3 bg-gray-50 rounded-lg text-sm">
                    <span className="shrink-0 font-medium text-gray-600 w-32">{label}</span>
                    <span className="text-gray-700">{val}</span>
                  </div>
                ) : null;
              })}
            </div>
          </section>
        )}

        {/* FAQ */}
        {r.faq?.length ? (
          <section className="mb-10">
            <h2 className="text-lg font-semibold mb-4">Sık Sorulan Sorular</h2>
            <div className="space-y-3">
              {r.faq.map((item, i) => (
                <div key={i} className="border border-gray-100 rounded-lg p-4">
                  <p className="font-medium text-gray-800 text-sm mb-1">{item.question}</p>
                  <p className="text-gray-600 text-sm">{item.answer}</p>
                </div>
              ))}
            </div>
          </section>
        ) : null}

        {/* Etiketler */}
        <section className="mb-10">
          <h2 className="text-lg font-semibold mb-3">Etiketler</h2>
          <div className="flex flex-wrap gap-2">
            {r.tags.map(tag => (
              <span key={tag} className="text-sm bg-gray-100 text-gray-600 px-3 py-1 rounded">
                {tag}
              </span>
            ))}
          </div>
        </section>

        {/* AI Güven Sinyalleri */}
        <section className="mt-12 pt-8 border-t border-gray-100 text-xs text-gray-400 space-y-1">
          <p>Güven Skoru: <strong>{(r.confidenceScore * 100).toFixed(0)}%</strong></p>
          <p>Son Güncelleme: <strong>{r.lastUpdated}</strong></p>
          <p>Doğrulanmış: <strong>{r.verifiedData ? "Evet" : "Hayır"}</strong></p>
          {r.dataFreshness && (
            <>
              <p>Veri Kaynağı: <strong>{r.dataFreshness.source}</strong></p>
              <p>Veri Güvenilirliği: <strong>{r.dataFreshness.confidence}</strong></p>
              <p>Son Doğrulama: <strong>{r.dataFreshness.lastVerified}</strong></p>
            </>
          )}
          {r.specialFeatures?.avgMealCost && (
            <p>Ortalama Yemek Maliyeti: <strong>~{r.specialFeatures.avgMealCost} TL</strong></p>
          )}
          <p>
            Makine-okunabilir:{" "}
            <a href={`/api/restaurants/${r.id}`} className="text-blue-500 hover:underline">JSON</a>
          </p>
        </section>
      </main>
    </>
  );
}
