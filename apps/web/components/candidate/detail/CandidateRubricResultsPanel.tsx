import { Badge } from "@/components/ui/Badge";
import type { CandidateDetailRubricResultDto } from "@/lib/api/types";
import { Card } from "@/components/ui/Card";

type CandidateRubricResultsPanelProps = {
  results: CandidateDetailRubricResultDto[];
};

function decisionLabel(result: CandidateDetailRubricResultDto) {
  if (result.criterion_type === "weighted") {
    return result.score_0_to_5 !== null ? `${result.score_0_to_5.toFixed(1)} / 5` : "未评分";
  }
  if (result.hard_requirement_decision === "pass") {
    return "通过";
  }
  if (result.hard_requirement_decision === "borderline") {
    return "待确认";
  }
  return "不通过";
}

function decisionTone(result: CandidateDetailRubricResultDto) {
  if (result.criterion_type === "weighted") {
    if (result.score_0_to_5 === null) {
      return "neutral" as const;
    }
    if (result.score_0_to_5 >= 4) {
      return "mint" as const;
    }
    if (result.score_0_to_5 >= 3) {
      return "lime" as const;
    }
    if (result.score_0_to_5 >= 2) {
      return "amber" as const;
    }
    if (result.score_0_to_5 >= 1) {
      return "orange" as const;
    }
    return "red" as const;
  }

  if (result.hard_requirement_decision === "pass") {
    return "mint" as const;
  }
  if (result.hard_requirement_decision === "borderline") {
    return "blue" as const;
  }
  return "amber" as const;
}

export function CandidateRubricResultsPanel({ results }: CandidateRubricResultsPanelProps) {
  return (
    <Card className="space-y-5">
      <div className="space-y-1">
        <p className="text-xs font-semibold uppercase tracking-[0.24em] text-[var(--foreground-muted)]">
          Rubric analysis
        </p>
        <h2 className="text-lg font-semibold tracking-tight text-[var(--foreground)]">逐项分析</h2>
        <p className="text-sm leading-6 text-[var(--foreground-soft)]">
          逐条查看当前岗位评估项下的判断、理由与证据点。
        </p>
      </div>

      <div className="space-y-4">
        {results.map((result) => (
          <div key={result.job_rubric_item_id} className="rounded-[24px] border border-[var(--border)] bg-[var(--panel-strong)] px-4 py-4">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div className="space-y-1">
                <p className="text-sm font-semibold text-[var(--foreground)]">{result.rubric_name}</p>
                <p className="text-sm leading-6 text-[var(--foreground-soft)]">{result.rubric_description}</p>
              </div>
              <div className="flex flex-wrap gap-2">
                <Badge tone="blue" className="px-2.5 py-1 text-xs font-medium">
                  {result.weight_label}
                </Badge>
                <Badge tone={decisionTone(result)} className="px-2.5 py-1 text-xs font-medium">
                  {decisionLabel(result)}
                </Badge>
              </div>
            </div>
            <div className="mt-4 space-y-3">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--foreground-muted)]">判断理由</p>
                <p className="mt-1 text-sm leading-6 text-[var(--foreground-soft)]">{result.reason_text}</p>
              </div>
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--foreground-muted)]">证据点</p>
                {result.evidence_points.length > 0 ? (
                  <div className="mt-2 flex flex-wrap gap-2">
                    {result.evidence_points.map((point, index) => (
                      <span
                        key={`${result.job_rubric_item_id}-evidence-${index}`}
                        className="rounded-full bg-[var(--panel-muted)] px-3 py-1 text-xs text-[var(--foreground-soft)]"
                      >
                        {point}
                      </span>
                    ))}
                  </div>
                ) : (
                  <p className="mt-1 text-sm leading-6 text-[var(--foreground-soft)]">暂无证据点。</p>
                )}
              </div>
              {result.uncertainty_note ? (
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--foreground-muted)]">不确定因素</p>
                  <p className="mt-1 text-sm leading-6 text-[var(--foreground-soft)]">{result.uncertainty_note}</p>
                </div>
              ) : null}
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}
