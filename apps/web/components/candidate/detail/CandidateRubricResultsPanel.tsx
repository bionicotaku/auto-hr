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

export function CandidateRubricResultsPanel({ results }: CandidateRubricResultsPanelProps) {
  return (
    <Card className="space-y-5">
      <div className="space-y-1">
        <h2 className="text-lg font-semibold tracking-tight text-slate-950">逐项分析</h2>
        <p className="text-sm leading-6 text-slate-600">逐条查看当前岗位评估项下的判断、理由与证据点。</p>
      </div>

      <div className="space-y-4">
        {results.map((result) => (
          <div key={result.job_rubric_item_id} className="rounded-2xl border border-slate-200 bg-white px-4 py-4">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div className="space-y-1">
                <p className="text-sm font-semibold text-slate-900">{result.rubric_name}</p>
                <p className="text-sm leading-6 text-slate-600">{result.rubric_description}</p>
              </div>
              <div className="flex flex-wrap gap-2">
                <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs text-slate-600">
                  {result.weight_label}
                </span>
                <span className="rounded-full bg-emerald-50 px-2.5 py-1 text-xs text-emerald-700">
                  {decisionLabel(result)}
                </span>
              </div>
            </div>
            <div className="mt-4 space-y-3">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">判断理由</p>
                <p className="mt-1 text-sm leading-6 text-slate-700">{result.reason_text}</p>
              </div>
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">证据点</p>
                {result.evidence_points.length > 0 ? (
                  <div className="mt-2 flex flex-wrap gap-2">
                    {result.evidence_points.map((point, index) => (
                      <span
                        key={`${result.job_rubric_item_id}-evidence-${index}`}
                        className="rounded-full bg-slate-100 px-3 py-1 text-xs text-slate-600"
                      >
                        {point}
                      </span>
                    ))}
                  </div>
                ) : (
                  <p className="mt-1 text-sm leading-6 text-slate-600">暂无证据点。</p>
                )}
              </div>
              {result.uncertainty_note ? (
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">不确定因素</p>
                  <p className="mt-1 text-sm leading-6 text-slate-600">{result.uncertainty_note}</p>
                </div>
              ) : null}
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}
