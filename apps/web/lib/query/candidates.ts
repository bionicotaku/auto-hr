"use client";

import { useMutation, useQuery } from "@tanstack/react-query";

import {
  createCandidateEmailDraft,
  createCandidateFeedback,
  createCandidateTag,
  getCandidateDetail,
  updateCandidateStatus,
} from "@/lib/api/candidates";
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

export function useCandidateDetailQuery(candidateId: string) {
  return useQuery<CandidateDetailDto>({
    queryKey: ["candidate-detail", candidateId],
    queryFn: () => getCandidateDetail(candidateId),
    enabled: Boolean(candidateId),
    retry: false,
  });
}

export function useCandidateStatusMutation(candidateId: string) {
  return useMutation<CandidateStatusUpdateResponseDto, Error, CandidateStatusUpdateRequestDto>({
    mutationFn: (payload) => updateCandidateStatus(candidateId, payload),
  });
}

export function useCandidateTagMutation(candidateId: string) {
  return useMutation<CandidateDetailTagDto, Error, CandidateTagCreateRequestDto>({
    mutationFn: (payload) => createCandidateTag(candidateId, payload),
  });
}

export function useCandidateFeedbackMutation(candidateId: string) {
  return useMutation<CandidateDetailFeedbackDto, Error, CandidateFeedbackCreateRequestDto>({
    mutationFn: (payload) => createCandidateFeedback(candidateId, payload),
  });
}

export function useCandidateEmailDraftMutation(candidateId: string) {
  return useMutation<CandidateDetailEmailDraftDto, Error, CandidateEmailDraftCreateRequestDto>({
    mutationFn: (payload) => createCandidateEmailDraft(candidateId, payload),
  });
}
