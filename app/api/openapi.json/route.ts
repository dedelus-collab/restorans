import { NextResponse } from "next/server";

const CORS_HEADERS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type",
  "Cache-Control": "public, s-maxage=86400",
  "Content-Type": "application/json; charset=utf-8",
};

export async function OPTIONS() {
  return new NextResponse(null, { status: 204, headers: CORS_HEADERS });
}

export async function GET() {
  const spec = {
    openapi: "3.1.0",
    info: {
      title: "Istanbul Restaurants API",
      description:
        "Türkiye restoranlarına ait AI-ready, yapılandırılmış veri API'si. " +
        "Her restoran kaydı; LLM özeti, senaryo analizleri, SSS, yakın çevre transit ve landmark bilgileri içerir.",
      version: "1.0.0",
      contact: {
        email: "data@restorans.io",
      },
      license: {
        name: "CC BY 4.0",
        url: "https://creativecommons.org/licenses/by/4.0/",
      },
    },
    servers: [
      {
        url: "https://restorans.vercel.app",
        description: "Production",
      },
      {
        url: "http://localhost:3000",
        description: "Local development",
      },
    ],
    paths: {
      "/api/restaurants": {
        get: {
          summary: "Restoran listesi",
          description:
            "Filtreleme ve sayfalama destekli restoran listesi döner. " +
            "Şehir, mahalle, mutfak türü, fiyat aralığı, puan ve etiketlere göre filtrelenebilir.",
          operationId: "listRestaurants",
          tags: ["Restaurants"],
          parameters: [
            {
              name: "city",
              in: "query",
              description: "Şehir slug'ı (örn. 'istanbul')",
              schema: { type: "string", example: "istanbul" },
            },
            {
              name: "q",
              in: "query",
              description: "Restoran adına göre metin arama",
              schema: { type: "string", example: "Hamdi" },
            },
            {
              name: "neighborhood",
              in: "query",
              description: "Mahalle adı (kısmi eşleşme desteklenir)",
              schema: { type: "string", example: "Beyoğlu" },
            },
            {
              name: "cuisine",
              in: "query",
              description: "Mutfak türü (kısmi eşleşme desteklenir)",
              schema: { type: "string", example: "Türk" },
            },
            {
              name: "tags",
              in: "query",
              description: "Virgülle ayrılmış etiket listesi",
              schema: { type: "string", example: "manzarali,romantik" },
            },
            {
              name: "maxPrice",
              in: "query",
              description: "Maksimum fiyat aralığı (1=ekonomik, 2=orta, 3=üst, 4=lüks)",
              schema: { type: "integer", enum: [1, 2, 3, 4], example: 3 },
            },
            {
              name: "minRating",
              in: "query",
              description: "Minimum ortalama puan (0-5)",
              schema: { type: "number", minimum: 0, maximum: 5, example: 4.0 },
            },
            {
              name: "page",
              in: "query",
              description: "Sayfa numarası (1'den başlar)",
              schema: { type: "integer", minimum: 1, default: 1 },
            },
            {
              name: "limit",
              in: "query",
              description: "Sayfa başına sonuç sayısı (max 100)",
              schema: { type: "integer", minimum: 1, maximum: 100, default: 20 },
            },
          ],
          responses: {
            "200": {
              description: "Başarılı",
              content: {
                "application/json": {
                  schema: { $ref: "#/components/schemas/RestaurantListResponse" },
                },
              },
            },
            "400": { $ref: "#/components/responses/BadRequest" },
            "401": { $ref: "#/components/responses/Unauthorized" },
            "429": { $ref: "#/components/responses/RateLimitExceeded" },
            "500": { $ref: "#/components/responses/InternalError" },
          },
          security: [{ RapidAPIKey: [] }],
        },
      },
      "/api/restaurants/{id}": {
        get: {
          summary: "Restoran detayı",
          description:
            "Tek bir restoranın tam detayını döner. " +
            "ID veya slug ile sorgulama yapılabilir. " +
            "SSS, senaryo özetleri, yakın transit/landmark ve rezervasyon linkleri dahildir.",
          operationId: "getRestaurant",
          tags: ["Restaurants"],
          parameters: [
            {
              name: "id",
              in: "path",
              required: true,
              description: "Restoran ID'si veya slug'ı",
              schema: { type: "string", example: "pera-antakya" },
            },
          ],
          responses: {
            "200": {
              description: "Başarılı",
              content: {
                "application/json": {
                  schema: { $ref: "#/components/schemas/RestaurantDetailResponse" },
                },
              },
            },
            "400": { $ref: "#/components/responses/BadRequest" },
            "401": { $ref: "#/components/responses/Unauthorized" },
            "404": { $ref: "#/components/responses/NotFound" },
            "429": { $ref: "#/components/responses/RateLimitExceeded" },
            "500": { $ref: "#/components/responses/InternalError" },
          },
          security: [{ RapidAPIKey: [] }],
        },
      },
    },
    components: {
      securitySchemes: {
        RapidAPIKey: {
          type: "apiKey",
          in: "header",
          name: "X-RapidAPI-Key",
          description: "RapidAPI abonelik anahtarınız",
        },
      },
      schemas: {
        Coordinates: {
          type: "object",
          properties: {
            lat: { type: "number", example: 41.0309965 },
            lng: { type: "number", example: 28.9738993 },
          },
        },
        Features: {
          type: "object",
          properties: {
            terrace:     { type: "boolean" },
            parking:     { type: "boolean" },
            wifi:        { type: "boolean" },
            reservation: { type: "boolean" },
            romantic:    { type: "boolean" },
            seaView:     { type: "boolean" },
            liveMusic:   { type: "boolean" },
            vegan:       { type: "boolean" },
          },
        },
        ContextualRatings: {
          type: "object",
          description: "1-5 arasında senaryo bazlı puanlar",
          properties: {
            businessLunch: { type: "integer", minimum: 1, maximum: 5 },
            romanticDate:  { type: "integer", minimum: 1, maximum: 5 },
            familyDining:  { type: "integer", minimum: 1, maximum: 5 },
            soloVisit:     { type: "integer", minimum: 1, maximum: 5 },
            groupDining:   { type: "integer", minimum: 1, maximum: 5 },
          },
        },
        ScenarioSummary: {
          type: "object",
          description: "Farklı senaryolar için kısa metin özetleri",
          properties: {
            birthday:   { type: "string", nullable: true },
            budget:     { type: "string", nullable: true },
            vegetarian: { type: "string", nullable: true },
            quickLunch: { type: "string", nullable: true },
            tourist:    { type: "string", nullable: true },
            romantic:   { type: "string", nullable: true },
            family:     { type: "string", nullable: true },
            lateNight:  { type: "string", nullable: true },
          },
        },
        TransitItem: {
          type: "object",
          properties: {
            name:       { type: "string" },
            type:       { type: "string", enum: ["metro", "tramvay", "vapur", "otobüs"] },
            distance_m: { type: "integer" },
            walk_min:   { type: "integer" },
          },
        },
        LandmarkItem: {
          type: "object",
          properties: {
            name:       { type: "string" },
            type:       { type: "string" },
            distance_m: { type: "integer" },
            walk_min:   { type: "integer" },
          },
        },
        FaqItem: {
          type: "object",
          properties: {
            question: { type: "string" },
            answer:   { type: "string" },
          },
        },
        RestaurantSummary: {
          type: "object",
          properties: {
            id:               { type: "string" },
            slug:             { type: "string" },
            url:              { type: "string", format: "uri" },
            name:             { type: "string" },
            city:             { type: "string" },
            city_slug:        { type: "string" },
            neighborhood:     { type: "string" },
            cuisine:          { type: "string" },
            cuisine_slug:     { type: "string", nullable: true },
            price_range:      { type: "integer", minimum: 1, maximum: 4 },
            avg_rating:       { type: "number" },
            review_count:     { type: "integer" },
            address:          { type: "string" },
            coordinates:      { $ref: "#/components/schemas/Coordinates" },
            phone:            { type: "string", nullable: true },
            website:          { type: "string", nullable: true },
            opening_hours:    { type: "string", nullable: true },
            hours_estimated:  { type: "boolean" },
            features:         { $ref: "#/components/schemas/Features" },
            tags:             { type: "array", items: { type: "string" } },
            llm_summary:      { type: "string", nullable: true },
            sentiment_summary: { type: "string", nullable: true },
            popular_dishes:   { type: "array", items: { type: "string" } },
            confidence_score: { type: "number", minimum: 0, maximum: 1 },
            verified_data:    { type: "boolean" },
            last_updated:     { type: "string", format: "date" },
          },
        },
        RestaurantDetail: {
          allOf: [
            { $ref: "#/components/schemas/RestaurantSummary" },
            {
              type: "object",
              properties: {
                highlights:         { type: "array", items: { type: "string" } },
                dietary_options:    { type: "array", items: { type: "string" } },
                noise_level:        { type: "string", nullable: true },
                avg_meal_cost_try:  { type: "integer", nullable: true },
                contextual_ratings: { $ref: "#/components/schemas/ContextualRatings" },
                scenario_summary:   { $ref: "#/components/schemas/ScenarioSummary" },
                faq: {
                  type: "array",
                  items: { $ref: "#/components/schemas/FaqItem" },
                },
                nearby: {
                  type: "object",
                  nullable: true,
                  properties: {
                    transit: {
                      type: "array",
                      items: { $ref: "#/components/schemas/TransitItem" },
                    },
                    landmarks: {
                      type: "array",
                      items: { $ref: "#/components/schemas/LandmarkItem" },
                    },
                  },
                },
                reservation_links: {
                  type: "object",
                  nullable: true,
                  properties: {
                    googleMaps: { type: "string", nullable: true },
                    website:    { type: "string", nullable: true },
                  },
                },
              },
            },
          ],
        },
        ListMeta: {
          type: "object",
          properties: {
            total:        { type: "integer" },
            page:         { type: "integer" },
            limit:        { type: "integer" },
            total_pages:  { type: "integer" },
            has_next:     { type: "boolean" },
            has_prev:     { type: "boolean" },
            source:       { type: "string" },
            description:  { type: "string" },
            llms_txt:     { type: "string" },
            schema:       { type: "string" },
            last_updated: { type: "string", format: "date" },
          },
        },
        RestaurantListResponse: {
          type: "object",
          properties: {
            meta: { $ref: "#/components/schemas/ListMeta" },
            data: {
              type: "array",
              items: { $ref: "#/components/schemas/RestaurantSummary" },
            },
          },
        },
        RestaurantDetailResponse: {
          type: "object",
          properties: {
            meta: {
              type: "object",
              properties: {
                source:       { type: "string" },
                schema:       { type: "string" },
                last_updated: { type: "string", format: "date" },
              },
            },
            data: { $ref: "#/components/schemas/RestaurantDetail" },
          },
        },
        ApiError: {
          type: "object",
          properties: {
            error: {
              type: "object",
              properties: {
                code:    { type: "string" },
                message: { type: "string" },
                details: { type: "object", nullable: true },
              },
            },
          },
        },
      },
      responses: {
        BadRequest: {
          description: "Geçersiz parametre",
          content: {
            "application/json": {
              schema: { $ref: "#/components/schemas/ApiError" },
              example: {
                error: {
                  code: "INVALID_PARAM",
                  message: "'maxPrice' parametresi 1, 2, 3 veya 4 olmalıdır.",
                  details: { param: "maxPrice" },
                },
              },
            },
          },
        },
        Unauthorized: {
          description: "Yetkisiz erişim — geçerli RapidAPI anahtarı gerekli",
          content: {
            "application/json": {
              schema: { $ref: "#/components/schemas/ApiError" },
              example: {
                error: {
                  code: "UNAUTHORIZED",
                  message: "Bu API yalnızca RapidAPI üzerinden erişilebilir.",
                },
              },
            },
          },
        },
        NotFound: {
          description: "Kaynak bulunamadı",
          content: {
            "application/json": {
              schema: { $ref: "#/components/schemas/ApiError" },
              example: {
                error: {
                  code: "NOT_FOUND",
                  message: "'bilinmeyen-slug' ile eşleşen restoran bulunamadı.",
                },
              },
            },
          },
        },
        InternalError: {
          description: "Sunucu hatası",
          content: {
            "application/json": {
              schema: { $ref: "#/components/schemas/ApiError" },
              example: {
                error: {
                  code: "INTERNAL_ERROR",
                  message: "Beklenmeyen bir hata oluştu.",
                },
              },
            },
          },
        },
        RateLimitExceeded: {
          description: "İstek limiti aşıldı",
          headers: {
            "Retry-After":          { schema: { type: "integer" } },
            "X-RateLimit-Limit":    { schema: { type: "integer" } },
            "X-RateLimit-Remaining": { schema: { type: "integer" } },
            "X-RateLimit-Reset":    { schema: { type: "integer" } },
          },
          content: {
            "application/json": {
              schema: { $ref: "#/components/schemas/ApiError" },
              example: {
                error: {
                  code: "RATE_LIMIT_EXCEEDED",
                  message: "Dakika başına istek limitine ulaştınız. Lütfen bekleyin.",
                  retry_after_seconds: 42,
                },
              },
            },
          },
        },
      },
    },
    tags: [
      {
        name: "Restaurants",
        description: "Restoran listeleme ve detay endpointleri",
        externalDocs: {
          description: "llms.txt",
          url: "https://restorans.vercel.app/llms.txt",
        },
      },
    ],
    externalDocs: {
      description: "AI dokümantasyonu (llms.txt)",
      url: "https://restorans.vercel.app/llms.txt",
    },
  };

  return NextResponse.json(spec, { headers: CORS_HEADERS });
}
