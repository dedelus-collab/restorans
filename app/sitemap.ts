import { MetadataRoute } from "next";
import { restaurants, getAllNeighborhoods } from "@/data/restaurants";
import { COLLECTIONS } from "@/lib/collections";

export default function sitemap(): MetadataRoute.Sitemap {
  const base = "https://restaurantsistanbul.vercel.app";

  const cities = [...new Set(restaurants.map(r => r.citySlug))];

  const cityPages = cities.map(city => ({
    url: `${base}/${city}`,
    lastModified: new Date(),
    changeFrequency: "weekly" as const,
    priority: 0.8,
  }));

  const collectionPages = COLLECTIONS.map(c => ({
    url: `${base}/istanbul/liste/${c.slug}`,
    lastModified: new Date(),
    changeFrequency: "weekly" as const,
    priority: 0.8,
  }));

  const neighborhoodPages = cities.flatMap(city =>
    getAllNeighborhoods(city)
      .filter(n => n.count >= 2)
      .map(n => ({
        url: `${base}/${city}/mahalle/${n.slug}`,
        lastModified: new Date(),
        changeFrequency: "weekly" as const,
        priority: 0.7,
      }))
  );

  const restaurantPages = restaurants.map(r => ({
    url: `${base}/${r.citySlug}/${r.slug}`,
    lastModified: r.lastUpdated ? new Date(r.lastUpdated) : new Date(),
    changeFrequency: "weekly" as const,
    priority: 0.9,
  }));

  return [
    { url: base, lastModified: new Date(), changeFrequency: "daily", priority: 1 },
    { url: `${base}/hakkinda`, lastModified: new Date(), changeFrequency: "monthly", priority: 0.5 },
    ...cityPages,
    ...collectionPages,
    ...neighborhoodPages,
    ...restaurantPages,
  ];
}
