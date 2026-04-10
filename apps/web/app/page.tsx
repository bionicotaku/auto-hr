import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";

const highlights = [
  {
    title: "JD + rubric 定义",
    description: "围绕岗位定义和评估规范建立统一事实源，避免后续评估口径漂移。",
  },
  {
    title: "Candidate 分析流水线",
    description: "从标准化抽取到 rubric 子任务评分，再到 supervisor 汇总，保持结构化产出。",
  },
  {
    title: "本地 Demo 交付",
    description: "前后端、SQLite、文件目录和 AI 约束都落在同一 monorepo，便于快速迭代。",
  },
];

export default function HomePage() {
  return (
    <main className="relative min-h-screen overflow-hidden bg-[radial-gradient(circle_at_top_left,_rgba(34,197,94,0.18),_transparent_32%),radial-gradient(circle_at_top_right,_rgba(14,165,233,0.2),_transparent_36%),linear-gradient(180deg,_#f7fbf8_0%,_#eef4ff_48%,_#f7f7f2_100%)] px-6 py-10 text-slate-950 sm:px-10 lg:px-12">
      <div className="absolute inset-x-0 top-0 h-52 bg-[linear-gradient(90deg,_rgba(255,255,255,0.55),_rgba(255,255,255,0.08),_rgba(255,255,255,0.55))] blur-3xl" />

      <div className="relative mx-auto flex w-full max-w-6xl flex-col gap-8">
        <section className="grid gap-6 rounded-[32px] border border-white/70 bg-white/75 p-8 shadow-[0_30px_80px_rgba(15,23,42,0.10)] backdrop-blur xl:grid-cols-[1.35fr_0.95fr] xl:p-10">
          <div className="flex flex-col gap-6">
            <div className="flex flex-wrap items-center gap-3">
              <Badge tone="accent">Phase 2 Web Skeleton</Badge>
              <Badge tone="neutral">Next.js App Router</Badge>
              <Badge tone="success">React Query Ready</Badge>
            </div>

            <div className="max-w-3xl space-y-4">
              <p className="text-sm font-semibold uppercase tracking-[0.28em] text-emerald-700">
                Recruiting workspace demo
              </p>
              <h1 className="max-w-3xl text-4xl font-semibold tracking-tight text-slate-950 sm:text-5xl">
                用一个统一工作台，把岗位定义、候选人分析和后续反馈串成一条稳定链路。
              </h1>
              <p className="max-w-2xl text-base leading-7 text-slate-600 sm:text-lg">
                当前前端基础层已经就位，后续页面会在这套视觉和状态约束上继续扩展，保证体验现代、节奏清晰、风格一致。
              </p>
            </div>

            <div className="flex flex-wrap gap-3">
              <Button href="/jobs" size="lg">
                进入岗位工作台
              </Button>
              <Button href="/candidates/demo" variant="secondary" size="lg">
                查看候选人详情骨架
              </Button>
            </div>
          </div>

          <Card className="border-0 bg-slate-950/95 text-white shadow-none">
            <div className="space-y-5">
              <div className="space-y-2">
                <p className="text-sm font-medium uppercase tracking-[0.24em] text-emerald-300/90">
                  Current front-end direction
                </p>
                <h2 className="text-2xl font-semibold tracking-tight">
                  现代化但克制的 B2B 产品感
                </h2>
              </div>

              <ul className="space-y-3 text-sm leading-6 text-slate-300">
                <li>统一视觉 token：色彩、圆角、阴影、边框、间距都由基础层约束。</li>
                <li>区块节奏清晰：标题、说明、操作和状态提示的层级固定。</li>
                <li>页面响应式：桌面和移动端共享同一份信息架构，不做割裂式布局。</li>
              </ul>
            </div>
          </Card>
        </section>

        <section className="grid gap-4 lg:grid-cols-3">
          {highlights.map((item) => (
            <Card key={item.title}>
              <div className="space-y-3">
                <p className="text-sm font-semibold uppercase tracking-[0.2em] text-sky-700">
                  {item.title}
                </p>
                <p className="text-sm leading-7 text-slate-600">{item.description}</p>
              </div>
            </Card>
          ))}
        </section>
      </div>
    </main>
  );
}
