import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";

const creationPaths = [
  {
    title: "已有描述导入",
    description: "适合手里已经有 JD 原文，希望快速生成 draft Job 并进入编辑页。",
    href: "/jobs/new/from-description",
    badge: "快速起步",
    tone: "accent" as const,
    action: "导入原始描述",
  },
  {
    title: "基础信息生成",
    description: "适合从岗位基础字段起步，让系统基于表单生成初始 JD 与 rubric 草稿。",
    href: "/jobs/new/from-form",
    badge: "结构化输入",
    tone: "success" as const,
    action: "填写基础信息",
  },
];

export function JobNewLanding() {
  return (
    <main className="relative min-h-screen overflow-hidden bg-[radial-gradient(circle_at_top_left,_rgba(14,165,233,0.18),_transparent_28%),radial-gradient(circle_at_top_right,_rgba(16,185,129,0.18),_transparent_30%),linear-gradient(180deg,_#f7fbf8_0%,_#eef6ff_48%,_#f7f7f1_100%)] px-6 py-10 text-slate-950 sm:px-10 lg:px-12">
      <div className="absolute inset-x-0 top-0 h-52 bg-[linear-gradient(90deg,_rgba(255,255,255,0.5),_rgba(255,255,255,0.08),_rgba(255,255,255,0.5))] blur-3xl" />

      <div className="relative mx-auto flex w-full max-w-6xl flex-col gap-8">
        <section className="grid gap-6 rounded-[32px] border border-white/70 bg-white/78 p-8 shadow-[0_30px_80px_rgba(15,23,42,0.10)] backdrop-blur xl:grid-cols-[1.35fr_0.95fr] xl:p-10">
          <div className="space-y-6">
            <div className="flex flex-wrap items-center gap-3">
              <Badge tone="accent">Phase 3</Badge>
              <Badge tone="neutral">Job Draft Creation</Badge>
            </div>

            <div className="max-w-3xl space-y-4">
              <p className="text-sm font-semibold uppercase tracking-[0.28em] text-emerald-700">
                New job entry
              </p>
              <h1 className="max-w-3xl text-4xl font-semibold tracking-tight text-slate-950 sm:text-5xl">
                选择一个创建入口，先生成 draft Job，再进入统一编辑页。
              </h1>
              <p className="max-w-2xl text-base leading-7 text-slate-600 sm:text-lg">
                这里不缓存结构化草稿，只负责把用户带到正确的输入路径。成功创建后会直接跳转到
                `/jobs/[jobId]/edit`。
              </p>
            </div>

            <div className="rounded-[28px] border border-slate-200 bg-slate-950 px-5 py-4 text-sm leading-6 text-slate-200 shadow-[0_20px_48px_rgba(15,23,42,0.12)]">
              新建流程的取消行为会删除 draft，因此这一页只提供入口选择，不保留任何临时结构化结果。
            </div>
          </div>

          <Card className="border-slate-900/5 bg-slate-950 text-white shadow-none">
            <div className="space-y-5">
              <div className="space-y-2">
                <p className="text-sm font-medium uppercase tracking-[0.24em] text-emerald-300/90">
                  Flow
                </p>
                <h2 className="text-2xl font-semibold tracking-tight">路径清晰，状态单一</h2>
              </div>

              <ol className="space-y-3 text-sm leading-6 text-slate-300">
                <li>1. 选择已有描述导入或基础信息生成。</li>
                <li>2. 填写最少必要信息并提交。</li>
                <li>3. 后端成功创建 draft Job 后跳转编辑页。</li>
              </ol>
            </div>
          </Card>
        </section>

        <section className="grid gap-4 lg:grid-cols-2">
          {creationPaths.map((item) => (
            <Card key={item.title} className="flex h-full flex-col gap-6">
              <div className="flex items-start justify-between gap-4">
                <div className="space-y-3">
                  <Badge tone={item.tone}>{item.badge}</Badge>
                  <div>
                    <h2 className="text-2xl font-semibold tracking-tight text-slate-950">{item.title}</h2>
                    <p className="mt-3 text-sm leading-7 text-slate-600">{item.description}</p>
                  </div>
                </div>
                <div className="mt-1 h-12 w-12 rounded-2xl bg-gradient-to-br from-sky-100 to-emerald-100 ring-1 ring-white/70" />
              </div>

              <div className="mt-auto">
                <Button href={item.href} size="lg">
                  {item.action}
                </Button>
              </div>
            </Card>
          ))}
        </section>
      </div>
    </main>
  );
}

