import { NextRequest, NextResponse } from "next/server";
import { restaurants } from "@/data/restaurants";
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

export async function GET(
  _request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;

  if (!id || id.trim() === "") {
    return apiError(400, "INVALID_PARAM", "A valid 'id' or 'slug' must be provided.", { param: "id" });
  }

  const r = restaurants.find(r => r.id === id || r.slug === id);

  if (!r) {
    return apiError(404, "NOT_FOUND", `No restaurant found matching '${id}'.`);
  }

  return NextResponse.json({
    meta: {
      source: "restorans",
      schema: "https://schema.org/Restaurant",
      last_updated: r.lastUpdated,
    },
    data: {
      id: r.id,
      slug: r.slug,
      url: `https://restaurantsistanbul.vercel.app/${r.citySlug}/${r.slug}`,
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
      highlights: r.highlights ?? [],
      llm_summary: r.llmSummary,
      sentiment_summary: r.sentimentSummary,
      popular_dishes: r.specialFeatures?.popularDishes ?? [],
      dietary_options: r.specialFeatures?.dietaryOptions ?? [],
      noise_level: r.specialFeatures?.noiseLevel ?? null,
      avg_meal_cost_try: r.specialFeatures?.avgMealCost ?? null,
      contextual_ratings: r.specialFeatures?.contextualRatings ?? null,
      scenario_summary: r.scenarioSummary ?? null,
      faq: r.faq ?? [],
      nearby: r.nearby ?? null,
      reservation_links: r.reservationLinks ?? null,
      confidence_score: r.confidenceScore,
      verified_data: r.verifiedData,
      last_updated: r.lastUpdated,
    },
  }, { headers: CORS_HEADERS });
}
