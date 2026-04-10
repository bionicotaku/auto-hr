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
        <h2 className="text-lg font-semibold tracking-tight text-slate-950">{title}</h2>
        <p className="text-sm leading-6 text-slate-600">{currentStage}</p>
      </div>
      <div className="space-y-2">
        <div className="h-2 w-full overflow-hidden rounded-full bg-slate-200">
          <div className="h-full rounded-full bg-slate-900 transition-all" style={{ width: `${percent}%` }} />
        </div>
        <p className="text-sm text-slate-600">
          已完成 {currentAiStep} / {totalAiSteps} 个 AI 分析步骤
        </p>
      </div>
      {errorMessage ? <p className="text-sm text-rose-600">{errorMessage}</p> : null}
    </Card>
  );
}
