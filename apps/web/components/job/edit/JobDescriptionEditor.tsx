import { Card } from "@/components/ui/Card";
import { Textarea } from "@/components/ui/Textarea";

type JobDescriptionEditorProps = {
  value: string;
  responsibilitiesValue: string;
  skillsValue: string;
  onChange: (value: string) => void;
  onResponsibilitiesChange: (value: string) => void;
  onSkillsChange: (value: string) => void;
  disabled?: boolean;
};

export function JobDescriptionEditor({
  value,
  responsibilitiesValue,
  skillsValue,
  onChange,
  onResponsibilitiesChange,
  onSkillsChange,
  disabled = false,
}: JobDescriptionEditorProps) {
  return (
    <Card className="space-y-5">
      <div className="space-y-2">
        <p className="text-xs font-semibold uppercase tracking-[0.24em] text-[var(--foreground-muted)]">
          Definition
        </p>
        <h2 className="text-lg font-semibold tracking-tight text-[var(--foreground)]">职位描述</h2>
        <p className="text-sm leading-6 text-[var(--foreground-soft)]">整理岗位职责、任职要求和工作方式。</p>
      </div>
      <Textarea
        aria-label="职位描述编辑区"
        className="min-h-[360px]"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        disabled={disabled}
      />

      <div className="grid gap-4 xl:grid-cols-2">
        <div className="space-y-2">
          <label className="text-sm font-semibold text-[var(--foreground)]">岗位职责</label>
          <Textarea
            aria-label="Responsibilities 编辑区"
            className="min-h-[180px]"
            value={responsibilitiesValue}
            onChange={(event) => onResponsibilitiesChange(event.target.value)}
            disabled={disabled}
          />
        </div>

        <div className="space-y-2">
          <label className="text-sm font-semibold text-[var(--foreground)]">关键技能</label>
          <Textarea
            aria-label="Skills 编辑区"
            className="min-h-[180px]"
            value={skillsValue}
            onChange={(event) => onSkillsChange(event.target.value)}
            disabled={disabled}
          />
        </div>
      </div>
    </Card>
  );
}
