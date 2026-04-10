import { ApiError } from "@/lib/api/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") ?? "";
const API_REQUEST_TIMEOUT_MS = 120000;

export function buildApiUrl(path: string) {
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

function createTimeoutError() {
  return new ApiError("请求超时，请稍后重试。", 408, null);
}

function createNetworkError(payload: unknown) {
  if (payload instanceof Error && payload.message.trim()) {
    return new ApiError(payload.message, 0, payload);
  }

  return new ApiError("网络连接失败，请稍后重试。", 0, payload);
}

function createAbortError() {
  return new ApiError("请求已取消。", 0, null);
}

function isAbortError(error: unknown) {
  return error instanceof DOMException
    ? error.name === "AbortError"
    : error instanceof Error && error.name === "AbortError";
}

async function buildApiError(response: Response) {
  let payload: unknown = null;
  const contentType = response.headers.get("content-type") ?? "";

  try {
    if (contentType.includes("application/json")) {
      payload = await response.json();
    } else {
      payload = await response.text();
    }
  } catch {
    try {
      payload = await response.text();
    } catch {
      payload = null;
    }
  }

  const message = extractErrorMessage(payload, `请求失败（${response.status}）`);
  return new ApiError(message, response.status, payload);
}

export async function apiRequest<T>(path: string, init: RequestInit = {}): Promise<T> {
  const abortController = new AbortController();
  const upstreamSignal = init.signal;
  const relayAbort = () => abortController.abort(upstreamSignal?.reason);
  let didTimeout = false;

  if (upstreamSignal) {
    if (upstreamSignal.aborted) {
      relayAbort();
    } else {
      upstreamSignal.addEventListener("abort", relayAbort, { once: true });
    }
  }

  let timeoutId: ReturnType<typeof setTimeout> | null = null;

  try {
    timeoutId = setTimeout(() => {
      didTimeout = true;
      abortController.abort("request_timeout");
    }, API_REQUEST_TIMEOUT_MS);

    const response = await fetch(buildApiUrl(path), {
      ...init,
      signal: abortController.signal,
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
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }

    if (didTimeout) {
      throw createTimeoutError();
    }

    if (isAbortError(error)) {
      throw upstreamSignal?.aborted ? createAbortError() : createTimeoutError();
    }

    throw createNetworkError(error);
  } finally {
    if (timeoutId) {
      clearTimeout(timeoutId);
    }
    if (upstreamSignal) {
      upstreamSignal.removeEventListener("abort", relayAbort);
    }
  }
}
