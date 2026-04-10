import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";

type ErrorStateCardProps = {
  title?: string;
  message: string;
  actionLabel?: string;
  onAction?: () => void;
};

export function ErrorStateCard({
  title = "加载失败",
  message,
  actionLabel,
  onAction,
}: ErrorStateCardProps) {
  return (
    <Card className="space-y-4">
      <div className="space-y-2">
        <p className="text-xs font-semibold uppercase tracking-[0.24em] text-[var(--foreground-muted)]">
          Error state
        </p>
        <h2 className="text-lg font-semibold tracking-tight text-[var(--foreground)]">{title}</h2>
        <p className="text-sm leading-7 text-[var(--foreground-soft)]">{message}</p>
      </div>
      {actionLabel && onAction ? (
        <div className="flex">
          <Button onClick={onAction} variant="secondary">
            {actionLabel}
          </Button>
        </div>
      ) : null}
    </Card>
  );
}
