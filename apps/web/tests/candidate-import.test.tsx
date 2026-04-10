import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactElement } from "react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { Providers } from "@/app/providers";
import CandidateImportPage from "@/app/jobs/[jobId]/candidates/new/page";

const pushMock = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push: pushMock,
  }),
}));

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

describe("Candidate import page", () => {
  beforeEach(() => {
    pushMock.mockReset();
    vi.stubGlobal("fetch", vi.fn());
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
    expect(screen.getByRole("button", { name: "生成" })).toBeDisabled();
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

  it("submits form data and navigates to candidate detail after success", async () => {
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
          candidate_id: "candidate-001",
          job_id: "job-001",
        }, 201),
      );

    renderWithProviders(
      await CandidateImportPage({ params: Promise.resolve({ jobId: "job-001" }) }),
    );

    const textarea = await screen.findByLabelText("候选人原始文本");
    fireEvent.change(textarea, {
      target: { value: "Candidate profile summary" },
    });

    const submitButton = screen.getByRole("button", { name: "生成" });
    expect(submitButton).not.toBeDisabled();

    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        "/api/jobs/job-001/candidates/import",
        expect.objectContaining({
          method: "POST",
          body: expect.any(FormData),
        }),
      );
      expect(pushMock).toHaveBeenCalledWith("/candidates/candidate-001");
    });
  });

  it("keeps entered input when import fails", async () => {
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
        mockJsonResponse({ message: "候选人导入失败" }, 422),
      );

    renderWithProviders(
      await CandidateImportPage({ params: Promise.resolve({ jobId: "job-001" }) }),
    );

    const textarea = await screen.findByLabelText("候选人原始文本");
    fireEvent.change(textarea, {
      target: { value: "Candidate profile summary" },
    });

    fireEvent.click(screen.getByRole("button", { name: "生成" }));

    expect(await screen.findByText("候选人导入失败")).toBeInTheDocument();
    expect(textarea).toHaveValue("Candidate profile summary");
    expect(pushMock).not.toHaveBeenCalled();
  });
});
