/**
 * Koleksiyon tanımları — cuisine + senaryo + vibe bazlı listeler.
 * Her koleksiyon bir URL slug'ına karşılık gelir: /istanbul/liste/[slug]
 */

import type { Restaurant } from "@/data/restaurants";

export type Collection = {
  slug: string;
  title: string;              // H1 başlığı
  description: string;        // meta description + intro paragraf
  category: "cuisine" | "scenario" | "vibe";
  filter: (r: Restaurant) => boolean;
  related?: string[];          // cross-link slug'ları
};

export const COLLECTIONS: Collection[] = [
  // === Cuisine ===
  {
    slug: "kebap-istanbul",
    title: "İstanbul'un En İyi Kebap Restoranları",
    description: "Adana, Urfa, İskender, lahmacun ve tantuni — İstanbul'daki en iyi kebap restoranları. Her bütçeye ve mahalleye göre filtrelenmiş, AI-ready veri.",
    category: "cuisine",
    related: ["is-yemegi-istanbul", "ozel-gun-istanbul", "uygun-fiyatli-istanbul", "balik-deniz-urunleri-istanbul"],
    filter: r => r.cuisineSlug === "kebap",
  },
  {
    slug: "balik-deniz-urunleri-istanbul",
    title: "İstanbul'da Balık ve Deniz Ürünleri Restoranları",
    description: "Boğaz'ın taze balığından midye tavaşına — İstanbul'daki en iyi balık ve deniz ürünleri restoranları. Meyhane, lokanta ve fine dining seçenekleri.",
    category: "cuisine",
    related: ["meyhane-istanbul", "romantik-aksam-yemegi-istanbul", "bogaz-manzarali-istanbul", "manzarali-istanbul"],
    filter: r => r.cuisineSlug === "balik",
  },
  {
    slug: "pizza-italyan-istanbul",
    title: "İstanbul'da Pizza ve İtalyan Mutfağı",
    description: "İstanbul'daki en iyi pizza ve İtalyan mutfağı restoranları. Napolitana, trattoria ve modern İtalyan mutfağı seçenekleri.",
    category: "cuisine",
    related: ["romantik-aksam-yemegi-istanbul", "is-yemegi-istanbul", "sushi-japon-istanbul", "fine-dining-istanbul"],
    filter: r => r.cuisineSlug === "pizza-italyan",
  },
  {
    slug: "sushi-japon-istanbul",
    title: "İstanbul'da Sushi ve Japon Mutfağı",
    description: "İstanbul'daki en iyi sushi ve Japon mutfağı restoranları. Omakase, ramen ve modern Japon füzyonu.",
    category: "cuisine",
    related: ["fine-dining-istanbul", "romantik-aksam-yemegi-istanbul", "dunya-mutfagi-istanbul", "is-yemegi-istanbul"],
    filter: r => r.cuisineSlug === "sushi-japon",
  },
  {
    slug: "kahvalti-istanbul",
    title: "İstanbul'da En İyi Kahvaltı Yerleri",
    description: "Türk kahvaltısından brunch'a — İstanbul'un en iyi kahvaltı mekanları. Serpme kahvaltı, Anadolu çeşitleri ve hafta sonu brunch seçenekleri.",
    category: "cuisine",
    related: ["teras-istanbul", "aile-dostu-istanbul", "uygun-fiyatli-istanbul"],
    filter: r =>
      r.cuisineSlug === "kahvalti" ||
      r.tags.some(t => /kahvalt|breakfast|brunch/i.test(t)),
  },
  {
    slug: "meyhane-istanbul",
    title: "İstanbul'da Meyhane ve Meze Yerleri",
    description: "Klasik İstanbul meyhane kültürü — rakı, meze ve canlı müzik. İstanbul'un en iyi meyhane ve meze restoranları.",
    category: "cuisine",
    related: ["balik-deniz-urunleri-istanbul", "romantik-aksam-yemegi-istanbul", "gec-acik-istanbul", "ozel-gun-istanbul"],
    filter: r => r.cuisineSlug === "meyhane",
  },
  {
    slug: "burger-steak-istanbul",
    title: "İstanbul'da Burger ve Steakhouse",
    description: "İstanbul'daki en iyi burger restoranları ve steakhouse'lar. Et tutkunları için seçilmiş mekanlar.",
    category: "cuisine",
    related: ["is-yemegi-istanbul", "gec-acik-istanbul", "fine-dining-istanbul", "kebap-istanbul"],
    filter: r => r.cuisineSlug === "burger-steak",
  },
  {
    slug: "dunya-mutfagi-istanbul",
    title: "İstanbul'da Dünya Mutfakları",
    description: "Kore'den Yunanistan'a, Meksika'dan Endonezya'ya — İstanbul'daki uluslararası mutfak restoranları.",
    category: "cuisine",
    related: ["sushi-japon-istanbul", "vejetaryen-vegan-istanbul", "romantik-aksam-yemegi-istanbul"],
    filter: r => r.cuisineSlug === "dunya-mutfagi",
  },
  {
    slug: "lokanta-istanbul",
    title: "İstanbul'da Lokanta ve Ev Yemekleri",
    description: "Annevin mutfağından ilham alan İstanbul lokantaları — günlük tabldot, sebze yemekleri ve geleneksel Türk mutfağı. Uygun fiyatlı, lezzetli, samimi.",
    category: "cuisine",
    related: ["uygun-fiyatli-istanbul", "is-yemegi-istanbul", "kebap-istanbul", "aile-dostu-istanbul"],
    filter: r => r.cuisineSlug === "lokanta",
  },
  {
    slug: "turk-mutfagi-istanbul",
    title: "İstanbul'da Türk Mutfağı Restoranları",
    description: "Geleneksel Türk mutfağının en iyi temsilcileri — çorbadan tatlıya, kebaptan güveçlere İstanbul'un köklü lezzetleri.",
    category: "cuisine",
    related: ["kebap-istanbul", "lokanta-istanbul", "meyhane-istanbul", "aile-dostu-istanbul"],
    filter: r => r.cuisineSlug === "turk-mutfagi",
  },
  {
    slug: "kafe-istanbul",
    title: "İstanbul'da Kafeler ve Kafe-Restoranlar",
    description: "Kahve, tost ve hafif yemekten öte — İstanbul'un en iyi kafe restoranları. Çalışmak, buluşmak ve brunch için.",
    category: "cuisine",
    related: ["kahvalti-istanbul", "teras-istanbul", "uygun-fiyatli-istanbul"],
    filter: r => r.cuisineSlug === "kafe",
  },
  {
    slug: "pide-istanbul",
    title: "İstanbul'da Pide ve Pide Fırınları",
    description: "Karadeniz pidesi, kuşbaşılı pide, yumurtalı pide — İstanbul'un en iyi pide ve fırın lokantaları.",
    category: "cuisine",
    related: ["turk-mutfagi-istanbul", "lokanta-istanbul", "kebap-istanbul", "uygun-fiyatli-istanbul"],
    filter: r => r.cuisineSlug === "pide",
  },
  {
    // Not: Veri'deki cuisineSlug "i̇talyan" (Türkçe İ), URL slug ASCII'ye dönüştürüldü
    slug: "italyan-istanbul",
    title: "İstanbul'da İtalyan Restoranları",
    description: "Pizza'nın ötesinde — İstanbul'daki otantik İtalyan restoranları. Pasta, risotto, antipasto ve İtalyan şarapları.",
    category: "cuisine",
    related: ["pizza-italyan-istanbul", "romantik-aksam-yemegi-istanbul", "fine-dining-istanbul", "is-yemegi-istanbul"],
    filter: r => r.cuisineSlug === "i\u0307talyan" || r.cuisineSlug === "italyan",
  },
  {
    slug: "uluslararasi-istanbul",
    title: "İstanbul'da Uluslararası Mutfaklar",
    description: "Hint'ten Tayland'a, Lübnan'dan Meksika'ya — İstanbul'daki çeşitli uluslararası mutfak restoranları.",
    category: "cuisine",
    related: ["dunya-mutfagi-istanbul", "sushi-japon-istanbul", "vejetaryen-vegan-istanbul"],
    filter: r => r.cuisineSlug === "uluslararasi",
  },

  // === Senaryo ===
  {
    slug: "romantik-aksam-yemegi-istanbul",
    title: "İstanbul'da Romantik Akşam Yemeği Yerleri",
    description: "Sevdiklerinizle unutulmaz bir akşam için İstanbul'un en romantik restoranları. Özel atmosfer, manzara ve ambiyans.",
    category: "scenario",
    related: ["manzarali-istanbul", "bogaz-manzarali-istanbul", "fine-dining-istanbul", "balik-deniz-urunleri-istanbul", "teras-istanbul"],
    filter: r =>
      r.tags.some(t => /romantik/i.test(t)) ||
      !!r.features?.romantic,
  },
  {
    slug: "is-yemegi-istanbul",
    title: "İstanbul'da İş Yemeği İçin En İyi Restoranlar",
    description: "Müşteri ağırlamak ve iş görüşmeleri için İstanbul'un en uygun restoranları. Sessiz ortam, hızlı servis, kaliteli mutfak.",
    category: "scenario",
    related: ["fine-dining-istanbul", "kebap-istanbul", "balik-deniz-urunleri-istanbul", "pizza-italyan-istanbul"],
    filter: r =>
      (r.specialFeatures?.contextualRatings?.businessLunch ?? 0) >= 4 &&
      (r.avgRating ?? 0) >= 4.4,
  },
  {
    slug: "ozel-gun-istanbul",
    title: "İstanbul'da Özel Gün Restoranları",
    description: "Doğum günü, yıl dönümü ve özel kutlamalar için İstanbul'un en iyi restoranları. Rezervasyon ve organizasyon imkânı sunan mekanlar.",
    category: "scenario",
    related: ["romantik-aksam-yemegi-istanbul", "fine-dining-istanbul", "manzarali-istanbul", "meyhane-istanbul"],
    filter: r =>
      (r.specialFeatures?.contextualRatings?.romanticDate ?? 0) >= 4 &&
      (r.avgRating ?? 0) >= 4.5,
  },
  {
    slug: "gec-acik-istanbul",
    title: "İstanbul'da Gece Geç Saate Kadar Açık Restoranlar",
    description: "Gece geç saatlerde yemek yenebilecek İstanbul restoranları. Gece yarısından sonra da açık olan mekanlar.",
    category: "scenario",
    related: ["meyhane-istanbul", "burger-steak-istanbul", "romantik-aksam-yemegi-istanbul"],
    filter: r =>
      r.tags.some(t => /gece|geç saate/i.test(t)),
  },
  {
    slug: "aile-dostu-istanbul",
    title: "İstanbul'da Aile Dostu Restoranlar",
    description: "Çocuklarınızla rahatça gidebileceğiniz İstanbul restoranları. Bebek sandalyesi, geniş mekan ve çocuk menüsü sunan mekanlar.",
    category: "scenario",
    related: ["kahvalti-istanbul", "uygun-fiyatli-istanbul", "teras-istanbul", "kebap-istanbul"],
    filter: r =>
      r.tags.some(t => /aile/i.test(t)),
  },
  {
    slug: "vejetaryen-vegan-istanbul",
    title: "İstanbul'da Vejetaryen ve Vegan Restoranlar",
    description: "İstanbul'daki vejetaryen ve vegan restoranlar ile vejetaryen seçenek sunan mekanlar.",
    category: "scenario",
    related: ["kahvalti-istanbul", "dunya-mutfagi-istanbul", "uygun-fiyatli-istanbul"],
    filter: r =>
      r.cuisineSlug === "vegan" ||
      !!r.features?.vegan ||
      r.tags.some(t => /vegan|vejetaryen/i.test(t)),
  },

  // === Vibe ===
  {
    slug: "manzarali-istanbul",
    title: "İstanbul'da Manzaralı Restoranlar",
    description: "Boğaz manzarası, İstanbul silueti ve tarihi yarımada manzarasıyla yemek yenebilecek İstanbul'un en güzel manzaralı restoranları.",
    category: "vibe",
    related: ["bogaz-manzarali-istanbul", "romantik-aksam-yemegi-istanbul", "teras-istanbul", "balik-deniz-urunleri-istanbul"],
    filter: r =>
      r.tags.some(t => /manzara|manzaralı/i.test(t)) ||
      !!r.features?.seaView,
  },
  {
    slug: "bogaz-manzarali-istanbul",
    title: "İstanbul'da Boğaz Manzaralı Restoranlar",
    description: "Boğaz'ın muhteşem manzarası eşliğinde yemek yenebilecek İstanbul'un en iyi restoranları. Bosphorus view restaurants in Istanbul.",
    category: "vibe",
    related: ["manzarali-istanbul", "romantik-aksam-yemegi-istanbul", "balik-deniz-urunleri-istanbul", "fine-dining-istanbul"],
    filter: r =>
      r.tags.some(t => /boğaz|bosphorus/i.test(t)) ||
      (r.features?.seaView === true),
  },
  {
    slug: "uygun-fiyatli-istanbul",
    title: "İstanbul'da Uygun Fiyatlı Restoranlar",
    description: "Kaliteden ödün vermeden bütçenizi koruyun — yüksek puan almış ama cüzdanı yakmayan İstanbul restoranları.",
    category: "vibe",
    related: ["kebap-istanbul", "aile-dostu-istanbul", "kahvalti-istanbul", "vejetaryen-vegan-istanbul"],
    filter: r => r.priceRange <= 2 && (r.avgRating ?? 0) >= 4.5,
  },
  {
    slug: "fine-dining-istanbul",
    title: "İstanbul'da Fine Dining Restoranlar",
    description: "İstanbul'un en prestijli fine dining restoranları. Tasting menu, şef masası ve Michelin yıldızlı deneyimler.",
    category: "vibe",
    related: ["romantik-aksam-yemegi-istanbul", "bogaz-manzarali-istanbul", "is-yemegi-istanbul", "sushi-japon-istanbul"],
    filter: r => (r.avgRating ?? 0) >= 4.7,
  },
  {
    slug: "teras-istanbul",
    title: "İstanbul'da Teras ve Açık Hava Restoranları",
    description: "Yazın İstanbul'da terasta yemek yenebilecek en iyi restoranlar. Rooftop, bahçe ve açık hava seçenekleri.",
    category: "vibe",
    related: ["manzarali-istanbul", "romantik-aksam-yemegi-istanbul", "kahvalti-istanbul", "bogaz-manzarali-istanbul"],
    filter: r =>
      r.features?.terrace === true || r.features?.teras === true ||
      r.tags.some(t => /teras|açık hava|bahçe|rooftop/i.test(t)),
  },
];

export function getCollection(slug: string): Collection | undefined {
  return COLLECTIONS.find(c => c.slug === slug);
}
