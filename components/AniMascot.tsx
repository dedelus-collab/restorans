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
