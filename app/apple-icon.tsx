import { ImageResponse } from "next/og";

export const size = { width: 180, height: 180 };
export const contentType = "image/png";

export default function AppleIcon() {
  return new ImageResponse(
    (
      <div
        style={{
          width: 180,
          height: 180,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
          borderRadius: 40,
        }}
      >
        {/* Chef hat top */}
        <div
          style={{
            position: "absolute",
            top: 10,
            left: 46,
            width: 88,
            height: 38,
            background: "white",
            borderRadius: 14,
            display: "flex",
          }}
        />
        <div
          style={{
            position: "absolute",
            top: 6,
            left: 40,
            width: 100,
            height: 24,
            background: "white",
            borderRadius: 60,
            display: "flex",
          }}
        />
        <div
          style={{
            position: "absolute",
            top: 44,
            left: 34,
            width: 112,
            height: 14,
            background: "#D8D8D8",
            borderRadius: 60,
            display: "flex",
          }}
        />
        {/* Hair */}
        <div
          style={{
            position: "absolute",
            top: 40,
            left: 22,
            width: 136,
            height: 90,
            background: "#1e1208",
            borderRadius: "50%",
            display: "flex",
          }}
        />
        {/* Face */}
        <div
          style={{
            position: "absolute",
            top: 58,
            left: 34,
            width: 112,
            height: 108,
            background: "#FFE0C8",
            borderRadius: "50%",
            display: "flex",
          }}
        />
        {/* Left eye white */}
        <div
          style={{
            position: "absolute",
            top: 74,
            left: 40,
            width: 34,
            height: 40,
            background: "white",
            borderRadius: "50%",
            display: "flex",
          }}
        />
        {/* Left iris */}
        <div
          style={{
            position: "absolute",
            top: 78,
            left: 43,
            width: 26,
            height: 32,
            background: "#4a8de8",
            borderRadius: "50%",
            display: "flex",
          }}
        />
        {/* Left pupil */}
        <div
          style={{
            position: "absolute",
            top: 84,
            left: 47,
            width: 16,
            height: 22,
            background: "#0d1b35",
            borderRadius: "50%",
            display: "flex",
          }}
        />
        {/* Left highlight */}
        <div
          style={{
            position: "absolute",
            top: 76,
            left: 57,
            width: 11,
            height: 11,
            background: "white",
            borderRadius: "50%",
            display: "flex",
          }}
        />
        {/* Right eye white */}
        <div
          style={{
            position: "absolute",
            top: 74,
            left: 106,
            width: 34,
            height: 40,
            background: "white",
            borderRadius: "50%",
            display: "flex",
          }}
        />
        {/* Right iris */}
        <div
          style={{
            position: "absolute",
            top: 78,
            left: 109,
            width: 26,
            height: 32,
            background: "#4a8de8",
            borderRadius: "50%",
            display: "flex",
          }}
        />
        {/* Right pupil */}
        <div
          style={{
            position: "absolute",
            top: 84,
            left: 115,
            width: 16,
            height: 22,
            background: "#0d1b35",
            borderRadius: "50%",
            display: "flex",
          }}
        />
        {/* Right highlight */}
        <div
          style={{
            position: "absolute",
            top: 76,
            left: 123,
            width: 11,
            height: 11,
            background: "white",
            borderRadius: "50%",
            display: "flex",
          }}
        />
        {/* Left blush */}
        <div
          style={{
            position: "absolute",
            top: 108,
            left: 28,
            width: 28,
            height: 14,
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
            top: 108,
            left: 124,
            width: 28,
            height: 14,
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
            top: 130,
            left: 62,
            width: 56,
            height: 28,
            borderBottom: "5px solid #e06070",
            borderRadius: "0 0 50% 50%",
            display: "flex",
          }}
        />
      </div>
    ),
    { ...size }
  );
}
