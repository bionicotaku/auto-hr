import { render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { Providers } from "@/app/providers";
import CandidateDetailPage from "@/app/candidates/[candidateId]/page";
import HomePage from "@/app/page";
import JobsPage from "@/app/jobs/page";
import { ApiError } from "@/lib/api/types";

const { redirectMock } = vi.hoisted(() => ({
  redirectMock: vi.fn(),
}));

vi.mock("next/navigation", async () => {
  const actual = await vi.importActual<typeof import("next/navigation")>("next/navigation");

  return {
    ...actual,
    redirect: redirectMock,
  };
});

describe("Workspace pages", () => {
  beforeEach(() => {
    redirectMock.mockReset();
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.useRealTimers();
    vi.unstubAllGlobals();
  });

  it("redirects the root route to jobs", () => {
    HomePage();

    expect(redirectMock).toHaveBeenCalledWith("/jobs");
  });

  it("renders the jobs overview empty state", () => {
    vi.mocked(fetch).mockResolvedValueOnce(
      new Response(JSON.stringify({ items: [] }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }),
    );

    render(
      <Providers>
        <JobsPage />
      </Providers>,
    );

    expect(screen.getByRole("heading", { name: "岗位" })).toBeInTheDocument();
  });

  it("shows the jobs overview error state when the request fails", async () => {
    vi.mocked(fetch).mockRejectedValueOnce(new Error("网络连接失败"));

    render(
      <Providers>
        <JobsPage />
      </Providers>,
    );

    expect(screen.getByRole("heading", { name: "岗位" })).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "加载失败" })).toBeInTheDocument();
      expect(screen.getByText("网络连接失败")).toBeInTheDocument();
    });
  });

  it("shows the jobs overview error state when the request times out", async () => {
    vi.mocked(fetch).mockRejectedValueOnce(new ApiError("请求超时，请稍后重试。", 408, null));

    render(
      <Providers>
        <JobsPage />
      </Providers>,
    );

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "加载失败" })).toBeInTheDocument();
      expect(screen.getByText("请求超时，请稍后重试。")).toBeInTheDocument();
    });
  });

  it("renders the candidate detail empty state", async () => {
    render(await CandidateDetailPage({ params: Promise.resolve({ candidateId: "cand-001" }) }));

    expect(screen.getByRole("heading", { name: "候选人详情" })).toBeInTheDocument();
    expect(screen.getByText("候选人 cand-001")).toBeInTheDocument();
  });
});
