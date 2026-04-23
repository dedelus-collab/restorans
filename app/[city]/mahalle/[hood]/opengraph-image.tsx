import { ImageResponse } from "next/og";

export const runtime = "nodejs";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

function formatHood(hood: string) {
  return hood
    .replace(/-/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

export default async function OgImage({
  params,
}: {
  params: Promise<{ city: string; hood: string }>;
}) {
  const { city, hood } = await params;
  const hoodName = formatHood(hood);
  const cityName = city.charAt(0).toUpperCase() + city.slice(1);

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
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <span style={{ color: "#3b82f6", fontSize: "24px", fontWeight: 700 }}>Istanbul Restaurants</span>
          <span style={{ color: "#475569", fontSize: "22px" }}>{cityName}</span>
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
          <div style={{ color: "#64748b", fontSize: "26px", display: "flex" }}>
            <span>Mahalle Rehberi</span>
          </div>
          <div
            style={{
              color: "#f8fafc",
              fontSize: "72px",
              fontWeight: 800,
              lineHeight: 1.05,
              letterSpacing: "-3px",
              display: "flex",
            }}
          >
            <span>{hoodName}</span>
          </div>
        </div>

        <div style={{ display: "flex", alignItems: "center" }}>
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
            <span>Restoranlar · restaurantsistanbul.vercel.app</span>
          </div>
        </div>
      </div>
    ),
    { ...size }
  );
}
