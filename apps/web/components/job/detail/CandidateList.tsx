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
        <h3 className="text-lg font-semibold tracking-tight text-slate-950">还没有匹配结果</h3>
        <p className="text-sm leading-7 text-slate-600">你可以先导入候选人资料，系统会在这里展示分析后的列表。</p>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {items.map((candidate) => (
        <CandidateListItem key={candidate.candidate_id} candidate={candidate} />
      ))}
    </div>
  );
}
