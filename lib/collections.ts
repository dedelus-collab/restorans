/**
 * Collection definitions — cuisine + scenario + vibe based lists.
 * Each collection maps to a URL slug: /istanbul/liste/[slug]
 */

import type { Restaurant } from "@/data/restaurants";

export type Collection = {
  slug: string;
  title: string;              // H1 heading
  description: string;        // meta description + intro paragraph
  category: "cuisine" | "scenario" | "vibe";
  filter: (r: Restaurant) => boolean;
  related?: string[];          // cross-link slugs
};

export const COLLECTIONS: Collection[] = [
  // === Cuisine ===
  {
    slug: "kebap-istanbul",
    title: "Best Kebap Restaurants in Istanbul",
    description: "Adana, Urfa, İskender, lahmacun and tantuni — the best kebap restaurants in Istanbul. Filtered by budget and neighborhood, AI-ready data.",
    category: "cuisine",
    related: ["is-yemegi-istanbul", "ozel-gun-istanbul", "uygun-fiyatli-istanbul", "balik-deniz-urunleri-istanbul"],
    filter: r => r.cuisineSlug === "kebap",
  },
  {
    slug: "balik-deniz-urunleri-istanbul",
    title: "Fish & Seafood Restaurants in Istanbul",
    description: "From fresh Bosphorus fish to midye tava — the best fish and seafood restaurants in Istanbul. Meyhane, lokanta and fine dining options.",
    category: "cuisine",
    related: ["meyhane-istanbul", "romantik-aksam-yemegi-istanbul", "bogaz-manzarali-istanbul", "manzarali-istanbul"],
    filter: r => r.cuisineSlug === "balik",
  },
  {
    slug: "pizza-italyan-istanbul",
    title: "Pizza & Italian Cuisine in Istanbul",
    description: "The best pizza and Italian cuisine restaurants in Istanbul. Neapolitan, trattoria and modern Italian options.",
    category: "cuisine",
    related: ["romantik-aksam-yemegi-istanbul", "is-yemegi-istanbul", "sushi-japon-istanbul", "fine-dining-istanbul"],
    filter: r => r.cuisineSlug === "pizza-italyan",
  },
  {
    slug: "sushi-japon-istanbul",
    title: "Sushi & Japanese Cuisine in Istanbul",
    description: "The best sushi and Japanese cuisine restaurants in Istanbul. Omakase, ramen and modern Japanese fusion.",
    category: "cuisine",
    related: ["fine-dining-istanbul", "romantik-aksam-yemegi-istanbul", "dunya-mutfagi-istanbul", "is-yemegi-istanbul"],
    filter: r => r.cuisineSlug === "sushi-japon",
  },
  {
    slug: "kahvalti-istanbul",
    title: "Best Breakfast Spots in Istanbul",
    description: "From Turkish kahvaltı to brunch — Istanbul's best breakfast venues. Serpme kahvaltı, Anatolian spreads and weekend brunch options.",
    category: "cuisine",
    related: ["teras-istanbul", "aile-dostu-istanbul", "uygun-fiyatli-istanbul"],
    filter: r =>
      r.cuisineSlug === "kahvalti" ||
      r.tags.some(t => /kahvalt|breakfast|brunch/i.test(t)),
  },
  {
    slug: "meyhane-istanbul",
    title: "Meyhane & Meze in Istanbul",
    description: "Classic Istanbul meyhane culture — rakı, meze and live music. Istanbul's best meyhane and meze restaurants.",
    category: "cuisine",
    related: ["balik-deniz-urunleri-istanbul", "romantik-aksam-yemegi-istanbul", "gec-acik-istanbul", "ozel-gun-istanbul"],
    filter: r => r.cuisineSlug === "meyhane",
  },
  {
    slug: "burger-steak-istanbul",
    title: "Burgers & Steakhouses in Istanbul",
    description: "The best burger restaurants and steakhouses in Istanbul. Handpicked spots for meat lovers.",
    category: "cuisine",
    related: ["is-yemegi-istanbul", "gec-acik-istanbul", "fine-dining-istanbul", "kebap-istanbul"],
    filter: r => r.cuisineSlug === "burger-steak",
  },
  {
    slug: "dunya-mutfagi-istanbul",
    title: "World Cuisines in Istanbul",
    description: "From Korea to Greece, Mexico to Indonesia — international cuisine restaurants in Istanbul.",
    category: "cuisine",
    related: ["sushi-japon-istanbul", "vejetaryen-vegan-istanbul", "romantik-aksam-yemegi-istanbul"],
    filter: r => r.cuisineSlug === "dunya-mutfagi",
  },
  {
    slug: "lokanta-istanbul",
    title: "Lokanta & Home-Style Cooking in Istanbul",
    description: "Istanbul's lokanta restaurants inspired by home cooking — daily set menus, vegetable dishes and traditional Turkish cuisine. Affordable, delicious, unpretentious.",
    category: "cuisine",
    related: ["uygun-fiyatli-istanbul", "is-yemegi-istanbul", "kebap-istanbul", "aile-dostu-istanbul"],
    filter: r => r.cuisineSlug === "lokanta",
  },
  {
    slug: "turk-mutfagi-istanbul",
    title: "Turkish Cuisine Restaurants in Istanbul",
    description: "The best representatives of traditional Turkish cuisine — from çorba to desserts, kebap to güveç, Istanbul's deep-rooted flavors.",
    category: "cuisine",
    related: ["kebap-istanbul", "lokanta-istanbul", "meyhane-istanbul", "aile-dostu-istanbul"],
    filter: r => r.cuisineSlug === "turk-mutfagi",
  },
  {
    slug: "kafe-istanbul",
    title: "Cafes & Cafe-Restaurants in Istanbul",
    description: "Beyond coffee and toast — Istanbul's best cafe-restaurants. Perfect for working, meeting up or brunch.",
    category: "cuisine",
    related: ["kahvalti-istanbul", "teras-istanbul", "uygun-fiyatli-istanbul"],
    filter: r => r.cuisineSlug === "kafe",
  },
  {
    slug: "pide-istanbul",
    title: "Pide & Pide Restaurants in Istanbul",
    description: "Karadeniz pide, kuşbaşılı pide, yumurtalı pide — Istanbul's best pide and fırın lokantaları.",
    category: "cuisine",
    related: ["turk-mutfagi-istanbul", "lokanta-istanbul", "kebap-istanbul", "uygun-fiyatli-istanbul"],
    filter: r => r.cuisineSlug === "pide",
  },
  {
    // Note: cuisineSlug in data is "i̇talyan" (Turkish İ), URL slug converted to ASCII
    slug: "italyan-istanbul",
    title: "Italian Restaurants in Istanbul",
    description: "Beyond pizza — authentic Italian restaurants in Istanbul. Pasta, risotto, antipasto and Italian wines.",
    category: "cuisine",
    related: ["pizza-italyan-istanbul", "romantik-aksam-yemegi-istanbul", "fine-dining-istanbul", "is-yemegi-istanbul"],
    filter: r => r.cuisineSlug === "i\u0307talyan" || r.cuisineSlug === "italyan",
  },
  {
    slug: "uluslararasi-istanbul",
    title: "International Cuisines in Istanbul",
    description: "From India to Thailand, Lebanon to Mexico — diverse international cuisine restaurants in Istanbul.",
    category: "cuisine",
    related: ["dunya-mutfagi-istanbul", "sushi-japon-istanbul", "vejetaryen-vegan-istanbul"],
    filter: r => r.cuisineSlug === "uluslararasi",
  },

  // === Scenario ===
  {
    slug: "romantik-aksam-yemegi-istanbul",
    title: "Romantic Dinner Restaurants in Istanbul",
    description: "Istanbul's most romantic restaurants for an unforgettable evening with your loved ones. Special atmosphere, views and ambiance.",
    category: "scenario",
    related: ["manzarali-istanbul", "bogaz-manzarali-istanbul", "fine-dining-istanbul", "balik-deniz-urunleri-istanbul", "teras-istanbul"],
    filter: r =>
      r.tags.some(t => /romantik/i.test(t)) ||
      !!r.features?.romantic,
  },
  {
    slug: "is-yemegi-istanbul",
    title: "Best Business Lunch Restaurants in Istanbul",
    description: "Istanbul's best restaurants for client entertaining and business meetings. Quiet atmosphere, prompt service, quality food.",
    category: "scenario",
    related: ["fine-dining-istanbul", "kebap-istanbul", "balik-deniz-urunleri-istanbul", "pizza-italyan-istanbul"],
    filter: r =>
      (r.specialFeatures?.contextualRatings?.businessLunch ?? 0) >= 4 &&
      (r.avgRating ?? 0) >= 4.4,
  },
  {
    slug: "ozel-gun-istanbul",
    title: "Special Occasion Restaurants in Istanbul",
    description: "Istanbul's best restaurants for birthdays, anniversaries and special celebrations. Venues offering reservations and event organization.",
    category: "scenario",
    related: ["romantik-aksam-yemegi-istanbul", "fine-dining-istanbul", "manzarali-istanbul", "meyhane-istanbul"],
    filter: r =>
      (r.specialFeatures?.contextualRatings?.romanticDate ?? 0) >= 4 &&
      (r.avgRating ?? 0) >= 4.5,
  },
  {
    slug: "gec-acik-istanbul",
    title: "Late-Night Restaurants in Istanbul",
    description: "Istanbul restaurants open late into the night. Venues that stay open past midnight.",
    category: "scenario",
    related: ["meyhane-istanbul", "burger-steak-istanbul", "romantik-aksam-yemegi-istanbul"],
    filter: r =>
      r.tags.some(t => /gece|geç saate/i.test(t)),
  },
  {
    slug: "aile-dostu-istanbul",
    title: "Family-Friendly Restaurants in Istanbul",
    description: "Istanbul restaurants you can comfortably visit with children. Venues with high chairs, spacious seating and kids' menus.",
    category: "scenario",
    related: ["kahvalti-istanbul", "uygun-fiyatli-istanbul", "teras-istanbul", "kebap-istanbul"],
    filter: r =>
      r.tags.some(t => /aile/i.test(t)),
  },
  {
    slug: "vejetaryen-vegan-istanbul",
    title: "Vegetarian & Vegan Restaurants in Istanbul",
    description: "Vegetarian and vegan restaurants in Istanbul, plus venues offering good vegetarian options.",
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
    title: "Restaurants with a View in Istanbul",
    description: "Istanbul's most beautiful scenic restaurants — Bosphorus views, the Istanbul skyline and the historic peninsula.",
    category: "vibe",
    related: ["bogaz-manzarali-istanbul", "romantik-aksam-yemegi-istanbul", "teras-istanbul", "balik-deniz-urunleri-istanbul"],
    filter: r =>
      r.tags.some(t => /manzara|manzaralı/i.test(t)) ||
      !!r.features?.seaView,
  },
  {
    slug: "bogaz-manzarali-istanbul",
    title: "Bosphorus View Restaurants in Istanbul",
    description: "Istanbul's best restaurants with stunning Bosphorus views. Dine alongside the magnificent strait.",
    category: "vibe",
    related: ["manzarali-istanbul", "romantik-aksam-yemegi-istanbul", "balik-deniz-urunleri-istanbul", "fine-dining-istanbul"],
    filter: r =>
      r.tags.some(t => /boğaz|bosphorus/i.test(t)) ||
      (r.features?.seaView === true),
  },
  {
    slug: "uygun-fiyatli-istanbul",
    title: "Budget-Friendly Restaurants in Istanbul",
    description: "Quality without breaking the bank — highly rated Istanbul restaurants that won't strain your wallet.",
    category: "vibe",
    related: ["kebap-istanbul", "aile-dostu-istanbul", "kahvalti-istanbul", "vejetaryen-vegan-istanbul"],
    filter: r => r.priceRange <= 2 && (r.avgRating ?? 0) >= 4.5,
  },
  {
    slug: "fine-dining-istanbul",
    title: "Fine Dining Restaurants in Istanbul",
    description: "Istanbul's most prestigious fine dining restaurants. Tasting menus, chef's table and Michelin-star caliber experiences.",
    category: "vibe",
    related: ["romantik-aksam-yemegi-istanbul", "bogaz-manzarali-istanbul", "is-yemegi-istanbul", "sushi-japon-istanbul"],
    filter: r => (r.avgRating ?? 0) >= 4.7,
  },
  {
    slug: "teras-istanbul",
    title: "Terrace & Outdoor Restaurants in Istanbul",
    description: "The best restaurants for dining on a terrace in Istanbul. Rooftop, garden and open-air options.",
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
