import { ImageResponse } from "next/og";
import { getRestaurantsByNeighborhood } from "@/data/restaurants";

export const runtime = "edge";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default async function OgImage({
  params,
}: {
  params: Promise<{ city: string; hood: string }>;
}) {
  const { city, hood } = await params;
  const list = getRestaurantsByNeighborhood(city, hood);
  const hoodName = list[0]?.neighborhood ?? hood;
  const cityName = list[0]?.city ?? city;
  const count = list.length;

  // Öne çıkan mutfak türleri
  const cuisineCounts: Record<string, number> = {};
  for (const r of list) {
    if (r.cuisine) cuisineCounts[r.cuisine] = (cuisineCounts[r.cuisine] ?? 0) + 1;
  }
  const topCuisines = Object.entries(cuisineCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 3)
    .map(([c]) => c);

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
        {/* Üst: logo + şehir */}
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <span style={{ color: "#3b82f6", fontSize: "24px", fontWeight: 700 }}>restorans</span>
          <span style={{ color: "#475569", fontSize: "22px" }}>{cityName}</span>
        </div>

        {/* Orta: mahalle adı */}
        <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
          <div style={{ color: "#64748b", fontSize: "26px" }}>Mahalle Rehberi</div>
          <div
            style={{
              color: "#f8fafc",
              fontSize: "72px",
              fontWeight: 800,
              lineHeight: 1.05,
              letterSpacing: "-3px",
            }}
          >
            {hoodName}
          </div>
        </div>

        {/* Alt: sayaç + mutfaklar */}
        <div style={{ display: "flex", gap: "16px", alignItems: "center" }}>
          <div
            style={{
              background: "#1e293b",
              border: "1px solid #334155",
              borderRadius: "12px",
              padding: "10px 24px",
              color: "#f8fafc",
              fontSize: "22px",
              fontWeight: 600,
            }}
          >
            {count} restoran
          </div>
          {topCuisines.map((c) => (
            <div
              key={c}
              style={{
                background: "#1e293b",
                border: "1px solid #334155",
                borderRadius: "999px",
                padding: "8px 20px",
                color: "#94a3b8",
                fontSize: "20px",
              }}
            >
              {c}
            </div>
          ))}
          <div style={{ marginLeft: "auto", color: "#475569", fontSize: "20px" }}>
            restorans.io
          </div>
        </div>
      </div>
    ),
    { ...size }
  );
}
