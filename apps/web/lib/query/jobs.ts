"use client";

import { useMutation, useQuery } from "@tanstack/react-query";

import {
  agentEditJobDraft,
  chatJobDraft,
  deleteJobDraft,
  finalizeJobDraft,
  getJobCandidates,
  getJobCandidateImportContext,
  getJobDetail,
  getJobEdit,
  getJobs,
  importCandidateToJob,
  regenerateJobDraft,
} from "@/lib/api/jobs";
import type {
  CandidateImportResponseDto,
  JobChatRequestDto,
  JobChatResponseDto,
  JobCandidateImportContextDto,
  JobCandidateListQueryDto,
  JobCandidateListResponseDto,
  JobDetailResponseDto,
  JobEditResponseDto,
  JobFinalizeRequestDto,
  JobFinalizeResponseDto,
  JobGeneratedContentRequestDto,
  JobGeneratedContentResponseDto,
  JobListResponseDto,
  JobRegenerateRequestDto,
} from "@/lib/api/types";

export function useJobsQuery() {
  return useQuery<JobListResponseDto>({
    queryKey: ["jobs"],
    queryFn: () => getJobs(),
    retry: false,
  });
}

export function useJobDetailQuery(jobId: string) {
  return useQuery<JobDetailResponseDto>({
    queryKey: ["job-detail", jobId],
    queryFn: () => getJobDetail(jobId),
    enabled: Boolean(jobId),
  });
}

export function useJobEditQuery(jobId: string) {
  return useQuery<JobEditResponseDto>({
    queryKey: ["job-edit", jobId],
    queryFn: () => getJobEdit(jobId),
    enabled: Boolean(jobId),
  });
}

export function useJobCandidateImportContextQuery(jobId: string) {
  return useQuery<JobCandidateImportContextDto>({
    queryKey: ["job-candidate-import-context", jobId],
    queryFn: () => getJobCandidateImportContext(jobId),
    enabled: Boolean(jobId),
  });
}

export function useJobCandidatesQuery(jobId: string, query: JobCandidateListQueryDto) {
  return useQuery<JobCandidateListResponseDto>({
    queryKey: ["job-candidates", jobId, query.sort, query.status, query.tags.join(","), query.q],
    queryFn: () => getJobCandidates(jobId, query),
    enabled: Boolean(jobId),
  });
}

export function useCandidateImportMutation(jobId: string) {
  return useMutation<CandidateImportResponseDto, Error, FormData>({
    mutationFn: (payload) => importCandidateToJob(jobId, payload),
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
