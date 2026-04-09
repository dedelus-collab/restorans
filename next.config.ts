import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Kısa / alternatif slug yönlendirmeleri
  async redirects() {
    return [
      { source: "/:city/liste/balik-istanbul",          destination: "/:city/liste/balik-deniz-urunleri-istanbul", permanent: true },
      { source: "/:city/liste/deniz-urunleri-istanbul", destination: "/:city/liste/balik-deniz-urunleri-istanbul", permanent: true },
      { source: "/:city/liste/pizza-istanbul",          destination: "/:city/liste/pizza-italyan-istanbul",        permanent: true },
      { source: "/:city/liste/italyan-mutfagi-istanbul",destination: "/:city/liste/italyan-istanbul",              permanent: true },
      { source: "/:city/liste/japon-istanbul",          destination: "/:city/liste/sushi-japon-istanbul",          permanent: true },
      { source: "/:city/liste/sushi-istanbul",          destination: "/:city/liste/sushi-japon-istanbul",          permanent: true },
      { source: "/:city/liste/burger-istanbul",         destination: "/:city/liste/burger-steak-istanbul",         permanent: true },
      { source: "/:city/liste/steak-istanbul",          destination: "/:city/liste/burger-steak-istanbul",         permanent: true },
      { source: "/:city/liste/vegan-istanbul",          destination: "/:city/liste/vejetaryen-vegan-istanbul",     permanent: true },
      { source: "/:city/liste/vejetaryen-istanbul",     destination: "/:city/liste/vejetaryen-vegan-istanbul",     permanent: true },
      { source: "/:city/liste/brunch-istanbul",         destination: "/:city/liste/kahvalti-istanbul",             permanent: true },
      { source: "/:city/liste/kahve-istanbul",          destination: "/:city/liste/kafe-istanbul",                 permanent: true },
    ];
  },

  // Güvenlik başlıkları
  async headers() {
    return [
      {
        source: "/api/:path*",
        headers: [
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "X-Frame-Options", value: "DENY" },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
        ],
      },
    ];
  },

  // Gereksiz X-Powered-By header'ını kaldır
  poweredByHeader: false,

  // Trailing slash tutarlılığı
  trailingSlash: false,
};

export default nextConfig;
