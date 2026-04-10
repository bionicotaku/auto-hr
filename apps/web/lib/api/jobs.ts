import { apiRequest } from "@/lib/api/client";
import type {
  CreateJobDraftResponseDto,
  CreateJobFromDescriptionRequestDto,
  CreateJobFromFormRequestDto,
} from "@/lib/api/types";
import { ApiError } from "@/lib/api/types";

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function toStringOrNull(value: unknown) {
  return typeof value === "string" && value.trim() ? value : null;
}

function normalizeJobDraftResponse(raw: unknown): CreateJobDraftResponseDto {
  if (!isRecord(raw)) {
    throw new Error("创建 Job draft 的响应格式不正确。");
  }

  const jobId = toStringOrNull(raw.jobId) ?? toStringOrNull(raw.job_id) ?? toStringOrNull(raw.id);
  if (!jobId) {
    throw new Error("创建 Job draft 的响应缺少 jobId。");
  }

  return {
    jobId,
    job_id: jobId,
    id: jobId,
    title: toStringOrNull(raw.title) ?? undefined,
    summary: toStringOrNull(raw.summary) ?? undefined,
    descriptionText: toStringOrNull(raw.descriptionText) ?? toStringOrNull(raw.description_text) ?? undefined,
    description_text: toStringOrNull(raw.description_text) ?? undefined,
  };
}

export async function createJobFromDescription(
  payload: CreateJobFromDescriptionRequestDto,
): Promise<CreateJobDraftResponseDto> {
  const response = await apiRequest<unknown>("/api/jobs/from-description", {
    method: "POST",
    body: JSON.stringify(payload),
  });

  return normalizeJobDraftResponse(response);
}

export async function createJobFromForm(payload: CreateJobFromFormRequestDto): Promise<CreateJobDraftResponseDto> {
  const response = await apiRequest<unknown>("/api/jobs/from-form", {
    method: "POST",
    body: JSON.stringify(payload),
  });

  return normalizeJobDraftResponse(response);
}

export function getJobApiErrorMessage(error: unknown) {
  if (error instanceof ApiError) {
    return error.message;
  }

  if (error instanceof Error) {
    return error.message;
  }

  return "请求失败，请稍后重试。";
}

