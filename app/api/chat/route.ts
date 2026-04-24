import { NextRequest, NextResponse } from "next/server";
import Groq from "groq-sdk";
import { restaurants, weightedScore } from "@/data/restaurants";

let client: Groq | null = null;
function getClient() {
  if (!client) client = new Groq({ apiKey: process.env.GROQ_API_KEY });
  return client;
}

// Smart keyword-based restaurant selector
function selectRelevantRestaurants(query: string) {
  const q = query.toLowerCase();

  const scored = restaurants.map(r => {
    let score = 0;

    // Cuisine
    if (/kebap|kebab|adana|iskender|lahmacun/.test(q) && r.cuisineSlug === "kebap") score += 10;
    if (/fish|seafood|balik|balık|sushi|deniz/.test(q) && r.cuisineSlug === "balik") score += 10;
    if (/breakfast|kahvaltı|kahvalti|brunch/.test(q) && r.cuisineSlug === "kahvalti") score += 10;
    if (/sushi|japanese|japon|ramen/.test(q) && r.cuisineSlug === "sushi-japon") score += 10;
    if (/pizza|italian|italyan/.test(q) && r.cuisineSlug === "pizza-italyan") score += 10;
    if (/meyhane|meze|raki|rakı/.test(q) && r.cuisineSlug === "meyhane") score += 10;
    if (/burger|steak|et/.test(q) && r.cuisineSlug === "burger-steak") score += 10;
    if (/vegan|vegetarian|vejetaryen/.test(q) && r.cuisineSlug === "vegan") score += 10;
    if (/pide|lahmacun/.test(q) && r.cuisineSlug === "pide") score += 10;

    // Scenario
    if (/romantic|date|candle|romantik|sevgili/.test(q) && r.tags.some(t => /romantik/i.test(t))) score += 8;
    if (/business|meeting|lunch|iş yemeği|toplantı/.test(q) && (r.specialFeatures?.contextualRatings?.businessLunch ?? 0) >= 4) score += 8;
    if (/family|çocuk|aile|kids/.test(q) && r.tags.some(t => /aile/i.test(t))) score += 8;
    if (/late|night|gece|geç|midnight/.test(q) && r.tags.some(t => /gece|geç saate/i.test(t))) score += 8;
    if (/special|birthday|anniversary|özel|doğum/.test(q) && (r.specialFeatures?.contextualRatings?.romanticDate ?? 0) >= 4) score += 8;

    // Features
    if (/view|scenic|manzara|bosphorus|boğaz|deniz/.test(q) && r.features?.seaView) score += 10;
    if (/terrace|outdoor|teras|açık hava|bahçe/.test(q) && r.features?.terrace) score += 8;
    if (/cheap|budget|affordable|uygun|ucuz/.test(q) && r.priceRange <= 2) score += 6;
    if (/fine dining|luxury|expensive|lüks|michelin/.test(q) && r.avgRating >= 4.7) score += 8;

    // Neighborhood
    const hoodKeywords: [RegExp, RegExp][] = [
      [/taksim/, /taksim/i],
      [/beşiktaş|besiktas/, /beşiktaş/i],
      [/kadıköy|kadiköy|kadikoy/, /kadıköy/i],
      [/ortaköy|ortakoy/, /ortaköy/i],
      [/sultanahmet|eminönü|eminonu/, /sultanahmet|eminönü/i],
      [/galata|beyoğlu|beyoglu/, /galata|beyoğlu/i],
      [/nişantaşı|nisantasi/, /nişantaşı/i],
      [/üsküdar|uskudar/, /üsküdar/i],
      [/bebek|etiler/, /bebek|etiler/i],
      [/moda/, /moda/i],
    ];
    for (const [queryRe, hoodRe] of hoodKeywords) {
      if (queryRe.test(q) && hoodRe.test(r.neighborhood ?? "")) score += 12;
    }

    // Rating boost
    score += (r.avgRating ?? 0) * 0.4;

    return { r, score };
  });

  const matched = scored.filter(x => x.score > 1).sort((a, b) => b.score - a.score).slice(0, 15).map(x => x.r);

  // Fallback: top-rated
  if (matched.length === 0) {
    return [...restaurants].sort((a, b) => weightedScore(b) - weightedScore(a)).slice(0, 10);
  }
  return matched;
}

function buildContext(list: typeof restaurants): string {
  return list.map(r => {
    const price = ["₺", "₺₺", "₺₺₺", "₺₺₺₺"][r.priceRange - 1] ?? "₺₺";
    const features = [
      r.features?.seaView && "sea view",
      r.features?.terrace && "terrace",
      r.features?.vegan && "vegan options",
      r.features?.reservations && "reservations",
    ].filter(Boolean).join(", ");
    const dishes = r.specialFeatures?.popularDishes?.slice(0, 3).join(", ");
    return [
      `**${r.name}** — ${r.neighborhood} | ${r.cuisine} | ${price} | ⭐${r.avgRating} (${r.reviewCount} reviews)`,
      `Summary: ${r.llmSummary}`,
      dishes ? `Popular dishes: ${dishes}` : null,
      features ? `Features: ${features}` : null,
      `Link: /${r.citySlug}/${r.slug}`,
    ].filter(Boolean).join("\n");
  }).join("\n\n---\n\n");
}

export async function POST(req: NextRequest) {
  const { message, history = [] } = await req.json();

  if (!message?.trim()) return NextResponse.json({ error: "No message" }, { status: 400 });
  if (!process.env.GROQ_API_KEY) return NextResponse.json({ error: "API key not configured" }, { status: 500 });

  const groq = getClient();
  const relevant = selectRelevantRestaurants(message);
  const context = buildContext(relevant);

  const systemPrompt = `You are a friendly and knowledgeable Istanbul restaurant guide assistant on restaurantsistanbul.com. You help users find the perfect restaurant.

You have access to a database of ${restaurants.length} Istanbul restaurants. Here are the most relevant restaurants for this query:

${context}

Rules:
- Recommend 2–3 specific restaurants with concrete reasons why they fit the request.
- Mention neighborhood, price range (₺=budget, ₺₺=mid, ₺₺₺=upscale, ₺₺₺₺=luxury), rating, and popular dishes.
- Always include the restaurant page link as a markdown link, e.g. [Restaurant Name](/istanbul/restaurant-slug), so the user can click to see full details.
- Be concise and conversational. No long bullet lists.
- Answer in the same language the user writes in (Turkish or English).
- If asked about a specific restaurant, share everything you know from the data.
- Don't invent information not present in the data.`;

  const messages = [
    ...(history as { role: string; content: string }[])
      .slice(-8)
      .map(m => ({ role: m.role as "user" | "assistant", content: m.content })),
    { role: "user" as const, content: message },
  ];

  const stream = await groq.chat.completions.create({
    model: "llama-3.3-70b-versatile",
    max_tokens: 600,
    stream: true,
    messages: [
      { role: "system", content: systemPrompt },
      ...messages,
    ],
  });

  const encoder = new TextEncoder();
  const readable = new ReadableStream({
    async start(controller) {
      for await (const chunk of stream) {
        const text = chunk.choices[0]?.delta?.content ?? "";
        if (text) controller.enqueue(encoder.encode(text));
      }
      controller.close();
    },
  });

  return new NextResponse(readable, {
    headers: {
      "Content-Type": "text/plain; charset=utf-8",
      "Cache-Control": "no-cache",
    },
  });
}
