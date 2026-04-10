import { apiRequest } from "@/lib/api/client";
import type { CandidateDetailDto } from "@/lib/api/types";

export function getCandidateDetail(candidateId: string): Promise<CandidateDetailDto> {
  return apiRequest<CandidateDetailDto>(`/api/candidates/${candidateId}`);
}
