import Link from "next/link";

type Props = {
  city: string;
  slug: string;
  name: string;
  district?: string;
  neighborhood?: string;
  cuisine: string;
  cuisineSlug?: string;
  priceRange: number;
  avgRating: number | null;
  reviewCount: number | null;
  llmSummary?: string;
  verifiedData?: boolean;
  tags?: string[];
  popularDishes?: string[];
  variant?: "compact" | "featured";
};

const CUISINE_THEMES: Record<string, { bg: string; emoji: string }> = {
  kebap:           { bg: "linear-gradient(135deg,#f97316,#dc2626)",  emoji: "🥩" },
  balik:           { bg: "linear-gradient(135deg,#0ea5e9,#0369a1)",  emoji: "🐟" },
  "pizza-italyan": { bg: "linear-gradient(135deg,#22c55e,#15803d)",  emoji: "🍕" },
  "sushi-japon":   { bg: "linear-gradient(135deg,#f43f5e,#9f1239)",  emoji: "🍣" },
  "burger-steak":  { bg: "linear-gradient(135deg,#f59e0b,#b45309)",  emoji: "🍔" },
  kahvalti:        { bg: "linear-gradient(135deg,#fcd34d,#f59e0b)",  emoji: "🍳" },
  meyhane:         { bg: "linear-gradient(135deg,#a855f7,#7e22ce)",  emoji: "🍷" },
  vegan:           { bg: "linear-gradient(135deg,#4ade80,#16a34a)",  emoji: "🥗" },
  lokanta:         { bg: "linear-gradient(135deg,#fb923c,#c2410c)",  emoji: "🫕" },
  kafe:            { bg: "linear-gradient(135deg,#d97706,#92400e)",  emoji: "☕" },
  pide:            { bg: "linear-gradient(135deg,#fbbf24,#d97706)",  emoji: "🫓" },
  "turk-mutfagi":  { bg: "linear-gradient(135deg,#ef4444,#7f1d1d)",  emoji: "🍲" },
  "dunya-mutfagi": { bg: "linear-gradient(135deg,#06b6d4,#0e7490)",  emoji: "🌍" },
  italyan:         { bg: "linear-gradient(135deg,#22c55e,#166534)",  emoji: "🍝" },
  seafood:         { bg: "linear-gradient(135deg,#38bdf8,#075985)",  emoji: "🦐" },
};

const DEFAULT_THEME = { bg: "linear-gradient(135deg,#64748b,#334155)", emoji: "🍽️" };

function getPriceSymbol(range: number): string {
  return range <= 1 ? "₺" : range === 2 ? "₺₺" : range === 3 ? "₺₺₺" : "₺₺₺₺";
}

function Stars({ rating }: { rating: number }) {
  const full  = Math.floor(rating);
  const half  = rating % 1 >= 0.3 && rating % 1 < 0.8;
  const empty = 5 - full - (half ? 1 : 0);
  return (
    <span className="text-amber-400 text-sm tracking-tight">
      {"★".repeat(full)}{half ? "½" : ""}<span className="text-gray-300">{"★".repeat(empty)}</span>
    </span>
  );
}

export function RestaurantCard({
  city, slug, name, district, neighborhood, cuisine, cuisineSlug,
  priceRange, avgRating, reviewCount, llmSummary, verifiedData,
  tags = [], popularDishes = [], variant = "compact",
}: Props) {
  const key = cuisineSlug?.toLowerCase().trim() ?? "";
  const theme = CUISINE_THEMES[key] ?? DEFAULT_THEME;
  const location = district || neighborhood || "";

  if (variant === "featured") {
    return (
      <Link href={`/${city}/${slug}`} className="group block rounded-2xl overflow-hidden border border-gray-200 bg-white hover:shadow-lg hover:-translate-y-0.5 transition-all duration-200">
        {/* Photo placeholder */}
        <div className="relative h-44 flex items-center justify-center" style={{ background: theme.bg }}>
          <span className="text-6xl drop-shadow-sm">{theme.emoji}</span>
          {verifiedData && (
            <span className="absolute top-3 right-3 text-xs bg-white/90 text-green-700 font-semibold px-2 py-0.5 rounded-full shadow-sm">
              ✓ Verified
            </span>
          )}
          <div className="absolute bottom-0 left-0 right-0 h-12 bg-gradient-to-t from-black/30 to-transparent" />
        </div>
        {/* Content */}
        <div className="p-4">
          <h3 className="font-bold text-gray-900 text-base mb-1 line-clamp-1 group-hover:text-blue-600 transition-colors">{name}</h3>
          <p className="text-xs text-gray-500 mb-2">{location} · {cuisine} · <span className="text-gray-700 font-medium">{getPriceSymbol(priceRange)}</span></p>
          {avgRating != null && (
            <div className="flex items-center gap-1.5 mb-2">
              <Stars rating={avgRating} />
              <span className="text-sm font-semibold text-gray-800">{avgRating}</span>
              <span className="text-xs text-gray-400">({reviewCount?.toLocaleString("en-US")})</span>
            </div>
          )}
          {llmSummary && (
            <p className="text-xs text-gray-500 line-clamp-2 leading-relaxed">{llmSummary}</p>
          )}
        </div>
      </Link>
    );
  }

  // Compact (list) variant
  return (
    <Link href={`/${city}/${slug}`} className="group flex gap-3 p-3 rounded-xl border border-gray-100 bg-white hover:border-gray-200 hover:shadow-md transition-all duration-150">
      {/* Thumb */}
      <div
        className="shrink-0 w-20 h-20 rounded-lg flex items-center justify-center text-3xl"
        style={{ background: theme.bg }}
      >
        {theme.emoji}
      </div>
      {/* Info */}
      <div className="flex-1 min-w-0">
        <div className="flex items-start justify-between gap-2">
          <h3 className="font-semibold text-gray-900 text-sm leading-snug line-clamp-1 group-hover:text-blue-600 transition-colors">
            {name}
            {verifiedData && <span className="ml-1.5 text-xs font-normal text-green-600">✓</span>}
          </h3>
          {avgRating != null && (
            <div className="shrink-0 text-right">
              <div className="text-sm font-bold text-gray-900">{avgRating}</div>
              <div className="text-xs text-gray-400">{reviewCount != null ? (reviewCount >= 1000 ? (reviewCount/1000).toFixed(1)+"K" : reviewCount) : ""}</div>
            </div>
          )}
        </div>
        <p className="text-xs text-gray-500 mt-0.5">{location} · {cuisine} · <span className="font-medium text-gray-700">{getPriceSymbol(priceRange)}</span></p>
        {avgRating != null && (
          <div className="mt-0.5">
            <Stars rating={avgRating} />
          </div>
        )}
        {popularDishes.length > 0 ? (
          <p className="text-xs text-gray-400 mt-1 line-clamp-1">{popularDishes.slice(0, 3).join(" · ")}</p>
        ) : llmSummary ? (
          <p className="text-xs text-gray-500 mt-1 line-clamp-1">{llmSummary}</p>
        ) : null}
      </div>
    </Link>
  );
}
