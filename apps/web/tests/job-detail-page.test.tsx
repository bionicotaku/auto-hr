import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactElement } from "react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { Providers } from "@/app/providers";
import JobDetailPage from "@/app/jobs/[jobId]/page";
import JobsPage from "@/app/jobs/page";
import { buildApiUrl } from "@/lib/api/client";

const pushMock = vi.fn();
const replaceMock = vi.fn();

const navigationState = {
  pathname: "/jobs/job-001",
  searchParams: new URLSearchParams(),
};

vi.mock("next/navigation", async () => {
  const actual = await vi.importActual<typeof import("next/navigation")>("next/navigation");

  return {
    ...actual,
    useRouter: () => ({
      push: pushMock,
      replace: replaceMock,
    }),
    usePathname: () => navigationState.pathname,
    useSearchParams: () => navigationState.searchParams,
  };
});

function renderWithProviders(node: ReactElement) {
  return render(<Providers>{node}</Providers>);
}

function mockJsonResponse(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: {
      "Content-Type": "application/json",
    },
  });
}

describe("Job detail pages", () => {
  beforeEach(() => {
    pushMock.mockReset();
    replaceMock.mockReset();
    navigationState.pathname = "/jobs/job-001";
    navigationState.searchParams = new URLSearchParams();
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    vi.useRealTimers();
  });

  it("renders the jobs page with real job cards", () => {
    const fetchMock = vi.mocked(fetch);
    fetchMock.mockResolvedValueOnce(
      mockJsonResponse({
        items: [
          {
            job_id: "job-001",
            title: "AI Recruiter",
            summary: "Own hiring",
            lifecycle_status: "active",
            candidate_count: 2,
            updated_at: "2026-04-09T00:00:00Z",
          },
        ],
      }),
    );

    renderWithProviders(<JobsPage />);

    expect(screen.getByRole("heading", { name: "岗位" })).toBeInTheDocument();
    return waitFor(() => {
      expect(screen.getByText("AI Recruiter")).toBeInTheDocument();
      expect(screen.getByRole("link", { name: "进入岗位" })).toHaveAttribute("href", "/jobs/job-001");
    });
  });

  it("renders job detail summary and candidate list", async () => {
    const fetchMock = vi.mocked(fetch);
    fetchMock
      .mockResolvedValueOnce(
        mockJsonResponse({
          job_id: "job-001",
          title: "AI Recruiter",
          summary: "Own hiring",
          description_text: "JD body",
          lifecycle_status: "active",
          candidate_count: 2,
          rubric_summary: [
            { name: "Execution", criterion_type: "weighted", weight_label: "70%" },
          ],
          structured_info_summary: [{ label: "地点", value: "Remote" }],
        }),
      )
      .mockResolvedValueOnce(
        mockJsonResponse({
          items: [
            {
              candidate_id: "candidate-001",
              full_name: "Ada Lovelace",
              ai_summary: "Strong operator",
              overall_score_percent: 92,
              current_status: "pending",
              tags: ["高匹配"],
              created_at: "2026-04-09T00:00:00Z",
            },
          ],
          available_tags: ["高匹配"],
        }),
      );

    renderWithProviders(await JobDetailPage({ params: Promise.resolve({ jobId: "job-001" }) }));

    expect(await screen.findByText("AI Recruiter")).toBeInTheDocument();
    expect(screen.getByText("Ada Lovelace")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "添加候选人" })).toHaveAttribute(
      "href",
      "/jobs/job-001/candidates/new",
    );
  });

  it("updates the candidate list without changing the URL", async () => {
    const fetchMock = vi.mocked(fetch);
    fetchMock
      .mockResolvedValueOnce(
        mockJsonResponse({
          job_id: "job-001",
          title: "AI Recruiter",
          summary: "Own hiring",
          description_text: "JD body",
          lifecycle_status: "active",
          candidate_count: 1,
          rubric_summary: [{ name: "Execution", criterion_type: "weighted", weight_label: "70%" }],
          structured_info_summary: [{ label: "地点", value: "Remote" }],
        }),
      )
      .mockResolvedValueOnce(
        mockJsonResponse({
          items: [],
          available_tags: ["高匹配", "需要复核"],
        }),
      )
      .mockResolvedValueOnce(
        mockJsonResponse({
          items: [],
          available_tags: ["高匹配", "需要复核", "制造业经验", "管理经验", "本地候选人"],
        }),
      )
      .mockResolvedValueOnce(
        mockJsonResponse({
          items: [],
          available_tags: ["高匹配", "需要复核", "制造业经验", "管理经验", "本地候选人"],
        }),
      );

    renderWithProviders(await JobDetailPage({ params: Promise.resolve({ jobId: "job-001" }) }));

    await screen.findByRole("heading", { name: "AI Recruiter" });
    await screen.findByRole("button", { name: "高匹配" });

    fireEvent.change(screen.getByLabelText("候选人排序"), {
      target: { value: "score_asc" },
    });

    await waitFor(() => {
      expect(fetchMock.mock.calls.at(-1)?.[0]).toBe(
        buildApiUrl("/api/jobs/job-001/candidates?sort=score_asc&status=all"),
      );
    });

    await screen.findByRole("button", { name: "高匹配" });
    fireEvent.click(screen.getByRole("button", { name: "高匹配" }));
    await waitFor(() => {
      expect(fetchMock.mock.calls.at(-1)?.[0]).toBe(
        buildApiUrl("/api/jobs/job-001/candidates?sort=score_asc&status=all&tags=%E9%AB%98%E5%8C%B9%E9%85%8D"),
      );
    });

    expect(replaceMock).not.toHaveBeenCalled();
  });

  it("keeps search input responsive and debounces candidate requests", async () => {
    const fetchMock = vi.mocked(fetch);
    fetchMock
      .mockResolvedValueOnce(
        mockJsonResponse({
          job_id: "job-001",
          title: "AI Recruiter",
          summary: "Own hiring",
          description_text: "JD body",
          lifecycle_status: "active",
          candidate_count: 1,
          rubric_summary: [{ name: "Execution", criterion_type: "weighted", weight_label: "70%" }],
          structured_info_summary: [{ label: "地点", value: "Remote" }],
        }),
      )
      .mockResolvedValueOnce(
        mockJsonResponse({
          items: [],
          available_tags: [],
        }),
      )
      .mockResolvedValueOnce(
        mockJsonResponse({
          items: [],
          available_tags: [],
        }),
      );

    renderWithProviders(await JobDetailPage({ params: Promise.resolve({ jobId: "job-001" }) }));

    const input = await screen.findByLabelText("搜索候选人");

    fireEvent.change(input, { target: { value: "Ada" } });
    fireEvent.change(input, { target: { value: "Ada " } });

    expect(input).toHaveValue("Ada ");
    expect(replaceMock).not.toHaveBeenCalled();
    expect(fetchMock).toHaveBeenCalledTimes(2);

    await waitFor(() => {
      expect(fetchMock.mock.calls.at(-1)?.[0]).toBe(
        buildApiUrl("/api/jobs/job-001/candidates?sort=score_desc&status=all&q=Ada"),
      );
    });
    expect(replaceMock).not.toHaveBeenCalled();
  });
});
