import { AppShell } from "@/components/layout/AppShell";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";

type CandidateDetailEmptyStateProps = {
  candidateId: string;
};

export function CandidateDetailEmptyState({ candidateId }: CandidateDetailEmptyStateProps) {
  return (
    <AppShell
      title="候选人详情"
      description="导入候选人资料后，这里会展示简历摘要、匹配分析和处理记录。"
      actions={
        <Button href="/jobs" variant="secondary">
          返回岗位
        </Button>
      }
    >
      <Card className="max-w-3xl space-y-3">
        <h2 className="text-xl font-semibold tracking-tight text-slate-950">候选人 {candidateId}</h2>
        <p className="text-sm leading-7 text-slate-600">
          当前页面已预留为候选人工作区入口。接入真实数据后，你可以在这里查看原始资料、分析结果和后续处理动作。
        </p>
      </Card>
    </AppShell>
  );
}
