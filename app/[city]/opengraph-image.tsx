import { ImageResponse } from "next/og";
import { getRestaurantsByCity } from "@/data/restaurants";

export const runtime = "nodejs";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default async function OgImage({
  params,
}: {
  params: Promise<{ city: string }>;
}) {
  const { city } = await params;
  const restaurants = getRestaurantsByCity(city);
  const cityName = restaurants[0]?.city ?? city;
  const count = restaurants.length;

  return new ImageResponse(
    (
      <div
        style={{
          background: "#0f172a",
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          padding: "80px",
        }}
      >
        <span style={{ color: "#3b82f6", fontSize: "24px", fontWeight: 700, marginBottom: "24px" }}>
          restorans
        </span>
        <div
          style={{
            color: "#f8fafc",
            fontSize: "72px",
            fontWeight: 800,
            lineHeight: 1.05,
            letterSpacing: "-3px",
            marginBottom: "20px",
            display: "flex",
          }}
        >
          <span>{cityName} Restoranları</span>
        </div>
        <div style={{ color: "#94a3b8", fontSize: "30px", marginBottom: "48px", display: "flex" }}>
          <span>{count} restoran · AI-ready veri · Schema.org</span>
        </div>
        <div style={{ display: "flex", gap: "16px" }}>
          {["FAQ", "Transit", "Popüler Yemekler", "Senaryo Analizi"].map((s) => (
            <div
              key={s}
              style={{
                background: "#1e293b",
                border: "1px solid #334155",
                borderRadius: "999px",
                padding: "8px 20px",
                color: "#cbd5e1",
                fontSize: "20px",
              }}
            >
              {s}
            </div>
          ))}
        </div>
        <div style={{ position: "absolute", bottom: "60px", right: "80px", color: "#475569", fontSize: "20px", display: "flex" }}>
          <span>restorans.vercel.app</span>
        </div>
      </div>
    ),
    { ...size }
  );
}
