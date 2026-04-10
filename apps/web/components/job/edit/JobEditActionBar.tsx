import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Spinner } from "@/components/ui/Spinner";

type JobEditActionBarProps = {
  isFinalizePending: boolean;
  isCancelPending: boolean;
  onCancel: () => void;
  onFinalize: () => void;
};

export function JobEditActionBar({
  isFinalizePending,
  isCancelPending,
  onCancel,
  onFinalize,
}: JobEditActionBarProps) {
  return (
    <Card className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
      <div className="space-y-1">
        <h2 className="text-lg font-semibold tracking-tight text-slate-950">操作</h2>
        <p className="text-sm leading-6 text-slate-600">检查内容后，可取消当前草稿或完成当前岗位。</p>
      </div>
      <div className="flex flex-wrap gap-3">
        <Button variant="ghost" onClick={onCancel} disabled={isFinalizePending || isCancelPending}>
          {isCancelPending ? (
            <span className="inline-flex items-center gap-2">
              <Spinner className="h-4 w-4 border-slate-300 border-t-slate-800" />
              取消中
            </span>
          ) : (
            "取消"
          )}
        </Button>
        <Button onClick={onFinalize} disabled={isFinalizePending || isCancelPending}>
          {isFinalizePending ? (
            <span className="inline-flex items-center gap-2">
              <Spinner className="h-4 w-4 border-white/30 border-t-white" />
              完成中
            </span>
          ) : (
            "完成"
          )}
        </Button>
      </div>
    </Card>
  );
}
