import { ImageResponse } from "next/og";
import { getRestaurantBySlug, getPriceSymbol } from "@/data/restaurants";

export const runtime = "nodejs";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default async function OgImage({
  params,
}: {
  params: Promise<{ city: string; slug: string }>;
}) {
  const { city, slug } = await params;
  const r = getRestaurantBySlug(city, slug);

  const name        = r?.name        ?? "Restoran";
  const cuisine     = r?.cuisine     ?? "";
  const neighborhood = r?.neighborhood ?? "";
  const rating      = r?.avgRating   ?? 0;
  const reviewCount = r?.reviewCount ?? 0;
  const price       = r ? getPriceSymbol(r.priceRange) : "";
  const summary     = r?.llmSummary  ?? "";

  return new ImageResponse(
    (
      <div
        style={{
          background: "#0f172a",
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          padding: "64px 80px",
        }}
      >
        {/* Üst: logo + mutfak */}
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <span style={{ color: "#3b82f6", fontSize: "24px", fontWeight: 700 }}>Istanbul Restaurants</span>
          {cuisine && (
            <span
              style={{
                background: "#1e293b",
                border: "1px solid #334155",
                borderRadius: "999px",
                padding: "6px 18px",
                color: "#94a3b8",
                fontSize: "20px",
              }}
            >
              {cuisine}
            </span>
          )}
        </div>

        {/* Orta: restoran adı + mahalle */}
        <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
          <div
            style={{
              color: "#f8fafc",
              fontSize: "64px",
              fontWeight: 800,
              lineHeight: 1.05,
              letterSpacing: "-2px",
              display: "flex",
            }}
          >
            <span>{name}</span>
          </div>
          {neighborhood && (
            <div style={{ color: "#64748b", fontSize: "28px", display: "flex" }}>
              <span>{neighborhood}</span>
            </div>
          )}
          {summary && (
            <div
              style={{
                color: "#94a3b8",
                fontSize: "22px",
                lineHeight: 1.5,
                maxWidth: "900px",
                marginTop: "8px",
                display: "flex",
              }}
            >
              <span>{summary.length > 140 ? summary.slice(0, 140) + "…" : summary}</span>
            </div>
          )}
        </div>

        {/* Alt: puan + fiyat + yorum */}
        <div style={{ display: "flex", gap: "24px", alignItems: "center" }}>
          {rating > 0 && (
            <div
              style={{
                background: "#1e293b",
                border: "1px solid #334155",
                borderRadius: "12px",
                padding: "10px 24px",
                display: "flex",
                alignItems: "center",
                gap: "8px",
              }}
            >
              <span style={{ color: "#fbbf24", fontSize: "22px" }}>★</span>
              <span style={{ color: "#f8fafc", fontSize: "26px", fontWeight: 700 }}>{rating}</span>
              {reviewCount > 0 && (
                <span style={{ color: "#64748b", fontSize: "18px" }}>
                  ({reviewCount.toLocaleString("tr-TR")})
                </span>
              )}
            </div>
          )}
          {price && (
            <div
              style={{
                background: "#1e293b",
                border: "1px solid #334155",
                borderRadius: "12px",
                padding: "10px 24px",
                color: "#94a3b8",
                fontSize: "22px",
                display: "flex",
              }}
            >
              <span>{price}</span>
            </div>
          )}
          <div style={{ marginLeft: "auto", color: "#475569", fontSize: "20px", display: "flex" }}>
            <span>restorans.vercel.app</span>
          </div>
        </div>
      </div>
    ),
    { ...size }
  );
}
