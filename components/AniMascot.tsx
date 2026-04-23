import React from "react";

// ─── Small inline chibi head — use next to section <h2> titles ───────────────
// variant: "chef" | "reviewer" | "foodie" | "explorer" | "star"
export function AniHead({
  variant = "chef",
  className,
}: {
  variant?: "chef" | "reviewer" | "foodie" | "explorer" | "star";
  className?: string;
}) {
  const face = { cx: 24, cy: 29, rx: 17, ry: 19, fill: "#FFE0C8" };

  const leftEye  = { cx: 16, cy: 27 };
  const rightEye = { cx: 32, cy: 27 };

  function Eye({ cx, cy, iris, pupil }: { cx: number; cy: number; iris: string; pupil?: string }) {
    return (
      <>
        <ellipse cx={cx} cy={cy} rx={7} ry={8.5} fill="white" />
        <ellipse cx={cx} cy={cy + 1} rx={5.5} ry={7} fill={iris} />
        <ellipse cx={cx} cy={cy + 2} rx={3} ry={4.5} fill={pupil ?? "#0d1b35"} />
        <circle  cx={cx + 2.5} cy={cy - 2} r={2.2} fill="white" />
        <circle  cx={cx - 1.5} cy={cy + 1} r={1}   fill="white" />
        {/* lash line */}
        <path d={`M${cx - 7} ${cy - 9} Q${cx} ${cy - 14} ${cx + 7} ${cy - 9}`}
              stroke="#0d1b35" strokeWidth="2.5" fill="none" strokeLinecap="round" />
      </>
    );
  }

  if (variant === "chef") {
    return (
      <svg viewBox="0 0 48 52" xmlns="http://www.w3.org/2000/svg" className={className} aria-hidden="true">
        {/* hair */}
        <path d="M7 30 Q6 12 24 7 Q42 12 41 30 Q41 42 24 44 Q7 42 7 30Z" fill="#1e1208" />
        {/* hat */}
        <rect x="12" y="3" width="24" height="14" rx="4" fill="white" />
        <ellipse cx="24" cy="3" rx="12" ry="4" fill="white" />
        <ellipse cx="24" cy="16" rx="16" ry="4" fill="#D8D8D8" />
        {/* face */}
        <ellipse {...face} />
        {/* bangs */}
        <path d="M7 29 Q7 20 12 15 Q17 11 21 13 Q22 16 21 20 Q23 17 24 17 Q25 17 27 20 Q26 16 27 13 Q31 11 36 15 Q41 20 41 29" fill="#1e1208" />
        <Eye {...leftEye}  iris="#4a8de8" />
        <Eye {...rightEye} iris="#4a8de8" />
        {/* eyebrows */}
        <path d="M10 20 Q16 16 22 18" stroke="#1e1208" strokeWidth="1.8" fill="none" strokeLinecap="round" />
        <path d="M26 18 Q32 16 38 20" stroke="#1e1208" strokeWidth="1.8" fill="none" strokeLinecap="round" />
        {/* smile */}
        <path d="M18 37 Q24 43 30 37" stroke="#e06070" strokeWidth="2" fill="none" strokeLinecap="round" />
        {/* blush */}
        <ellipse cx="10" cy="34" rx="5" ry="3" fill="#FFB0BE" opacity="0.55" />
        <ellipse cx="38" cy="34" rx="5" ry="3" fill="#FFB0BE" opacity="0.55" />
      </svg>
    );
  }

  if (variant === "reviewer") {
    return (
      <svg viewBox="0 0 48 52" xmlns="http://www.w3.org/2000/svg" className={className} aria-hidden="true">
        {/* hair */}
        <path d="M7 30 Q6 12 24 7 Q42 12 41 30 Q41 42 24 44 Q7 42 7 30Z" fill="#2a1a0a" />
        {/* face */}
        <ellipse {...face} />
        {/* bangs — side-parted */}
        <path d="M7 28 Q7 16 11 11 Q18 6 28 9 Q35 10 38 7 Q42 12 41 28" fill="#2a1a0a" />
        {/* side hair detail */}
        <path d="M7 30 Q8 38 10 42" stroke="#2a1a0a" strokeWidth="6" fill="none" strokeLinecap="round" />
        <Eye {...leftEye}  iris="#6b4a2a" />
        <Eye {...rightEye} iris="#6b4a2a" />
        {/* round glasses */}
        <circle cx="16" cy="27" r="8.5" fill="none" stroke="#555" strokeWidth="1.5" />
        <circle cx="32" cy="27" r="8.5" fill="none" stroke="#555" strokeWidth="1.5" />
        <line x1="24.5" y1="27" x2="23.5" y2="27" stroke="#555" strokeWidth="1.5" />
        <line x1="7.5"  y1="24" x2="7"    y2="24" stroke="#555" strokeWidth="1.5" />
        <line x1="40.5" y1="24" x2="41"   y2="24" stroke="#555" strokeWidth="1.5" />
        {/* glass tint */}
        <circle cx="16" cy="27" r="8" fill="#b8d4ff" opacity="0.15" />
        <circle cx="32" cy="27" r="8" fill="#b8d4ff" opacity="0.15" />
        {/* eyebrows — thoughtful */}
        <path d="M9 18 Q16 14 22 17" stroke="#2a1a0a" strokeWidth="1.8" fill="none" strokeLinecap="round" />
        <path d="M26 16 Q32 13 38 17" stroke="#2a1a0a" strokeWidth="1.8" fill="none" strokeLinecap="round" />
        {/* small thoughtful smile */}
        <path d="M20 38 Q24 41 28 38" stroke="#e06070" strokeWidth="1.8" fill="none" strokeLinecap="round" />
        {/* tiny notepad */}
        <rect x="33" y="38" width="10" height="12" rx="1.5" fill="white" stroke="#ccc" strokeWidth="1" />
        <line x1="35" y1="42" x2="41" y2="42" stroke="#aaa" strokeWidth="0.8" />
        <line x1="35" y1="44" x2="41" y2="44" stroke="#aaa" strokeWidth="0.8" />
        <line x1="35" y1="46" x2="39" y2="46" stroke="#aaa" strokeWidth="0.8" />
      </svg>
    );
  }

  if (variant === "foodie") {
    return (
      <svg viewBox="0 0 48 52" xmlns="http://www.w3.org/2000/svg" className={className} aria-hidden="true">
        {/* hair */}
        <path d="M7 30 Q6 12 24 7 Q42 12 41 30 Q41 42 24 44 Q7 42 7 30Z" fill="#8b1a1a" />
        {/* ahoge spike */}
        <path d="M24 7 Q28 -2 24 -5 Q20 -2 24 7" fill="#8b1a1a" />
        {/* face */}
        <ellipse {...face} />
        {/* bangs */}
        <path d="M7 29 Q7 20 12 15 Q17 11 22 14 Q23 17 22 21 Q24 18 24 17 Q24 18 26 21 Q25 17 26 14 Q31 11 36 15 Q41 20 41 29" fill="#8b1a1a" />
        {/* star eyes! */}
        <ellipse cx={leftEye.cx}  cy={leftEye.cy}  rx={7} ry={8.5} fill="white" />
        <ellipse cx={rightEye.cx} cy={rightEye.cy} rx={7} ry={8.5} fill="white" />
        {/* star iris left */}
        <path d={`M${leftEye.cx} ${leftEye.cy - 5} L${leftEye.cx + 1.5} ${leftEye.cy - 1.5} L${leftEye.cx + 5} ${leftEye.cy} L${leftEye.cx + 1.5} ${leftEye.cy + 1.5} L${leftEye.cx} ${leftEye.cy + 5} L${leftEye.cx - 1.5} ${leftEye.cy + 1.5} L${leftEye.cx - 5} ${leftEye.cy} L${leftEye.cx - 1.5} ${leftEye.cy - 1.5}Z`} fill="#FBBF24" />
        {/* star iris right */}
        <path d={`M${rightEye.cx} ${rightEye.cy - 5} L${rightEye.cx + 1.5} ${rightEye.cy - 1.5} L${rightEye.cx + 5} ${rightEye.cy} L${rightEye.cx + 1.5} ${rightEye.cy + 1.5} L${rightEye.cx} ${rightEye.cy + 5} L${rightEye.cx - 1.5} ${rightEye.cy + 1.5} L${rightEye.cx - 5} ${rightEye.cy} L${rightEye.cx - 1.5} ${rightEye.cy - 1.5}Z`} fill="#FBBF24" />
        {/* pupil center */}
        <circle cx={leftEye.cx}  cy={leftEye.cy}  r={2.5} fill="#0d1b35" />
        <circle cx={rightEye.cx} cy={rightEye.cy} r={2.5} fill="#0d1b35" />
        {/* lash lines */}
        <path d={`M9 18 Q16 13 23 18`}  stroke="#0d1b35" strokeWidth="2.5" fill="none" strokeLinecap="round" />
        <path d={`M25 18 Q32 13 39 18`} stroke="#0d1b35" strokeWidth="2.5" fill="none" strokeLinecap="round" />
        {/* eyebrows raised — excited */}
        <path d="M9 15 Q16 10 22 13"  stroke="#8b1a1a" strokeWidth="1.8" fill="none" strokeLinecap="round" />
        <path d="M26 13 Q32 10 39 15" stroke="#8b1a1a" strokeWidth="1.8" fill="none" strokeLinecap="round" />
        {/* big open smile */}
        <path d="M16 36 Q24 45 32 36" stroke="#e06070" strokeWidth="2.5" fill="#FFB0BE" opacity="0.6" strokeLinecap="round" />
        {/* sparkle dots */}
        <circle cx="6"  cy="12" r="1.5" fill="#FBBF24" opacity="0.8" />
        <circle cx="42" cy="12" r="1.5" fill="#FBBF24" opacity="0.8" />
        <circle cx="4"  cy="20" r="1"   fill="#FBBF24" opacity="0.6" />
        <circle cx="44" cy="20" r="1"   fill="#FBBF24" opacity="0.6" />
        {/* blush */}
        <ellipse cx="10" cy="34" rx="5" ry="3" fill="#FFB0BE" opacity="0.7" />
        <ellipse cx="38" cy="34" rx="5" ry="3" fill="#FFB0BE" opacity="0.7" />
      </svg>
    );
  }

  if (variant === "explorer") {
    return (
      <svg viewBox="0 0 48 52" xmlns="http://www.w3.org/2000/svg" className={className} aria-hidden="true">
        {/* hair */}
        <path d="M7 30 Q6 12 24 7 Q42 12 41 30 Q41 42 24 44 Q7 42 7 30Z" fill="#1a3a1a" />
        {/* face */}
        <ellipse {...face} />
        {/* bangs */}
        <path d="M7 28 Q8 18 14 13 Q19 9 24 11 Q29 9 34 13 Q40 18 41 28" fill="#1a3a1a" />
        {/* headband */}
        <rect x="6" y="18" width="36" height="5" rx="2.5" fill="#e05555" />
        {/* headband knot on side */}
        <ellipse cx="41" cy="20" rx="5" ry="4" fill="#e05555" />
        <path d="M38 17 Q41 14 44 17" stroke="#cc3333" strokeWidth="1.5" fill="none" />
        <path d="M38 23 Q41 26 44 23" stroke="#cc3333" strokeWidth="1.5" fill="none" />
        <Eye {...leftEye}  iris="#2d7a2d" />
        <Eye {...rightEye} iris="#2d7a2d" />
        {/* determined eyebrows */}
        <path d="M9 17 Q16 13 22 16"  stroke="#1a3a1a" strokeWidth="2" fill="none" strokeLinecap="round" />
        <path d="M26 16 Q32 13 39 17" stroke="#1a3a1a" strokeWidth="2" fill="none" strokeLinecap="round" />
        {/* confident smirk */}
        <path d="M18 38 Q24 43 32 39" stroke="#e06070" strokeWidth="2" fill="none" strokeLinecap="round" />
        {/* small compass icon */}
        <circle cx="10" cy="44" r="5" fill="none" stroke="#FBBF24" strokeWidth="1.2" />
        <line x1="10" y1="40" x2="10" y2="42" stroke="#e05555" strokeWidth="1.5" strokeLinecap="round" />
        <line x1="10" y1="46" x2="10" y2="48" stroke="#aaa"    strokeWidth="1.5" strokeLinecap="round" />
        <line x1="6"  y1="44" x2="8"  y2="44" stroke="#aaa"    strokeWidth="1.5" strokeLinecap="round" />
        <line x1="12" y1="44" x2="14" y2="44" stroke="#aaa"    strokeWidth="1.5" strokeLinecap="round" />
      </svg>
    );
  }

  // variant === "star" — for ratings
  return (
    <svg viewBox="0 0 48 52" xmlns="http://www.w3.org/2000/svg" className={className} aria-hidden="true">
      {/* hair */}
      <path d="M7 30 Q6 12 24 7 Q42 12 41 30 Q41 42 24 44 Q7 42 7 30Z" fill="#4a2080" />
      {/* face */}
      <ellipse {...face} />
      {/* bangs with twin tails hint */}
      <path d="M7 29 Q7 18 13 13 Q18 9 24 11 Q30 9 35 13 Q41 18 41 29" fill="#4a2080" />
      {/* twin-tail strands */}
      <path d="M7  30 Q4  40 8  48" stroke="#4a2080" strokeWidth="7" fill="none" strokeLinecap="round" />
      <path d="M41 30 Q44 40 40 48" stroke="#4a2080" strokeWidth="7" fill="none" strokeLinecap="round" />
      <Eye {...leftEye}  iris="#9b59d0" />
      <Eye {...rightEye} iris="#9b59d0" />
      {/* eyebrows */}
      <path d="M9 18 Q16 14 22 17"  stroke="#4a2080" strokeWidth="1.8" fill="none" strokeLinecap="round" />
      <path d="M26 17 Q32 14 39 18" stroke="#4a2080" strokeWidth="1.8" fill="none" strokeLinecap="round" />
      {/* smile */}
      <path d="M18 37 Q24 43 30 37" stroke="#e06070" strokeWidth="2" fill="none" strokeLinecap="round" />
      {/* blush */}
      <ellipse cx="10" cy="34" rx="5" ry="3" fill="#FFB0BE" opacity="0.55" />
      <ellipse cx="38" cy="34" rx="5" ry="3" fill="#FFB0BE" opacity="0.55" />
      {/* small star above head */}
      <path d="M24 2 L25.2 5.6 L29 5.6 L26 7.8 L27.2 11.4 L24 9.2 L20.8 11.4 L22 7.8 L19 5.6 L22.8 5.6Z"
            fill="#FBBF24" />
    </svg>
  );
}


// ─── Speech bubble ─────────────────────────────────────────────────────────────
export function SpeechBubble({ text, className }: { text: string; className?: string }) {
  return (
    <div className={`relative inline-block ${className ?? ""}`}>
      <div className="bg-white border border-gray-200 rounded-2xl rounded-bl-none px-3 py-1.5 text-xs font-semibold text-gray-800 shadow-sm whitespace-nowrap">
        {text}
      </div>
      <div className="absolute -bottom-2 left-3 w-0 h-0 border-l-8 border-r-0 border-t-8 border-l-transparent border-t-white" />
      <div
        className="absolute left-[11px] w-0 h-0 border-l-[7px] border-r-0 border-t-[7px] border-l-transparent border-t-gray-200"
        style={{ bottom: "-9px", zIndex: -1 }}
      />
    </div>
  );
}


// ─── Full-body mascot (homepage hero) ─────────────────────────────────────────
export function AniMascot({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 180 265"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      aria-label="Istanbul Restaurants mascot"
    >
      {/* hair back */}
      <path d="M30 120 Q26 48 90 16 Q154 48 150 120 Q150 165 120 177 Q90 183 60 177 Q30 165 30 120Z" fill="#1e1208" />

      {/* chef hat */}
      <rect x="46" y="10" width="88" height="48" rx="11" fill="white" />
      <ellipse cx="90" cy="12" rx="44" ry="14" fill="white" />
      <ellipse cx="90" cy="56" rx="55" ry="11" fill="#D8D8D8" />
      <rect x="46" y="48" width="88" height="9" rx="2" fill="#E8E8E8" />
      <line x1="62"  y1="10" x2="62"  y2="48" stroke="#F0F0F0" strokeWidth="1.5" />
      <line x1="90"  y1="10" x2="90"  y2="48" stroke="#F0F0F0" strokeWidth="1.5" />
      <line x1="118" y1="10" x2="118" y2="48" stroke="#F0F0F0" strokeWidth="1.5" />

      {/* face */}
      <ellipse cx="90" cy="124" rx="58" ry="63" fill="#FFE0C8" />

      {/* hair bangs */}
      <path d="M32 116 Q28 76 50 56 Q64 43 79 50 Q85 55 82 70 Q88 62 90 62 Q92 62 98 70 Q95 55 101 50 Q116 43 130 56 Q152 76 148 116" fill="#1e1208" />
      <path d="M30 120 Q32 140 37 152" stroke="#1e1208" strokeWidth="13" fill="none" strokeLinecap="round" />
      <path d="M150 120 Q148 140 143 152" stroke="#1e1208" strokeWidth="13" fill="none" strokeLinecap="round" />

      {/* left eye */}
      <ellipse cx="67" cy="119" rx="20" ry="23" fill="white" />
      <ellipse cx="67" cy="122" rx="16" ry="19" fill="#4a8de8" />
      <ellipse cx="67" cy="124" rx="10" ry="13" fill="#0d1b35" />
      <circle  cx="73" cy="114" r="5.5" fill="white" />
      <circle  cx="62" cy="121" r="2.5" fill="white" />
      <path d="M48 107 Q67 98 86 107" stroke="#0d1b35" strokeWidth="3.5" fill="none" strokeLinecap="round" />
      <path d="M49 133 Q67 139 85 133" stroke="#d4956a" strokeWidth="1" fill="none" strokeLinecap="round" opacity="0.45" />

      {/* right eye */}
      <ellipse cx="113" cy="119" rx="20" ry="23" fill="white" />
      <ellipse cx="113" cy="122" rx="16" ry="19" fill="#4a8de8" />
      <ellipse cx="113" cy="124" rx="10" ry="13" fill="#0d1b35" />
      <circle  cx="119" cy="114" r="5.5" fill="white" />
      <circle  cx="108" cy="121" r="2.5" fill="white" />
      <path d="M94 107 Q113 98 132 107" stroke="#0d1b35" strokeWidth="3.5" fill="none" strokeLinecap="round" />
      <path d="M95 133 Q113 139 131 133" stroke="#d4956a" strokeWidth="1" fill="none" strokeLinecap="round" opacity="0.45" />

      {/* eyebrows */}
      <path d="M50 101 Q67 93 84 99"   stroke="#1e1208" strokeWidth="3" fill="none" strokeLinecap="round" />
      <path d="M96 99  Q113 93 130 101" stroke="#1e1208" strokeWidth="3" fill="none" strokeLinecap="round" />

      {/* nose */}
      <path d="M87 143 Q90 148 93 143" stroke="#c47a52" strokeWidth="1.5" fill="none" strokeLinecap="round" />

      {/* mouth */}
      <path d="M79 156 Q90 168 101 156" stroke="#e06070" strokeWidth="2.5" fill="none" strokeLinecap="round" />

      {/* blush */}
      <ellipse cx="47" cy="144" rx="14" ry="8" fill="#FFB0BE" opacity="0.55" />
      <ellipse cx="133" cy="144" rx="14" ry="8" fill="#FFB0BE" opacity="0.55" />

      {/* neck */}
      <rect x="78" y="180" width="24" height="18" fill="#FFE0C8" />

      {/* body */}
      <path d="M8 265 L20 192 Q40 180 90 177 Q140 180 160 192 L172 265Z" fill="#111827" />

      {/* apron */}
      <path d="M67 185 Q90 178 113 185 L116 265 L64 265Z" fill="white" />

      {/* collar */}
      <path d="M73 180 L90 192 L107 180" stroke="white" strokeWidth="2.5" fill="none" strokeLinejoin="round" />

      {/* left arm */}
      <path d="M20 200 Q2 216 5 245" stroke="#111827" strokeWidth="23" fill="none" strokeLinecap="round" />
      <circle cx="5" cy="245" r="14" fill="#FFE0C8" />

      {/* right arm */}
      <path d="M160 200 Q178 214 175 242" stroke="#111827" strokeWidth="23" fill="none" strokeLinecap="round" />
      <circle cx="175" cy="242" r="14" fill="#FFE0C8" />

      {/* sparkles */}
      <g transform="translate(158,42)" opacity="0.8">
        <path d="M0-9 2-2 9 0 2 2 0 9-2 2-9 0-2-2Z" fill="#FBBF24" />
      </g>
      <g transform="translate(18,72)" opacity="0.65">
        <path d="M0-6 1.5-1.5 6 0 1.5 1.5 0 6-1.5 1.5-6 0-1.5-1.5Z" fill="#FBBF24" />
      </g>
      <circle cx="162" cy="68" r="2.5" fill="#FBBF24" opacity="0.7" />
      <circle cx="152" cy="80" r="1.5" fill="#FBBF24" opacity="0.5" />
      <circle cx="18"  cy="55" r="1.5" fill="#FBBF24" opacity="0.5" />
    </svg>
  );
}


// ─── Kawaii food icon characters for homepage cards ───────────────────────────
// variant: "romantic" | "fish" | "kebap" | "scenic" | "business" | "night" | "breakfast" | "finedining"
export function KawaiiIcon({
  variant = "romantic",
  className,
  style,
}: {
  variant?: "romantic" | "fish" | "kebap" | "scenic" | "business" | "night" | "breakfast" | "finedining";
  className?: string;
  style?: React.CSSProperties;
}) {
  if (variant === "romantic") {
    return (
      <svg viewBox="0 0 56 56" xmlns="http://www.w3.org/2000/svg" className={className} style={style} aria-hidden="true">
        <path d="M28 50 Q10 38 6 24 Q4 14 14 10 Q20 8 24 12 Q26 14 28 17 Q30 14 32 12 Q36 8 42 10 Q52 14 50 24 Q46 38 28 50Z" fill="#fb7185" />
        <circle cx="20" cy="26" r="6" fill="white" />
        <circle cx="20" cy="26" r="4.5" fill="#f43f5e" />
        <circle cx="20" cy="26.5" r="2.5" fill="#0d1b35" />
        <circle cx="22" cy="24" r="1.3" fill="white" />
        <circle cx="36" cy="26" r="6" fill="white" />
        <circle cx="36" cy="26" r="4.5" fill="#f43f5e" />
        <circle cx="36" cy="26.5" r="2.5" fill="#0d1b35" />
        <circle cx="38" cy="24" r="1.3" fill="white" />
        <ellipse cx="13" cy="32" rx="4" ry="2.5" fill="#FFB0BE" opacity="0.7" />
        <ellipse cx="43" cy="32" rx="4" ry="2.5" fill="#FFB0BE" opacity="0.7" />
        <path d="M22 36 Q28 42 34 36" stroke="#e05555" strokeWidth="2" fill="none" strokeLinecap="round" />
        <path d="M5 14 Q6.5 12 8 14 Q9.5 16 6.5 18 Q3.5 16 5 14Z" fill="#fda4af" />
        <path d="M47 10 Q48 8.5 49 10 Q50 11.5 48 13 Q46 11.5 47 10Z" fill="#fda4af" />
        <path d="M48 42 Q49 40.5 50 42 Q51 43.5 49 45 Q47 43.5 48 42Z" fill="#fda4af" opacity="0.7" />
      </svg>
    );
  }

  if (variant === "fish") {
    return (
      <svg viewBox="0 0 56 56" xmlns="http://www.w3.org/2000/svg" className={className} style={style} aria-hidden="true">
        {/* rice base */}
        <ellipse cx="28" cy="46" rx="22" ry="9" fill="white" stroke="#E5E7EB" strokeWidth="1" />
        <ellipse cx="28" cy="44" rx="20" ry="7" fill="white" />
        {/* salmon top */}
        <path d="M6 38 Q6 22 28 20 Q50 22 50 38 Q40 42 28 42 Q16 42 6 38Z" fill="#fda4af" />
        <path d="M12 24 Q28 18 44 24" stroke="#fb7185" strokeWidth="2" fill="none" opacity="0.5" />
        <path d="M10 30 Q28 24 46 30" stroke="#fb7185" strokeWidth="1.5" fill="none" opacity="0.4" />
        {/* cat ears */}
        <path d="M12 24 Q9 15 14 17 Q17 18 16 24" fill="#fda4af" />
        <path d="M44 24 Q47 15 42 17 Q39 18 40 24" fill="#fda4af" />
        <path d="M13 23 Q10.5 16 14 17.5 Q16 18 15.5 23" fill="#fb7185" opacity="0.5" />
        <path d="M43 23 Q45.5 16 42 17.5 Q40 18 40.5 23" fill="#fb7185" opacity="0.5" />
        {/* eyes */}
        <circle cx="22" cy="31" r="5.5" fill="white" />
        <circle cx="22" cy="31" r="4" fill="#4a8de8" />
        <circle cx="22" cy="31.5" r="2.3" fill="#0d1b35" />
        <circle cx="23.5" cy="29.5" r="1.2" fill="white" />
        <circle cx="34" cy="31" r="5.5" fill="white" />
        <circle cx="34" cy="31" r="4" fill="#4a8de8" />
        <circle cx="34" cy="31.5" r="2.3" fill="#0d1b35" />
        <circle cx="35.5" cy="29.5" r="1.2" fill="white" />
        <ellipse cx="15" cy="35" rx="3.5" ry="2" fill="#FFB0BE" opacity="0.7" />
        <ellipse cx="41" cy="35" rx="3.5" ry="2" fill="#FFB0BE" opacity="0.7" />
        <path d="M24 37 Q28 41 32 37" stroke="#e06070" strokeWidth="1.8" fill="none" strokeLinecap="round" />
        {/* wasabi accent */}
        <circle cx="49" cy="11" r="6" fill="#4ade80" />
        <circle cx="47" cy="9" r="2" fill="#86efac" opacity="0.6" />
        <circle cx="50" cy="13" r="1" fill="#86efac" opacity="0.5" />
      </svg>
    );
  }

  if (variant === "kebap") {
    return (
      <svg viewBox="0 0 56 56" xmlns="http://www.w3.org/2000/svg" className={className} style={style} aria-hidden="true">
        {/* flame glow */}
        <ellipse cx="28" cy="14" rx="14" ry="8" fill="#fbbf24" opacity="0.25" />
        {/* flame */}
        <path d="M28 4 Q32 10 36 8 Q34 16 38 18 Q36 26 28 28 Q20 26 18 18 Q22 16 20 8 Q24 10 28 4Z" fill="#f97316" />
        <path d="M28 8 Q30 12 33 11 Q31 17 33 19 Q31 24 28 25 Q25 24 23 19 Q25 17 23 11 Q26 12 28 8Z" fill="#fbbf24" />
        <path d="M28 14 Q29 17 31 16 Q30 20 28 21 Q26 20 25 16 Q27 17 28 14Z" fill="white" opacity="0.55" />
        {/* meat body */}
        <ellipse cx="28" cy="42" rx="20" ry="13" fill="#92400e" />
        <ellipse cx="28" cy="40" rx="19" ry="12" fill="#a16207" />
        <path d="M16 38 Q22 34 30 38" stroke="#78350f" strokeWidth="2.5" fill="none" strokeLinecap="round" />
        <path d="M20 44 Q26 40 34 44" stroke="#78350f" strokeWidth="2.5" fill="none" strokeLinecap="round" />
        {/* eyes */}
        <circle cx="22" cy="39" r="5.5" fill="white" />
        <circle cx="22" cy="39" r="4" fill="#451a03" />
        <circle cx="22" cy="39.5" r="2.3" fill="#0d1b35" />
        <circle cx="23.5" cy="37.5" r="1.2" fill="white" />
        <circle cx="34" cy="39" r="5.5" fill="white" />
        <circle cx="34" cy="39" r="4" fill="#451a03" />
        <circle cx="34" cy="39.5" r="2.3" fill="#0d1b35" />
        <circle cx="35.5" cy="37.5" r="1.2" fill="white" />
        <path d="M17 33 Q22 30 27 32" stroke="#78350f" strokeWidth="2" fill="none" strokeLinecap="round" />
        <path d="M29 32 Q34 30 39 33" stroke="#78350f" strokeWidth="2" fill="none" strokeLinecap="round" />
        <path d="M22 48 Q28 53 34 48" stroke="#c2410c" strokeWidth="2" fill="none" strokeLinecap="round" />
        <ellipse cx="14" cy="43" rx="3.5" ry="2" fill="#FFB0BE" opacity="0.5" />
        <ellipse cx="42" cy="43" rx="3.5" ry="2" fill="#FFB0BE" opacity="0.5" />
      </svg>
    );
  }

  if (variant === "scenic") {
    return (
      <svg viewBox="0 0 56 56" xmlns="http://www.w3.org/2000/svg" className={className} style={style} aria-hidden="true">
        {/* water body */}
        <ellipse cx="28" cy="36" rx="22" ry="20" fill="#38bdf8" />
        {/* sky */}
        <path d="M6 36 Q6 14 28 10 Q50 14 50 36" fill="#7dd3fc" />
        {/* wave */}
        <path d="M8 36 Q14 31 20 36 Q26 41 32 36 Q38 31 48 36" stroke="white" strokeWidth="1.5" fill="none" opacity="0.6" />
        {/* bridge */}
        <path d="M10 26 Q28 18 46 26" stroke="white" strokeWidth="2" fill="none" opacity="0.7" />
        <line x1="18" y1="26" x2="18" y2="20" stroke="white" strokeWidth="1.5" opacity="0.7" />
        <line x1="38" y1="26" x2="38" y2="20" stroke="white" strokeWidth="1.5" opacity="0.7" />
        {/* sparkle eyes */}
        <circle cx="22" cy="32" r="6" fill="white" />
        <circle cx="22" cy="32" r="4.5" fill="#0284c7" />
        <circle cx="22" cy="32.5" r="2.5" fill="#0d1b35" />
        <circle cx="24" cy="30" r="1.5" fill="white" />
        <circle cx="20.5" cy="33" r="0.8" fill="white" />
        <circle cx="34" cy="32" r="6" fill="white" />
        <circle cx="34" cy="32" r="4.5" fill="#0284c7" />
        <circle cx="34" cy="32.5" r="2.5" fill="#0d1b35" />
        <circle cx="36" cy="30" r="1.5" fill="white" />
        <circle cx="32.5" cy="33" r="0.8" fill="white" />
        <ellipse cx="14" cy="37" rx="4" ry="2.5" fill="#bae6fd" opacity="0.8" />
        <ellipse cx="42" cy="37" rx="4" ry="2.5" fill="#bae6fd" opacity="0.8" />
        <path d="M22 41 Q28 46 34 41" stroke="#0369a1" strokeWidth="2" fill="none" strokeLinecap="round" />
        <path d="M4 18 L4.8 15.5 L5.6 18 L8 18.8 L5.6 19.6 L4.8 22 L4 19.6 L1.5 18.8Z" fill="#FBBF24" opacity="0.8" />
        <path d="M50 12 L50.6 10.2 L51.2 12 L53 12.6 L51.2 13.2 L50.6 15 L50 13.2 L48.2 12.6Z" fill="#FBBF24" opacity="0.7" />
        <circle cx="46" cy="20" r="1.5" fill="#FBBF24" opacity="0.7" />
      </svg>
    );
  }

  if (variant === "business") {
    return (
      <svg viewBox="0 0 56 56" xmlns="http://www.w3.org/2000/svg" className={className} style={style} aria-hidden="true">
        {/* cup body */}
        <path d="M10 22 L14 52 Q14 54 28 54 Q42 54 42 52 L46 22Z" fill="#b45309" />
        <ellipse cx="28" cy="22" rx="18" ry="6" fill="#92400e" />
        {/* cream top */}
        <ellipse cx="28" cy="20" rx="18" ry="6" fill="#fef3c7" />
        <path d="M12 20 Q28 14 44 20" fill="#fef9ee" />
        {/* steam */}
        <path d="M20 12 Q21 8 20 4" stroke="#9ca3af" strokeWidth="2" fill="none" strokeLinecap="round" />
        <path d="M28 10 Q29 6 28 2" stroke="#9ca3af" strokeWidth="2" fill="none" strokeLinecap="round" />
        <path d="M36 12 Q37 8 36 4" stroke="#9ca3af" strokeWidth="2" fill="none" strokeLinecap="round" />
        {/* handle */}
        <path d="M42 28 Q52 28 52 38 Q52 48 42 48" stroke="#78350f" strokeWidth="4" fill="none" strokeLinecap="round" />
        {/* face */}
        <circle cx="22" cy="36" r="5.5" fill="white" />
        <circle cx="22" cy="36" r="4" fill="#92400e" />
        <circle cx="22" cy="36.5" r="2.3" fill="#0d1b35" />
        <circle cx="23.5" cy="34.5" r="1.2" fill="white" />
        <circle cx="34" cy="36" r="5.5" fill="white" />
        <circle cx="34" cy="36" r="4" fill="#92400e" />
        <circle cx="34" cy="36.5" r="2.3" fill="#0d1b35" />
        <circle cx="35.5" cy="34.5" r="1.2" fill="white" />
        {/* glasses */}
        <circle cx="22" cy="36" r="6.5" fill="none" stroke="#555" strokeWidth="1.2" />
        <circle cx="34" cy="36" r="6.5" fill="none" stroke="#555" strokeWidth="1.2" />
        <line x1="28.5" y1="36" x2="27.5" y2="36" stroke="#555" strokeWidth="1.2" />
        <circle cx="22" cy="36" r="6" fill="#b8d4ff" opacity="0.1" />
        <circle cx="34" cy="36" r="6" fill="#b8d4ff" opacity="0.1" />
        <path d="M23 45 Q28 49 33 45" stroke="#78350f" strokeWidth="1.8" fill="none" strokeLinecap="round" />
        {/* tie */}
        <path d="M28 20 L26 28 L28 34 L30 28Z" fill="#e05555" />
      </svg>
    );
  }

  if (variant === "night") {
    return (
      <svg viewBox="0 0 56 56" xmlns="http://www.w3.org/2000/svg" className={className} style={style} aria-hidden="true">
        {/* dark circle bg */}
        <circle cx="28" cy="28" r="26" fill="#1e1b4b" />
        {/* crescent moon */}
        <path d="M14 14 Q28 6 40 14 Q50 22 48 36 Q44 50 28 52 Q12 50 8 36 Q6 22 14 14Z" fill="#fbbf24" />
        <path d="M28 10 Q42 14 44 28 Q44 44 28 50 Q14 46 11 32 Q10 18 24 11 Q26 10.5 28 10Z" fill="#1e1b4b" />
        {/* cat ears */}
        <path d="M16 22 Q13 14 18 16 Q21 17 20 22" fill="#fbbf24" />
        <path d="M16 22 Q14 16 18 17 Q20 18 19.5 22" fill="#f59e0b" opacity="0.6" />
        {/* sleepy eyes */}
        <path d="M19 30 Q22 27 25 30" stroke="#1e1b4b" strokeWidth="2.5" fill="none" strokeLinecap="round" />
        <circle cx="22" cy="31" r="1.2" fill="#1e1b4b" />
        <path d="M30 28 Q33 25 36 28" stroke="#1e1b4b" strokeWidth="2.5" fill="none" strokeLinecap="round" />
        <circle cx="33" cy="29" r="1.2" fill="#1e1b4b" />
        <ellipse cx="17" cy="35" rx="3.5" ry="2" fill="#fda4af" opacity="0.6" />
        <ellipse cx="37" cy="33" rx="3.5" ry="2" fill="#fda4af" opacity="0.6" />
        <path d="M24 38 Q28 42 32 38" stroke="#92400e" strokeWidth="1.8" fill="none" strokeLinecap="round" />
        {/* stars */}
        <circle cx="8" cy="12" r="1.5" fill="white" />
        <circle cx="48" cy="8" r="1" fill="white" />
        <circle cx="50" cy="20" r="1.5" fill="white" />
        <circle cx="6" cy="28" r="1" fill="white" />
        <path d="M44 43 L44.6 41.4 L45.2 43 L46.8 43.6 L45.2 44.2 L44.6 45.8 L44 44.2 L42.4 43.6Z" fill="white" opacity="0.8" />
        <path d="M4 42 L4.4 40.8 L4.8 42 L6 42.4 L4.8 42.8 L4.4 44 L4 42.8 L2.8 42.4Z" fill="white" opacity="0.6" />
      </svg>
    );
  }

  if (variant === "breakfast") {
    return (
      <svg viewBox="0 0 56 56" xmlns="http://www.w3.org/2000/svg" className={className} style={style} aria-hidden="true">
        {/* egg white */}
        <ellipse cx="28" cy="38" rx="24" ry="17" fill="white" stroke="#F3F4F6" strokeWidth="1" />
        {/* yolk */}
        <circle cx="28" cy="30" r="15" fill="#fbbf24" />
        <circle cx="22" cy="26" r="5" fill="#fde68a" opacity="0.5" />
        {/* steam */}
        <path d="M20 12 Q21 8 20 4" stroke="#d1d5db" strokeWidth="2" fill="none" strokeLinecap="round" />
        <path d="M28 10 Q29 6 28 2" stroke="#d1d5db" strokeWidth="2" fill="none" strokeLinecap="round" />
        <path d="M36 12 Q37 8 36 4" stroke="#d1d5db" strokeWidth="2" fill="none" strokeLinecap="round" />
        {/* eyes */}
        <circle cx="23" cy="29" r="5.5" fill="white" />
        <circle cx="23" cy="29" r="4" fill="#d97706" />
        <circle cx="23" cy="29.5" r="2.3" fill="#0d1b35" />
        <circle cx="24.5" cy="27.5" r="1.2" fill="white" />
        <circle cx="33" cy="29" r="5.5" fill="white" />
        <circle cx="33" cy="29" r="4" fill="#d97706" />
        <circle cx="33" cy="29.5" r="2.3" fill="#0d1b35" />
        <circle cx="34.5" cy="27.5" r="1.2" fill="white" />
        {/* happy brows */}
        <path d="M18 23 Q23 20 28 22" stroke="#d97706" strokeWidth="1.5" fill="none" strokeLinecap="round" />
        <path d="M28 22 Q33 20 38 23" stroke="#d97706" strokeWidth="1.5" fill="none" strokeLinecap="round" />
        <path d="M21 37 Q28 44 35 37" stroke="#c2410c" strokeWidth="2" fill="#fde68a" opacity="0.35" strokeLinecap="round" />
        <ellipse cx="16" cy="33" rx="4" ry="2.5" fill="#FFB0BE" opacity="0.6" />
        <ellipse cx="40" cy="33" rx="4" ry="2.5" fill="#FFB0BE" opacity="0.6" />
        {/* sun sparkle */}
        <path d="M4 10 L5 8 L6 10 L8 11 L6 12 L5 14 L4 12 L2 11Z" fill="#fbbf24" opacity="0.7" />
        <circle cx="50" cy="14" r="3" fill="#fbbf24" opacity="0.5" />
      </svg>
    );
  }

  // finedining
  return (
    <svg viewBox="0 0 56 56" xmlns="http://www.w3.org/2000/svg" className={className} style={style} aria-hidden="true">
      {/* plate */}
      <ellipse cx="28" cy="52" rx="24" ry="4.5" fill="#E5E7EB" />
      <ellipse cx="28" cy="51" rx="22" ry="3.5" fill="#F9FAFB" />
      {/* dome */}
      <path d="M6 46 Q6 20 28 16 Q50 20 50 46Z" fill="#d1d5db" />
      <path d="M8 46 Q8 22 28 18 Q48 22 48 46Z" fill="#e5e7eb" />
      {/* shine */}
      <path d="M14 30 Q20 22 30 20" stroke="white" strokeWidth="2.5" fill="none" strokeLinecap="round" opacity="0.7" />
      {/* knob */}
      <ellipse cx="28" cy="16" rx="5" ry="3" fill="#9ca3af" />
      <ellipse cx="28" cy="14" rx="4" ry="2.5" fill="#d1d5db" />
      {/* face */}
      <circle cx="22" cy="35" r="5.5" fill="white" />
      <circle cx="22" cy="35" r="4" fill="#6b7280" />
      <circle cx="22" cy="35.5" r="2.3" fill="#0d1b35" />
      <circle cx="23.5" cy="33.5" r="1.2" fill="white" />
      <circle cx="34" cy="35" r="5.5" fill="white" />
      <circle cx="34" cy="35" r="4" fill="#6b7280" />
      <circle cx="34" cy="35.5" r="2.3" fill="#0d1b35" />
      <circle cx="35.5" cy="33.5" r="1.2" fill="white" />
      {/* elegant brows */}
      <path d="M17 29 Q22 25 27 27" stroke="#374151" strokeWidth="1.5" fill="none" strokeLinecap="round" />
      <path d="M29 27 Q34 25 39 29" stroke="#374151" strokeWidth="1.5" fill="none" strokeLinecap="round" />
      <path d="M24 43 Q28 46 32 43" stroke="#374151" strokeWidth="1.8" fill="none" strokeLinecap="round" />
      {/* sparkles */}
      <path d="M2 32 L2.8 29.5 L3.6 32 L6 32.8 L3.6 33.6 L2.8 36 L2 33.6 L-0.5 32.8Z" fill="#FBBF24" opacity="0.8" />
      <path d="M50 26 L50.8 23.5 L51.6 26 L54 26.8 L51.6 27.6 L50.8 30 L50 27.6 L47.5 26.8Z" fill="#FBBF24" opacity="0.8" />
      <circle cx="46" cy="18" r="2" fill="#FBBF24" opacity="0.6" />
      <circle cx="10" cy="22" r="1.5" fill="#FBBF24" opacity="0.5" />
    </svg>
  );
}


// ─── Full-body chibi characters for collection cards ──────────────────────────
export function AniChibi({
  variant = "chef",
  className,
}: {
  variant?: "chef" | "reviewer" | "foodie" | "explorer" | "star";
  className?: string;
}) {
  if (variant === "chef") {
    return (
      <svg viewBox="0 0 60 82" xmlns="http://www.w3.org/2000/svg" className={className} aria-hidden="true">
        <rect x="18" y="2" width="24" height="11" rx="3" fill="white" />
        <ellipse cx="30" cy="2" rx="12" ry="3.5" fill="white" />
        <ellipse cx="30" cy="12" rx="16" ry="3.5" fill="#D8D8D8" />
        <path d="M10 26 Q9 12 30 7 Q51 12 50 26 Q50 38 30 40 Q10 38 10 26Z" fill="#1e1208" />
        <ellipse cx="30" cy="23" rx="13" ry="15" fill="#FFE0C8" />
        <path d="M17 24 Q17 17 20 13 Q24 9 27 11 Q28 13 27 16 Q29 13 30 13 Q31 13 33 16 Q32 13 33 11 Q36 9 40 13 Q43 17 43 24" fill="#1e1208" />
        <ellipse cx="22" cy="20" rx="5" ry="6" fill="white" />
        <ellipse cx="22" cy="21" rx="3.8" ry="5" fill="#4a8de8" />
        <ellipse cx="22" cy="22" rx="2.2" ry="3.2" fill="#0d1b35" />
        <circle cx="24" cy="18" r="1.6" fill="white" />
        <path d="M17 14 Q22 11 27 14" stroke="#0d1b35" strokeWidth="1.8" fill="none" strokeLinecap="round" />
        <ellipse cx="38" cy="20" rx="5" ry="6" fill="white" />
        <ellipse cx="38" cy="21" rx="3.8" ry="5" fill="#4a8de8" />
        <ellipse cx="38" cy="22" rx="2.2" ry="3.2" fill="#0d1b35" />
        <circle cx="40" cy="18" r="1.6" fill="white" />
        <path d="M33 14 Q38 11 43 14" stroke="#0d1b35" strokeWidth="1.8" fill="none" strokeLinecap="round" />
        <path d="M17 13 Q22 10 27 12" stroke="#1e1208" strokeWidth="1.4" fill="none" strokeLinecap="round" />
        <path d="M33 12 Q38 10 43 13" stroke="#1e1208" strokeWidth="1.4" fill="none" strokeLinecap="round" />
        <path d="M24 30 Q30 35 36 30" stroke="#e06070" strokeWidth="1.8" fill="none" strokeLinecap="round" />
        <ellipse cx="12" cy="26" rx="4" ry="2.5" fill="#FFB0BE" opacity="0.55" />
        <ellipse cx="48" cy="26" rx="4" ry="2.5" fill="#FFB0BE" opacity="0.55" />
        <rect x="26" y="37" width="8" height="5" fill="#FFE0C8" />
        <path d="M5 82 L10 44 Q18 38 30 36 Q42 38 50 44 L55 82Z" fill="#111827" />
        <path d="M20 40 Q30 36 40 40 L42 82 L18 82Z" fill="white" />
        <path d="M26 40 L30 46 L34 40" stroke="white" strokeWidth="2" fill="none" />
        <path d="M10 46 Q2 52 3 62" stroke="#111827" strokeWidth="8" fill="none" strokeLinecap="round" />
        <circle cx="3" cy="62" r="5" fill="#FFE0C8" />
        <path d="M50 46 Q58 52 57 61" stroke="#111827" strokeWidth="8" fill="none" strokeLinecap="round" />
        <circle cx="57" cy="61" r="5" fill="#FFE0C8" />
        <line x1="57" y1="56" x2="57" y2="46" stroke="#FBBF24" strokeWidth="2.5" strokeLinecap="round" />
        <ellipse cx="57" cy="45" rx="3" ry="2" fill="#FBBF24" />
      </svg>
    );
  }

  if (variant === "reviewer") {
    return (
      <svg viewBox="0 0 60 82" xmlns="http://www.w3.org/2000/svg" className={className} aria-hidden="true">
        <path d="M10 26 Q9 12 30 7 Q51 12 50 26 Q50 38 30 40 Q10 38 10 26Z" fill="#2a1a0a" />
        <ellipse cx="30" cy="23" rx="13" ry="15" fill="#FFE0C8" />
        <path d="M10 25 Q10 15 13 10 Q18 6 25 8 Q27 10 26 14 Q28 11 30 11 Q35 9 40 12 Q46 16 50 25" fill="#2a1a0a" />
        <path d="M10 26 Q11 33 12 38" stroke="#2a1a0a" strokeWidth="5" fill="none" strokeLinecap="round" />
        <ellipse cx="22" cy="20" rx="5" ry="6" fill="white" />
        <ellipse cx="22" cy="21" rx="3.8" ry="5" fill="#6b4a2a" />
        <ellipse cx="22" cy="22" rx="2.2" ry="3.2" fill="#0d1b35" />
        <circle cx="24" cy="18" r="1.6" fill="white" />
        <path d="M17 14 Q22 11 27 14" stroke="#0d1b35" strokeWidth="1.8" fill="none" strokeLinecap="round" />
        <ellipse cx="38" cy="20" rx="5" ry="6" fill="white" />
        <ellipse cx="38" cy="21" rx="3.8" ry="5" fill="#6b4a2a" />
        <ellipse cx="38" cy="22" rx="2.2" ry="3.2" fill="#0d1b35" />
        <circle cx="40" cy="18" r="1.6" fill="white" />
        <path d="M33 14 Q38 11 43 14" stroke="#0d1b35" strokeWidth="1.8" fill="none" strokeLinecap="round" />
        <circle cx="22" cy="20" r="7" fill="none" stroke="#555" strokeWidth="1.3" />
        <circle cx="38" cy="20" r="7" fill="none" stroke="#555" strokeWidth="1.3" />
        <line x1="29" y1="20" x2="31" y2="20" stroke="#555" strokeWidth="1.3" />
        <line x1="10" y1="18" x2="15" y2="18" stroke="#555" strokeWidth="1.3" />
        <line x1="45" y1="18" x2="50" y2="18" stroke="#555" strokeWidth="1.3" />
        <circle cx="22" cy="20" r="6.5" fill="#b8d4ff" opacity="0.12" />
        <circle cx="38" cy="20" r="6.5" fill="#b8d4ff" opacity="0.12" />
        <path d="M16 12 Q22 9 27 11" stroke="#2a1a0a" strokeWidth="1.4" fill="none" strokeLinecap="round" />
        <path d="M33 11 Q38 9 44 12" stroke="#2a1a0a" strokeWidth="1.4" fill="none" strokeLinecap="round" />
        <path d="M25 30 Q30 34 35 30" stroke="#e06070" strokeWidth="1.6" fill="none" strokeLinecap="round" />
        <rect x="26" y="37" width="8" height="5" fill="#FFE0C8" />
        <path d="M5 82 L10 44 Q18 38 30 36 Q42 38 50 44 L55 82Z" fill="#1e3a5f" />
        <path d="M24 40 L30 46 L36 40 L34 82 L26 82Z" fill="white" />
        <path d="M30 44 L28 53 L30 61 L32 53Z" fill="#e05555" />
        <path d="M24 40 L17 51 L26 51" fill="#162d47" />
        <path d="M36 40 L43 51 L34 51" fill="#162d47" />
        <path d="M10 46 Q2 52 3 62" stroke="#1e3a5f" strokeWidth="8" fill="none" strokeLinecap="round" />
        <circle cx="3" cy="62" r="5" fill="#FFE0C8" />
        <path d="M50 46 Q58 50 58 60" stroke="#1e3a5f" strokeWidth="8" fill="none" strokeLinecap="round" />
        <circle cx="58" cy="60" r="5" fill="#FFE0C8" />
        <rect x="52" y="49" width="11" height="14" rx="1.5" fill="white" stroke="#ccc" strokeWidth="1" />
        <line x1="54" y1="53" x2="61" y2="53" stroke="#aaa" strokeWidth="0.8" />
        <line x1="54" y1="55.5" x2="61" y2="55.5" stroke="#aaa" strokeWidth="0.8" />
        <line x1="54" y1="58" x2="59" y2="58" stroke="#aaa" strokeWidth="0.8" />
      </svg>
    );
  }

  if (variant === "foodie") {
    return (
      <svg viewBox="0 0 60 82" xmlns="http://www.w3.org/2000/svg" className={className} aria-hidden="true">
        <path d="M10 26 Q9 12 30 7 Q51 12 50 26 Q50 38 30 40 Q10 38 10 26Z" fill="#8b1a1a" />
        <path d="M30 7 Q33 0 30 -2 Q27 0 30 7" fill="#8b1a1a" />
        <ellipse cx="30" cy="23" rx="13" ry="15" fill="#FFE0C8" />
        <path d="M17 24 Q17 17 20 13 Q24 9 27 11 Q28 13 27 16 Q29 13 30 13 Q31 13 33 16 Q32 13 33 11 Q36 9 40 13 Q43 17 43 24" fill="#8b1a1a" />
        <ellipse cx="22" cy="20" rx="5" ry="6" fill="white" />
        <ellipse cx="38" cy="20" rx="5" ry="6" fill="white" />
        <path d="M22 14 L23.1 17.3 L26.5 17.3 L23.8 19.3 L24.9 22.5 L22 20.5 L19.1 22.5 L20.2 19.3 L17.5 17.3 L20.9 17.3Z" fill="#FBBF24" />
        <path d="M38 14 L39.1 17.3 L42.5 17.3 L39.8 19.3 L40.9 22.5 L38 20.5 L35.1 22.5 L36.2 19.3 L33.5 17.3 L36.9 17.3Z" fill="#FBBF24" />
        <circle cx="22" cy="19" r="2" fill="#0d1b35" />
        <circle cx="38" cy="19" r="2" fill="#0d1b35" />
        <path d="M17 14 Q22 11 27 14" stroke="#0d1b35" strokeWidth="1.8" fill="none" strokeLinecap="round" />
        <path d="M33 14 Q38 11 43 14" stroke="#0d1b35" strokeWidth="1.8" fill="none" strokeLinecap="round" />
        <path d="M17 11 Q22 8 27 10" stroke="#8b1a1a" strokeWidth="1.4" fill="none" strokeLinecap="round" />
        <path d="M33 10 Q38 8 43 11" stroke="#8b1a1a" strokeWidth="1.4" fill="none" strokeLinecap="round" />
        <path d="M22 29 Q30 37 38 29" stroke="#e06070" strokeWidth="2" fill="#FFB0BE" opacity="0.5" strokeLinecap="round" />
        <ellipse cx="12" cy="26" rx="4" ry="2.5" fill="#FFB0BE" opacity="0.7" />
        <ellipse cx="48" cy="26" rx="4" ry="2.5" fill="#FFB0BE" opacity="0.7" />
        <circle cx="7" cy="10" r="1.3" fill="#FBBF24" opacity="0.8" />
        <circle cx="53" cy="10" r="1.3" fill="#FBBF24" opacity="0.8" />
        <rect x="26" y="37" width="8" height="5" fill="#FFE0C8" />
        <path d="M5 82 L10 44 Q18 38 30 36 Q42 38 50 44 L55 82Z" fill="#f59e0b" />
        <path d="M21 60 Q30 57 39 60 L39 72 Q30 75 21 72Z" fill="#d97706" />
        <path d="M26 40 L30 46 L34 40" stroke="#d97706" strokeWidth="3" fill="none" />
        <path d="M10 46 Q2 52 3 62" stroke="#f59e0b" strokeWidth="8" fill="none" strokeLinecap="round" />
        <circle cx="3" cy="62" r="5" fill="#FFE0C8" />
        <path d="M50 46 Q58 52 57 62" stroke="#f59e0b" strokeWidth="8" fill="none" strokeLinecap="round" />
        <circle cx="57" cy="62" r="5" fill="#FFE0C8" />
        <ellipse cx="57" cy="56" rx="6" ry="3.5" fill="white" stroke="#ddd" strokeWidth="1" />
        <ellipse cx="57" cy="57" rx="5" ry="2" fill="#fde68a" />
        <path d="M53 50 Q54 47 53 44" stroke="#aaa" strokeWidth="1.2" fill="none" strokeLinecap="round" />
        <path d="M57 49 Q58 46 57 43" stroke="#aaa" strokeWidth="1.2" fill="none" strokeLinecap="round" />
      </svg>
    );
  }

  if (variant === "explorer") {
    return (
      <svg viewBox="0 0 60 82" xmlns="http://www.w3.org/2000/svg" className={className} aria-hidden="true">
        <path d="M10 26 Q9 12 30 7 Q51 12 50 26 Q50 38 30 40 Q10 38 10 26Z" fill="#1a3a1a" />
        <ellipse cx="30" cy="23" rx="13" ry="15" fill="#FFE0C8" />
        <path d="M10 25 Q11 16 16 11 Q21 7 27 9 Q29 11 28 15 Q30 12 30 12 Q32 12 32 15 Q31 11 33 9 Q39 7 44 11 Q49 16 50 25" fill="#1a3a1a" />
        <rect x="9" y="16" width="42" height="4.5" rx="2.2" fill="#e05555" />
        <ellipse cx="50" cy="18" rx="5" ry="3.5" fill="#e05555" />
        <path d="M47 15 Q50 12 53 15" stroke="#cc3333" strokeWidth="1.2" fill="none" />
        <path d="M47 21 Q50 24 53 21" stroke="#cc3333" strokeWidth="1.2" fill="none" />
        <ellipse cx="22" cy="21" rx="5" ry="6" fill="white" />
        <ellipse cx="22" cy="22" rx="3.8" ry="5" fill="#2d7a2d" />
        <ellipse cx="22" cy="23" rx="2.2" ry="3.2" fill="#0d1b35" />
        <circle cx="24" cy="19" r="1.6" fill="white" />
        <path d="M17 15 Q22 12 27 15" stroke="#0d1b35" strokeWidth="1.8" fill="none" strokeLinecap="round" />
        <ellipse cx="38" cy="21" rx="5" ry="6" fill="white" />
        <ellipse cx="38" cy="22" rx="3.8" ry="5" fill="#2d7a2d" />
        <ellipse cx="38" cy="23" rx="2.2" ry="3.2" fill="#0d1b35" />
        <circle cx="40" cy="19" r="1.6" fill="white" />
        <path d="M33 15 Q38 12 43 15" stroke="#0d1b35" strokeWidth="1.8" fill="none" strokeLinecap="round" />
        <path d="M16 13 Q22 10 27 12" stroke="#1a3a1a" strokeWidth="1.6" fill="none" strokeLinecap="round" />
        <path d="M33 12 Q38 10 44 13" stroke="#1a3a1a" strokeWidth="1.6" fill="none" strokeLinecap="round" />
        <path d="M24 31 Q30 36 37 32" stroke="#e06070" strokeWidth="1.8" fill="none" strokeLinecap="round" />
        <rect x="26" y="37" width="8" height="5" fill="#FFE0C8" />
        <path d="M5 82 L10 44 Q18 38 30 36 Q42 38 50 44 L55 82Z" fill="#78716c" />
        <path d="M24 40 L30 46 L36 40 L34 82 L26 82Z" fill="#16a34a" />
        <path d="M24 40 L16 52 L27 52" fill="#6b6560" />
        <path d="M36 40 L44 52 L33 52" fill="#6b6560" />
        <path d="M10 46 Q2 52 3 62" stroke="#78716c" strokeWidth="8" fill="none" strokeLinecap="round" />
        <circle cx="3" cy="62" r="5" fill="#FFE0C8" />
        <path d="M50 46 Q58 52 57 62" stroke="#78716c" strokeWidth="8" fill="none" strokeLinecap="round" />
        <circle cx="57" cy="62" r="5" fill="#FFE0C8" />
        <rect x="51" y="49" width="11" height="9" rx="1" fill="#fef3c7" stroke="#d97706" strokeWidth="0.8" />
        <line x1="55" y1="49" x2="55" y2="58" stroke="#d97706" strokeWidth="0.6" />
        <path d="M53 53 Q55 51 57 53 Q59 55 57 57 Q55 59 53 57 Q51 55 53 53Z" stroke="#e05555" strokeWidth="0.8" fill="none" />
        <circle cx="48" cy="5" r="1.2" fill="#FBBF24" opacity="0.7" />
        <circle cx="7" cy="8" r="1.1" fill="#FBBF24" opacity="0.6" />
      </svg>
    );
  }

  // variant === "star"
  return (
    <svg viewBox="0 0 60 82" xmlns="http://www.w3.org/2000/svg" className={className} aria-hidden="true">
      <path d="M10 26 Q9 12 30 7 Q51 12 50 26 Q50 38 30 40 Q10 38 10 26Z" fill="#4a2080" />
      <path d="M10 26 Q7 38 9 50" stroke="#4a2080" strokeWidth="8" fill="none" strokeLinecap="round" />
      <path d="M50 26 Q53 38 51 50" stroke="#4a2080" strokeWidth="8" fill="none" strokeLinecap="round" />
      <path d="M30 2 L31.5 5.5 L35.5 5.5 L32.5 7.8 L33.8 11.5 L30 9.2 L26.2 11.5 L27.5 7.8 L24.5 5.5 L28.5 5.5Z" fill="#FBBF24" />
      <ellipse cx="30" cy="23" rx="13" ry="15" fill="#FFE0C8" />
      <path d="M17 24 Q17 17 20 13 Q24 9 27 11 Q28 13 27 16 Q29 13 30 13 Q31 13 33 16 Q32 13 33 11 Q36 9 40 13 Q43 17 43 24" fill="#4a2080" />
      <ellipse cx="22" cy="20" rx="5" ry="6" fill="white" />
      <ellipse cx="22" cy="21" rx="3.8" ry="5" fill="#9b59d0" />
      <ellipse cx="22" cy="22" rx="2.2" ry="3.2" fill="#0d1b35" />
      <circle cx="24" cy="18" r="1.6" fill="white" />
      <circle cx="20" cy="21" r="0.9" fill="white" />
      <path d="M17 14 Q22 11 27 14" stroke="#0d1b35" strokeWidth="1.8" fill="none" strokeLinecap="round" />
      <ellipse cx="38" cy="20" rx="5" ry="6" fill="white" />
      <ellipse cx="38" cy="21" rx="3.8" ry="5" fill="#9b59d0" />
      <ellipse cx="38" cy="22" rx="2.2" ry="3.2" fill="#0d1b35" />
      <circle cx="40" cy="18" r="1.6" fill="white" />
      <circle cx="36" cy="21" r="0.9" fill="white" />
      <path d="M33 14 Q38 11 43 14" stroke="#0d1b35" strokeWidth="1.8" fill="none" strokeLinecap="round" />
      <path d="M16 12 Q22 9 27 11" stroke="#4a2080" strokeWidth="1.4" fill="none" strokeLinecap="round" />
      <path d="M33 11 Q38 9 44 12" stroke="#4a2080" strokeWidth="1.4" fill="none" strokeLinecap="round" />
      <path d="M24 30 Q30 35 36 30" stroke="#e06070" strokeWidth="1.8" fill="none" strokeLinecap="round" />
      <ellipse cx="12" cy="26" rx="4" ry="2.5" fill="#FFB0BE" opacity="0.55" />
      <ellipse cx="48" cy="26" rx="4" ry="2.5" fill="#FFB0BE" opacity="0.55" />
      <rect x="26" y="37" width="8" height="5" fill="#FFE0C8" />
      <path d="M5 82 L12 46 Q20 38 30 36 Q40 38 48 46 L55 82Z" fill="#f9a8d4" />
      <path d="M10 68 Q30 74 50 68 L55 82 L5 82Z" fill="#f472b6" />
      <path d="M27.5 54 Q30 50 32.5 54 Q35 58 30 62 Q25 58 27.5 54Z" fill="#e879a0" />
      <path d="M26 40 L30 45 L34 40" stroke="white" strokeWidth="2.5" fill="none" />
      <circle cx="30" cy="46" r="2.5" fill="#e879a0" />
      <path d="M6 55 L7 52.5 L8 55 L10.5 56 L8 57 L7 59.5 L6 57 L3.5 56Z" fill="#FBBF24" opacity="0.75" />
      <path d="M52 60 L53 57.5 L54 60 L56.5 61 L54 62 L53 64.5 L52 62 L49.5 61Z" fill="#FBBF24" opacity="0.75" />
      <path d="M12 48 Q4 54 5 64" stroke="#f9a8d4" strokeWidth="8" fill="none" strokeLinecap="round" />
      <circle cx="5" cy="64" r="5" fill="#FFE0C8" />
      <path d="M48 48 Q56 54 55 64" stroke="#f9a8d4" strokeWidth="8" fill="none" strokeLinecap="round" />
      <circle cx="55" cy="64" r="5" fill="#FFE0C8" />
    </svg>
  );
}
