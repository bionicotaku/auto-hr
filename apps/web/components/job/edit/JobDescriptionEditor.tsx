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
    <Card className="space-y-4">
      <div className="space-y-2">
        <h2 className="text-lg font-semibold tracking-tight text-slate-950">职位描述</h2>
        <p className="text-sm leading-6 text-slate-600">整理岗位职责、任职要求和工作方式。</p>
      </div>
      <Textarea
        aria-label="职位描述编辑区"
        className="min-h-[420px] bg-slate-50"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        disabled={disabled}
      />

      <div className="space-y-2">
        <label className="text-sm font-semibold text-slate-800">Responsibilities</label>
        <Textarea
          aria-label="Responsibilities 编辑区"
          className="min-h-[160px] bg-slate-50"
          value={responsibilitiesValue}
          onChange={(event) => onResponsibilitiesChange(event.target.value)}
          disabled={disabled}
        />
      </div>

      <div className="space-y-2">
        <label className="text-sm font-semibold text-slate-800">Skills</label>
        <Textarea
          aria-label="Skills 编辑区"
          className="min-h-[160px] bg-slate-50"
          value={skillsValue}
          onChange={(event) => onSkillsChange(event.target.value)}
          disabled={disabled}
        />
      </div>
    </Card>
  );
}
