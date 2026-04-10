import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Spinner } from "@/components/ui/Spinner";

type JobEditActionBarProps = {
  isRegeneratePending: boolean;
  onRegenerate: () => void;
};

export function JobEditActionBar({
  isRegeneratePending,
  onRegenerate,
}: JobEditActionBarProps) {
  return (
    <Card className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
      <div className="space-y-1">
        <h2 className="text-lg font-semibold tracking-tight text-slate-950">操作</h2>
        <p className="text-sm leading-6 text-slate-600">检查内容后，再重新生成或完成当前岗位。</p>
      </div>
      <div className="flex flex-wrap gap-3">
        <Button variant="secondary" onClick={onRegenerate} disabled={isRegeneratePending}>
          {isRegeneratePending ? (
            <span className="inline-flex items-center gap-2">
              <Spinner className="h-4 w-4 border-slate-300 border-t-slate-800" />
              重新生成中
            </span>
          ) : (
            "重新生成"
          )}
        </Button>
        <Button href="/jobs" variant="ghost">
          取消
        </Button>
        <Button disabled>完成</Button>
      </div>
    </Card>
  );
}
