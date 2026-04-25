"use client";
import { useState, useRef, useEffect } from "react";
import Link from "next/link";

type SearchEntry = {
  slug: string;
  name: string;
  cuisine: string;
  neighborhood: string;
  avgRating: number | null;
  priceRange: string | number;
};

export function SearchBar({ entries }: { entries: SearchEntry[] }) {
  const [query, setQuery] = useState("");
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  const results = query.trim().length < 2 ? [] : entries.filter(r => {
    const q = query.toLowerCase();
    return (
      r.name.toLowerCase().includes(q) ||
      r.cuisine.toLowerCase().includes(q) ||
      r.neighborhood.toLowerCase().includes(q)
    );
  }).slice(0, 7);

  useEffect(() => {
    function handler(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    }
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  return (
    <div ref={ref} className="relative w-full max-w-xl mx-auto">
      <div className="relative">
        <svg className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
          <circle cx="11" cy="11" r="8" /><path d="m21 21-4.35-4.35" />
        </svg>
        <input
          type="text"
          value={query}
          onChange={e => { setQuery(e.target.value); setOpen(true); }}
          onFocus={() => setOpen(true)}
          placeholder="Search restaurant, cuisine or neighborhood…"
          className="w-full pl-11 pr-4 py-3.5 border border-gray-200 rounded-xl text-sm bg-white shadow-sm focus:outline-none focus:border-gray-400 focus:ring-2 focus:ring-gray-100 transition-all"
        />
        {query && (
          <button onClick={() => { setQuery(""); setOpen(false); }} className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path d="M18 6 6 18M6 6l12 12"/></svg>
          </button>
        )}
      </div>

      {open && results.length > 0 && (
        <div className="absolute top-full mt-2 w-full bg-white border border-gray-200 rounded-xl shadow-lg z-50 overflow-hidden">
          {results.map(r => (
            <Link
              key={r.slug}
              href={`/istanbul/${r.slug}`}
              onClick={() => { setQuery(""); setOpen(false); }}
              className="flex items-center justify-between px-4 py-3 hover:bg-gray-50 transition-colors border-b border-gray-100 last:border-0"
            >
              <div>
                <div className="text-sm font-medium text-gray-900">{r.name}</div>
                <div className="text-xs text-gray-400 mt-0.5">{r.cuisine} · {r.neighborhood}</div>
              </div>
              <div className="text-right shrink-0 ml-4">
                {r.avgRating != null && (
                  <div className="text-sm font-semibold text-gray-700">★ {r.avgRating}</div>
                )}
              </div>
            </Link>
          ))}
          {query.trim().length >= 2 && (
            <Link
              href={`/istanbul`}
              onClick={() => setOpen(false)}
              className="block text-center text-xs text-blue-500 hover:text-blue-700 py-3 bg-gray-50"
            >
              Browse all restaurants →
            </Link>
          )}
        </div>
      )}

      {open && query.trim().length >= 2 && results.length === 0 && (
        <div className="absolute top-full mt-2 w-full bg-white border border-gray-200 rounded-xl shadow-lg z-50 px-4 py-5 text-center">
          <p className="text-sm text-gray-500">No results for <strong>{query}</strong></p>
          <Link href="/istanbul" className="text-xs text-blue-500 hover:underline mt-1 block">Browse all restaurants →</Link>
        </div>
      )}
    </div>
  );
}
