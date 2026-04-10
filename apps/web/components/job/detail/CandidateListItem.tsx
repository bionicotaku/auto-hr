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

function getStatusTone(status: JobCandidateListItemDto["current_status"]) {
  switch (status) {
    case "in_progress":
    case "offer_sent":
      return "blue" as const;
    case "hired":
      return "mint" as const;
    case "pending":
    case "rejected":
      return "amber" as const;
  }
}

function getSignalTone(score: number | null) {
  if (score === null) {
    return "neutral" as const;
  }
  if (score >= 80) {
    return "mint" as const;
  }
  if (score >= 60) {
    return "lime" as const;
  }
  if (score >= 40) {
    return "amber" as const;
  }
  if (score >= 20) {
    return "orange" as const;
  }
  return "red" as const;
}

export function CandidateListItem({ candidate }: CandidateListItemProps) {
  return (
    <Link
      href={`/candidates/${candidate.candidate_id}`}
      className="grid cursor-pointer grid-cols-1 gap-4 border-t border-[var(--border)] px-5 py-4 transition-all duration-200 ease-out md:grid-cols-[0.82fr_2.88fr_88px_88px] motion-reduce:transition-none hover:-translate-y-0.5 hover:bg-[var(--panel-subtle)] hover:shadow-[inset_0_1px_0_rgba(255,255,255,0.24),0_14px_28px_rgba(15,23,42,0.08)] focus-visible:relative focus-visible:z-10 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--ring)]"
    >
      <div className="flex items-center justify-center">
        <div className="space-y-1">
          <h3 className="text-center text-lg font-semibold tracking-tight text-[var(--foreground)]">
            {candidate.full_name}
          </h3>
          <div className="flex flex-wrap items-center gap-2">
            {candidate.tags.slice(0, 2).map((tag) => (
              <Badge
                key={tag}
                tone="blue"
                className="font-medium"
              >
                {tag}
              </Badge>
            ))}
            {candidate.tags.length > 2 ? (
              <span className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--foreground-muted)]">
                +{candidate.tags.length - 2}
              </span>
            ) : null}
          </div>
        </div>
      </div>

      <div className="flex items-center">
        <p className="text-sm leading-6 text-[var(--foreground-soft)]">{candidate.ai_summary}</p>
      </div>

      <div className="flex items-center justify-center">
        <Badge tone={getStatusTone(candidate.current_status)}>
          {getStatusLabel(candidate.current_status)}
        </Badge>
      </div>

      <div className="flex items-center justify-center">
        <Badge tone={getSignalTone(candidate.overall_score_percent)}>
          {candidate.overall_score_percent ?? "--"}
        </Badge>
      </div>
    </Link>
  );
}
