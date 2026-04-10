import { apiRequest, buildApiUrl } from "@/lib/api/client";
import type { AnalysisRunDto } from "@/lib/api/types";

export function getAnalysisRun(runId: string): Promise<AnalysisRunDto> {
  return apiRequest<AnalysisRunDto>(`/api/analysis-runs/${runId}`);
}

export function createAnalysisRunEventSource(runId: string): EventSource {
  return new EventSource(buildApiUrl(`/api/analysis-runs/${runId}/events`));
}
