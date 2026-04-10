import { apiRequest } from "@/lib/api/client";
import type {
  CandidateDetailDto,
  CandidateDetailEmailDraftDto,
  CandidateDetailFeedbackDto,
  CandidateDetailTagDto,
  CandidateEmailDraftCreateRequestDto,
  CandidateFeedbackCreateRequestDto,
  CandidateStatusUpdateRequestDto,
  CandidateStatusUpdateResponseDto,
  CandidateTagCreateRequestDto,
} from "@/lib/api/types";

export function getCandidateDetail(candidateId: string): Promise<CandidateDetailDto> {
  return apiRequest<CandidateDetailDto>(`/api/candidates/${candidateId}`);
}

export function updateCandidateStatus(
  candidateId: string,
  payload: CandidateStatusUpdateRequestDto,
): Promise<CandidateStatusUpdateResponseDto> {
  return apiRequest<CandidateStatusUpdateResponseDto>(`/api/candidates/${candidateId}/status`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export function createCandidateTag(
  candidateId: string,
  payload: CandidateTagCreateRequestDto,
): Promise<CandidateDetailTagDto> {
  return apiRequest<CandidateDetailTagDto>(`/api/candidates/${candidateId}/tags`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function createCandidateFeedback(
  candidateId: string,
  payload: CandidateFeedbackCreateRequestDto,
): Promise<CandidateDetailFeedbackDto> {
  return apiRequest<CandidateDetailFeedbackDto>(`/api/candidates/${candidateId}/feedbacks`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function createCandidateEmailDraft(
  candidateId: string,
  payload: CandidateEmailDraftCreateRequestDto,
): Promise<CandidateDetailEmailDraftDto> {
  return apiRequest<CandidateDetailEmailDraftDto>(`/api/candidates/${candidateId}/email-drafts`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
