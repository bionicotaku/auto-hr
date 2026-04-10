import { render, screen, waitFor } from "@testing-library/react";
import type { ReactElement } from "react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import CandidateDetailPage from "@/app/candidates/[candidateId]/page";
import { Providers } from "@/app/providers";

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

describe("Candidate detail page", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("renders the five candidate detail panels", async () => {
    vi.mocked(fetch).mockResolvedValueOnce(
      mockJsonResponse({
        candidate_id: "candidate-001",
        job: {
          job_id: "job-001",
          title: "AI Recruiter",
        },
        raw_input: {
          raw_text_input: "Candidate raw input",
          documents: [
            {
              id: "doc-001",
              document_type: "resume",
              filename: "resume.pdf",
              storage_path: "data/uploads/candidates/candidate-001/resume.pdf",
              mime_type: "application/pdf",
              extracted_text: "Resume extracted text",
              page_count: 2,
              upload_order: 1,
            },
          ],
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
          work_experiences: [
            {
              company_name: "Auto HR",
              title: "Recruiting Lead",
              description_normalized: "Led recruiting operations",
            },
          ],
          educations: [
            {
              school_name: "Oxford",
              degree: "BSc",
              major: "Mathematics",
            },
          ],
          skills: {
            skills_raw: ["Recruiting", "Ops"],
            skills_normalized: ["Recruiting Ops"],
          },
          employment_preferences: {
            preferred_locations: ["New York"],
            preferred_work_modes: ["Hybrid"],
          },
          application_answers: [
            {
              question_text: "Notice period",
              answer_text: "Two weeks",
            },
          ],
          additional_information: {
            uncategorized_highlights: ["Built dashboards"],
            parser_notes: ["Resume had two formats"],
          },
        },
        rubric_results: [
          {
            job_rubric_item_id: "rubric-001",
            rubric_name: "执行力",
            rubric_description: "推进招聘流程",
            criterion_type: "weighted",
            weight_label: "70%",
            score_0_to_5: 4.0,
            hard_requirement_decision: null,
            reason_text: "Strong execution",
            evidence_points: ["Built hiring workflow"],
            uncertainty_note: "Need one more data point",
          },
        ],
        supervisor_summary: {
          hard_requirement_overall: "all_pass",
          overall_score_5: 4.5,
          overall_score_percent: 90,
          ai_summary: "Strong recruiting operator",
          evidence_points: ["Built structured interview loops"],
          recommendation: "advance",
          tags: [
            {
              id: "tag-001",
              name: "高匹配",
              source: "ai",
            },
          ],
        },
        action_context: {
          current_status: "pending",
          feedbacks: [
            {
              id: "feedback-001",
              author_name: "Evan",
              note_text: "值得继续跟进",
              created_at: "2026-04-10T00:00:00Z",
            },
          ],
          email_drafts: [
            {
              id: "draft-001",
              draft_type: "advance",
              subject: "下一轮沟通安排",
              body: "我们希望与你继续沟通。",
              created_at: "2026-04-10T00:00:00Z",
              updated_at: "2026-04-10T00:00:00Z",
            },
          ],
        },
      }),
    );

    renderWithProviders(await CandidateDetailPage({ params: Promise.resolve({ candidateId: "candidate-001" }) }));

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Ada Lovelace" })).toBeInTheDocument();
      expect(screen.getByRole("heading", { name: "原始输入" })).toBeInTheDocument();
      expect(screen.getByRole("heading", { name: "标准化信息" })).toBeInTheDocument();
      expect(screen.getByRole("heading", { name: "逐项分析" })).toBeInTheDocument();
      expect(screen.getByRole("heading", { name: "汇总结论" })).toBeInTheDocument();
      expect(screen.getByRole("heading", { name: "处理状态" })).toBeInTheDocument();
    });
  });

  it("renders the error state when the request fails", async () => {
    vi.mocked(fetch).mockRejectedValue(new Error("网络连接失败"));

    renderWithProviders(await CandidateDetailPage({ params: Promise.resolve({ candidateId: "candidate-001" }) }));

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "加载失败" })).toBeInTheDocument();
      expect(screen.getByText("网络连接失败")).toBeInTheDocument();
    });
  });
});
