import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

// In-memory rate limiter
// Not: Çoklu sunucu ortamında (Vercel, vb.) Upstash Redis kullanın
const rateLimitMap = new Map<string, { count: number; resetAt: number }>();

const WINDOW_MS = 60_000; // 1 dakika
const MAX_REQUESTS = parseInt(process.env.RATE_LIMIT_PER_MINUTE ?? "60", 10);

// Süresi geçmiş girdileri periyodik olarak temizle (memory leak önlemi)
let lastCleanup = Date.now();
function maybeCleanup() {
  const now = Date.now();
  if (now - lastCleanup < 5 * 60_000) return; // 5 dakikada bir
  for (const [key, entry] of rateLimitMap) {
    if (now > entry.resetAt) rateLimitMap.delete(key);
  }
  lastCleanup = now;
}

function getRateLimitKey(req: NextRequest): string {
  return (
    req.headers.get("x-rapidapi-key") ??
    req.headers.get("x-forwarded-for")?.split(",")[0].trim() ??
    "anonymous"
  );
}

function checkRateLimit(key: string): {
  allowed: boolean;
  remaining: number;
  resetAt: number;
} {
  const now = Date.now();
  const entry = rateLimitMap.get(key);

  if (!entry || now > entry.resetAt) {
    const resetAt = now + WINDOW_MS;
    rateLimitMap.set(key, { count: 1, resetAt });
    return { allowed: true, remaining: MAX_REQUESTS - 1, resetAt };
  }

  entry.count += 1;
  return {
    allowed: entry.count <= MAX_REQUESTS,
    remaining: Math.max(0, MAX_REQUESTS - entry.count),
    resetAt: entry.resetAt,
  };
}

const BOT_PATTERN = /GPTBot|OAI-SearchBot|ChatGPT-User|ClaudeBot|anthropic-ai|PerplexityBot|Googlebot|Google-Extended|bingbot|DuckDuckBot|YandexBot|Applebot|cohere-ai|AI2Bot|YouBot|CCBot|Diffbot|Amazonbot/i;

function logBotAccess(request: NextRequest) {
  const ua = request.headers.get("user-agent") ?? "";
  if (!BOT_PATTERN.test(ua)) return;
  const path = request.nextUrl.pathname + (request.nextUrl.search || "");
  const ip = request.headers.get("x-forwarded-for")?.split(",")[0].trim() ?? "-";
  console.log(`[BOT] ${new Date().toISOString()} | ${ua} | ${path} | ip:${ip}`);
}

export function proxy(request: NextRequest) {
  // Bot erişimini logla
  logBotAccess(request);

  // Türkçe birleştirici karakter (i + U+0307 = i%CC%87) URL'leri normalize et
  // Aksi halde x-next-cache-tags header'ında ERR_INVALID_CHAR hatası oluşur
  const path = request.nextUrl.pathname;
  if (path.includes("\u0307")) {
    const url = request.nextUrl.clone();
    url.pathname = path.replace(/\u0307/g, "");
    return NextResponse.redirect(url, 308);
  }

  // OPTIONS preflight isteklerini doğrulama olmadan geçir (CORS için gerekli)
  if (request.method === "OPTIONS") {
    return NextResponse.next();
  }

  // RapidAPI Proxy Secret doğrulaması
  // RapidAPI, isteklere X-RapidAPI-Proxy-Secret header'ı ekler
  // Bu secret'ı RapidAPI dashboard'undan alıp .env'e ekleyin
  const proxySecret = process.env.RAPIDAPI_PROXY_SECRET;
  if (proxySecret) {
    const incoming = request.headers.get("x-rapidapi-proxy-secret");
    if (incoming !== proxySecret) {
      return Response.json(
        { error: { code: "UNAUTHORIZED", message: "Bu API yalnızca RapidAPI üzerinden erişilebilir." } },
        {
          status: 401,
          headers: {
            "Access-Control-Allow-Origin": "*",
            "Content-Type": "application/json; charset=utf-8",
          },
        }
      );
    }
  }

  // Rate limiting
  maybeCleanup();
  const key = getRateLimitKey(request);
  const { allowed, remaining, resetAt } = checkRateLimit(key);
  const retryAfter = Math.ceil((resetAt - Date.now()) / 1000);

  if (!allowed) {
    return Response.json(
      {
        error: {
          code: "RATE_LIMIT_EXCEEDED",
          message: "Dakika başına istek limitine ulaştınız. Lütfen bekleyin.",
          details: { retry_after_seconds: retryAfter },
        },
      },
      {
        status: 429,
        headers: {
          "Access-Control-Allow-Origin": "*",
          "Content-Type": "application/json; charset=utf-8",
          "Retry-After": String(retryAfter),
          "X-RateLimit-Limit": String(MAX_REQUESTS),
          "X-RateLimit-Remaining": "0",
          "X-RateLimit-Reset": String(Math.ceil(resetAt / 1000)),
        },
      }
    );
  }

  const response = NextResponse.next();
  response.headers.set("X-RateLimit-Limit", String(MAX_REQUESTS));
  response.headers.set("X-RateLimit-Remaining", String(remaining));
  response.headers.set("X-RateLimit-Reset", String(Math.ceil(resetAt / 1000)));
  return response;
}

export const config = {
  // openapi.json spec herkese açık olmalı, auth dışında bırak
  matcher: "/api/((?!openapi\\.json).*)",
};
