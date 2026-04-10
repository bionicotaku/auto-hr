import Link from "next/link";

import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import type { JobCandidateListItemDto } from "@/lib/api/types";

type CandidateListItemProps = {
  candidate: JobCandidateListItemDto;
};

function getStatusLabel(status: JobCandidateListItemDto["current_status"]) {
  switch (status) {
    case "pending":
      return "待处理";
    case "in_progress":
      return "正在推进";
    case "rejected":
      return "已拒绝";
    case "offer_sent":
      return "已发 offer";
    case "hired":
      return "已入职";
  }
}

export function CandidateListItem({ candidate }: CandidateListItemProps) {
  return (
    <Link href={`/candidates/${candidate.candidate_id}`}>
      <Card className="space-y-4 transition hover:border-slate-300 hover:shadow-[0_16px_36px_rgba(15,23,42,0.08)]">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div className="space-y-2">
            <div className="flex items-center gap-3">
              <h3 className="text-lg font-semibold tracking-tight text-slate-950">{candidate.full_name}</h3>
              <Badge tone={candidate.current_status === "in_progress" ? "accent" : "neutral"}>
                {getStatusLabel(candidate.current_status)}
              </Badge>
            </div>
            <p className="max-w-3xl text-sm leading-7 text-slate-600">{candidate.ai_summary}</p>
          </div>
          <div className="rounded-2xl bg-slate-950 px-4 py-3 text-white">
            <p className="text-xs uppercase tracking-[0.18em] text-slate-300">总分</p>
            <p className="mt-1 text-2xl font-semibold">{candidate.overall_score_percent ?? "--"}</p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {candidate.tags.map((tag) => (
            <span key={tag} className="rounded-2xl border border-slate-200 bg-slate-50 px-3 py-1 text-xs font-medium text-slate-600">
              {tag}
            </span>
          ))}
        </div>
      </Card>
    </Link>
  );
}
