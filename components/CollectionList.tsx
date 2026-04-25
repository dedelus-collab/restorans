"use client";
import { useState } from "react";
import Link from "next/link";

type Restaurant = {
  id: string | number;
  slug: string;
  name: string;
  city: string;
  neighborhood: string;
  district: string;
  cuisine: string;
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

function getPriceSymbol(range: number): string {
  return range <= 1 ? "₺" : range === 2 ? "₺₺" : range === 3 ? "₺₺₺" : "₺₺₺₺";
}

export function CollectionList({ city, list, topDistricts }: Props) {
  const [active, setActive] = useState<string | null>(null);

  const filtered = active ? list.filter(r => r.district === active) : list;

  return (
    <>
      {/* District filter */}
      {topDistricts.length > 1 && (
        <section className="mb-8">
          <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">Districts</h2>
          <div className="flex flex-wrap gap-2">
            {active && (
              <button
                onClick={() => setActive(null)}
                className="text-xs bg-gray-900 text-white px-2.5 py-1 rounded-full flex items-center gap-1 transition-colors"
              >
                ✕ Clear
              </button>
            )}
            {topDistricts.map(([name, count]) => (
              <button
                key={name}
                onClick={() => setActive(active === name ? null : name)}
                className={`text-xs px-2.5 py-1 rounded-full transition-colors ${
                  active === name
                    ? "bg-gray-900 text-white"
                    : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                }`}
              >
                {name} <span className={active === name ? "text-gray-300" : "text-gray-400"}>({count})</span>
              </button>
            ))}
          </div>
          {active && (
            <p className="text-xs text-gray-400 mt-2">
              Showing {filtered.length} restaurant{filtered.length !== 1 ? "s" : ""} in {active}
            </p>
          )}
        </section>
      )}

      {/* Restaurant list */}
      <div className="divide-y divide-gray-100">
        {filtered.map((r, idx) => (
          <Link
            key={r.id}
            href={`/${city}/${r.slug}`}
            className="block py-6 hover:bg-gray-50 transition-colors px-2 -mx-2 rounded"
          >
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  {!active && idx < 3 && (
                    <span className="text-xs font-bold text-amber-600 bg-amber-50 px-1.5 py-0.5 rounded">
                      #{idx + 1}
                    </span>
                  )}
                  <h2 className="font-semibold">{r.name}</h2>
                  {r.verifiedData && (
                    <span className="text-xs bg-green-50 text-green-700 px-2 py-0.5 rounded">Verified</span>
                  )}
                </div>
                <p className="text-sm text-gray-500">
                  {r.district || r.neighborhood} · {r.cuisine} · {getPriceSymbol(r.priceRange)}
                </p>
                <p className="text-sm text-gray-600 mt-2">{r.llmSummary}</p>
                {r.specialFeatures?.popularDishes && r.specialFeatures.popularDishes.length > 0 && (
                  <p className="text-xs text-gray-500 mt-2">
                    <span className="text-gray-400">Popular: </span>
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
                <div className="text-xs text-gray-400">{r.reviewCount} reviews</div>
                <div className="text-xs text-gray-400 mt-0.5">{getPriceSymbol(r.priceRange)}</div>
              </div>
            </div>
          </Link>
        ))}
      </div>
    </>
  );
}
