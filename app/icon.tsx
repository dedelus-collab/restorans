import { ImageResponse } from "next/og";

export const size = { width: 64, height: 64 };
export const contentType = "image/png";

export default function Icon() {
  return new ImageResponse(
    (
      <div
        style={{
          width: 64,
          height: 64,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          borderRadius: "50%",
          background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        }}
      >
        {/* Chef hat */}
        <div
          style={{
            position: "absolute",
            top: 4,
            left: 16,
            width: 32,
            height: 14,
            background: "white",
            borderRadius: 6,
            display: "flex",
          }}
        />
        <div
          style={{
            position: "absolute",
            top: 2,
            left: 14,
            width: 36,
            height: 8,
            background: "white",
            borderRadius: 20,
            display: "flex",
          }}
        />
        <div
          style={{
            position: "absolute",
            top: 16,
            left: 12,
            width: 40,
            height: 5,
            background: "#D8D8D8",
            borderRadius: 20,
            display: "flex",
          }}
        />
        {/* Hair */}
        <div
          style={{
            position: "absolute",
            top: 14,
            left: 8,
            width: 48,
            height: 32,
            background: "#1e1208",
            borderRadius: "50%",
            display: "flex",
          }}
        />
        {/* Face */}
        <div
          style={{
            position: "absolute",
            top: 20,
            left: 12,
            width: 40,
            height: 38,
            background: "#FFE0C8",
            borderRadius: "50%",
            display: "flex",
          }}
        />
        {/* Left eye white */}
        <div
          style={{
            position: "absolute",
            top: 26,
            left: 14,
            width: 12,
            height: 14,
            background: "white",
            borderRadius: "50%",
            display: "flex",
          }}
        />
        {/* Left iris */}
        <div
          style={{
            position: "absolute",
            top: 28,
            left: 15,
            width: 9,
            height: 11,
            background: "#4a8de8",
            borderRadius: "50%",
            display: "flex",
          }}
        />
        {/* Left pupil */}
        <div
          style={{
            position: "absolute",
            top: 30,
            left: 16,
            width: 6,
            height: 8,
            background: "#0d1b35",
            borderRadius: "50%",
            display: "flex",
          }}
        />
        {/* Left highlight */}
        <div
          style={{
            position: "absolute",
            top: 27,
            left: 19,
            width: 4,
            height: 4,
            background: "white",
            borderRadius: "50%",
            display: "flex",
          }}
        />
        {/* Right eye white */}
        <div
          style={{
            position: "absolute",
            top: 26,
            left: 38,
            width: 12,
            height: 14,
            background: "white",
            borderRadius: "50%",
            display: "flex",
          }}
        />
        {/* Right iris */}
        <div
          style={{
            position: "absolute",
            top: 28,
            left: 39,
            width: 9,
            height: 11,
            background: "#4a8de8",
            borderRadius: "50%",
            display: "flex",
          }}
        />
        {/* Right pupil */}
        <div
          style={{
            position: "absolute",
            top: 30,
            left: 40,
            width: 6,
            height: 8,
            background: "#0d1b35",
            borderRadius: "50%",
            display: "flex",
          }}
        />
        {/* Right highlight */}
        <div
          style={{
            position: "absolute",
            top: 27,
            left: 43,
            width: 4,
            height: 4,
            background: "white",
            borderRadius: "50%",
            display: "flex",
          }}
        />
        {/* Left blush */}
        <div
          style={{
            position: "absolute",
            top: 38,
            left: 10,
            width: 10,
            height: 5,
            background: "#FFB0BE",
            borderRadius: "50%",
            opacity: 0.7,
            display: "flex",
          }}
        />
        {/* Right blush */}
        <div
          style={{
            position: "absolute",
            top: 38,
            left: 44,
            width: 10,
            height: 5,
            background: "#FFB0BE",
            borderRadius: "50%",
            opacity: 0.7,
            display: "flex",
          }}
        />
        {/* Smile */}
        <div
          style={{
            position: "absolute",
            top: 46,
            left: 22,
            width: 20,
            height: 10,
            borderBottom: "3px solid #e06070",
            borderRadius: "0 0 50% 50%",
            display: "flex",
          }}
        />
      </div>
    ),
    { ...size }
  );
}
