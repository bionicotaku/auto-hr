import { AppShell } from "@/components/layout/AppShell";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";

const creationPaths = [
  {
    title: "导入职位描述",
    description: "粘贴已有职位描述，快速生成岗位初稿。",
    href: "/jobs/new/from-description",
    action: "导入职位描述",
  },
  {
    title: "填写岗位信息",
    description: "先填写岗位名称、地点和要求，再进入编辑页继续完善。",
    href: "/jobs/new/from-form",
    action: "填写岗位信息",
  },
];

export function JobNewLanding() {
  return (
    <AppShell
      title="新建岗位"
      description="选择一种方式开始。生成岗位初稿后，你可以继续编辑职位描述与评估规范。"
      actions={
        <Button href="/jobs" variant="secondary">
          返回岗位
        </Button>
      }
    >
      <div className="grid gap-6 lg:grid-cols-2">
        {creationPaths.map((item) => (
          <Card key={item.title} className="flex h-full flex-col gap-6">
            <div className="space-y-3">
              <h2 className="text-2xl font-semibold tracking-tight text-slate-950">{item.title}</h2>
              <p className="text-sm leading-7 text-slate-600">{item.description}</p>
            </div>

            <div className="mt-auto">
              <Button href={item.href} size="lg">
                {item.action}
              </Button>
            </div>
          </Card>
        ))}
      </div>
    </AppShell>
  );
}
