import { NextResponse } from "next/server";

const CORS_HEADERS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, X-RapidAPI-Key, X-RapidAPI-Host",
  "Content-Type": "application/json; charset=utf-8",
};

export type ApiErrorCode =
  | "INVALID_PARAM"
  | "NOT_FOUND"
  | "UNAUTHORIZED"
  | "RATE_LIMIT_EXCEEDED"
  | "INTERNAL_ERROR";

export function apiError(
  status: number,
  code: ApiErrorCode,
  message: string,
  details?: Record<string, unknown>
) {
  return NextResponse.json(
    { error: { code, message, ...(details ? { details } : {}) } },
    { status, headers: CORS_HEADERS }
  );
}
