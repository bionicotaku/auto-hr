import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";

export default function JobsPage() {
  return (
    <main className="relative min-h-screen overflow-hidden bg-[radial-gradient(circle_at_top_left,_rgba(14,165,233,0.18),_transparent_28%),radial-gradient(circle_at_top_right,_rgba(16,185,129,0.18),_transparent_30%),linear-gradient(180deg,_#f7fbf8_0%,_#eef6ff_48%,_#f7f7f1_100%)] px-6 py-10 text-slate-950 sm:px-10 lg:px-12">
      <div className="absolute inset-x-0 top-0 h-52 bg-[linear-gradient(90deg,_rgba(255,255,255,0.5),_rgba(255,255,255,0.08),_rgba(255,255,255,0.5))] blur-3xl" />

      <div className="relative mx-auto flex w-full max-w-6xl flex-col gap-8">
        <section className="grid gap-6 rounded-[32px] border border-white/70 bg-white/78 p-8 shadow-[0_30px_80px_rgba(15,23,42,0.10)] backdrop-blur xl:grid-cols-[1.35fr_0.95fr] xl:p-10">
          <div className="space-y-6">
            <div className="flex flex-wrap items-center gap-3">
              <Badge tone="accent">Jobs</Badge>
              <Badge tone="neutral">Workspace</Badge>
            </div>

            <div className="space-y-4">
              <p className="text-sm font-semibold uppercase tracking-[0.28em] text-emerald-700">
                Recruiting workspace
              </p>
              <h1 className="text-4xl font-semibold tracking-tight text-slate-950 sm:text-5xl">
                岗位工作台
              </h1>
              <p className="max-w-2xl text-base leading-7 text-slate-600 sm:text-lg">
                这里后续会承载 Job 列表、筛选和详情入口。当前阶段先提供一个清晰的 Job 新建入口。
              </p>
            </div>
          </div>

          <Card className="border-slate-900/5 bg-slate-950 text-white shadow-none">
            <div className="space-y-5">
              <p className="text-sm font-medium uppercase tracking-[0.24em] text-emerald-300/90">
                Jump in
              </p>
              <h2 className="text-2xl font-semibold tracking-tight">先创建 draft，再进入编辑</h2>
              <p className="text-sm leading-6 text-slate-300">
                新建入口页会把流程拆成已有描述导入和基础信息生成两条路径。
              </p>
              <Button href="/jobs/new" size="lg">
                新建 Job
              </Button>
            </div>
          </Card>
        </section>

        <section className="grid gap-4 lg:grid-cols-3">
          <Card>
            <p className="text-sm font-semibold uppercase tracking-[0.18em] text-sky-700">入口</p>
            <p className="mt-3 text-sm leading-7 text-slate-600">`/jobs/new` 负责路径选择，不持有草稿状态。</p>
          </Card>
          <Card>
            <p className="text-sm font-semibold uppercase tracking-[0.18em] text-sky-700">草稿</p>
            <p className="mt-3 text-sm leading-7 text-slate-600">创建成功后直接跳转 `/jobs/[jobId]/edit`。</p>
          </Card>
          <Card>
            <p className="text-sm font-semibold uppercase tracking-[0.18em] text-sky-700">约束</p>
            <p className="mt-3 text-sm leading-7 text-slate-600">失败时保留输入，不缓存结构化草稿。</p>
          </Card>
        </section>
      </div>
    </main>
  );
}
