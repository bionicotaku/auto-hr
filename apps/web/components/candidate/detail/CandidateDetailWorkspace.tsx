"use client";

import { AppShell } from "@/components/layout/AppShell";
import { CandidateActionPanel } from "@/components/candidate/detail/CandidateActionPanel";
import { CandidateNormalizedPanel } from "@/components/candidate/detail/CandidateNormalizedPanel";
import { CandidateRawInputPanel } from "@/components/candidate/detail/CandidateRawInputPanel";
import { CandidateRubricResultsPanel } from "@/components/candidate/detail/CandidateRubricResultsPanel";
import { CandidateSupervisorPanel } from "@/components/candidate/detail/CandidateSupervisorPanel";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { ErrorStateCard } from "@/components/ui/ErrorStateCard";
import { Spinner } from "@/components/ui/Spinner";
import { getJobApiErrorMessage } from "@/lib/api/jobs";
import { useCandidateDetailQuery } from "@/lib/query/candidates";

type CandidateDetailWorkspaceProps = {
  candidateId: string;
};

export function CandidateDetailWorkspace({ candidateId }: CandidateDetailWorkspaceProps) {
  const detailQuery = useCandidateDetailQuery(candidateId);

  if (detailQuery.isLoading) {
    return (
      <AppShell title="候选人详情" description="正在加载候选人分析结果。">
        <Card className="flex min-h-[260px] items-center justify-center">
          <div className="inline-flex items-center gap-2 text-sm text-slate-600">
            <Spinner className="h-4 w-4 border-slate-300 border-t-slate-800" />
            正在加载候选人详情
          </div>
        </Card>
      </AppShell>
    );
  }

  if (detailQuery.isError) {
    return (
      <AppShell title="候选人详情" description="加载失败，请稍后重试。">
        <ErrorStateCard
          message={getJobApiErrorMessage(detailQuery.error)}
          actionLabel="重试"
          onAction={() => {
            void detailQuery.refetch();
          }}
        />
      </AppShell>
    );
  }

  if (!detailQuery.data) {
    return null;
  }

  const detail = detailQuery.data;

  return (
    <AppShell
      title={detail.normalized_profile.identity.full_name || "候选人详情"}
      description="查看原始输入、标准化信息、逐项分析结果和当前处理状态。"
      actions={
        <Button href={`/jobs/${detail.job.job_id}`} variant="secondary">
          返回岗位
        </Button>
      }
    >
      <div className="space-y-6">
        <CandidateNormalizedPanel normalizedProfile={detail.normalized_profile} />
        <CandidateRawInputPanel rawInput={detail.raw_input} />
        <CandidateSupervisorPanel
          supervisorSummary={detail.supervisor_summary}
          jobTitle={detail.job.title}
        />
        <CandidateRubricResultsPanel results={detail.rubric_results} />
        <CandidateActionPanel
          candidateId={detail.candidate_id}
          actionContext={detail.action_context}
          tags={detail.supervisor_summary.tags}
        />
      </div>
    </AppShell>
  );
}
