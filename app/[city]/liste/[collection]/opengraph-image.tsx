import { ImageResponse } from "next/og";
import { getCollection } from "@/lib/collections";
import { getRestaurantsByCity } from "@/data/restaurants";

export const runtime = "nodejs";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

const CATEGORY_LABEL: Record<string, string> = {
  cuisine: "Mutfak",
  scenario: "Senaryo",
  vibe: "Vibe",
};

export default async function OgImage({
  params,
}: {
  params: Promise<{ city: string; collection: string }>;
}) {
  const { city, collection: colSlug } = await params;
  const col = getCollection(colSlug);
  const allRestaurants = getRestaurantsByCity(city);
  const count = col ? allRestaurants.filter(col.filter).length : 0;

  const title = col?.title ?? "Koleksiyon";
  const desc  = col?.description ?? "";
  const categoryLabel = col ? CATEGORY_LABEL[col.category] ?? "" : "";

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
        {/* Üst: logo + kategori */}
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <span style={{ color: "#3b82f6", fontSize: "24px", fontWeight: 700 }}>Istanbul Restaurants</span>
          {categoryLabel && (
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
              {categoryLabel}
            </span>
          )}
        </div>

        {/* Orta: başlık + açıklama */}
        <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          <div
            style={{
              color: "#f8fafc",
              fontSize: "54px",
              fontWeight: 800,
              lineHeight: 1.1,
              letterSpacing: "-2px",
              maxWidth: "950px",
              display: "flex",
            }}
          >
            <span>{title}</span>
          </div>
          {desc && (
            <div style={{ color: "#94a3b8", fontSize: "22px", lineHeight: 1.5, maxWidth: "900px", display: "flex" }}>
              <span>{desc.length > 130 ? desc.slice(0, 130) + "…" : desc}</span>
            </div>
          )}
        </div>

        {/* Alt: sayaç */}
        <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
          {count > 0 && (
            <div
              style={{
                background: "#1e293b",
                border: "1px solid #334155",
                borderRadius: "12px",
                padding: "10px 24px",
                color: "#f8fafc",
                fontSize: "22px",
                fontWeight: 600,
                display: "flex",
              }}
            >
              <span>{count} restaurants</span>
            </div>
          )}
          <div style={{ marginLeft: "auto", color: "#475569", fontSize: "20px", display: "flex" }}>
            <span>www.restaurantsistanbul.com</span>
          </div>
        </div>
      </div>
    ),
    { ...size }
  );
}
