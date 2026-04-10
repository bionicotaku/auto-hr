"use client";

import { AppShell } from "@/components/layout/AppShell";
import { CandidateActionPanel } from "@/components/candidate/detail/CandidateActionPanel";
import { CandidateNormalizedPanel } from "@/components/candidate/detail/CandidateNormalizedPanel";
import { CandidateRawInputPanel } from "@/components/candidate/detail/CandidateRawInputPanel";
import { CandidateRubricResultsPanel } from "@/components/candidate/detail/CandidateRubricResultsPanel";
import { CandidateSupervisorPanel } from "@/components/candidate/detail/CandidateSupervisorPanel";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
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
        <Card className="space-y-2">
          <h2 className="text-lg font-semibold tracking-tight text-slate-950">加载失败</h2>
          <p className="text-sm leading-7 text-slate-600">{getJobApiErrorMessage(detailQuery.error)}</p>
        </Card>
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
        <div className="grid gap-6 xl:grid-cols-[1.08fr_0.92fr]">
          <CandidateRawInputPanel rawInput={detail.raw_input} />
          <CandidateNormalizedPanel normalizedProfile={detail.normalized_profile} />
        </div>
        <div className="grid gap-6 xl:grid-cols-[1.08fr_0.92fr]">
          <CandidateRubricResultsPanel results={detail.rubric_results} />
          <CandidateSupervisorPanel
            supervisorSummary={detail.supervisor_summary}
            jobTitle={detail.job.title}
          />
        </div>
        <CandidateActionPanel
          candidateId={detail.candidate_id}
          actionContext={detail.action_context}
          tags={detail.supervisor_summary.tags}
        />
      </div>
    </AppShell>
  );
}
