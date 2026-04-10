import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import CandidateDetailPage from "@/app/candidates/[candidateId]/page";
import HomePage from "@/app/page";
import JobEditPage from "@/app/jobs/[jobId]/edit/page";
import JobsPage from "@/app/jobs/page";

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
  });

  it("redirects the root route to jobs", () => {
    HomePage();

    expect(redirectMock).toHaveBeenCalledWith("/jobs");
  });

  it("renders the jobs overview", () => {
    render(<JobsPage />);

    expect(screen.getByRole("heading", { name: "岗位" })).toBeInTheDocument();
    expect(screen.getAllByRole("link", { name: "新建岗位" })).toHaveLength(2);
  });

  it("renders the job edit workspace shell", async () => {
    render(await JobEditPage({ params: Promise.resolve({ jobId: "job-123" }) }));

    expect(screen.getByRole("heading", { name: "岗位编辑" })).toBeInTheDocument();
    expect(screen.getByText("编号 job-123")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "职位描述" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "评估规范" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "修改要求" })).toBeInTheDocument();
  });

  it("renders the candidate detail empty state", async () => {
    render(await CandidateDetailPage({ params: Promise.resolve({ candidateId: "cand-001" }) }));

    expect(screen.getByRole("heading", { name: "候选人详情" })).toBeInTheDocument();
    expect(screen.getByText("候选人 cand-001")).toBeInTheDocument();
  });
});
