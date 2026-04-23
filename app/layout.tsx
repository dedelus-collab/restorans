import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "Istanbul Restaurants — AI-Ready Data",
  description:
    "Structured data for 453 Istanbul restaurants. FAQ, transit distances, popular dishes, curated lists — optimized for ChatGPT, Perplexity, and other AI systems.",
  metadataBase: new URL("https://restaurantsistanbul.vercel.app"),
  alternates: { canonical: "https://restaurantsistanbul.vercel.app" },
  openGraph: {
    type: "website",
    locale: "en_US",
    url: "https://restaurantsistanbul.vercel.app",
    siteName: "Istanbul Restaurants",
    title: "Istanbul Restaurants Database",
    description: "453 Istanbul restaurants — Schema.org, FAQ, transit, popular dishes. AI-optimized data platform.",
  },
  twitter: {
    card: "summary_large_image",
    title: "Istanbul Restaurants Database",
    description: "453 Istanbul restaurants — AI-ready data, curated lists, neighborhood guides.",
  },
  other: {
    "llms-txt": "https://restaurantsistanbul.vercel.app/llms.txt",
    "ai-plugin": "https://restaurantsistanbul.vercel.app/.well-known/ai-plugin.json",
    "openapi": "https://restaurantsistanbul.vercel.app/api/openapi.json",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-white text-gray-900 antialiased">
        <nav className="border-b border-gray-100 bg-white sticky top-0 z-10">
          <div className="max-w-4xl mx-auto px-6 h-12 flex items-center justify-between">
            <Link href="/" className="font-bold text-gray-900 tracking-tight">
              Istanbul Restaurants
            </Link>
            <div className="flex items-center gap-5 text-sm text-gray-500">
              <Link href="/istanbul" className="hover:text-gray-900 transition-colors">
                Istanbul
              </Link>
              <Link href="/istanbul/liste/romantik-aksam-yemegi-istanbul" className="hover:text-gray-900 transition-colors hidden sm:block">
                Romantic
              </Link>
              <Link href="/istanbul/liste/manzarali-istanbul" className="hover:text-gray-900 transition-colors hidden sm:block">
                Scenic
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
          <div className="max-w-4xl mx-auto px-6 space-y-4">
            {/* Status bar */}
            <div className="flex flex-wrap gap-4 items-center text-xs">
              <span className="flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-green-400 inline-block"></span>
                <span className="text-gray-500 font-medium">API Online</span>
              </span>
              <span className="text-gray-300">·</span>
              <span className="text-gray-500">Database last updated: <strong className="text-gray-600">April 2026</strong></span>
              <span className="text-gray-300">·</span>
              <span className="text-gray-500">453 restaurants · 78 neighborhoods · 25 collections</span>
              <span className="text-gray-300">·</span>
              <span className="text-gray-500">Data sources: OpenStreetMap + LLM enrichment</span>
            </div>
            {/* Links */}
            <div className="flex flex-wrap gap-4 justify-between">
              <span>© 2026 Istanbul Restaurants</span>
              <div className="flex gap-4">
                <Link href="/hakkinda" className="hover:underline">About</Link>
                <Link href="/api-docs" className="hover:underline">API Docs</Link>
                <Link href="/llms.txt" className="hover:underline">llms.txt</Link>
                <Link href="/sitemap.xml" className="hover:underline">sitemap.xml</Link>
                <Link href="/api/restaurants?city=istanbul" className="hover:underline">JSON API</Link>
              </div>
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
