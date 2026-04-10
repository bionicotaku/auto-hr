import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactElement } from "react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { Providers } from "@/app/providers";
import JobNewFromDescriptionPage from "@/app/jobs/new/from-description/page";
import JobNewFromFormPage from "@/app/jobs/new/from-form/page";
import JobNewPage from "@/app/jobs/new/page";

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

describe("Job creation pages", () => {
  beforeEach(() => {
    pushMock.mockReset();
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("renders the new job entry page", () => {
    renderWithProviders(<JobNewPage />);

    expect(screen.getByRole("heading", { name: "新建岗位" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "导入职位描述" })).toHaveAttribute(
      "href",
      "/jobs/new/from-description",
    );
    expect(screen.getByRole("link", { name: "填写岗位信息" })).toHaveAttribute("href", "/jobs/new/from-form");
  });

  it("submits the description flow and navigates to the edit page on success", async () => {
    const fetchMock = vi.mocked(fetch);
    fetchMock.mockResolvedValueOnce(mockJsonResponse({ jobId: "job-123" }));

    renderWithProviders(<JobNewFromDescriptionPage />);

    fireEvent.change(screen.getByLabelText("职位描述"), {
      target: { value: "Senior frontend engineer needed." },
    });
    fireEvent.click(screen.getByRole("button", { name: "生成岗位初稿" }));

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        "/api/jobs/from-description",
        expect.objectContaining({
          method: "POST",
          body: JSON.stringify({ description_text: "Senior frontend engineer needed." }),
        }),
      );
      expect(pushMock).toHaveBeenCalledWith("/jobs/job-123/edit");
    });
  });

  it("shows the description flow error and keeps the input value", async () => {
    const fetchMock = vi.mocked(fetch);
    fetchMock.mockResolvedValueOnce(mockJsonResponse({ message: "描述解析失败" }, 400));

    renderWithProviders(<JobNewFromDescriptionPage />);

    const textarea = screen.getByLabelText("职位描述");
    fireEvent.change(textarea, {
      target: { value: "Broken description" },
    });
    fireEvent.click(screen.getByRole("button", { name: "生成岗位初稿" }));

    expect(await screen.findByText("描述解析失败")).toBeInTheDocument();
    expect(textarea).toHaveValue("Broken description");
    expect(pushMock).not.toHaveBeenCalled();
  });

  it("submits the form flow and navigates to the edit page on success", async () => {
    const fetchMock = vi.mocked(fetch);
    fetchMock.mockResolvedValueOnce(mockJsonResponse({ id: "job-456" }));

    renderWithProviders(<JobNewFromFormPage />);

    fireEvent.change(screen.getByLabelText("岗位名称"), {
      target: { value: "Senior Frontend Engineer" },
    });
    fireEvent.change(screen.getByLabelText("部门"), {
      target: { value: "Product" },
    });
    fireEvent.change(screen.getByLabelText("地点"), {
      target: { value: "Remote" },
    });
    fireEvent.change(screen.getByLabelText("资历要求"), {
      target: { value: "Senior" },
    });
    fireEvent.click(screen.getByRole("button", { name: "生成岗位初稿" }));

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        "/api/jobs/from-form",
        expect.objectContaining({
          method: "POST",
        }),
      );
      expect(pushMock).toHaveBeenCalledWith("/jobs/job-456/edit");
    });
  });

  it("shows the form flow error and keeps the entered values", async () => {
    const fetchMock = vi.mocked(fetch);
    fetchMock.mockResolvedValueOnce(mockJsonResponse({ detail: "表单校验失败" }, 422));

    renderWithProviders(<JobNewFromFormPage />);

    const titleInput = screen.getByLabelText("岗位名称");
    fireEvent.change(titleInput, {
      target: { value: "Senior Frontend Engineer" },
    });
    fireEvent.change(screen.getByLabelText("部门"), {
      target: { value: "Product" },
    });
    fireEvent.change(screen.getByLabelText("地点"), {
      target: { value: "Remote" },
    });
    fireEvent.change(screen.getByLabelText("资历要求"), {
      target: { value: "Senior" },
    });
    fireEvent.click(screen.getByRole("button", { name: "生成岗位初稿" }));

    expect(await screen.findByText("表单校验失败")).toBeInTheDocument();
    expect(titleInput).toHaveValue("Senior Frontend Engineer");
    expect(pushMock).not.toHaveBeenCalled();
  });
});
