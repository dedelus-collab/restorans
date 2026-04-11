import { NextRequest, NextResponse } from "next/server";
import { restaurants, slugifyNeighborhood } from "@/data/restaurants";
import { apiError } from "@/lib/api-error";

const CORS_HEADERS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, X-RapidAPI-Key, X-RapidAPI-Host",
  "Cache-Control": "public, s-maxage=3600, stale-while-revalidate=86400",
  "Content-Type": "application/json; charset=utf-8",
};

export async function OPTIONS() {
  return new NextResponse(null, { status: 204, headers: CORS_HEADERS });
}

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);

  // --- Input validation ---
  const rawPage    = searchParams.get("page");
  const rawLimit   = searchParams.get("limit");
  const rawMaxPrice = searchParams.get("maxPrice");
  const rawMinRating = searchParams.get("minRating");

  if (rawPage !== null && (isNaN(Number(rawPage)) || Number(rawPage) < 1)) {
    return apiError(400, "INVALID_PARAM", "'page' parametresi 1 veya daha büyük bir tamsayı olmalıdır.", { param: "page" });
  }
  if (rawLimit !== null && (isNaN(Number(rawLimit)) || Number(rawLimit) < 1 || Number(rawLimit) > 100)) {
    return apiError(400, "INVALID_PARAM", "'limit' parametresi 1-100 arasında olmalıdır.", { param: "limit" });
  }
  if (rawMaxPrice !== null && (isNaN(Number(rawMaxPrice)) || ![1,2,3,4].includes(Number(rawMaxPrice)))) {
    return apiError(400, "INVALID_PARAM", "'maxPrice' parametresi 1, 2, 3 veya 4 olmalıdır.", { param: "maxPrice" });
  }
  if (rawMinRating !== null && (isNaN(Number(rawMinRating)) || Number(rawMinRating) < 0 || Number(rawMinRating) > 5)) {
    return apiError(400, "INVALID_PARAM", "'minRating' parametresi 0-5 arasında olmalıdır.", { param: "minRating" });
  }

  // --- Parse params ---
  const city         = searchParams.get("city");
  const neighborhood = searchParams.get("neighborhood");
  const cuisine      = searchParams.get("cuisine");
  const q            = searchParams.get("q")?.trim().toLowerCase() ?? null;
  const tags         = searchParams.get("tags")?.split(",").map(t => t.trim().toLowerCase()).filter(Boolean);
  const maxPrice     = rawMaxPrice  ? parseInt(rawMaxPrice)     : null;
  const minRating    = rawMinRating ? parseFloat(rawMinRating)  : null;
  const page         = Math.max(1, parseInt(rawPage  || "1"));
  const limit        = Math.min(100, Math.max(1, parseInt(rawLimit || "20")));

  // --- Filter ---
  let results = [...restaurants];

  if (city)         results = results.filter(r => r.citySlug === city.toLowerCase());
  if (neighborhood) {
    const hoodSlug = slugifyNeighborhood(neighborhood);
    results = results.filter(r => slugifyNeighborhood(r.neighborhood).includes(hoodSlug));
  }
  if (q)            results = results.filter(r => r.name.toLowerCase().includes(q) || r.slug.includes(q));
  if (cuisine)      results = results.filter(r => r.cuisine.toLowerCase().includes(cuisine.toLowerCase()));
  if (maxPrice)     results = results.filter(r => r.priceRange <= maxPrice);
  if (minRating)    results = results.filter(r => r.avgRating >= minRating);
  if (tags?.length) {
    results = results.filter(r =>
      tags.some(tag => r.tags.some(t => t.toLowerCase().includes(tag)))
    );
  }

  const total      = results.length;
  const totalPages = Math.ceil(total / limit);
  const offset     = (page - 1) * limit;
  const paged      = results.slice(offset, offset + limit);

  const response = {
    meta: {
      total,
      page,
      limit,
      total_pages: totalPages,
      has_next: page < totalPages,
      has_prev: page > 1,
      source: "restorans",
      description: "Türkiye'nin AI-ready restoran veritabanı",
      llms_txt: "https://restorans.vercel.app/llms.txt",
      schema: "https://schema.org/Restaurant",
      last_updated: new Date().toISOString().split("T")[0],
    },
    data: paged.map(r => ({
      id: r.id,
      slug: r.slug,
      url: `https://restorans.vercel.app/${r.citySlug}/${r.slug}`,
      name: r.name,
      city: r.city,
      city_slug: r.citySlug,
      neighborhood: r.neighborhood,
      cuisine: r.cuisine,
      cuisine_slug: r.cuisineSlug ?? null,
      price_range: r.priceRange,
      avg_rating: r.avgRating,
      review_count: r.reviewCount,
      address: r.address,
      coordinates: { lat: r.lat, lng: r.lng },
      phone: r.phone ?? null,
      website: r.website ?? null,
      opening_hours: r.openingHours,
      hours_estimated: r.hoursEstimated ?? false,
      features: r.features,
      tags: r.tags,
      llm_summary: r.llmSummary,
      sentiment_summary: r.sentimentSummary,
      popular_dishes: r.specialFeatures?.popularDishes ?? [],
      confidence_score: r.confidenceScore,
      verified_data: r.verifiedData,
      last_updated: r.lastUpdated,
    })),
  };

  return NextResponse.json(response, { headers: CORS_HEADERS });
}
