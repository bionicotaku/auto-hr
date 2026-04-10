import { AppShell } from "@/components/layout/AppShell";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Textarea } from "@/components/ui/Textarea";

type JobEditWorkspaceProps = {
  jobId: string;
};

const rubricExamples = [
  {
    title: "核心能力",
    detail: "整理最重要的胜任力，并写清楚什么样的经历才算通过。",
  },
  {
    title: "必须项",
    detail: "把不可妥协的要求单独列出，避免和一般加分项混在一起。",
  },
  {
    title: "评分标准",
    detail: "让每个评估项都能被清晰判断，方便后续查看候选人是否匹配。",
  },
];

export function JobEditWorkspace({ jobId }: JobEditWorkspaceProps) {
  return (
    <AppShell
      title="岗位编辑"
      description="继续完善职位描述与评估规范。"
      actions={
        <>
          <Button href="/jobs" variant="secondary">
            返回岗位
          </Button>
          <Button disabled>完成</Button>
        </>
      }
    >
      <Card className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
        <div className="space-y-2">
          <p className="text-sm font-semibold text-slate-900">岗位草稿</p>
          <p className="text-sm leading-6 text-slate-600">确认描述与评估规范后，再完成当前岗位。</p>
        </div>
        <div className="flex flex-wrap items-center gap-3 text-sm text-slate-600">
          <span className="rounded-full bg-amber-50 px-3 py-1 text-amber-700 ring-1 ring-amber-200">草稿</span>
          <span className="rounded-full bg-slate-100 px-3 py-1 ring-1 ring-slate-200">编号 {jobId}</span>
        </div>
      </Card>

      <div className="grid gap-6 xl:grid-cols-[1.2fr_0.95fr_0.85fr]">
        <Card className="space-y-4">
          <div className="space-y-2">
            <h2 className="text-lg font-semibold tracking-tight text-slate-950">职位描述</h2>
            <p className="text-sm leading-6 text-slate-600">在这里整理岗位职责、任职要求和工作方式。</p>
          </div>
          <Textarea
            aria-label="职位描述编辑区"
            className="min-h-[420px] bg-slate-50"
            defaultValue="岗位描述将在这里编辑。"
            readOnly
          />
        </Card>

        <Card className="space-y-4">
          <div className="space-y-2">
            <h2 className="text-lg font-semibold tracking-tight text-slate-950">评估规范</h2>
            <p className="text-sm leading-6 text-slate-600">把需要重点判断的能力、必须项和评分标准整理清楚。</p>
          </div>

          <div className="space-y-3">
            {rubricExamples.map((item) => (
              <div key={item.title} className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-4">
                <p className="text-sm font-semibold text-slate-900">{item.title}</p>
                <p className="mt-1 text-sm leading-6 text-slate-600">{item.detail}</p>
              </div>
            ))}
          </div>
        </Card>

        <Card className="space-y-4">
          <div className="space-y-2">
            <h2 className="text-lg font-semibold tracking-tight text-slate-950">修改要求</h2>
            <p className="text-sm leading-6 text-slate-600">直接输入你希望调整的内容，建议会显示在这里。</p>
          </div>

          <div className="rounded-2xl border border-dashed border-slate-300 bg-slate-50 px-4 py-4 text-sm leading-6 text-slate-600">
            暂无消息。
          </div>

          <Textarea
            aria-label="修改要求输入框"
            className="min-h-[180px] bg-slate-50"
            placeholder="例如：把必须项单独列出，并弱化不必要的加分要求。"
            disabled
          />

          <Button className="w-full" disabled>
            发送要求
          </Button>
        </Card>
      </div>

      <Card className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div className="space-y-1">
          <h2 className="text-lg font-semibold tracking-tight text-slate-950">操作</h2>
          <p className="text-sm leading-6 text-slate-600">检查内容后，再重新生成或完成当前岗位。</p>
        </div>
        <div className="flex flex-wrap gap-3">
          <Button variant="secondary" disabled>
            重新生成
          </Button>
          <Button href="/jobs" variant="ghost">
            取消
          </Button>
          <Button disabled>完成</Button>
        </div>
      </Card>
    </AppShell>
  );
}
