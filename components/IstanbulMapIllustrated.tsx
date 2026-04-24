"use client";
import Link from "next/link";

const W = 780;
const H = 480;

const DISTRICTS = [
  // — Avrupa yakası —
  { name: "Sarıyer",        slug: "sariyer",        x: 296, y: 62  },
  { name: "Arnavutköy",     slug: "arnavutkoy",     x: 90,  y: 92  },
  { name: "Sultangazi",     slug: "sultangazi",     x: 182, y: 100 },
  { name: "Kâğıthane",     slug: "kagithane",      x: 230, y: 130 },
  { name: "Eyüpsultan",    slug: "eyupsultan",     x: 148, y: 178 },
  { name: "Gaziosmanpaşa", slug: "gaziosmanpasa",  x: 190, y: 152 },
  { name: "Şişli",          slug: "sisli",          x: 254, y: 174 },
  { name: "Beyoğlu",        slug: "beyoglu",        x: 268, y: 228 },
  { name: "Beşiktaş",       slug: "besiktas",       x: 288, y: 268 },
  { name: "Fatih",           slug: "fatih",          x: 192, y: 318 },
  { name: "Bayrampaşa",     slug: "bayramspasa",    x: 202, y: 250 },
  { name: "Güngören",       slug: "gungoren",       x: 146, y: 280 },
  { name: "Zeytinburnu",   slug: "zeytinburnu",    x: 140, y: 336 },
  { name: "Bahçelievler",   slug: "bahcelievler",   x: 120, y: 308 },
  { name: "Bakırköy",       slug: "bakirkoy",       x: 106, y: 362 },
  { name: "Avcılar",        slug: "avcilar",        x: 62,  y: 354 },
  { name: "Büyükçekmece",   slug: "buyukcekmece",   x: 36,  y: 322 },
  { name: "Beylikdüzü",    slug: "beylikduzu",     x: 34,  y: 378 },
  { name: "Esenyurt",       slug: "esenyurt",       x: 60,  y: 278 },
  // — Anadolu yakası —
  { name: "Beykoz",         slug: "beykoz",         x: 498, y: 108 },
  { name: "Üsküdar",        slug: "uskudar",        x: 448, y: 222 },
  { name: "Ümraniye",      slug: "umraniye",       x: 516, y: 216 },
  { name: "Çekmeköy",      slug: "cekmekoy",       x: 572, y: 198 },
  { name: "Kadıköy",       slug: "kadikoy",        x: 448, y: 294 },
  { name: "Ataşehir",      slug: "atasehir",       x: 520, y: 270 },
  { name: "Maltepe",        slug: "maltepe",        x: 514, y: 342 },
  { name: "Kartal",          slug: "kartal",         x: 558, y: 360 },
  { name: "Pendik",          slug: "pendik",         x: 604, y: 378 },
  { name: "Adalar",          slug: "adalar",         x: 622, y: 452 },
];

const COUNTS: Record<string, number> = {
  fatih: 28, beyoglu: 18, besiktas: 17, kadikoy: 16,
  sisli: 10, sariyer: 9, uskudar: 7, umraniye: 7,
  beykoz: 6, esenyurt: 6, bahcelievler: 6,
  atasehir: 5, cekmekoy: 5, bakirkoy: 5, maltepe: 5,
  kagithane: 4, gungoren: 4,
  kartal: 3, zeytinburnu: 3, avcilar: 3, buyukcekmece: 3,
  beylikduzu: 2, pendik: 2, eyupsultan: 2,
  adalar: 1, bayramspasa: 1, sultangazi: 1, gaziosmanpasa: 1, arnavutkoy: 1,
};

// Köprü verisi
const BRIDGES = [
  { label: "Yavuz Sultan Selim", x1: 352, y1: 72,  x2: 436, y2: 70  },
  { label: "Fatih Sultan Mehmet", x1: 357, y1: 155, x2: 438, y2: 152 },
  { label: "15 Temmuz",          x1: 360, y1: 265, x2: 438, y2: 262 },
];

// Dekoratif ağaçlar
const TREES = [
  [112,62],[136,74],[78,118],[92,140],[54,198],[46,224],
  [510,68],[532,80],[556,94],[630,114],[664,136],[712,106],[688,182],
];

// Tekneler
const BOATS = [
  { x: 382, y: 198, s: 1   },
  { x: 375, y: 308, s: 0.9 },
  { x: 155, y: 438, s: 1.1 },
  { x: 480, y: 430, s: 1   },
  { x: 310, y: 445, s: 0.8 },
  { x: 680, y: 445, s: 1   },
];

export function IstanbulMapIllustrated() {
  return (
    <div
      className="relative w-full rounded-2xl overflow-hidden border border-blue-200 shadow-xl"
      style={{ aspectRatio: `${W}/${H}` }}
    >
      {/* ─── SVG Harita ─── */}
      <svg
        viewBox={`0 0 ${W} ${H}`}
        xmlns="http://www.w3.org/2000/svg"
        className="absolute inset-0 w-full h-full"
        aria-hidden="true"
      >
        <defs>
          {/* Su gradyanı */}
          <linearGradient id="sea" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%"   stopColor="#1E74BE"/>
            <stop offset="55%"  stopColor="#3E9DD4"/>
            <stop offset="100%" stopColor="#60C0EA"/>
          </linearGradient>
          {/* Avrupa arazi */}
          <linearGradient id="euLand" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%"   stopColor="#68B865"/>
            <stop offset="100%" stopColor="#4EA44B"/>
          </linearGradient>
          {/* Asya arazi */}
          <linearGradient id="asLand" x1="1" y1="0" x2="0" y2="1">
            <stop offset="0%"   stopColor="#6ABA67"/>
            <stop offset="100%" stopColor="#52A64F"/>
          </linearGradient>
          {/* Arazi gölge filtre */}
          <filter id="lshadow" x="-8%" y="-8%" width="116%" height="116%">
            <feDropShadow dx="2" dy="4" stdDeviation="5"
              floodColor="#0A4878" floodOpacity="0.35"/>
          </filter>
          {/* Dalga pattern */}
          <pattern id="waves" x="0" y="0" width="60" height="20" patternUnits="userSpaceOnUse">
            <path d="M 0 10 Q 15 5 30 10 Q 45 15 60 10"
              stroke="rgba(255,255,255,0.15)" strokeWidth="1.2" fill="none"/>
          </pattern>
        </defs>

        {/* ── Su arka planı ── */}
        <rect width={W} height={H} fill="url(#sea)"/>
        <rect width={W} height={H} fill="url(#waves)" opacity="0.6"/>

        {/* ── AVRUPA ARAZİSİ (Haliç delikli) ── */}
        <path
          fillRule="evenodd"
          fill="url(#euLand)"
          stroke="#3A7837"
          strokeWidth="1.8"
          strokeLinejoin="round"
          filter="url(#lshadow)"
          d={`
            M 0,0 L 352,0
            C 354,55  356,110 357,162
            C 358,202 359,232 360,256
            C 350,278 338,306 325,328
            C 313,348 303,366 294,383
            C 282,399 275,416 273,430
            C 247,448 204,458 156,462
            C 106,466 50,460 0,450 Z

            M 360,256
            C 344,254 320,252 293,252
            C 266,252 238,250 212,242
            C 198,236 184,232 173,228
            C 176,262 190,280 216,288
            C 245,296 278,296 308,294
            C 335,292 352,284 360,270 Z
          `}
        />

        {/* ── ASYA ARAZİSİ ── */}
        <path
          fill="url(#asLand)"
          stroke="#3A7837"
          strokeWidth="1.8"
          strokeLinejoin="round"
          filter="url(#lshadow)"
          d={`
            M 408,0 L 780,0 L 780,480 L 640,480
            C 612,476 580,468 552,456
            C 526,445 502,430 482,412
            C 466,396 455,376 449,352
            C 444,328 441,302 439,275
            C 437,248 437,220 437,192
            C 437,158 439,122 441,88
            C 443,56 450,26 408,0 Z
          `}
        />

        {/* ── ADALAR ── */}
        <ellipse cx="632" cy="458" rx="26" ry="11" fill="#5CB458" stroke="#3A7837" strokeWidth="1.2"/>
        <ellipse cx="670" cy="463" rx="17" ry="8"  fill="#5CB458" stroke="#3A7837" strokeWidth="1.2"/>
        <ellipse cx="598" cy="454" rx="13" ry="7"  fill="#5CB458" stroke="#3A7837" strokeWidth="1.2"/>

        {/* ── KÖPRÜLER ── */}
        {BRIDGES.map(({ x1, y1, x2, y2 }, i) => {
          const mx = (x1 + x2) / 2;
          const my = Math.min(y1, y2) - 11;
          return (
            <g key={i} opacity={i === 0 ? 0.75 : 0.95}>
              <line x1={x1} y1={y1} x2={x2} y2={y2}
                stroke="#F0C040" strokeWidth={i === 0 ? 2.5 : 3.5}/>
              {/* Asma köprü telleri */}
              <line x1={x1} y1={y1} x2={mx} y2={my}
                stroke="#F0C040" strokeWidth="1.5" strokeDasharray="4,3"/>
              <line x1={x2} y1={y2} x2={mx} y2={my}
                stroke="#F0C040" strokeWidth="1.5" strokeDasharray="4,3"/>
              <circle cx={mx - 18} cy={y1 - 1} r={i === 0 ? 3 : 4} fill="#F0C040"/>
              <circle cx={mx + 18} cy={y2 - 1} r={i === 0 ? 3 : 4} fill="#F0C040"/>
            </g>
          );
        })}

        {/* ── Sultanahmet silüeti ── */}
        <g transform="translate(212,325)" opacity="0.72">
          <rect x="-11" y="-9" width="22" height="9" fill="#D4B860" rx="1"/>
          <ellipse cx="0" cy="-9" rx="11" ry="7" fill="#D4B860"/>
          <line x1="-13" y1="-9" x2="-15" y2="-24" stroke="#D4B860" strokeWidth="2"/>
          <circle cx="-15" cy="-24" r="2" fill="#D4B860"/>
          <line x1="13" y1="-9" x2="15" y2="-24" stroke="#D4B860" strokeWidth="2"/>
          <circle cx="15" cy="-24" r="2" fill="#D4B860"/>
          <line x1="0" y1="-16" x2="0" y2="-27" stroke="#D4B860" strokeWidth="1.5"/>
        </g>

        {/* ── Galata Kulesi ── */}
        <g transform="translate(273,235)" opacity="0.78">
          <rect x="-4" y="-20" width="8" height="20" fill="#D4B860" rx="1.5"/>
          <ellipse cx="0" cy="-20" rx="5.5" ry="4" fill="#C4A850"/>
          <line x1="0" y1="-24" x2="0" y2="-30" stroke="#D4B860" strokeWidth="1.5"/>
        </g>

        {/* ── Kız Kulesi (Boğaz'da küçük ada) ── */}
        <g transform="translate(397,255)" opacity="0.7">
          <ellipse cx="0" cy="3" rx="5" ry="3" fill="#7AB878"/>
          <rect x="-2" y="-8" width="4" height="11" fill="#D4B860" rx="1"/>
          <ellipse cx="0" cy="-8" rx="3" ry="2.5" fill="#C4A850"/>
        </g>

        {/* ── Dekoratif ağaçlar ── */}
        {TREES.map(([tx, ty], i) => (
          <g key={i} transform={`translate(${tx},${ty})`} opacity="0.62">
            <circle r="6"  fill="#287A24"/>
            <circle cx="5"  r="5" fill="#329A2E"/>
            <circle cy="6"  r="5" fill="#246E20"/>
          </g>
        ))}

        {/* ── Tekneler ── */}
        {BOATS.map(({ x, y, s }, i) => (
          <g key={i} transform={`translate(${x},${y}) scale(${s})`}>
            <path d="M -9 2 L 9 2 L 7 -2 L -7 -2 Z"
              fill="rgba(255,255,255,0.88)" stroke="rgba(180,215,235,0.7)" strokeWidth="0.6"/>
            <line x1="0" y1="-2" x2="0" y2="-10"
              stroke="rgba(210,210,210,0.8)" strokeWidth="0.8"/>
            {i % 2 === 0 && (
              <path d="M 0 -10 L 7 -6 L 0 -2 Z"
                fill="rgba(255,220,90,0.55)" stroke="none"/>
            )}
          </g>
        ))}

        {/* ── Su etiketi ── */}
        <text x="388" y="210" fill="rgba(255,255,255,0.72)"
          fontSize="9" fontStyle="italic" fontWeight="bold"
          fontFamily="Georgia,serif" textAnchor="middle"
          transform="rotate(-84,388,210)">İstanbul Boğazı</text>

        <text x="282" y="272" fill="rgba(255,255,255,0.68)"
          fontSize="9" fontStyle="italic"
          fontFamily="Georgia,serif" textAnchor="middle"
          transform="rotate(-16,282,272)">Haliç</text>

        <text x="210" y="445" fill="rgba(255,255,255,0.62)"
          fontSize="14" fontStyle="italic" fontWeight="bold"
          fontFamily="Georgia,serif" textAnchor="middle">Marmara Denizi</text>

        <text x="615" y="22" fill="rgba(255,255,255,0.55)"
          fontSize="10" fontStyle="italic"
          fontFamily="Georgia,serif" textAnchor="middle">Karadeniz</text>
      </svg>

      {/* ─── İlçe etiketleri (HTML overlay) ─── */}
      {DISTRICTS.map(d => {
        const count = COUNTS[d.slug] ?? 0;
        const left = `${(d.x / W) * 100}%`;
        const top  = `${(d.y / H) * 100}%`;
        const isLg = count >= 10;
        const isMd = count >= 5 && count < 10;

        return (
          <Link
            key={d.slug}
            href={`/istanbul/ilce/${d.slug}`}
            className={[
              "absolute transform -translate-x-1/2 -translate-y-1/2 z-10",
              "whitespace-nowrap rounded-full border shadow-sm",
              "hover:shadow-lg hover:scale-110 hover:z-20",
              "transition-all duration-150 font-semibold leading-none",
              isLg
                ? "bg-red-600 border-red-700 text-white px-2.5 py-1 text-[11px]"
                : isMd
                  ? "bg-amber-500 border-amber-600 text-white px-2 py-[3px] text-[10px]"
                  : "bg-white/90 border-gray-300 text-gray-700 px-2 py-[2px] text-[9px]",
            ].join(" ")}
            style={{ left, top }}
            title={`${d.name} — ${count} restoran`}
          >
            {d.name}
            {isLg && (
              <span className="ml-1 opacity-80 text-[8px]">{count}</span>
            )}
          </Link>
        );
      })}

      {/* ─── Sol üst başlık ─── */}
      <div className="absolute top-2 left-2 bg-white/85 backdrop-blur-sm
          rounded-xl px-3 py-1.5 shadow border border-white/50 pointer-events-none">
        <div className="text-xs font-bold text-gray-800 leading-tight">İstanbul</div>
        <div className="text-[9px] text-gray-500 leading-tight">Restoran İlçe Haritası</div>
      </div>

      {/* ─── Sağ alt lejant ─── */}
      <div className="absolute bottom-2 right-2 bg-white/85 backdrop-blur-sm
          rounded-xl px-2.5 py-2 shadow border border-white/50 flex flex-col gap-1 pointer-events-none">
        {([
          { cls: "bg-red-600",                        lbl: "10+ restoran" },
          { cls: "bg-amber-500",                      lbl: "5–9 restoran" },
          { cls: "bg-white border border-gray-300",   lbl: "1–4 restoran" },
        ] as { cls: string; lbl: string }[]).map(({ cls, lbl }) => (
          <div key={lbl} className="flex items-center gap-1.5">
            <span className={`w-3 h-3 rounded-full ${cls} inline-block shrink-0`}/>
            <span className="text-[8px] text-gray-600">{lbl}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
