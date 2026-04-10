import { afterEach, describe, expect, it, vi } from "vitest";

import { apiRequest } from "@/lib/api/client";

describe("apiRequest", () => {
  afterEach(() => {
    vi.useRealTimers();
    vi.unstubAllGlobals();
  });

  it("rejects with a timeout error when the request does not resolve", async () => {
    vi.useFakeTimers();
    vi.stubGlobal(
      "fetch",
      vi.fn((_, init?: RequestInit) => {
        return new Promise<Response>((_, reject) => {
          const signal = init?.signal;
          if (signal) {
            signal.addEventListener(
              "abort",
              () => reject(new DOMException("The operation was aborted.", "AbortError")),
              { once: true },
            );
          }
        });
      }),
    );

    const requestPromise = apiRequest("/api/jobs");
    const assertion = expect(requestPromise).rejects.toMatchObject({
      message: "请求超时，请稍后重试。",
      status: 408,
    });

    await vi.advanceTimersByTimeAsync(120000);

    await assertion;
  });

  it("surfaces plain-text api errors instead of falling back to network failure", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () =>
        new Response("Invalid schema for response_format 'job_draft_schema'.", {
          status: 422,
          headers: { "Content-Type": "text/plain; charset=utf-8" },
        }),
      ),
    );

    await expect(apiRequest("/api/jobs")).rejects.toMatchObject({
      message: "Invalid schema for response_format 'job_draft_schema'.",
      status: 422,
    });
  });

  it("falls back to status message when json error body is malformed", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () =>
        new Response("{bad-json", {
          status: 500,
          headers: { "Content-Type": "application/json" },
        }),
      ),
    );

    await expect(apiRequest("/api/jobs")).rejects.toMatchObject({
      message: "请求失败（500）",
      status: 500,
    });
  });
});
