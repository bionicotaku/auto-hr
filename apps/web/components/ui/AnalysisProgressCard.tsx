import { Card } from "@/components/ui/Card";

type AnalysisProgressCardProps = {
  title: string;
  currentStage: string;
  currentAiStep: number;
  totalAiSteps: number;
  errorMessage?: string | null;
};

export function AnalysisProgressCard({
  title,
  currentStage,
  currentAiStep,
  totalAiSteps,
  errorMessage,
}: AnalysisProgressCardProps) {
  const safeTotal = Math.max(totalAiSteps, 1);
  const percent = Math.max(0, Math.min(100, Math.round((currentAiStep / safeTotal) * 100)));

  return (
    <Card className="space-y-4">
      <div className="space-y-2">
        <p className="text-xs font-semibold uppercase tracking-[0.24em] text-[var(--foreground-muted)]">
          Analysis run
        </p>
        <h2 className="text-lg font-semibold tracking-tight text-[var(--foreground)]">{title}</h2>
        <p className="text-sm leading-6 text-[var(--foreground-soft)]">{currentStage}</p>
      </div>
      <div className="space-y-2">
        <div className="h-2 w-full overflow-hidden rounded-full bg-[var(--panel-muted)]">
          <div
            className="h-full rounded-full bg-[var(--accent)] transition-all motion-reduce:transition-none"
            style={{ width: `${percent}%` }}
          />
        </div>
        <p className="text-sm text-[var(--foreground-soft)]">
          已完成 {currentAiStep} / {totalAiSteps} 个 AI 分析步骤
        </p>
      </div>
      {errorMessage ? <p className="text-sm text-[var(--foreground)]">{errorMessage}</p> : null}
    </Card>
  );
}
