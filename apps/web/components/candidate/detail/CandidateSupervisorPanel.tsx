import type { CandidateDetailSupervisorDto } from "@/lib/api/types";
import { Badge } from "@/components/ui/Badge";
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

function hardRequirementTone(value: CandidateDetailSupervisorDto["hard_requirement_overall"]) {
  if (value === "all_pass") {
    return "mint" as const;
  }
  if (value === "has_borderline") {
    return "blue" as const;
  }
  return "amber" as const;
}

function recommendationTone(value: CandidateDetailSupervisorDto["recommendation"]) {
  if (value === "advance") {
    return "mint" as const;
  }
  if (value === "manual_review") {
    return "blue" as const;
  }
  return "amber" as const;
}

export function CandidateSupervisorPanel({
  supervisorSummary,
  jobTitle,
}: CandidateSupervisorPanelProps) {
  return (
    <Card className="space-y-5">
      <div className="space-y-1">
        <p className="text-xs font-semibold uppercase tracking-[0.24em] text-[var(--foreground-muted)]">
          Supervisor summary
        </p>
        <h2 className="text-lg font-semibold tracking-tight text-[var(--foreground)]">汇总结论</h2>
        <p className="text-sm leading-6 text-[var(--foreground-soft)]">
          围绕 {jobTitle} 汇总最终结论、总分和核心证据。
        </p>
      </div>

      <div className="flex flex-wrap gap-2">
        <Badge tone={hardRequirementTone(supervisorSummary.hard_requirement_overall)} className="text-sm">
          {hardRequirementLabel(supervisorSummary.hard_requirement_overall)}
        </Badge>
        <Badge tone={recommendationTone(supervisorSummary.recommendation)} className="text-sm">
          {recommendationLabel(supervisorSummary.recommendation)}
        </Badge>
      </div>

      <div className="grid gap-3 sm:grid-cols-1">
        <div className="rounded-[24px] border border-[var(--border)] bg-[var(--panel-muted)] px-4 py-4">
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--foreground-muted)]">
            总分（百分制）
          </p>
          <p className="mt-2 text-2xl font-semibold tracking-tight text-[var(--foreground)]">
            {supervisorSummary.overall_score_percent !== null
              ? `${Math.round(supervisorSummary.overall_score_percent)}`
              : "--"}
          </p>
        </div>
      </div>

      <div>
        <p className="text-sm font-medium text-[var(--foreground)]">AI 总结</p>
        <p className="mt-2 text-sm leading-7 text-[var(--foreground-soft)]">{supervisorSummary.ai_summary}</p>
      </div>

      <div className="space-y-2">
        <p className="text-sm font-medium text-[var(--foreground)]">核心证据点</p>
        {supervisorSummary.evidence_points.length > 0 ? (
          <div className="flex flex-wrap gap-2">
            {supervisorSummary.evidence_points.map((point, index) => (
              <span
                key={`summary-evidence-${index}`}
                className="rounded-full bg-[var(--panel-muted)] px-3 py-1 text-xs text-[var(--foreground-soft)]"
              >
                {point}
              </span>
            ))}
          </div>
        ) : (
          <p className="text-sm leading-6 text-[var(--foreground-soft)]">暂无证据点。</p>
        )}
      </div>

      <div className="space-y-2">
        <p className="text-sm font-medium text-[var(--foreground)]">标签</p>
        {supervisorSummary.tags.length > 0 ? (
          <div className="flex flex-wrap gap-2">
            {supervisorSummary.tags.map((tag) => (
              <Badge key={tag.id} tone="blue" className="text-xs font-medium">
                {tag.name}
              </Badge>
            ))}
          </div>
        ) : (
          <p className="text-sm leading-6 text-[var(--foreground-soft)]">当前没有标签。</p>
        )}
      </div>
    </Card>
  );
}
