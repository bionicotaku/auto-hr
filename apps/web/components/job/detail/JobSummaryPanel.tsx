import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import type { JobDetailResponseDto } from "@/lib/api/types";

type JobSummaryPanelProps = {
  job: JobDetailResponseDto;
};

export function JobSummaryPanel({ job }: JobSummaryPanelProps) {
  return (
    <Card className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="space-y-3">
          <div className="flex items-center gap-3">
            <Badge tone={job.lifecycle_status === "active" ? "success" : "neutral"}>
              {job.lifecycle_status === "active" ? "已生效" : "草稿"}
            </Badge>
            <Badge tone="blue">{job.candidate_count} 位候选人</Badge>
          </div>
          <div className="space-y-2">
            <h2 className="text-2xl font-semibold tracking-tight text-[var(--foreground)]">{job.title}</h2>
            <p className="max-w-3xl text-sm leading-7 text-[var(--foreground-soft)]">{job.summary}</p>
          </div>
        </div>
        <div className="flex flex-wrap gap-3">
          <Button href={`/jobs/${job.job_id}/edit`} variant="secondary">
            编辑岗位
          </Button>
          <Button href={`/jobs/${job.job_id}/candidates/new`}>添加候选人</Button>
        </div>
      </div>

      <div className="grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
        <div className="space-y-3">
          <h3 className="text-sm font-semibold uppercase tracking-[0.18em] text-[var(--foreground-muted)]">工作描述</h3>
          <div className="rounded-[24px] border border-[var(--border)] bg-[var(--panel-muted)] p-4">
            <p className="whitespace-pre-wrap text-sm leading-7 text-[var(--foreground-soft)]">
              {job.description_text}
            </p>
          </div>
        </div>

        <div className="space-y-5">
          <div className="space-y-3">
            <h3 className="text-sm font-semibold uppercase tracking-[0.18em] text-[var(--foreground-muted)]">评估规范</h3>
            <div className="flex flex-wrap gap-2">
              {job.rubric_summary.map((item) => (
                <div
                  key={`${item.name}-${item.weight_label}`}
                  className="inline-flex items-center gap-2 rounded-full border border-[var(--border)] bg-[var(--panel-strong)] px-3 py-2 text-sm text-[var(--foreground-soft)]"
                >
                  <span className="font-medium text-[var(--foreground)]">{item.name}</span>
                  <Badge tone="blue" className="px-2.5 py-0.5 text-[11px] font-medium">
                    {item.weight_label}
                  </Badge>
                </div>
              ))}
            </div>
          </div>

          <div className="space-y-3">
            <h3 className="text-sm font-semibold uppercase tracking-[0.18em] text-[var(--foreground-muted)]">岗位摘要</h3>
            <div className="grid gap-3 sm:grid-cols-2">
              {job.structured_info_summary.map((item) => (
                <div key={item.label} className="rounded-[22px] border border-[var(--border)] bg-[var(--panel-muted)] p-4">
                  <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--foreground-muted)]">
                    {item.label}
                  </p>
                  <p className="mt-2 text-sm font-medium text-[var(--foreground)]">{item.value}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </Card>
  );
}
