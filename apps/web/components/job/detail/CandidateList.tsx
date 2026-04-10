import { Card } from "@/components/ui/Card";
import type { JobCandidateListItemDto } from "@/lib/api/types";
import { CandidateListItem } from "@/components/job/detail/CandidateListItem";

type CandidateListProps = {
  items: JobCandidateListItemDto[];
};

export function CandidateList({ items }: CandidateListProps) {
  if (items.length === 0) {
    return (
      <Card className="space-y-2">
        <p className="text-xs font-semibold uppercase tracking-[0.24em] text-[var(--foreground-muted)]">
          Candidate list
        </p>
        <h3 className="text-lg font-semibold tracking-tight text-[var(--foreground)]">还没有匹配结果</h3>
        <p className="text-sm leading-7 text-[var(--foreground-soft)]">
          你可以先导入候选人资料，系统会在这里展示分析后的列表。
        </p>
      </Card>
    );
  }

  return (
    <div className="overflow-hidden rounded-[28px] border border-[var(--border)] bg-[var(--panel-strong)] shadow-[var(--shadow-card)] backdrop-blur-xl">
      <div className="grid grid-cols-[0.82fr_2.88fr_88px_88px] gap-4 px-5 py-4 text-xs font-semibold uppercase tracking-[0.24em] text-[var(--foreground-muted)]">
        <span className="text-center">Candidate</span>
        <span className="text-center">AI 分析</span>
        <span className="text-center">Status</span>
        <span className="text-center">Signal</span>
      </div>
      {items.map((candidate) => (
        <CandidateListItem key={candidate.candidate_id} candidate={candidate} />
      ))}
    </div>
  );
}
