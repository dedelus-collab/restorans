export type Restaurant = {
  id: string;
  slug: string;
  name: string;
  city: string;
  citySlug: string;
  neighborhood: string;
  cuisine: string;
  cuisineSlug?: string;
  priceRange: 1 | 2 | 3 | 4;
  avgRating: number;
  reviewCount: number;
  address: string;
  lat: number;
  lng: number;
  phone?: string;
  website?: string;
  openingHours: string;
  hoursEstimated?: boolean;
  features: {
    terrace?: boolean;
    teras?: boolean;
    parking?: boolean;
    wifi?: boolean;
    reservation?: boolean;
    rezervasyon?: boolean;
    romantic?: boolean;
    seaView?: boolean;
    liveMusic?: boolean;
    vegan?: boolean;
    [key: string]: boolean | undefined;
  };
  tags: string[];
  highlights?: string[];
  sentimentSummary: string;
  llmSummary: string;
  lastUpdated: string;
  verifiedData: boolean;
  confidenceScore: number;
  hasReviews?: boolean;
  // AI-native zengin alanlar
  specialFeatures?: {
    signatureDish?: string;
    signatureDishes?: string[];
    popularDishes?: string[];
    dietaryOptions?: string[];
    noiseLevel?: string;
    avgMealCost?: number;
    laptopFriendly?: boolean;
    outdoorHeating?: boolean;
    groupTables?: boolean;
    lighting?: string;
    criticalMinus?: string;
    standoutPlus?: string;
    contextualRatings?: {
      businessLunch?: number;
      romanticDate?: number;
      familyDining?: number;
      soloVisit?: number;
      groupDining?: number;
    };
  };
  scenarioSummary?: {
    birthday?: string;
    budget?: string;
    vegetarian?: string;
    quickLunch?: string;
    tourist?: string;
    romantic?: string;
    family?: string;
    lateNight?: string;
  };
  faq?: Array<{ question: string; answer: string }>;
  dataFreshness?: {
    lastVerified: string;
    source: string;
    confidence: string;
  };
  menuItems?: string[];
  priceDetail?: {
    starterRange?: string;
    mainCourseRange?: string;
    dessertRange?: string;
    drinkRange?: string;
    avgPerPerson?: string;
  };
  reservationLinks?: {
    googleMaps?: string;
    website?: string;
  };
  photoUrl?: string;
  nearby?: {
    transit?: Array<{
      name: string;
      type: "metro" | "tramvay" | "vapur" | "marmaray" | string;
      distance_m: number;
      walk_min: number;
    }>;
    landmarks?: Array<{
      name: string;
      type: string;
      distance_m: number;
      walk_min: number;
    }>;
  };
};

import { istanbulRestaurants } from "./istanbul";
import newRestaurantsRaw from "./new_restaurants.json";

export const restaurants: Restaurant[] = [
  ...istanbulRestaurants,
  ...(newRestaurantsRaw as Restaurant[]),
];

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const _mockRestaurants: Restaurant[] = [
  {
    id: "1",
    slug: "ciya-sofrasi",
    name: "Çiya Sofrası",
    city: "İstanbul",
    citySlug: "istanbul",
    neighborhood: "Kadıköy",
    cuisine: "Türk, Anadolu",
    priceRange: 2,
    avgRating: 4.8,
    reviewCount: 3200,
    address: "Güneşlibahçe Sk. No:43, Kadıköy, İstanbul",
    lat: 40.9901,
    lng: 29.0289,
    phone: "+90 216 336 30 13",
    website: "https://www.ciyasofrasi.com",
    openingHours: "Mo-Su 11:00-22:00",
    features: { terrace: true, reservation: false, wifi: false },
    tags: ["anadolu mutfağı", "otantik", "uygun fiyat", "kadıköy", "meyhane tadında"],
    sentimentSummary: "Yorumların %92'si lezzeti övüyor. Servis samimiyet vurgulanan başlıca özellik. Kalabalık saatlerde bekleme süresi en çok şikayet edilen konu.",
    llmSummary: "Kadıköy'de 30 yıldır hizmet veren, Anadolu'nun unutulmaya yüz tutmuş yemeklerini sunan efsane lokanta. Orta fiyat aralığında, samimi atmosferiyle günlük değişen menüsüyle öne çıkıyor. Rezervasyon kabul etmiyor, erken gitmeniz öneriliyor.",
    lastUpdated: "2025-04-04",
    verifiedData: true,
    confidenceScore: 0.97,
  },
  {
    id: "2",
    slug: "mikla",
    name: "Mikla",
    city: "İstanbul",
    citySlug: "istanbul",
    neighborhood: "Beyoğlu",
    cuisine: "Modern Türk, Fine Dining",
    priceRange: 4,
    avgRating: 4.6,
    reviewCount: 1800,
    address: "Meşrutiyet Cad. No:15, Marmara Pera Hotel, Beyoğlu, İstanbul",
    lat: 41.0332,
    lng: 28.9775,
    phone: "+90 212 293 56 56",
    website: "https://www.miklarestaurant.com",
    openingHours: "Mo-Su 18:00-00:00",
    features: { terrace: true, reservation: true, seaView: true, romantic: true },
    tags: ["panoramik manzara", "fine dining", "romantik", "boğaz manzarası", "özel gece"],
    sentimentSummary: "Yorumların %88'i manzarayı ve sunum kalitesini övüyor. %75'i özel geceler için öneriyor. Fiyat/performans konusunda görüşler ikiye bölünüyor.",
    llmSummary: "İstanbul silüetine karşı panoramik terası ve ödüllü mutfağıyla şehrin en prestijli restoranlarından biri. Akşam yemekleri için rezervasyon şart. Romantik buluşmalar ve özel günler için idealdir. Yüksek fiyat aralığında konumlanıyor.",
    lastUpdated: "2025-04-04",
    verifiedData: true,
    confidenceScore: 0.95,
  },
  {
    id: "3",
    slug: "hamdi-restaurant",
    name: "Hamdi Restaurant",
    city: "İstanbul",
    citySlug: "istanbul",
    neighborhood: "Eminönü",
    cuisine: "Türk, Kebap",
    priceRange: 3,
    avgRating: 4.5,
    reviewCount: 5600,
    address: "Kalçın Sk. No:17, Eminönü, İstanbul",
    lat: 41.0172,
    lng: 28.9703,
    phone: "+90 212 528 03 90",
    website: "https://www.hamdi.com.tr",
    openingHours: "Mo-Su 11:30-23:30",
    features: { terrace: true, reservation: true, seaView: true, parking: false },
    tags: ["altın boynuz manzarası", "kebap", "turistik", "tarihî yarımada", "et"],
    sentimentSummary: "Yorumların %85'i manzara ve kebap kalitesini övüyor. Turistik lokasyon nedeniyle servis hızı zaman zaman eleştiriliyor. Akşam rezervasyonu kesinlikle öneriliyor.",
    llmSummary: "Eminönü'nde Altın Boynuz manzaralı teras katıyla İstanbul'un en ikonik kebapçılarından biri. Türk mutfağının klasiklerini sunuyor. Turistler ve yerel halk tarafından birlikte tercih edilen, orta-üst fiyat aralığında bir mekan.",
    lastUpdated: "2025-04-04",
    verifiedData: true,
    confidenceScore: 0.93,
  },
  {
    id: "4",
    slug: "karakoy-lokantasi",
    name: "Karaköy Lokantası",
    city: "İstanbul",
    citySlug: "istanbul",
    neighborhood: "Karaköy",
    cuisine: "Türk, Deniz Ürünleri",
    priceRange: 3,
    avgRating: 4.7,
    reviewCount: 2100,
    address: "Kemeraltı Cad. No:37A, Karaköy, İstanbul",
    lat: 41.0233,
    lng: 28.9752,
    openingHours: "Mo-Sa 12:00-23:00",
    features: { reservation: true, wifi: true, romantic: false },
    tags: ["deniz ürünleri", "karaköy", "şık", "balık", "meyhane"],
    sentimentSummary: "Yorumların %90'ı taze balık ve deniz ürünlerini övüyor. Mekan atmosferi sıkça beğeni alıyor. Hafta sonları dolup taşıyor, rezervasyon şart.",
    llmSummary: "Karaköy'ün kalbinde, taze Boğaz balıklarıyla öne çıkan şık bir lokanta. Deniz ürünleri konusunda şehrin referans noktalarından biri. Haftalık değişen menüsüyle mevsimselliğe önem veriyor. Öğle ve akşam yemekleri için rezervasyon önerilir.",
    lastUpdated: "2025-04-04",
    verifiedData: true,
    confidenceScore: 0.94,
  },
  {
    id: "5",
    slug: "under-istanbul",
    name: "Under İstanbul",
    city: "İstanbul",
    citySlug: "istanbul",
    neighborhood: "Galata",
    cuisine: "Fusion, Modern Avrupa",
    priceRange: 4,
    avgRating: 4.4,
    reviewCount: 980,
    address: "Galata, Beyoğlu, İstanbul",
    lat: 41.026,
    lng: 28.974,
    openingHours: "Tu-Su 18:00-23:30",
    features: { reservation: true, romantic: true, wifi: true },
    tags: ["deneyimsel yemek", "modern", "galata", "tasting menu", "gizli mekan"],
    sentimentSummary: "Yorumların %80'i yenilikçi sunumları ve ambiyansı övüyor. Tasting menu deneyimi en beğenilen yön. Fiyat beklentiden yüksek bulanlar var.",
    llmSummary: "Galata'da saklı, deneyimsel tasting menu'sü ile öne çıkan modern fusion restoran. Özel geceler ve gastronomi tutkunları için biçilmiş kaftan. Rezervasyon zorunlu, fiyat aralığı premium. Pazartesi kapalı.",
    lastUpdated: "2025-04-04",
    verifiedData: false,
    confidenceScore: 0.82,
  },
];

export function getRestaurantBySlug(citySlug: string, slug: string) {
  return restaurants.find(r => r.citySlug === citySlug && r.slug === slug);
}

export function getRestaurantsByCity(citySlug: string) {
  return restaurants.filter(r => r.citySlug === citySlug);
}

export function getAllSlugs() {
  return restaurants.map(r => ({ city: r.citySlug, slug: r.slug }));
}

export function getPriceSymbol(range: number) {
  return "₺".repeat(range);
}

// Mahalle adindan URL slug'i uret (TR karakterleri normalize et)
export function slugifyNeighborhood(name: string): string {
  const map: Record<string, string> = {
    "ş": "s", "ç": "c", "ğ": "g", "ü": "u", "ö": "o", "ı": "i",
    "â": "a", "î": "i", "û": "u",
    "Ş": "s", "Ç": "c", "Ğ": "g", "Ü": "u", "Ö": "o", "İ": "i", "I": "i",
  };
  let s = name;
  for (const [k, v] of Object.entries(map)) s = s.split(k).join(v);
  s = s.toLowerCase()
    .replace(/mahallesi/g, "")
    .replace(/[^a-z0-9\s-]/g, "")
    .trim()
    .replace(/\s+/g, "-")
    .replace(/-+/g, "-");
  return s;
}

// Bayesian weighted score: puan + yorum sayısını birleştirir.
// Düşük yorumlu restoranlar küresel ortalamayla dengelenir.
const GLOBAL_AVG = 4.3;
const MIN_VOTES  = 80;  // bu kadar yorum olmadan tam güven verilmez

export function weightedScore(r: { avgRating?: number; reviewCount?: number }): number {
  const rating = r.avgRating  ?? 0;
  const votes  = r.reviewCount ?? 0;
  return (votes * rating + MIN_VOTES * GLOBAL_AVG) / (votes + MIN_VOTES);
}

export function getRestaurantsByNeighborhood(citySlug: string, hoodSlug: string) {
  return restaurants.filter(
    r => r.citySlug === citySlug && slugifyNeighborhood(r.neighborhood) === hoodSlug
  );
}

export function getRestaurantsByCuisine(citySlug: string, cuisineSlug: string) {
  return restaurants.filter(
    r => r.citySlug === citySlug && r.cuisineSlug === cuisineSlug
  );
}

export function getAllCuisines(citySlug: string) {
  const map = new Map<string, { slug: string; name: string; count: number }>();
  for (const r of restaurants) {
    if (r.citySlug !== citySlug || !r.cuisineSlug) continue;
    const existing = map.get(r.cuisineSlug);
    if (existing) existing.count += 1;
    else map.set(r.cuisineSlug, { slug: r.cuisineSlug, name: r.cuisine, count: 1 });
  }
  return Array.from(map.values()).sort((a, b) => b.count - a.count);
}

export function getRestaurantsByTag(citySlug: string, tag: string) {
  return restaurants.filter(
    r => r.citySlug === citySlug && r.tags.some(t => t.toLowerCase().includes(tag.toLowerCase()))
  );
}

import neighborhoodToDistrict from "./neighborhood_to_district.json";

const hoodDistrictMap = neighborhoodToDistrict as Record<string, string>;

export function slugifyDistrict(name: string): string {
  const map: Record<string, string> = {
    "ş": "s", "ç": "c", "ğ": "g", "ü": "u", "ö": "o", "ı": "i",
    "â": "a", "î": "i", "û": "u",
    "Ş": "s", "Ç": "c", "Ğ": "g", "Ü": "u", "Ö": "o", "İ": "i", "I": "i",
  };
  let s = name;
  for (const [k, v] of Object.entries(map)) s = s.split(k).join(v);
  return s.toLowerCase().replace(/[^a-z0-9-]/g, "-").replace(/-+/g, "-").replace(/^-|-$/g, "");
}

export function getDistrictForRestaurant(r: Restaurant): string {
  return hoodDistrictMap[r.neighborhood] || "";
}

export function getAllDistricts(citySlug: string) {
  const map = new Map<string, { slug: string; name: string; count: number }>();
  for (const r of restaurants) {
    if (r.citySlug !== citySlug) continue;
    const district = hoodDistrictMap[r.neighborhood];
    if (!district) continue;
    const slug = slugifyDistrict(district);
    const existing = map.get(slug);
    if (existing) existing.count += 1;
    else map.set(slug, { slug, name: district, count: 1 });
  }
  return Array.from(map.values()).sort((a, b) => b.count - a.count);
}

export function getRestaurantsByDistrict(citySlug: string, districtSlug: string) {
  return restaurants.filter(r => {
    if (r.citySlug !== citySlug) return false;
    const district = hoodDistrictMap[r.neighborhood];
    return district && slugifyDistrict(district) === districtSlug;
  });
}

export function getAllNeighborhoods(citySlug: string) {
  const map = new Map<string, { slug: string; name: string; count: number }>();
  for (const r of restaurants) {
    if (r.citySlug !== citySlug || !r.neighborhood) continue;
    const slug = slugifyNeighborhood(r.neighborhood);
    if (!slug) continue;
    const existing = map.get(slug);
    if (existing) existing.count += 1;
    else map.set(slug, { slug, name: r.neighborhood, count: 1 });
  }
  return Array.from(map.values()).sort((a, b) => b.count - a.count);
}
