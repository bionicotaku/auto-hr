import { Card } from "@/components/ui/Card";
import type { JobCandidateImportContextDto } from "@/lib/api/types";

type CandidateImportContextCardProps = {
  context: JobCandidateImportContextDto;
};

export function CandidateImportContextCard({ context }: CandidateImportContextCardProps) {
  return (
    <Card className="space-y-3">
      <div className="flex flex-wrap items-center gap-3">
        <span className="rounded-full bg-slate-100 px-3 py-1 text-sm text-slate-700 ring-1 ring-slate-200">
          岗位编号 {context.job_id}
        </span>
        <span className="rounded-full bg-amber-50 px-3 py-1 text-sm text-amber-700 ring-1 ring-amber-200">
          {context.lifecycle_status === "active" ? "已生效岗位" : "草稿岗位"}
        </span>
      </div>
      <div className="space-y-2">
        <h2 className="text-xl font-semibold tracking-tight text-slate-950">{context.title}</h2>
        <p className="text-sm leading-7 text-slate-600">{context.summary}</p>
      </div>
    </Card>
  );
}
