export function AniMascot({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 180 265"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      aria-label="Istanbul Restaurants mascot"
    >
      {/* ── HAIR (back layer) ── */}
      <path
        d="M30 120 Q26 48 90 16 Q154 48 150 120 Q150 165 120 177 Q90 183 60 177 Q30 165 30 120Z"
        fill="#1e1208"
      />

      {/* ── CHEF HAT ── */}
      <rect x="46" y="10" width="88" height="48" rx="11" fill="white" />
      <ellipse cx="90" cy="12" rx="44" ry="14" fill="white" />
      <ellipse cx="90" cy="56" rx="55" ry="11" fill="#D8D8D8" />
      {/* hat band */}
      <rect x="46" y="48" width="88" height="9" rx="2" fill="#E8E8E8" />
      {/* subtle vertical creases */}
      <line x1="62"  y1="10" x2="62"  y2="48" stroke="#F0F0F0" strokeWidth="1.5" />
      <line x1="90"  y1="10" x2="90"  y2="48" stroke="#F0F0F0" strokeWidth="1.5" />
      <line x1="118" y1="10" x2="118" y2="48" stroke="#F0F0F0" strokeWidth="1.5" />

      {/* ── FACE ── */}
      <ellipse cx="90" cy="124" rx="58" ry="63" fill="#FFE0C8" />

      {/* ── HAIR BANGS (front) ── */}
      <path
        d="M32 116 Q28 76 50 56 Q64 43 79 50 Q85 55 82 70 Q88 62 90 62 Q92 62 98 70 Q95 55 101 50 Q116 43 130 56 Q152 76 148 116"
        fill="#1e1208"
      />
      {/* side hair strands */}
      <path d="M30 120 Q32 140 37 152" stroke="#1e1208" strokeWidth="13" fill="none" strokeLinecap="round" />
      <path d="M150 120 Q148 140 143 152" stroke="#1e1208" strokeWidth="13" fill="none" strokeLinecap="round" />

      {/* ── LEFT EYE ── */}
      <ellipse cx="67" cy="119" rx="20" ry="23" fill="white" />
      <ellipse cx="67" cy="122" rx="16" ry="19" fill="#4a8de8" />
      <ellipse cx="67" cy="124" rx="10" ry="13" fill="#0d1b35" />
      <circle  cx="73" cy="114" r="5.5" fill="white" />
      <circle  cx="62" cy="121" r="2.5" fill="white" />
      {/* upper lash */}
      <path d="M48 107 Q67 98 86 107" stroke="#0d1b35" strokeWidth="3.5" fill="none" strokeLinecap="round" />
      {/* lower lid */}
      <path d="M49 133 Q67 139 85 133" stroke="#d4956a" strokeWidth="1" fill="none" strokeLinecap="round" opacity="0.45" />

      {/* ── RIGHT EYE ── */}
      <ellipse cx="113" cy="119" rx="20" ry="23" fill="white" />
      <ellipse cx="113" cy="122" rx="16" ry="19" fill="#4a8de8" />
      <ellipse cx="113" cy="124" rx="10" ry="13" fill="#0d1b35" />
      <circle  cx="119" cy="114" r="5.5" fill="white" />
      <circle  cx="108" cy="121" r="2.5" fill="white" />
      <path d="M94 107 Q113 98 132 107" stroke="#0d1b35" strokeWidth="3.5" fill="none" strokeLinecap="round" />
      <path d="M95 133 Q113 139 131 133" stroke="#d4956a" strokeWidth="1" fill="none" strokeLinecap="round" opacity="0.45" />

      {/* ── EYEBROWS ── */}
      <path d="M50 101 Q67 93 84 99"  stroke="#1e1208" strokeWidth="3"   fill="none" strokeLinecap="round" />
      <path d="M96 99  Q113 93 130 101" stroke="#1e1208" strokeWidth="3" fill="none" strokeLinecap="round" />

      {/* ── NOSE ── */}
      <path d="M87 143 Q90 148 93 143" stroke="#c47a52" strokeWidth="1.5" fill="none" strokeLinecap="round" />

      {/* ── MOUTH ── */}
      <path d="M79 156 Q90 168 101 156" stroke="#e06070" strokeWidth="2.5" fill="none" strokeLinecap="round" />

      {/* ── BLUSH ── */}
      <ellipse cx="47" cy="144" rx="14" ry="8" fill="#FFB0BE" opacity="0.55" />
      <ellipse cx="133" cy="144" rx="14" ry="8" fill="#FFB0BE" opacity="0.55" />

      {/* ── NECK ── */}
      <rect x="78" y="180" width="24" height="18" fill="#FFE0C8" />

      {/* ── BODY / DARK JACKET ── */}
      <path d="M8 265 L20 192 Q40 180 90 177 Q140 180 160 192 L172 265Z" fill="#111827" />

      {/* ── WHITE APRON ── */}
      <path d="M67 185 Q90 178 113 185 L116 265 L64 265Z" fill="white" />

      {/* ── COLLAR ── */}
      <path d="M73 180 L90 192 L107 180" stroke="white" strokeWidth="2.5" fill="none" strokeLinejoin="round" />

      {/* ── LEFT ARM ── */}
      <path d="M20 200 Q2 216 5 245" stroke="#111827" strokeWidth="23" fill="none" strokeLinecap="round" />
      <circle cx="5" cy="245" r="14" fill="#FFE0C8" />

      {/* ── RIGHT ARM (slight raise) ── */}
      <path d="M160 200 Q178 214 175 242" stroke="#111827" strokeWidth="23" fill="none" strokeLinecap="round" />
      <circle cx="175" cy="242" r="14" fill="#FFE0C8" />

      {/* ── SPARKLE decorations ── */}
      {/* top-right star */}
      <g transform="translate(158,42)" opacity="0.8">
        <path d="M0-9 2-2 9 0 2 2 0 9-2 2-9 0-2-2Z" fill="#FBBF24" />
      </g>
      {/* small star left */}
      <g transform="translate(18,72)" opacity="0.65">
        <path d="M0-6 1.5-1.5 6 0 1.5 1.5 0 6-1.5 1.5-6 0-1.5-1.5Z" fill="#FBBF24" />
      </g>
      {/* tiny dot sparkles */}
      <circle cx="162" cy="68" r="2.5" fill="#FBBF24" opacity="0.7" />
      <circle cx="152" cy="80" r="1.5" fill="#FBBF24" opacity="0.5" />
      <circle cx="18"  cy="55" r="1.5" fill="#FBBF24" opacity="0.5" />
    </svg>
  );
}

/** Small reaction bubble — floats next to mascot */
export function SpeechBubble({ text, className }: { text: string; className?: string }) {
  return (
    <div className={`relative inline-block ${className ?? ""}`}>
      <div className="bg-white border border-gray-200 rounded-2xl rounded-bl-none px-3 py-1.5 text-xs font-semibold text-gray-800 shadow-sm whitespace-nowrap">
        {text}
      </div>
      {/* bubble tail */}
      <div className="absolute -bottom-2 left-3 w-0 h-0 border-l-8 border-r-0 border-t-8 border-l-transparent border-t-white" />
      <div className="absolute -bottom-[9px] left-[11px] w-0 h-0 border-l-[7px] border-r-0 border-t-[7px] border-l-transparent border-t-gray-200" style={{zIndex:-1}} />
    </div>
  );
}
