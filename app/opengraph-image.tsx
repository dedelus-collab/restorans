import { ImageResponse } from "next/og";

export const runtime = "nodejs";
export const alt = "restorans — İstanbul Restoran Veritabanı";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default function OgImage() {
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
        {/* Logo */}
        <div style={{ display: "flex", alignItems: "center", gap: "16px", marginBottom: "32px" }}>
          <div
            style={{
              background: "#3b82f6",
              borderRadius: "12px",
              width: "56px",
              height: "56px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: "28px",
            }}
          >
            🍽
          </div>
          <span style={{ color: "#f8fafc", fontSize: "36px", fontWeight: 700, letterSpacing: "-1px" }}>
            restorans
          </span>
        </div>

        {/* Başlık */}
        <div
          style={{
            color: "#f8fafc",
            fontSize: "56px",
            fontWeight: 800,
            lineHeight: 1.1,
            letterSpacing: "-2px",
            marginBottom: "24px",
            display: "flex",
            flexDirection: "column",
          }}
        >
          <span>İstanbul Restoran</span>
          <span>Veritabanı</span>
        </div>

        {/* Alt yazı */}
        <div style={{ color: "#94a3b8", fontSize: "26px", marginBottom: "48px", display: "flex" }}>
          <span>453 restoran · AI-ready veri · Schema.org</span>
        </div>

        {/* Stat pills */}
        <div style={{ display: "flex", gap: "16px" }}>
          {["453 Restoran", "19 Koleksiyon", "78 Mahalle", "1M+ Yorum"].map((s) => (
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

        {/* Domain */}
        <div
          style={{
            position: "absolute",
            bottom: "60px",
            right: "80px",
            color: "#475569",
            fontSize: "22px",
          }}
        >
          restorans.vercel.app
        </div>
      </div>
    ),
    { ...size }
  );
}
