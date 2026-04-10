import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Textarea } from "@/components/ui/Textarea";

type CandidateImportFormProps = {
  textValue: string;
  onTextChange: (value: string) => void;
  disabledReason: string | null;
  globalError: string | null;
  onSubmit: () => void;
  onCancel: () => void;
  submitDisabled: boolean;
  isSubmitting: boolean;
};

export function CandidateImportForm({
  textValue,
  onTextChange,
  disabledReason,
  globalError,
  onSubmit,
  onCancel,
  submitDisabled,
  isSubmitting,
}: CandidateImportFormProps) {
  return (
    <Card className="space-y-4">
      <div className="space-y-2">
        <p className="text-xs font-semibold uppercase tracking-[0.24em] text-[var(--foreground-muted)]">
          Raw input
        </p>
        <h2 className="text-lg font-semibold tracking-tight text-[var(--foreground)]">候选人文本</h2>
        <p className="text-sm leading-7 text-[var(--foreground-soft)]">
          粘贴候选人的简历摘要、推荐语或其他补充说明，方便后续统一整理。
        </p>
      </div>

      <div className="space-y-2">
        <label className="text-sm font-medium text-[var(--foreground)]" htmlFor="candidate-raw-text">
          候选人原始文本
        </label>
        <Textarea
          id="candidate-raw-text"
          aria-label="候选人原始文本"
          value={textValue}
          onChange={(event) => onTextChange(event.target.value)}
          placeholder="例如：候选人的背景简介、推荐意见、补充说明等。"
          rows={12}
        />
      </div>

      {disabledReason ? <p className="text-sm text-[var(--foreground-soft)]">{disabledReason}</p> : null}
      {globalError ? <p className="text-sm text-[var(--foreground)]">{globalError}</p> : null}

      <div className="flex flex-wrap gap-3">
        <Button size="lg" disabled={submitDisabled} onClick={onSubmit}>
          {isSubmitting ? "分析中..." : "分析"}
        </Button>
        <Button type="button" variant="secondary" size="lg" onClick={onCancel} disabled={isSubmitting}>
          取消
        </Button>
      </div>
    </Card>
  );
}
