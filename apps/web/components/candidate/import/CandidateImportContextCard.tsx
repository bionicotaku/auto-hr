import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import type { JobCandidateImportContextDto } from "@/lib/api/types";

type CandidateImportContextCardProps = {
  context: JobCandidateImportContextDto;
};

export function CandidateImportContextCard({ context }: CandidateImportContextCardProps) {
  return (
    <Card className="space-y-3">
      <div className="flex flex-wrap items-center gap-3">
        <span className="rounded-full bg-[var(--panel-muted)] px-3 py-1 text-sm text-[var(--foreground-soft)] ring-1 ring-[var(--border)]">
          岗位编号 {context.job_id}
        </span>
        <Badge
          className="text-sm tracking-[0.14em]"
          tone={context.lifecycle_status === "active" ? "success" : "warning"}
        >
          {context.lifecycle_status === "active" ? "已生效岗位" : "草稿岗位"}
        </Badge>
      </div>
      <div className="space-y-2">
        <p className="text-xs font-semibold uppercase tracking-[0.24em] text-[var(--foreground-muted)]">
          Import context
        </p>
        <h2 className="text-xl font-semibold tracking-tight text-[var(--foreground)]">{context.title}</h2>
        <p className="text-sm leading-7 text-[var(--foreground-soft)]">{context.summary}</p>
      </div>
    </Card>
  );
}
