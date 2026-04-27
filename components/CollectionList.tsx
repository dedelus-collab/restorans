"use client";
import { useState } from "react";
import Link from "next/link";

type Transit = { name: string; type: string; walk_min: number };

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
  openingHours?: string;
  features?: {
    terrace?: boolean;
    teras?: boolean;
    wifi?: boolean;
    reservation?: boolean;
    rezervasyon?: boolean;
    seaView?: boolean;
    liveMusic?: boolean;
    vegan?: boolean;
    parking?: boolean;
  };
  specialFeatures?: {
    popularDishes?: string[];
    avgMealCost?: number;
    noiseLevel?: string;
    standoutPlus?: string;
    criticalMinus?: string;
    contextualRatings?: { businessLunch?: number; romanticDate?: number; groupDining?: number };
  } | null;
  priceDetail?: { avgPerPerson?: string; mainCourseRange?: string };
  nearby?: { transit?: Transit[] };
};

type Props = {
  city: string;
  list: Restaurant[];
  topDistricts: [string, number][];
};

const CUISINE_PHOTOS: Record<string, { photo: string; color: string }> = {
  kebap:           { photo: "https://images.unsplash.com/photo-1529543544282-ea669407fca3?w=600&q=75&auto=format&fit=crop", color: "#b91c1c" },
  balik:           { photo: "https://images.unsplash.com/photo-1560717845-968823efbee1?w=600&q=75&auto=format&fit=crop", color: "#0369a1" },
  "pizza-italyan": { photo: "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=600&q=75&auto=format&fit=crop", color: "#166534" },
  "sushi-japon":   { photo: "https://images.unsplash.com/photo-1579584425555-c3ce17fd4351?w=600&q=75&auto=format&fit=crop", color: "#9f1239" },
  "burger-steak":  { photo: "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=600&q=75&auto=format&fit=crop", color: "#b45309" },
  kahvalti:        { photo: "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=600&q=75&auto=format&fit=crop", color: "#b45309" },
  meyhane:         { photo: "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=600&q=75&auto=format&fit=crop", color: "#7e22ce" },
  vegan:           { photo: "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=600&q=75&auto=format&fit=crop", color: "#15803d" },
  lokanta:         { photo: "https://images.unsplash.com/photo-1547592180-85f173990554?w=600&q=75&auto=format&fit=crop", color: "#c2410c" },
  kafe:            { photo: "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=600&q=75&auto=format&fit=crop", color: "#92400e" },
  pide:            { photo: "https://images.unsplash.com/photo-1555507036-ab1f4038808a?w=600&q=75&auto=format&fit=crop", color: "#d97706" },
  "turk-mutfagi":  { photo: "https://images.unsplash.com/photo-1547592180-85f173990554?w=600&q=75&auto=format&fit=crop", color: "#991b1b" },
  "dunya-mutfagi": { photo: "https://images.unsplash.com/photo-1559339352-11d035aa65de?w=600&q=75&auto=format&fit=crop", color: "#0e7490" },
  italyan:         { photo: "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=600&q=75&auto=format&fit=crop", color: "#166534" },
  seafood:         { photo: "https://images.unsplash.com/photo-1560717845-968823efbee1?w=600&q=75&auto=format&fit=crop", color: "#075985" },
};
const DEFAULT_PHOTO = { photo: "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=600&q=75&auto=format&fit=crop", color: "#334155" };

const TRANSIT_ICONS: Record<string, string> = {
  metro: "M", tramvay: "T", marmaray: "M", vapur: "V", metrobus: "MB",
};

function getPriceSymbol(range: number) {
  return range <= 1 ? "₺" : range === 2 ? "₺₺" : range === 3 ? "₺₺₺" : "₺₺₺₺";
}

function Stars({ rating }: { rating: number }) {
  const full = Math.floor(rating);
  const half = rating % 1 >= 0.3 && rating % 1 < 0.8;
  const empty = 5 - full - (half ? 1 : 0);
  return (
    <span className="text-amber-400 text-xs tracking-tight">
      {"★".repeat(full)}{half ? "½" : ""}<span className="text-gray-200">{"★".repeat(empty)}</span>
    </span>
  );
}

function RichCard({ r, rank }: { r: Restaurant; rank: number }) {
  const theme = CUISINE_PHOTOS[r.cuisineSlug?.toLowerCase().trim() ?? ""] ?? DEFAULT_PHOTO;
  const location = r.district || r.neighborhood || "";
  const dishes = r.specialFeatures?.popularDishes ?? [];
  const transit = r.nearby?.transit?.[0];
  const avgCost = r.specialFeatures?.avgMealCost
    ? `~${r.specialFeatures.avgMealCost}₺`
    : r.priceDetail?.avgPerPerson
    ? r.priceDetail.avgPerPerson.replace(" TL", "₺")
    : null;
  const f = r.features ?? {};
  const hasTerrace = f.terrace || f.teras;
  const hasReservation = f.reservation || f.rezervasyon;
  const standout = r.specialFeatures?.standoutPlus;

  return (
    <Link
      href={`/${r.city === "İstanbul" ? "istanbul" : r.city.toLowerCase()}/${r.slug}`}
      className="group block rounded-2xl overflow-hidden border border-gray-200 bg-white hover:shadow-xl hover:-translate-y-1 transition-all duration-200"
    >
      {/* Photo */}
      <div
        className="relative h-44 overflow-hidden"
        style={{ backgroundImage: `url('${theme.photo}')`, backgroundSize: "cover", backgroundPosition: "center" }}
      >
        <div className="absolute inset-0 bg-black/20 group-hover:bg-black/10 transition-colors" />
        <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent" />

        {/* Rank badge */}
        {rank <= 3 && (
          <span className="absolute top-3 left-3 text-xs font-black bg-amber-400 text-white px-2 py-0.5 rounded-full shadow">
            #{rank}
          </span>
        )}

        {/* Verified */}
        {r.verifiedData && (
          <span className="absolute top-3 right-3 text-xs bg-white/90 text-green-700 font-semibold px-2 py-0.5 rounded-full shadow-sm">
            ✓ Verified
          </span>
        )}

        {/* Rating overlay on photo */}
        {r.avgRating != null && (
          <div className="absolute bottom-3 left-3 flex items-center gap-1.5">
            <Stars rating={r.avgRating} />
            <span className="text-white font-black text-sm drop-shadow">{r.avgRating}</span>
            <span className="text-white/60 text-xs">({r.reviewCount != null ? (r.reviewCount >= 1000 ? (r.reviewCount / 1000).toFixed(1) + "K" : r.reviewCount) : ""})</span>
          </div>
        )}
      </div>

      {/* Content */}
      <div className="p-4">
        {/* Name + location */}
        <h3 className="font-black text-gray-900 text-base mb-0.5 line-clamp-1 group-hover:text-blue-600 transition-colors">
          {r.name}
        </h3>
        <p className="text-xs text-gray-500 mb-3">
          {location} · {r.cuisine} · <span className="font-semibold text-gray-700">{getPriceSymbol(r.priceRange)}</span>
        </p>

        {/* Summary */}
        {r.llmSummary && (
          <p className="text-sm text-gray-700 leading-relaxed line-clamp-3 mb-3">{r.llmSummary}</p>
        )}

        {/* Standout quote */}
        {standout && (
          <p className="text-xs text-blue-700 bg-blue-50 border border-blue-100 rounded-lg px-3 py-1.5 mb-3 leading-relaxed">
            ✦ {standout}
          </p>
        )}

        {/* Popular dishes */}
        {dishes.length > 0 && (
          <div className="flex flex-wrap gap-1 mb-3">
            {dishes.slice(0, 4).map(d => (
              <span key={d} className="text-xs bg-amber-50 text-amber-800 border border-amber-200 px-2 py-0.5 rounded-full font-medium">
                {d}
              </span>
            ))}
          </div>
        )}

        {/* Info bar */}
        <div className="flex flex-wrap items-center gap-x-3 gap-y-1.5 pt-3 border-t border-gray-100">
          {transit && (
            <span className="flex items-center gap-1 text-xs text-gray-600">
              <span className="w-4 h-4 rounded-sm bg-gray-800 text-white flex items-center justify-center text-[9px] font-black shrink-0">
                {TRANSIT_ICONS[transit.type] ?? "🚌"}
              </span>
              {transit.name} <span className="text-gray-400">{transit.walk_min}dk</span>
            </span>
          )}
          {avgCost && (
            <span className="text-xs text-gray-600 flex items-center gap-1">
              <span className="text-gray-400">💰</span> {avgCost}<span className="text-gray-400">/kişi</span>
            </span>
          )}
          {hasTerrace && <span className="text-xs text-gray-500 bg-gray-50 border border-gray-200 px-1.5 py-0.5 rounded">🌿 Teras</span>}
          {f.seaView && <span className="text-xs text-gray-500 bg-gray-50 border border-gray-200 px-1.5 py-0.5 rounded">🌊 Deniz</span>}
          {f.wifi && <span className="text-xs text-gray-500 bg-gray-50 border border-gray-200 px-1.5 py-0.5 rounded">📶 WiFi</span>}
          {hasReservation && <span className="text-xs text-gray-500 bg-gray-50 border border-gray-200 px-1.5 py-0.5 rounded">📅 Rezervasyon</span>}
        </div>
      </div>
    </Link>
  );
}

export function CollectionList({ city, list, topDistricts }: Props) {
  const [active, setActive] = useState<string | null>(null);
  const filtered = active ? list.filter(r => r.district === active) : list;

  return (
    <>
      {/* District filter */}
      {topDistricts.length > 1 && (
        <section className="mb-8">
          <h2 className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-3">Filter by District</h2>
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
                {name} <span className="text-gray-400 text-xs">({count})</span>
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
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
        {filtered.map((r, idx) => (
          <RichCard key={r.id} r={r} rank={!active ? idx + 1 : 999} />
        ))}
      </div>
    </>
  );
}
