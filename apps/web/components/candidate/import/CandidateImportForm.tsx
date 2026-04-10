import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Textarea } from "@/components/ui/Textarea";

type CandidateImportFormProps = {
  textValue: string;
  onTextChange: (value: string) => void;
  disabledReason: string | null;
  globalError: string | null;
  onCancel: () => void;
};

export function CandidateImportForm({
  textValue,
  onTextChange,
  disabledReason,
  globalError,
  onCancel,
}: CandidateImportFormProps) {
  return (
    <Card className="space-y-4">
      <div className="space-y-2">
        <h2 className="text-lg font-semibold tracking-tight text-slate-950">候选人文本</h2>
        <p className="text-sm leading-7 text-slate-600">粘贴候选人的简历摘要、推荐语或其他补充说明，方便后续统一整理。</p>
      </div>

      <div className="space-y-2">
        <label className="text-sm font-medium text-slate-800" htmlFor="candidate-raw-text">
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

      {disabledReason ? <p className="text-sm text-amber-700">{disabledReason}</p> : null}
      {globalError ? <p className="text-sm text-rose-600">{globalError}</p> : null}

      <div className="flex flex-wrap gap-3">
        <Button size="lg" disabled>
          生成
        </Button>
        <Button type="button" variant="secondary" size="lg" onClick={onCancel}>
          取消
        </Button>
      </div>
    </Card>
  );
}
