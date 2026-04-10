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
    responsibilities: ["Publish role", "Coordinate interview loop"],
    skills: ["Recruiting ops", "Stakeholder management"],
    original_description_input: "Raw input",
    original_form_input_json: null,
    editor_history_summary: null,
    editor_recent_messages_json: [],
    created_at: "2026-04-09T00:00:00Z",
    updated_at: "2026-04-09T00:00:00Z",
    finalized_at: null,
    rubric_items: [
      {
        sort_order: 1,
        name: "Execution",
        description: "Can run hiring",
        criterion_type: "weighted",
        weight_input: 70,
      },
    ],
  };
}

function makeActiveEditPayload() {
  return {
    ...makeEditPayload(),
    lifecycle_status: "active" as const,
    finalized_at: "2026-04-10T00:00:00Z",
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
    expect(screen.getByLabelText("Responsibilities 编辑区")).toHaveValue("Publish role\nCoordinate interview loop");
    expect(screen.getByLabelText("Skills 编辑区")).toHaveValue("Recruiting ops\nStakeholder management");
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
          title: "Updated AI Recruiter",
          summary: "Own the recruiting funnel with a tighter hiring bar.",
          description_text: "Agent updated JD",
          structured_info_json: {
            location: "Hybrid",
            responsibilities: ["Run kickoff", "Manage hiring cadence"],
            skills: ["Hiring strategy", "Funnel ops"],
          },
          rubric_items: [
            {
              sort_order: 1,
              name: "Updated Execution",
              description: "Updated description",
              criterion_type: "weighted",
              weight_input: 80,
            },
          ],
          responsibilities: ["Run kickoff", "Manage hiring cadence"],
          skills: ["Hiring strategy", "Funnel ops"],
        }),
      );

    renderWithProviders(<JobEditWorkspace jobId="job-123" />);

    await screen.findByDisplayValue("Initial JD body");
    fireEvent.change(screen.getByLabelText("修改要求输入框"), {
      target: { value: "直接修改" },
    });
    fireEvent.click(screen.getByRole("button", { name: "生成新版" }));

    await screen.findByDisplayValue("Agent updated JD");
    expect(screen.getByDisplayValue("Updated Execution")).toBeInTheDocument();
    expect(screen.getByText("Updated AI Recruiter")).toBeInTheDocument();
    expect(screen.getByText("Own the recruiting funnel with a tighter hiring bar.")).toBeInTheDocument();
    expect(screen.getByText("Hybrid")).toBeInTheDocument();
    expect(screen.getByLabelText("Responsibilities 编辑区")).toHaveValue("Run kickoff\nManage hiring cadence");
    expect(screen.getByLabelText("Skills 编辑区")).toHaveValue("Hiring strategy\nFunnel ops");
  });

  it("finalizes the job and navigates back to jobs", async () => {
    const fetchMock = vi.mocked(fetch);
    fetchMock
      .mockResolvedValueOnce(mockJsonResponse(makeEditPayload()))
      .mockResolvedValueOnce(mockJsonResponse({ job_id: "job-123", lifecycle_status: "active" }));

    renderWithProviders(<JobEditWorkspace jobId="job-123" />);

    await screen.findByDisplayValue("Initial JD body");
    fireEvent.click(screen.getByRole("button", { name: "保存" }));

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("/api/jobs/job-123/finalize"),
        expect.objectContaining({
          method: "POST",
        }),
      );
      expect(pushMock).toHaveBeenCalledWith("/jobs");
    });
  });

  it("returns to the job detail page after saving an active job with changes", async () => {
    const fetchMock = vi.mocked(fetch);
    fetchMock
      .mockResolvedValueOnce(mockJsonResponse(makeActiveEditPayload()))
      .mockResolvedValueOnce(mockJsonResponse({ job_id: "job-123", lifecycle_status: "active" }));

    renderWithProviders(<JobEditWorkspace jobId="job-123" />);

    const description = await screen.findByLabelText("职位描述编辑区");
    fireEvent.change(description, {
      target: { value: "Updated active JD" },
    });
    fireEvent.click(screen.getByRole("button", { name: "保存" }));

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("/api/jobs/job-123/finalize"),
        expect.objectContaining({
          method: "POST",
        }),
      );
      expect(pushMock).toHaveBeenCalledWith("/jobs/job-123");
    });
  });

  it("keeps local truth when finalize fails", async () => {
    const fetchMock = vi.mocked(fetch);
    fetchMock
      .mockResolvedValueOnce(mockJsonResponse(makeEditPayload()))
      .mockResolvedValueOnce(mockJsonResponse({ message: "最终定稿失败" }, 422));

    renderWithProviders(<JobEditWorkspace jobId="job-123" />);

    const description = await screen.findByLabelText("职位描述编辑区");
    const responsibilities = screen.getByLabelText("Responsibilities 编辑区");
    fireEvent.change(description, {
      target: { value: "Locally edited JD" },
    });
    fireEvent.change(responsibilities, {
      target: { value: "Own funnel\nPartner hiring team" },
    });
    fireEvent.click(screen.getByRole("button", { name: "保存" }));

    expect(await screen.findByText("最终定稿失败")).toBeInTheDocument();
    expect(description).toHaveValue("Locally edited JD");
    expect(responsibilities).toHaveValue("Own funnel\nPartner hiring team");
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
        expect.stringContaining("/api/jobs/job-123/draft"),
        expect.objectContaining({
          method: "DELETE",
        }),
      );
      expect(pushMock).toHaveBeenCalledWith("/jobs");
    });
  });

  it("returns to the job detail page on cancel for active jobs", async () => {
    const fetchMock = vi.mocked(fetch);
    fetchMock.mockResolvedValueOnce(mockJsonResponse(makeActiveEditPayload()));

    renderWithProviders(<JobEditWorkspace jobId="job-123" />);

    await screen.findByDisplayValue("Initial JD body");
    fireEvent.click(screen.getByRole("button", { name: "取消" }));

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledTimes(1);
      expect(pushMock).toHaveBeenCalledWith("/jobs/job-123");
    });
  });

  it("returns to the job detail page without saving when active job has no changes", async () => {
    const fetchMock = vi.mocked(fetch);
    fetchMock.mockResolvedValueOnce(mockJsonResponse(makeActiveEditPayload()));

    renderWithProviders(<JobEditWorkspace jobId="job-123" />);

    await screen.findByDisplayValue("Initial JD body");
    fireEvent.click(screen.getByRole("button", { name: "保存" }));

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledTimes(1);
      expect(pushMock).toHaveBeenCalledWith("/jobs/job-123");
    });
  });
});
