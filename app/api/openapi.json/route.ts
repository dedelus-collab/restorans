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
        "AI-ready, structured data API for Istanbul restaurants. " +
        "Each restaurant record contains an LLM summary, scenario analyses, FAQ, nearby transit and landmark data.",
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
        url: "https://www.restaurantsistanbul.com",
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
          summary: "Restaurant list",
          description:
            "Returns a paginated, filterable list of restaurants. " +
            "Filter by city, neighborhood, cuisine type, price range, rating and tags.",
          operationId: "listRestaurants",
          tags: ["Restaurants"],
          parameters: [
            {
              name: "city",
              in: "query",
              description: "City slug (e.g. 'istanbul')",
              schema: { type: "string", example: "istanbul" },
            },
            {
              name: "q",
              in: "query",
              description: "Text search by restaurant name",
              schema: { type: "string", example: "Hamdi" },
            },
            {
              name: "neighborhood",
              in: "query",
              description: "Neighborhood name (partial match supported)",
              schema: { type: "string", example: "Beyoglu" },
            },
            {
              name: "cuisine",
              in: "query",
              description: "Cuisine type (partial match supported)",
              schema: { type: "string", example: "kebap" },
            },
            {
              name: "tags",
              in: "query",
              description: "Comma-separated tag list",
              schema: { type: "string", example: "manzarali,romantik" },
            },
            {
              name: "maxPrice",
              in: "query",
              description: "Maximum price range (1=budget, 2=mid, 3=upper, 4=luxury)",
              schema: { type: "integer", enum: [1, 2, 3, 4], example: 3 },
            },
            {
              name: "minRating",
              in: "query",
              description: "Minimum average rating (0-5)",
              schema: { type: "number", minimum: 0, maximum: 5, example: 4.0 },
            },
            {
              name: "page",
              in: "query",
              description: "Page number (starts at 1)",
              schema: { type: "integer", minimum: 1, default: 1 },
            },
            {
              name: "limit",
              in: "query",
              description: "Results per page (max 100)",
              schema: { type: "integer", minimum: 1, maximum: 100, default: 20 },
            },
          ],
          responses: {
            "200": {
              description: "Success",
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
          summary: "Restaurant detail",
          description:
            "Returns full detail for a single restaurant. " +
            "Query by ID or slug. " +
            "Includes FAQ, scenario summaries, nearby transit/landmarks and reservation links.",
          operationId: "getRestaurant",
          tags: ["Restaurants"],
          parameters: [
            {
              name: "id",
              in: "path",
              required: true,
              description: "Restaurant ID or slug",
              schema: { type: "string", example: "pera-antakya" },
            },
          ],
          responses: {
            "200": {
              description: "Success",
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
          description: "Your RapidAPI subscription key",
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
          description: "Scenario-based ratings on a 1-5 scale",
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
          description: "Short text summaries for different dining scenarios",
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
            type:       { type: "string", enum: ["metro", "tram", "ferry", "bus"] },
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
          description: "Invalid parameter",
          content: {
            "application/json": {
              schema: { $ref: "#/components/schemas/ApiError" },
              example: {
                error: {
                  code: "INVALID_PARAM",
                  message: "'maxPrice' must be 1, 2, 3 or 4.",
                  details: { param: "maxPrice" },
                },
              },
            },
          },
        },
        Unauthorized: {
          description: "Unauthorized — valid RapidAPI key required",
          content: {
            "application/json": {
              schema: { $ref: "#/components/schemas/ApiError" },
              example: {
                error: {
                  code: "UNAUTHORIZED",
                  message: "This API is only accessible via RapidAPI.",
                },
              },
            },
          },
        },
        NotFound: {
          description: "Resource not found",
          content: {
            "application/json": {
              schema: { $ref: "#/components/schemas/ApiError" },
              example: {
                error: {
                  code: "NOT_FOUND",
                  message: "No restaurant found matching 'unknown-slug'.",
                },
              },
            },
          },
        },
        InternalError: {
          description: "Server error",
          content: {
            "application/json": {
              schema: { $ref: "#/components/schemas/ApiError" },
              example: {
                error: {
                  code: "INTERNAL_ERROR",
                  message: "An unexpected error occurred.",
                },
              },
            },
          },
        },
        RateLimitExceeded: {
          description: "Rate limit exceeded",
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
                  message: "You have reached the per-minute request limit. Please wait.",
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
        description: "Restaurant listing and detail endpoints",
        externalDocs: {
          description: "llms.txt",
          url: "https://www.restaurantsistanbul.com/llms.txt",
        },
      },
    ],
    externalDocs: {
      description: "AI documentation (llms.txt)",
      url: "https://www.restaurantsistanbul.com/llms.txt",
    },
  };

  return NextResponse.json(spec, { headers: CORS_HEADERS });
}
