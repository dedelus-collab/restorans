"use client";
import { useState } from "react";
import { RestaurantCard } from "./RestaurantCard";

type Restaurant = {
  id: string | number;
  slug: string;
  name: string;
  city: string;
  neighborhood: string;
  district: string;
  cuisine: string;
  cuisineSlug?: string;
  priceRange: number;
  avgRating: number | null;
  reviewCount: number | null;
  llmSummary: string;
  verifiedData: boolean;
  tags: string[];
  specialFeatures?: { popularDishes?: string[] } | null;
};

type Props = {
  city: string;
  list: Restaurant[];
  topDistricts: [string, number][];
};

export function CollectionList({ city, list, topDistricts }: Props) {
  const [active, setActive] = useState<string | null>(null);

  const filtered = active ? list.filter(r => r.district === active) : list;

  return (
    <>
      {/* District filter */}
      {topDistricts.length > 1 && (
        <section className="mb-8">
          <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-3">Filter by District</h2>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setActive(null)}
              className={`text-sm px-3 py-1.5 rounded-full border transition-colors ${
                active === null
                  ? "bg-gray-900 border-gray-900 text-white"
                  : "bg-gray-50 border-gray-200 text-gray-600 hover:bg-gray-100"
              }`}
            >
              All ({list.length})
            </button>
            {topDistricts.map(([name, count]) => (
              <button
                key={name}
                onClick={() => setActive(active === name ? null : name)}
                className={`text-sm px-3 py-1.5 rounded-full border transition-colors ${
                  active === name
                    ? "bg-gray-900 border-gray-900 text-white"
                    : "bg-gray-50 border-gray-200 text-gray-600 hover:bg-gray-100"
                }`}
              >
                {name} <span className={active === name ? "text-gray-400" : "text-gray-400"}>({count})</span>
              </button>
            ))}
          </div>
          {active && (
            <p className="text-xs text-gray-400 mt-2">
              {filtered.length} restaurant{filtered.length !== 1 ? "s" : ""} in {active}
            </p>
          )}
        </section>
      )}

      {/* Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {filtered.map((r, idx) => (
          <div key={r.id} className="relative">
            {!active && idx < 3 && (
              <span className="absolute top-3 left-3 z-10 text-xs font-bold bg-amber-400 text-white px-2 py-0.5 rounded-full shadow">
                #{idx + 1}
              </span>
            )}
            <RestaurantCard
              city={city}
              slug={r.slug}
              name={r.name}
              district={r.district}
              neighborhood={r.neighborhood}
              cuisine={r.cuisine}
              cuisineSlug={r.cuisineSlug}
              priceRange={r.priceRange}
              avgRating={r.avgRating}
              reviewCount={r.reviewCount}
              llmSummary={r.llmSummary}
              verifiedData={r.verifiedData}
              tags={r.tags}
              popularDishes={r.specialFeatures?.popularDishes ?? []}
              variant="featured"
            />
          </div>
        ))}
      </div>
    </>
  );
}
