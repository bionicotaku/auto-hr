import type { CandidateDetailSupervisorDto } from "@/lib/api/types";
import { Card } from "@/components/ui/Card";

type CandidateSupervisorPanelProps = {
  supervisorSummary: CandidateDetailSupervisorDto;
  jobTitle: string;
};

function hardRequirementLabel(value: CandidateDetailSupervisorDto["hard_requirement_overall"]) {
  if (value === "all_pass") {
    return "硬门槛全部通过";
  }
  if (value === "has_borderline") {
    return "存在待确认硬门槛";
  }
  return "存在未通过硬门槛";
}

function recommendationLabel(value: CandidateDetailSupervisorDto["recommendation"]) {
  if (value === "advance") {
    return "建议推进";
  }
  if (value === "manual_review") {
    return "建议人工复核";
  }
  if (value === "hold") {
    return "建议暂缓";
  }
  return "建议淘汰";
}

export function CandidateSupervisorPanel({
  supervisorSummary,
  jobTitle,
}: CandidateSupervisorPanelProps) {
  return (
    <Card className="space-y-5">
      <div className="space-y-1">
        <h2 className="text-lg font-semibold tracking-tight text-slate-950">汇总结论</h2>
        <p className="text-sm leading-6 text-slate-600">围绕 {jobTitle} 汇总最终结论、总分和核心证据。</p>
      </div>

      <div className="flex flex-wrap gap-2">
        <span className="rounded-full bg-slate-100 px-3 py-1 text-sm text-slate-700">
          {hardRequirementLabel(supervisorSummary.hard_requirement_overall)}
        </span>
        <span className="rounded-full bg-emerald-50 px-3 py-1 text-sm text-emerald-700">
          {recommendationLabel(supervisorSummary.recommendation)}
        </span>
      </div>

      <div className="grid gap-3 sm:grid-cols-2">
        <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-4">
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">总分（5 分）</p>
          <p className="mt-2 text-2xl font-semibold tracking-tight text-slate-950">
            {supervisorSummary.overall_score_5 !== null ? supervisorSummary.overall_score_5.toFixed(1) : "--"}
          </p>
        </div>
        <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-4">
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">总分（百分制）</p>
          <p className="mt-2 text-2xl font-semibold tracking-tight text-slate-950">
            {supervisorSummary.overall_score_percent !== null
              ? `${Math.round(supervisorSummary.overall_score_percent)}`
              : "--"}
          </p>
        </div>
      </div>

      <div>
        <p className="text-sm font-medium text-slate-900">AI 总结</p>
        <p className="mt-2 text-sm leading-7 text-slate-700">{supervisorSummary.ai_summary}</p>
      </div>

      <div className="space-y-2">
        <p className="text-sm font-medium text-slate-900">核心证据点</p>
        {supervisorSummary.evidence_points.length > 0 ? (
          <div className="flex flex-wrap gap-2">
            {supervisorSummary.evidence_points.map((point, index) => (
              <span key={`summary-evidence-${index}`} className="rounded-full bg-slate-100 px-3 py-1 text-xs text-slate-600">
                {point}
              </span>
            ))}
          </div>
        ) : (
          <p className="text-sm leading-6 text-slate-600">暂无证据点。</p>
        )}
      </div>

      <div className="space-y-2">
        <p className="text-sm font-medium text-slate-900">标签</p>
        {supervisorSummary.tags.length > 0 ? (
          <div className="flex flex-wrap gap-2">
            {supervisorSummary.tags.map((tag) => (
              <span key={tag.id} className="rounded-full bg-sky-50 px-3 py-1 text-xs text-sky-700">
                {tag.name}
              </span>
            ))}
          </div>
        ) : (
          <p className="text-sm leading-6 text-slate-600">当前没有标签。</p>
        )}
      </div>
    </Card>
  );
}
