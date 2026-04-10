import { render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { Providers } from "@/app/providers";
import CandidateDetailPage from "@/app/candidates/[candidateId]/page";
import HomePage from "@/app/page";
import JobsPage from "@/app/jobs/page";
import { ApiError } from "@/lib/api/types";

const { redirectMock, pushMock } = vi.hoisted(() => ({
  redirectMock: vi.fn(),
  pushMock: vi.fn(),
}));

vi.mock("next/navigation", async () => {
  const actual = await vi.importActual<typeof import("next/navigation")>("next/navigation");

  return {
    ...actual,
    redirect: redirectMock,
    useRouter: () => ({
      push: pushMock,
    }),
  };
});

describe("Workspace pages", () => {
  beforeEach(() => {
    redirectMock.mockReset();
    pushMock.mockReset();
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
    expect(screen.getByRole("button", { name: "返回上一页" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "切换到深色模式" })).toBeInTheDocument();
  });

  it("navigates through the floating back button on the jobs page", () => {
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

    screen.getByRole("button", { name: "返回上一页" }).click();

    expect(pushMock).toHaveBeenCalledWith("/");
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
      expect(screen.getByRole("button", { name: "重试" })).toBeInTheDocument();
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
      expect(screen.getByRole("button", { name: "重试" })).toBeInTheDocument();
    });
  });

  it("renders the candidate detail empty state", async () => {
    vi.mocked(fetch).mockResolvedValueOnce(
      new Response(
        JSON.stringify({
          candidate_id: "cand-001",
          job: {
            job_id: "job-001",
            title: "AI Recruiter",
          },
          raw_input: {
            raw_text_input: "Candidate raw input",
            documents: [],
          },
          normalized_profile: {
            identity: {
              full_name: "Ada Lovelace",
              current_title: "Recruiting Lead",
              current_company: "Auto HR",
              location_text: "Remote",
              email: "ada@example.com",
              phone: "123456",
              linkedin_url: "https://linkedin.example/ada",
            },
            profile_summary: {
              professional_summary_raw: "Built hiring systems",
              professional_summary_normalized: "Built hiring systems for global teams",
              years_of_total_experience: 8,
              years_of_relevant_experience: 6,
              seniority_level: "Lead",
            },
            work_experiences: [],
            educations: [],
            skills: {
              skills_raw: ["Recruiting"],
              skills_normalized: ["Recruiting Ops"],
            },
            employment_preferences: {},
            application_answers: [],
            additional_information: {},
          },
          rubric_results: [],
          supervisor_summary: {
            hard_requirement_overall: "all_pass",
            overall_score_percent: 90,
            ai_summary: "Strong recruiting operator",
            evidence_points: ["Built structured interview loops"],
            recommendation: "advance",
            tags: [],
          },
          action_context: {
            current_status: "pending",
            feedbacks: [],
            email_drafts: [],
          },
        }),
        {
          status: 200,
          headers: { "Content-Type": "application/json" },
        },
      ),
    );

    render(
      <Providers>
        {await CandidateDetailPage({ params: Promise.resolve({ candidateId: "cand-001" }) })}
      </Providers>,
    );

    expect(screen.getByRole("heading", { name: "候选人详情" })).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Ada Lovelace" })).toBeInTheDocument();
      expect(screen.getByRole("heading", { name: "原始输入" })).toBeInTheDocument();
    });
  });
});
