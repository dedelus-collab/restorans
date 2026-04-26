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

export function CityRestaurantList({ city, list, topDistricts }: Props) {
  const [active, setActive] = useState<string | null>(null);

  const filtered = active ? list.filter(r => r.district === active) : list;

  return (
    <>
      {/* District filter */}
      {topDistricts.length > 1 && (
        <div className="mb-6 flex flex-wrap gap-2">
          <button
            onClick={() => setActive(null)}
            className={`text-sm px-3 py-1.5 rounded-full border transition-colors ${
              active === null
                ? "bg-blue-600 border-blue-600 text-white shadow-sm"
                : "bg-blue-50 border-blue-100 text-blue-700 hover:bg-blue-100"
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
                  ? "bg-blue-600 border-blue-600 text-white shadow-sm"
                  : "bg-blue-50 border-blue-100 text-blue-700 hover:bg-blue-100"
              }`}
            >
              {name} <span className={active === name ? "text-blue-200" : "text-blue-400"}>({count})</span>
            </button>
          ))}
        </div>
      )}

      {active && (
        <p className="text-xs text-gray-400 mb-4">
          {filtered.length} restaurant{filtered.length !== 1 ? "s" : ""} in {active}
        </p>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {filtered.map(r => (
          <RestaurantCard
            key={r.id}
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
            variant="compact"
          />
        ))}
      </div>
    </>
  );
}
