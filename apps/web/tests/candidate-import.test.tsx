import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactElement } from "react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { Providers } from "@/app/providers";
import CandidateImportPage from "@/app/jobs/[jobId]/candidates/new/page";

const pushMock = vi.fn();
const eventSourceInstances: FakeEventSource[] = [];

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push: pushMock,
  }),
}));

function renderWithProviders(node: ReactElement) {
  return render(<Providers>{node}</Providers>);
}

class FakeEventSource {
  static instances = eventSourceInstances;
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

describe("Candidate import page", () => {
  beforeEach(() => {
    pushMock.mockReset();
    eventSourceInstances.length = 0;
    vi.stubGlobal("fetch", vi.fn());
    vi.stubGlobal("EventSource", FakeEventSource as unknown as typeof EventSource);
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("renders the import page and job context", async () => {
    const fetchMock = vi.mocked(fetch);
    fetchMock.mockResolvedValueOnce(
      mockJsonResponse({
        job_id: "job-001",
        title: "AI Recruiter",
        summary: "Own the recruiting workflow.",
        lifecycle_status: "active",
      }),
    );

    renderWithProviders(
      await CandidateImportPage({ params: Promise.resolve({ jobId: "job-001" }) }),
    );

    expect(await screen.findByRole("heading", { name: "导入候选人" })).toBeInTheDocument();
    expect(await screen.findByText("AI Recruiter")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "分析" })).toBeDisabled();
  });

  it("shows the empty-input validation message", async () => {
    const fetchMock = vi.mocked(fetch);
    fetchMock.mockResolvedValueOnce(
      mockJsonResponse({
        job_id: "job-001",
        title: "AI Recruiter",
        summary: "Own the recruiting workflow.",
        lifecycle_status: "active",
      }),
    );

    renderWithProviders(
      await CandidateImportPage({ params: Promise.resolve({ jobId: "job-001" }) }),
    );

    expect(await screen.findByText("请先填写候选人文本或上传至少一份 PDF。")).toBeInTheDocument();
  });

  it("rejects more than four files and keeps the page state", async () => {
    const fetchMock = vi.mocked(fetch);
    fetchMock.mockResolvedValueOnce(
      mockJsonResponse({
        job_id: "job-001",
        title: "AI Recruiter",
        summary: "Own the recruiting workflow.",
        lifecycle_status: "active",
      }),
    );

    renderWithProviders(
      await CandidateImportPage({ params: Promise.resolve({ jobId: "job-001" }) }),
    );

    const input = await screen.findByLabelText("选择 PDF 文件");
    fireEvent.change(input, {
      target: {
        files: [
          new File(["1"], "1.pdf", { type: "application/pdf" }),
          new File(["2"], "2.pdf", { type: "application/pdf" }),
          new File(["3"], "3.pdf", { type: "application/pdf" }),
          new File(["4"], "4.pdf", { type: "application/pdf" }),
          new File(["5"], "5.pdf", { type: "application/pdf" }),
        ],
      },
    });

    expect(await screen.findByText("最多上传 4 个 PDF 文件。")).toBeInTheDocument();
  });

  it("rejects non-pdf files and clears the error after a valid upload", async () => {
    const fetchMock = vi.mocked(fetch);
    fetchMock.mockResolvedValueOnce(
      mockJsonResponse({
        job_id: "job-001",
        title: "AI Recruiter",
        summary: "Own the recruiting workflow.",
        lifecycle_status: "active",
      }),
    );

    renderWithProviders(
      await CandidateImportPage({ params: Promise.resolve({ jobId: "job-001" }) }),
    );

    const input = await screen.findByLabelText("选择 PDF 文件");

    fireEvent.change(input, {
      target: {
        files: [new File(["bad"], "notes.txt", { type: "text/plain" })],
      },
    });

    expect(await screen.findByText("只能上传 PDF 文件。")).toBeInTheDocument();

    fireEvent.change(input, {
      target: {
        files: [new File(["good"], "resume.pdf", { type: "application/pdf" })],
      },
    });

    await waitFor(() => {
      expect(screen.queryByText("只能上传 PDF 文件。")).not.toBeInTheDocument();
      expect(screen.getByText("resume.pdf")).toBeInTheDocument();
    });
  });

  it("accepts dropped pdf files instead of letting the browser open them", async () => {
    const fetchMock = vi.mocked(fetch);
    fetchMock.mockResolvedValueOnce(
      mockJsonResponse({
        job_id: "job-001",
        title: "AI Recruiter",
        summary: "Own the recruiting workflow.",
        lifecycle_status: "active",
      }),
    );

    renderWithProviders(
      await CandidateImportPage({ params: Promise.resolve({ jobId: "job-001" }) }),
    );

    const dropzoneText = await screen.findByText("选择 PDF 文件");
    const dropzone = dropzoneText.closest("label");
    const file = new File(["resume"], "resume.pdf", { type: "application/pdf" });

    expect(dropzone).not.toBeNull();

    fireEvent.drop(dropzone as HTMLElement, {
      dataTransfer: {
        files: [file],
        types: ["Files"],
      },
    });

    expect(await screen.findByText("resume.pdf")).toBeInTheDocument();
    expect(pushMock).not.toHaveBeenCalled();
  });

  it("keeps entered text and navigates back to jobs on cancel", async () => {
    const fetchMock = vi.mocked(fetch);
    fetchMock.mockResolvedValueOnce(
      mockJsonResponse({
        job_id: "job-001",
        title: "AI Recruiter",
        summary: "Own the recruiting workflow.",
        lifecycle_status: "active",
      }),
    );

    renderWithProviders(
      await CandidateImportPage({ params: Promise.resolve({ jobId: "job-001" }) }),
    );

    const textarea = await screen.findByLabelText("候选人原始文本");
    fireEvent.change(textarea, {
      target: { value: "Candidate profile summary" },
    });

    expect(textarea).toHaveValue("Candidate profile summary");

    fireEvent.click(screen.getByRole("button", { name: "取消" }));
    expect(pushMock).toHaveBeenCalledWith("/jobs");
    expect(textarea).toHaveValue("Candidate profile summary");
  });

  it("uses the floating back button to return to the current job", async () => {
    const fetchMock = vi.mocked(fetch);
    fetchMock.mockResolvedValueOnce(
      mockJsonResponse({
        job_id: "job-001",
        title: "AI Recruiter",
        summary: "Own the recruiting workflow.",
        lifecycle_status: "active",
      }),
    );

    renderWithProviders(
      await CandidateImportPage({ params: Promise.resolve({ jobId: "job-001" }) }),
    );

    await screen.findByText("AI Recruiter");
    fireEvent.click(screen.getByRole("button", { name: "返回上一页" }));

    expect(pushMock).toHaveBeenCalledWith("/jobs/job-001");
  });

  it("starts an analysis run and navigates to candidate detail after completion", async () => {
    const fetchMock = vi.mocked(fetch);
    fetchMock
      .mockResolvedValueOnce(
        mockJsonResponse({
          job_id: "job-001",
          title: "AI Recruiter",
          summary: "Own the recruiting workflow.",
          lifecycle_status: "active",
        }),
      )
      .mockResolvedValueOnce(
        mockJsonResponse({
          run_id: "run-001",
          run_type: "candidate_import",
          status: "queued",
          total_ai_steps: 6,
        }, 201),
      );

    renderWithProviders(
      await CandidateImportPage({ params: Promise.resolve({ jobId: "job-001" }) }),
    );

    const textarea = await screen.findByLabelText("候选人原始文本");
    fireEvent.change(textarea, {
      target: { value: "Candidate profile summary" },
    });

    const submitButton = screen.getByRole("button", { name: "分析" });
    expect(submitButton).not.toBeDisabled();

    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("/api/jobs/job-001/candidate-import-runs"),
        expect.objectContaining({
          method: "POST",
          body: expect.any(FormData),
        }),
      );
    });

    expect(await screen.findByText("候选人分析进度")).toBeInTheDocument();
    expect(eventSourceInstances[0]?.url).toContain("/api/analysis-runs/run-001/events");

    await act(async () => {
      eventSourceInstances[0].emit("connected", {
        run_id: "run-001",
        run_type: "candidate_import",
        status: "running",
        current_stage: "preparing",
        current_ai_step: 0,
        total_ai_steps: 6,
      });
      eventSourceInstances[0].emit("progress", {
        run_id: "run-001",
        run_type: "candidate_import",
        current_stage: "standardizing",
        current_ai_step: 1,
        total_ai_steps: 6,
        message: "AI 已完成候选人标准化",
      });
      eventSourceInstances[0].emit("completed", {
        run_id: "run-001",
        run_type: "candidate_import",
        result_resource_type: "candidate",
        result_resource_id: "candidate-001",
      });
    });

    await waitFor(() => {
      expect(pushMock).toHaveBeenCalledWith("/candidates/candidate-001");
    });
  });

  it("keeps entered input when analysis run fails", async () => {
    const fetchMock = vi.mocked(fetch);
    fetchMock
      .mockResolvedValueOnce(
        mockJsonResponse({
          job_id: "job-001",
          title: "AI Recruiter",
          summary: "Own the recruiting workflow.",
          lifecycle_status: "active",
        }),
      )
      .mockResolvedValueOnce(
        mockJsonResponse({
          run_id: "run-001",
          run_type: "candidate_import",
          status: "queued",
          total_ai_steps: 6,
        }, 201),
      );

    renderWithProviders(
      await CandidateImportPage({ params: Promise.resolve({ jobId: "job-001" }) }),
    );

    const textarea = await screen.findByLabelText("候选人原始文本");
    fireEvent.change(textarea, {
      target: { value: "Candidate profile summary" },
    });

    fireEvent.click(screen.getByRole("button", { name: "分析" }));

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("/api/jobs/job-001/candidate-import-runs"),
        expect.objectContaining({ method: "POST" }),
      );
    });

    await act(async () => {
      eventSourceInstances[0].emit("failed", {
        run_id: "run-001",
        run_type: "candidate_import",
        message: "候选人导入失败",
      });
    });

    expect(await screen.findByText("候选人导入失败")).toBeInTheDocument();
    expect(textarea).toHaveValue("Candidate profile summary");
    expect(pushMock).not.toHaveBeenCalled();
  });
});
