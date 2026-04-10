import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";

type JobDraftEditPlaceholderProps = {
  jobId: string;
};

export function JobDraftEditPlaceholder({ jobId }: JobDraftEditPlaceholderProps) {
  return (
    <main className="min-h-screen bg-slate-50 px-6 py-12">
      <div className="mx-auto flex max-w-5xl flex-col gap-6">
        <section className="rounded-[32px] border border-white/70 bg-[radial-gradient(circle_at_top_left,_rgba(14,165,233,0.16),_transparent_36%),linear-gradient(180deg,_rgba(255,255,255,0.96)_0%,_rgba(248,250,252,0.96)_100%)] p-8 shadow-[0_24px_64px_rgba(15,23,42,0.08)] backdrop-blur">
          <div className="flex flex-wrap items-center gap-3">
            <Badge tone="accent">Job draft</Badge>
            <Badge tone="neutral">{jobId}</Badge>
          </div>

          <h1 className="mt-4 text-3xl font-semibold tracking-tight text-slate-950">
            Job 编辑页占位
          </h1>
          <p className="mt-4 max-w-3xl text-sm leading-7 text-slate-600">
            当前步骤只负责承接 draft 创建后的跳转。Phase 4 会在这里补齐 B 页面主体，但本阶段不提前实现编辑逻辑。
          </p>
        </section>

        <Card className="space-y-5">
          <div className="space-y-2">
            <p className="text-sm font-semibold uppercase tracking-[0.2em] text-sky-700">Next step</p>
            <p className="text-sm leading-7 text-slate-600">
              这里保留一个最小承接页，确保 `/jobs/[jobId]/edit` 的跳转链路完整，不缓存任何结构化草稿。
            </p>
          </div>

          <div className="flex flex-wrap gap-3">
            <Button href="/jobs">返回 Jobs</Button>
            <Button href="/jobs/new" variant="secondary">
              继续创建 Job
            </Button>
          </div>
        </Card>
      </div>
    </main>
  );
}

