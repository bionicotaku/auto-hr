import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactElement } from "react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { Providers } from "@/app/providers";
import { JobEditWorkspace } from "@/components/job/edit/JobEditWorkspace";

const pushMock = vi.fn();
const eventSourceInstances: FakeEventSource[] = [];

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

class FakeEventSource {
  listeners = new Map<string, Array<(event: MessageEvent<string>) => void>>();
  onerror: ((this: EventSource, ev: Event) => unknown) | null = null;
  url: string;

  constructor(url: string) {
    this.url = url;
    eventSourceInstances.push(this);
  }

  addEventListener(type: string, listener: (event: MessageEvent<string>) => void) {
    const current = this.listeners.get(type) ?? [];
    current.push(listener);
    this.listeners.set(type, current);
  }

  close() {
    return undefined;
  }

  emit(type: string, payload: unknown) {
    const listeners = this.listeners.get(type) ?? [];
    for (const listener of listeners) {
      listener(new MessageEvent("message", { data: JSON.stringify(payload) }));
    }
  }
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
    eventSourceInstances.length = 0;
    vi.stubGlobal("fetch", vi.fn());
    vi.stubGlobal("EventSource", FakeEventSource as unknown as typeof EventSource);
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

  it("starts a finalize run and navigates to job detail after completion", async () => {
    const fetchMock = vi.mocked(fetch);
    fetchMock
      .mockResolvedValueOnce(mockJsonResponse(makeEditPayload()))
      .mockResolvedValueOnce(
        mockJsonResponse({
          run_id: "run-job-123",
          run_type: "job_finalize",
          status: "queued",
          total_ai_steps: 2,
        }),
      );

    renderWithProviders(<JobEditWorkspace jobId="job-123" />);

    await screen.findByDisplayValue("Initial JD body");
    fireEvent.click(screen.getByRole("button", { name: "保存" }));

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("/api/jobs/job-123/finalize-runs"),
        expect.objectContaining({
          method: "POST",
        }),
      );
    });

    expect(await screen.findByText("岗位分析进度")).toBeInTheDocument();

    await act(async () => {
      eventSourceInstances[0].emit("connected", {
        run_id: "run-job-123",
        run_type: "job_finalize",
        status: "running",
        current_stage: "preparing",
        current_ai_step: 0,
        total_ai_steps: 2,
      });
      eventSourceInstances[0].emit("progress", {
        run_id: "run-job-123",
        run_type: "job_finalize",
        current_stage: "finalizing_definition",
        current_ai_step: 1,
        total_ai_steps: 2,
        message: "AI 已完成岗位标题与摘要生成",
      });
      eventSourceInstances[0].emit("progress", {
        run_id: "run-job-123",
        run_type: "job_finalize",
        current_stage: "finalizing_definition",
        current_ai_step: 2,
        total_ai_steps: 2,
        message: "AI 已完成评估项定稿：1",
      });
      eventSourceInstances[0].emit("completed", {
        run_id: "run-job-123",
        run_type: "job_finalize",
        result_resource_type: "job",
        result_resource_id: "job-123",
      });
    });

    await waitFor(() => {
      expect(pushMock).toHaveBeenCalledWith("/jobs/job-123");
    });
    expect(screen.getByText("已完成 2 / 2 个 AI 分析步骤")).toBeInTheDocument();
  });

  it("returns to the job detail page after saving an active job with changes", async () => {
    const fetchMock = vi.mocked(fetch);
    fetchMock
      .mockResolvedValueOnce(mockJsonResponse(makeActiveEditPayload()))
      .mockResolvedValueOnce(
        mockJsonResponse({
          run_id: "run-job-123",
          run_type: "job_finalize",
          status: "queued",
          total_ai_steps: 2,
        }),
      );

    renderWithProviders(<JobEditWorkspace jobId="job-123" />);

    const description = await screen.findByLabelText("职位描述编辑区");
    fireEvent.change(description, {
      target: { value: "Updated active JD" },
    });
    fireEvent.click(screen.getByRole("button", { name: "保存" }));

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("/api/jobs/job-123/finalize-runs"),
        expect.objectContaining({
          method: "POST",
        }),
      );
    });

    await act(async () => {
      eventSourceInstances[0].emit("completed", {
        run_id: "run-job-123",
        run_type: "job_finalize",
        result_resource_type: "job",
        result_resource_id: "job-123",
      });
    });

    await waitFor(() => {
      expect(pushMock).toHaveBeenCalledWith("/jobs/job-123");
    });
  });

  it("keeps local truth when finalize run fails", async () => {
    const fetchMock = vi.mocked(fetch);
    fetchMock
      .mockResolvedValueOnce(mockJsonResponse(makeEditPayload()))
      .mockResolvedValueOnce(
        mockJsonResponse({
          run_id: "run-job-123",
          run_type: "job_finalize",
          status: "queued",
          total_ai_steps: 2,
        }),
      );

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

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("/api/jobs/job-123/finalize-runs"),
        expect.objectContaining({ method: "POST" }),
      );
    });

    await act(async () => {
      eventSourceInstances[0].emit("failed", {
        run_id: "run-job-123",
        run_type: "job_finalize",
        message: "最终定稿失败",
      });
    });

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

  it("uses the floating back button to leave a draft edit page", async () => {
    const fetchMock = vi.mocked(fetch);
    fetchMock.mockResolvedValueOnce(mockJsonResponse(makeEditPayload()));

    renderWithProviders(<JobEditWorkspace jobId="job-123" />);

    await screen.findByDisplayValue("Initial JD body");
    fireEvent.click(screen.getByRole("button", { name: "返回上一页" }));

    expect(pushMock).toHaveBeenCalledWith("/jobs");
  });

  it("uses the floating back button to leave an active edit page", async () => {
    const fetchMock = vi.mocked(fetch);
    fetchMock.mockResolvedValueOnce(mockJsonResponse(makeActiveEditPayload()));

    renderWithProviders(<JobEditWorkspace jobId="job-123" />);

    await screen.findByDisplayValue("Initial JD body");
    fireEvent.click(screen.getByRole("button", { name: "返回上一页" }));

    expect(pushMock).toHaveBeenCalledWith("/jobs/job-123");
  });
});
