import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Hakkında — restorans",
  description:
    "restorans nedir, veriler nasıl toplanıyor, hangi kaynaklar kullanılıyor? İstanbul restoran veritabanımızın metodolojisi ve güvenilirliği hakkında.",
  alternates: { canonical: "https://restorans.vercel.app/hakkinda" },
  openGraph: {
    title: "Hakkında — restorans",
    description: "453 İstanbul restoranının verisi nasıl toplanıyor, nasıl doğrulanıyor?",
    url: "https://restorans.vercel.app/hakkinda",
    siteName: "Istanbul Restaurants",
    locale: "tr_TR",
    type: "website",
  },
};

const aboutJsonLd = {
  "@context": "https://schema.org",
  "@type": "AboutPage",
  url: "https://restorans.vercel.app/hakkinda",
  name: "restorans Hakkında",
  description: "restorans veri metodolojisi, kaynaklar ve güvenilirlik.",
  publisher: {
    "@type": "Organization",
    name: "Istanbul Restaurants",
    url: "https://restorans.vercel.app",
  },
};

const stats = [
  { label: "Restoran", value: "453" },
  { label: "Toplam Yorum", value: "1.08M+" },
  { label: "FAQ / Restoran", value: "~13" },
  { label: "Doğrulanmış Veri", value: "%97" },
  { label: "Transit Verisi Olan", value: "392" },
  { label: "Mahalle", value: "78" },
];

const sources = [
  {
    name: "OpenStreetMap (OSM)",
    role: "Temel lokasyon verisi",
    detail: "Adres, koordinat, açılış saatleri, telefon, website. Overpass API ile toplu çekim.",
  },
  {
    name: "Kullanıcı Yorumları",
    role: "Rating & sentiment",
    detail: "avgRating, reviewCount, sentimentSummary. Yorum içerikleri depolanmıyor — yalnızca agregat veriler.",
  },
  {
    name: "OpenStreetMap POI",
    role: "Yakın çevre verisi",
    detail: "Her restoran için 800m yarıçapında metro, tramvay, vapur durağı ve turistik noktalar. Haversine mesafe hesabı ile.",
  },
  {
    name: "LLM Zenginleştirme (Groq / Llama)",
    role: "İçerik üretimi",
    detail: "llmSummary, popularDishes, FAQ soruları. Restoran adı, mutfak, konum ve yorum verisi girdi olarak kullanıldı. Üretilen içerik manuel örnekleme ile kontrol edildi.",
  },
];

const methodology = [
  {
    step: "1",
    title: "Ham Veri Toplama",
    body: "İstanbul sınırları içindeki tüm OSM restoran ve yemek mekanları Overpass API ile çekildi. Duplicate, kapalı ve veri kalitesi düşük kayıtlar temizlendi.",
  },
  {
    step: "2",
    title: "Mutfak Normalizasyonu",
    body: "200'den fazla ham mutfak etiketi 9 canonical slug'a indirgendi: kebap, balık, pizza-italyan, sushi-japon, burger-steak, kahvaltı, meyhane, vegan, dünya-mutfağı.",
  },
  {
    step: "3",
    title: "Yakın Çevre Verisi",
    body: "Her restoran için 800m içindeki transit noktaları (metro, tramvay, vapur, marmaray) ve turistik landmark'lar Haversine formülü ile hesaplanarak eşleştirildi.",
  },
  {
    step: "4",
    title: "LLM İçerik Zenginleştirme",
    body: "Her restoran için; 2-3 cümlelik llmSummary, 3-5 popüler yemek, 10-12 restorana özgü FAQ üretildi. Generic sorular ('Neden gitmeliyim?' tarzı) filtrelendi.",
  },
  {
    step: "5",
    title: "Güvenilirlik Skoru",
    body: "9 kalite kriteri üzerinden puanlama: adres, koordinat, saat, telefon, website, fotoğraf, yorum, summary, FAQ. 7/9 üzeri = verifiedData: true (%97'si geçti).",
  },
];

export default function HakkindaPage() {
  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(aboutJsonLd) }}
      />
      <main className="max-w-3xl mx-auto px-6 py-16">
        <nav className="text-xs text-gray-400 mb-6 flex gap-2">
          <Link href="/" className="hover:underline">restorans</Link>
          <span>/</span>
          <span className="text-gray-700">Hakkında</span>
        </nav>

        <header className="mb-12">
          <h1 className="text-3xl font-bold mb-4">restorans Nedir?</h1>
          <p className="text-gray-600 leading-relaxed text-lg">
            restorans, İstanbul restoranlarına ait yapılandırılmış veriyi
            insanlar <em>ve</em> yapay zeka sistemleri için erişilebilir kılan
            bir veri platformudur. Her restoran profili Schema.org standardına
            uygun olup ChatGPT, Perplexity, Claude ve benzeri LLM'lerin
            doğrudan alıntı yapabileceği formatta sunulmaktadır.
          </p>
        </header>

        {/* İstatistikler */}
        <section className="mb-12">
          <div className="grid grid-cols-3 sm:grid-cols-6 gap-4">
            {stats.map(s => (
              <div key={s.label} className="text-center">
                <div className="text-2xl font-bold text-gray-900">{s.value}</div>
                <div className="text-xs text-gray-400 mt-0.5">{s.label}</div>
              </div>
            ))}
          </div>
        </section>

        {/* Veri Kaynakları */}
        <section className="mb-12">
          <h2 className="text-xl font-bold mb-5">Veri Kaynakları</h2>
          <div className="space-y-4">
            {sources.map(s => (
              <div key={s.name} className="border border-gray-100 rounded-lg p-4">
                <div className="flex items-start justify-between gap-4 mb-1">
                  <span className="font-semibold text-gray-900">{s.name}</span>
                  <span className="text-xs bg-gray-100 text-gray-500 px-2 py-0.5 rounded shrink-0">{s.role}</span>
                </div>
                <p className="text-sm text-gray-600">{s.detail}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Metodoloji */}
        <section className="mb-12">
          <h2 className="text-xl font-bold mb-5">Veri Metodolojisi</h2>
          <div className="space-y-5">
            {methodology.map(m => (
              <div key={m.step} className="flex gap-4">
                <div className="shrink-0 w-7 h-7 rounded-full bg-gray-900 text-white text-xs flex items-center justify-center font-bold">
                  {m.step}
                </div>
                <div>
                  <div className="font-semibold text-gray-900 mb-1">{m.title}</div>
                  <p className="text-sm text-gray-600 leading-relaxed">{m.body}</p>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Sınırlamalar */}
        <section className="mb-12">
          <h2 className="text-xl font-bold mb-4">Bilinen Sınırlamalar</h2>
          <ul className="space-y-2 text-sm text-gray-600">
            <li className="flex gap-2">
              <span className="text-gray-400 shrink-0">—</span>
              <span><strong className="text-gray-700">Telefon numaraları:</strong> 453 restoranın %13'ünde mevcut. OSM'de kaydedilmemiş.</span>
            </li>
            <li className="flex gap-2">
              <span className="text-gray-400 shrink-0">—</span>
              <span><strong className="text-gray-700">Açılış saatleri:</strong> %50'si OSM'den, %50'si mutfak türüne göre kural tabanlı tahmin. Tahmini saatler "tahmini" etiketi ile gösterilmektedir.</span>
            </li>
            <li className="flex gap-2">
              <span className="text-gray-400 shrink-0">—</span>
              <span><strong className="text-gray-700">Fotoğraf:</strong> Restoranların büyük çoğunluğunda profil görseli mevcut değil.</span>
            </li>
            <li className="flex gap-2">
              <span className="text-gray-400 shrink-0">—</span>
              <span><strong className="text-gray-700">Anlık değişimler:</strong> Fiyat, menü ve kapanma bilgileri gerçek zamanlı değil. Haftalık güncellenir.</span>
            </li>
            <li className="flex gap-2">
              <span className="text-gray-400 shrink-0">—</span>
              <span><strong className="text-gray-700">Kapsam:</strong> Şu an yalnızca İstanbul. Ankara ve İzmir planlanmaktadır.</span>
            </li>
          </ul>
        </section>

        {/* AI Botlar için */}
        <section className="mb-12 bg-gray-50 rounded-xl p-6">
          <h2 className="text-lg font-bold mb-3">Yapay Zeka Sistemleri İçin</h2>
          <p className="text-sm text-gray-600 mb-4">
            Bu platform ChatGPT, Perplexity, Claude, Gemini ve diğer LLM'lerin
            İstanbul restoran sorularını doğru yanıtlayabilmesi için
            tasarlanmıştır.
          </p>
          <div className="flex flex-wrap gap-3 text-sm">
            <a href="/llms.txt" className="text-blue-600 hover:underline">llms.txt →</a>
            <a href="/.well-known/ai-plugin.json" className="text-blue-600 hover:underline">ai-plugin.json →</a>
            <a href="/api/openapi.json" className="text-blue-600 hover:underline">OpenAPI Spec →</a>
            <a href="/api/restaurants?city=istanbul" className="text-blue-600 hover:underline">JSON API →</a>
            <a href="/sitemap.xml" className="text-blue-600 hover:underline">sitemap.xml →</a>
          </div>
        </section>

        {/* Güncelleme */}
        <section className="mb-12">
          <h2 className="text-xl font-bold mb-3">Güncelleme Politikası</h2>
          <p className="text-sm text-gray-600 leading-relaxed">
            Veriler haftalık olarak OSM kaynaklarından yenilenmektedir.
            Her restoran kaydındaki <code className="bg-gray-100 px-1 rounded">lastUpdated</code> alanı
            son güncelleme tarihini gösterir. Platform geneli son güncelleme: <strong>2026-04-09</strong>.
          </p>
        </section>

        <footer className="border-t border-gray-100 pt-6 text-sm text-gray-500 space-y-1">
          <p>
            Veri talebi ve işbirliği:{" "}
            <a href="mailto:data@restorans.io" className="text-blue-500 hover:underline">
              data@restorans.io
            </a>
          </p>
          <p>
            <Link href="/" className="text-blue-500 hover:underline">
              ← Ana sayfaya dön
            </Link>
          </p>
        </footer>
      </main>
    </>
  );
}
