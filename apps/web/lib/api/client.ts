import { ApiError } from "@/lib/api/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") ?? "";

function buildUrl(path: string) {
  return API_BASE_URL ? `${API_BASE_URL}${path}` : path;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function firstStringValue(values: Array<unknown>): string | null {
  for (const value of values) {
    if (typeof value === "string" && value.trim()) {
      return value;
    }
  }

  return null;
}

function extractErrorMessage(payload: unknown, fallback: string) {
  if (typeof payload === "string" && payload.trim()) {
    return payload;
  }

  if (!isRecord(payload)) {
    return fallback;
  }

  const directMessage = firstStringValue([payload.message, payload.detail, payload.error]);
  if (directMessage) {
    return directMessage;
  }

  if (isRecord(payload.error)) {
    const nestedErrorMessage = firstStringValue([
      payload.error.message,
      payload.error.detail,
      payload.error.code,
    ]);
    if (nestedErrorMessage) {
      return nestedErrorMessage;
    }
  }

  const detail = payload.detail;
  if (Array.isArray(detail) && detail.length > 0) {
    const firstItem = detail[0];
    if (typeof firstItem === "string" && firstItem.trim()) {
      return firstItem;
    }

    if (isRecord(firstItem)) {
      const nestedMessage = firstStringValue([firstItem.message, firstItem.detail, firstItem.error]);
      if (nestedMessage) {
        return nestedMessage;
      }
    }
  }

  return fallback;
}

async function buildApiError(response: Response) {
  const contentType = response.headers.get("content-type") ?? "";
  let payload: unknown = null;

  if (contentType.includes("application/json")) {
    payload = await response.json();
  } else {
    payload = await response.text();
  }

  const message = extractErrorMessage(payload, `请求失败（${response.status}）`);
  return new ApiError(message, response.status, payload);
}

export async function apiRequest<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(buildUrl(path), {
    ...init,
    headers: {
      Accept: "application/json",
      ...(typeof init.body === "string" ? { "Content-Type": "application/json" } : {}),
      ...(init.headers ?? {}),
    },
  });

  if (!response.ok) {
    throw await buildApiError(response);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  const contentType = response.headers.get("content-type") ?? "";
  if (contentType.includes("application/json")) {
    return (await response.json()) as T;
  }

  return (await response.text()) as T;
}
