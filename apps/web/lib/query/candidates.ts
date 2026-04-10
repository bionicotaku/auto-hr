"use client";

import { useQuery } from "@tanstack/react-query";

import { getCandidateDetail } from "@/lib/api/candidates";
import type { CandidateDetailDto } from "@/lib/api/types";

export function useCandidateDetailQuery(candidateId: string) {
  return useQuery<CandidateDetailDto>({
    queryKey: ["candidate-detail", candidateId],
    queryFn: () => getCandidateDetail(candidateId),
    enabled: Boolean(candidateId),
    retry: false,
  });
}
