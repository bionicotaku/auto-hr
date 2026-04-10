import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactElement } from "react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { Providers } from "@/app/providers";
import { JobEditWorkspace } from "@/components/job/edit/JobEditWorkspace";

const pushMock = vi.fn();

vi.mock("next/navigation", async () => {
  const actual = await vi.importActual<typeof import("next/navigation")>("next/navigation");

  return {
    ...actual,
    useRouter: () => ({
      push: pushMock,
    }),
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

function makeEditPayload() {
  return {
    id: "job-123",
    lifecycle_status: "draft",
    creation_mode: "from_description",
    title: "AI Recruiter",
    summary: "Own hiring",
    description_text: "Initial JD body",
    structured_info_json: {
      location: "Remote",
    },
    original_description_input: "Raw input",
    original_form_input_json: null,
    editor_history_summary: null,
    editor_recent_messages_json: [],
    created_at: "2026-04-09T00:00:00Z",
    updated_at: "2026-04-09T00:00:00Z",
    finalized_at: null,
    rubric_items: [
      {
        id: "rubric-1",
        sort_order: 1,
        name: "Execution",
        description: "Can run hiring",
        criterion_type: "weighted",
        weight_input: 70,
        weight_normalized: 0.7,
        scoring_standard_json: { score_5: "Excellent" },
        agent_prompt_text: "Judge execution",
        evidence_guidance_text: "Look for ownership",
      },
    ],
  };
}

describe("Job edit workspace", () => {
  beforeEach(() => {
    pushMock.mockReset();
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("loads the draft and initializes local truth state", async () => {
    const fetchMock = vi.mocked(fetch);
    fetchMock.mockResolvedValueOnce(mockJsonResponse(makeEditPayload()));

    renderWithProviders(<JobEditWorkspace jobId="job-123" />);

    expect(await screen.findByDisplayValue("Initial JD body")).toBeInTheDocument();
    expect(screen.getByDisplayValue("Execution")).toBeInTheDocument();
  });

  it("keeps the editor content unchanged after chat", async () => {
    const fetchMock = vi.mocked(fetch);
    fetchMock
      .mockResolvedValueOnce(mockJsonResponse(makeEditPayload()))
      .mockResolvedValueOnce(mockJsonResponse({ reply_text: "建议拆分必须项。" }));

    renderWithProviders(<JobEditWorkspace jobId="job-123" />);

    const description = await screen.findByLabelText("职位描述编辑区");
    fireEvent.change(screen.getByLabelText("修改要求输入框"), {
      target: { value: "给我建议" },
    });
    fireEvent.click(screen.getByRole("button", { name: "获取建议" }));

    await screen.findByText("建议拆分必须项。");
    expect(description).toHaveValue("Initial JD body");
  });

  it("applies returned content after agent edit", async () => {
    const fetchMock = vi.mocked(fetch);
    fetchMock
      .mockResolvedValueOnce(mockJsonResponse(makeEditPayload()))
      .mockResolvedValueOnce(
        mockJsonResponse({
          description_text: "Agent updated JD",
          rubric_items: [
            {
              sort_order: 1,
              name: "Updated Execution",
              description: "Updated description",
              criterion_type: "weighted",
              weight_input: 80,
              weight_normalized: 0.8,
              scoring_standard_json: { score_5: "Excellent" },
              agent_prompt_text: "Judge updated execution",
              evidence_guidance_text: "Look for impact",
            },
          ],
        }),
      );

    renderWithProviders(<JobEditWorkspace jobId="job-123" />);

    await screen.findByDisplayValue("Initial JD body");
    fireEvent.change(screen.getByLabelText("修改要求输入框"), {
      target: { value: "直接修改" },
    });
    fireEvent.click(screen.getByRole("button", { name: "应用修改" }));

    await screen.findByDisplayValue("Agent updated JD");
    expect(screen.getByDisplayValue("Updated Execution")).toBeInTheDocument();
  });

  it("applies regenerated content", async () => {
    const fetchMock = vi.mocked(fetch);
    fetchMock
      .mockResolvedValueOnce(mockJsonResponse(makeEditPayload()))
      .mockResolvedValueOnce(
        mockJsonResponse({
          description_text: "Regenerated JD",
          rubric_items: [
            {
              sort_order: 1,
              name: "Regenerated Execution",
              description: "Regenerated description",
              criterion_type: "weighted",
              weight_input: 75,
              weight_normalized: 0.75,
              scoring_standard_json: { score_5: "Excellent" },
              agent_prompt_text: "Judge regenerated execution",
              evidence_guidance_text: "Look for scope",
            },
          ],
        }),
      );

    renderWithProviders(<JobEditWorkspace jobId="job-123" />);

    await screen.findByDisplayValue("Initial JD body");
    fireEvent.click(screen.getByRole("button", { name: "重新生成" }));

    await waitFor(() => {
      expect(screen.getByDisplayValue("Regenerated JD")).toBeInTheDocument();
    });
    expect(screen.getByText("已重新生成当前岗位定义。")).toBeInTheDocument();
  });

  it("finalizes the job and navigates back to jobs", async () => {
    const fetchMock = vi.mocked(fetch);
    fetchMock
      .mockResolvedValueOnce(mockJsonResponse(makeEditPayload()))
      .mockResolvedValueOnce(mockJsonResponse({ job_id: "job-123", lifecycle_status: "active" }));

    renderWithProviders(<JobEditWorkspace jobId="job-123" />);

    await screen.findByDisplayValue("Initial JD body");
    fireEvent.click(screen.getByRole("button", { name: "完成" }));

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        "/api/jobs/job-123/finalize",
        expect.objectContaining({
          method: "POST",
        }),
      );
      expect(pushMock).toHaveBeenCalledWith("/jobs");
    });
  });

  it("keeps local truth when finalize fails", async () => {
    const fetchMock = vi.mocked(fetch);
    fetchMock
      .mockResolvedValueOnce(mockJsonResponse(makeEditPayload()))
      .mockResolvedValueOnce(mockJsonResponse({ message: "最终定稿失败" }, 422));

    renderWithProviders(<JobEditWorkspace jobId="job-123" />);

    const description = await screen.findByLabelText("职位描述编辑区");
    fireEvent.change(description, {
      target: { value: "Locally edited JD" },
    });
    fireEvent.click(screen.getByRole("button", { name: "完成" }));

    expect(await screen.findByText("最终定稿失败")).toBeInTheDocument();
    expect(description).toHaveValue("Locally edited JD");
    expect(pushMock).not.toHaveBeenCalled();
  });

  it("deletes the draft on cancel and navigates back to jobs", async () => {
    const fetchMock = vi.mocked(fetch);
    fetchMock
      .mockResolvedValueOnce(mockJsonResponse(makeEditPayload()))
      .mockResolvedValueOnce(new Response(null, { status: 204 }));

    renderWithProviders(<JobEditWorkspace jobId="job-123" />);

    await screen.findByDisplayValue("Initial JD body");
    fireEvent.click(screen.getByRole("button", { name: "取消" }));

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        "/api/jobs/job-123/draft",
        expect.objectContaining({
          method: "DELETE",
        }),
      );
      expect(pushMock).toHaveBeenCalledWith("/jobs");
    });
  });
});
