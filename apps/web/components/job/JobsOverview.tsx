import { AppShell } from "@/components/layout/AppShell";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";

export function JobsOverview() {
  return (
    <AppShell
      title="岗位"
      description="创建并维护岗位定义，统一职位描述和评估规范。"
      actions={
        <Button href="/jobs/new" size="lg">
          新建岗位
        </Button>
      }
    >
      <div className="grid gap-6 xl:grid-cols-[1.4fr_0.9fr]">
        <Card className="flex min-h-[320px] flex-col justify-between">
          <div className="space-y-3">
            <h2 className="text-xl font-semibold tracking-tight text-slate-950">还没有岗位</h2>
            <p className="max-w-xl text-sm leading-7 text-slate-600">
              从一个新岗位开始。你可以直接导入已有职位描述，也可以先填写岗位信息，再进入统一编辑页继续完善。
            </p>
          </div>

          <div className="flex flex-wrap gap-3">
            <Button href="/jobs/new" size="lg">
              新建岗位
            </Button>
            <Button href="/jobs/new/from-description" variant="secondary">
              导入职位描述
            </Button>
          </div>
        </Card>

        <Card className="space-y-4">
          <div className="space-y-2">
            <h2 className="text-lg font-semibold tracking-tight text-slate-950">开始方式</h2>
            <p className="text-sm leading-7 text-slate-600">选择最适合当前场景的入口，先拿到岗位初稿，再进入编辑工作区。</p>
          </div>

          <div className="space-y-3">
            <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-4">
              <p className="text-sm font-semibold text-slate-900">导入职位描述</p>
              <p className="mt-1 text-sm leading-6 text-slate-600">适合已经有现成 JD 的岗位。</p>
            </div>
            <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-4">
              <p className="text-sm font-semibold text-slate-900">填写岗位信息</p>
              <p className="mt-1 text-sm leading-6 text-slate-600">适合先从岗位名称、地点和要求起步。</p>
            </div>
          </div>
        </Card>
      </div>
    </AppShell>
  );
}
