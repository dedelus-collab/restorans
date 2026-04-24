"use client";
import Image from "next/image";
import Link from "next/link";

// Pozisyonlar resmin yüzde değerleri olarak (x%, y%)
// Gerçek istanbul haritasına göre ayarlandı
const DISTRICTS = [
  // ── Avrupa Yakası ──
  { name: "Sarıyer",        slug: "sariyer",        x: 43, y: 14 },
  { name: "Arnavutköy",     slug: "arnavutkoy",     x: 10, y: 16 },
  { name: "Sultangazi",     slug: "sultangazi",     x: 22, y: 20 },
  { name: "Kâğıthane",     slug: "kagithane",      x: 32, y: 26 },
  { name: "Gaziosmanpaşa", slug: "gaziosmanpasa",  x: 23, y: 30 },
  { name: "Eyüpsultan",    slug: "eyupsultan",     x: 18, y: 38 },
  { name: "Şişli",          slug: "sisli",          x: 35, y: 34 },
  { name: "Beyoğlu",        slug: "beyoglu",        x: 38, y: 46 },
  { name: "Beşiktaş",       slug: "besiktas",       x: 42, y: 55 },
  { name: "Fatih",           slug: "fatih",          x: 28, y: 57 },
  { name: "Bayrampaşa",     slug: "bayramspasa",    x: 26, y: 46 },
  { name: "Esenyurt",       slug: "esenyurt",       x: 9,  y: 46 },
  { name: "Güngören",       slug: "gungoren",       x: 18, y: 52 },
  { name: "Bahçelievler",   slug: "bahcelievler",   x: 14, y: 59 },
  { name: "Zeytinburnu",   slug: "zeytinburnu",    x: 20, y: 65 },
  { name: "Bakırköy",       slug: "bakirkoy",       x: 13, y: 70 },
  { name: "Avcılar",        slug: "avcilar",        x: 7,  y: 66 },
  { name: "Büyükçekmece",   slug: "buyukcekmece",   x: 4,  y: 57 },
  { name: "Beylikdüzü",    slug: "beylikduzu",     x: 4,  y: 72 },
  // ── Anadolu Yakası ──
  { name: "Beykoz",         slug: "beykoz",         x: 64, y: 20 },
  { name: "Üsküdar",        slug: "uskudar",        x: 57, y: 43 },
  { name: "Ümraniye",      slug: "umraniye",       x: 68, y: 40 },
  { name: "Çekmeköy",      slug: "cekmekoy",       x: 75, y: 33 },
  { name: "Kadıköy",       slug: "kadikoy",        x: 57, y: 56 },
  { name: "Ataşehir",      slug: "atasehir",       x: 68, y: 52 },
  { name: "Maltepe",        slug: "maltepe",        x: 67, y: 65 },
  { name: "Kartal",          slug: "kartal",         x: 73, y: 68 },
  { name: "Pendik",          slug: "pendik",         x: 80, y: 73 },
  { name: "Adalar",          slug: "adalar",         x: 84, y: 88 },
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

export function IstanbulMapIllustrated() {
  return (
    <div className="relative w-full rounded-2xl overflow-hidden shadow-xl border border-gray-200"
      style={{ aspectRatio: "605 / 454" }}
    >
      {/* Arka plan harita resmi */}
      <Image
        src="/istanbul-map.jpg"
        alt="İstanbul illüstrasyon haritası"
        fill
        className="object-cover object-center"
        priority
        sizes="(max-width: 768px) 100vw, 896px"
      />

      {/* Tıklanabilir ilçe etiketleri */}
      {DISTRICTS.map(d => {
        const count = COUNTS[d.slug] ?? 0;
        const isLg = count >= 10;
        const isMd = count >= 5 && count < 10;

        return (
          <Link
            key={d.slug}
            href={`/istanbul/ilce/${d.slug}`}
            className={[
              "absolute transform -translate-x-1/2 -translate-y-1/2 z-10",
              "whitespace-nowrap rounded-full border shadow",
              "hover:shadow-xl hover:scale-110 hover:z-20",
              "transition-all duration-150 font-bold leading-none select-none",
              isLg
                ? "bg-red-600/90 border-red-800 text-white px-2.5 py-1 text-[11px]"
                : isMd
                  ? "bg-amber-500/90 border-amber-700 text-white px-2 py-[3px] text-[10px]"
                  : "bg-white/80 border-gray-400 text-gray-800 px-1.5 py-[2px] text-[9px]",
            ].join(" ")}
            style={{ left: `${d.x}%`, top: `${d.y}%` }}
            title={`${d.name} — ${count} restoran`}
          >
            {d.name}
            {count >= 5 && (
              <span className="ml-1 opacity-75 text-[8px] font-normal">{count}</span>
            )}
          </Link>
        );
      })}

      {/* Sol üst başlık */}
      <div className="absolute top-2 left-2 bg-white/80 backdrop-blur-sm
          rounded-xl px-3 py-1.5 shadow border border-white/60 pointer-events-none z-20">
        <div className="text-xs font-bold text-gray-800 leading-tight">İstanbul</div>
        <div className="text-[9px] text-gray-500 leading-tight">Restoran İlçe Haritası</div>
      </div>

      {/* Sağ alt lejant */}
      <div className="absolute bottom-2 right-2 bg-white/80 backdrop-blur-sm
          rounded-xl px-2.5 py-2 shadow border border-white/60 flex flex-col gap-1 pointer-events-none z-20">
        {[
          { cls: "bg-red-600",   lbl: "10+ restoran" },
          { cls: "bg-amber-500", lbl: "5–9 restoran" },
          { cls: "bg-white border border-gray-400", lbl: "1–4 restoran" },
        ].map(({ cls, lbl }) => (
          <div key={lbl} className="flex items-center gap-1.5">
            <span className={`w-3 h-3 rounded-full ${cls} inline-block shrink-0`} />
            <span className="text-[8px] text-gray-600">{lbl}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
