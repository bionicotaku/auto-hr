"use client";

import { useMutation, useQuery } from "@tanstack/react-query";

import {
  agentEditJobDraft,
  chatJobDraft,
  deleteJobDraft,
  finalizeJobDraft,
  getJobEdit,
  regenerateJobDraft,
} from "@/lib/api/jobs";
import type {
  JobChatRequestDto,
  JobChatResponseDto,
  JobEditResponseDto,
  JobFinalizeRequestDto,
  JobFinalizeResponseDto,
  JobGeneratedContentRequestDto,
  JobGeneratedContentResponseDto,
  JobRegenerateRequestDto,
} from "@/lib/api/types";

export function useJobEditQuery(jobId: string) {
  return useQuery<JobEditResponseDto>({
    queryKey: ["job-edit", jobId],
    queryFn: () => getJobEdit(jobId),
    enabled: Boolean(jobId),
  });
}

export function useJobChatMutation(jobId: string) {
  return useMutation<JobChatResponseDto, Error, JobChatRequestDto>({
    mutationFn: (payload) => chatJobDraft(jobId, payload),
  });
}

export function useJobAgentEditMutation(jobId: string) {
  return useMutation<JobGeneratedContentResponseDto, Error, JobGeneratedContentRequestDto>({
    mutationFn: (payload) => agentEditJobDraft(jobId, payload),
  });
}

export function useJobRegenerateMutation(jobId: string) {
  return useMutation<JobGeneratedContentResponseDto, Error, JobRegenerateRequestDto>({
    mutationFn: (payload) => regenerateJobDraft(jobId, payload),
  });
}

export function useJobFinalizeMutation(jobId: string) {
  return useMutation<JobFinalizeResponseDto, Error, JobFinalizeRequestDto>({
    mutationFn: (payload) => finalizeJobDraft(jobId, payload),
  });
}

export function useDeleteJobDraftMutation(jobId: string) {
  return useMutation<void, Error, void>({
    mutationFn: () => deleteJobDraft(jobId),
  });
}
