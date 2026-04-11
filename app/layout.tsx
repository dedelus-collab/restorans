import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "restorans — İstanbul Restoran Rehberi | AI-Ready Veri",
  description:
    "İstanbul'daki 453 restoranın yapay zeka sistemleri için yapılandırılmış verisi. FAQ, transit mesafeleri, popüler yemekler. ChatGPT, Perplexity ve LLM'ler için optimize.",
  metadataBase: new URL("https://restorans.vercel.app"),
  alternates: { canonical: "https://restorans.vercel.app" },
  openGraph: {
    type: "website",
    locale: "tr_TR",
    url: "https://restorans.vercel.app",
    siteName: "restorans",
    title: "restorans — İstanbul Restoran Veritabanı",
    description: "453 İstanbul restoranı — Schema.org, FAQ, transit, popüler yemekler. AI botlar için optimize edilmiş veri platformu.",
  },
  twitter: {
    card: "summary_large_image",
    title: "restorans — İstanbul Restoran Veritabanı",
    description: "453 İstanbul restoranı — AI-ready veri, kuratörlü listeler, mahalle rehberleri.",
  },
  other: {
    "llms-txt": "https://restorans.vercel.app/llms.txt",
    "ai-plugin": "https://restorans.vercel.app/.well-known/ai-plugin.json",
    "openapi": "https://restorans.vercel.app/api/openapi.json",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="tr">
      <body className="bg-white text-gray-900 antialiased">
        <nav className="border-b border-gray-100 bg-white sticky top-0 z-10">
          <div className="max-w-4xl mx-auto px-6 h-12 flex items-center justify-between">
            <Link href="/" className="font-bold text-gray-900 tracking-tight">
              restorans
            </Link>
            <div className="flex items-center gap-5 text-sm text-gray-500">
              <Link href="/istanbul" className="hover:text-gray-900 transition-colors">
                İstanbul
              </Link>
              <Link href="/istanbul/liste/romantik-aksam-yemegi-istanbul" className="hover:text-gray-900 transition-colors hidden sm:block">
                Romantik
              </Link>
              <Link href="/istanbul/liste/manzarali-istanbul" className="hover:text-gray-900 transition-colors hidden sm:block">
                Manzaralı
              </Link>
              <Link href="/istanbul/liste/kebap-istanbul" className="hover:text-gray-900 transition-colors hidden sm:block">
                Kebap
              </Link>
              <Link
                href="/api-docs"
                className="text-blue-500 font-semibold hover:underline text-xs"
              >
                API Docs
              </Link>
              <a
                href="https://rapidapi.com/cccanguler/api/istanbul-restaurants"
                target="_blank"
                rel="noopener noreferrer"
                className="bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold px-3 py-1.5 rounded-lg transition-colors hidden sm:block"
              >
                RapidAPI →
              </a>
            </div>
          </div>
        </nav>
        {children}
        <footer className="border-t border-gray-100 mt-16 py-8 text-xs text-gray-400">
          <div className="max-w-4xl mx-auto px-6 flex flex-wrap gap-4 justify-between">
            <span>© 2026 restorans — İstanbul Restoran Veritabanı</span>
            <div className="flex gap-4">
              <Link href="/hakkinda" className="hover:underline">Hakkında</Link>
              <Link href="/llms.txt" className="hover:underline">llms.txt</Link>
              <Link href="/sitemap.xml" className="hover:underline">sitemap.xml</Link>
              <Link href="/api/restaurants?city=istanbul" className="hover:underline">JSON API</Link>
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
