import { Card } from "@/components/ui/Card";
import { Textarea } from "@/components/ui/Textarea";

type JobDescriptionEditorProps = {
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
};

export function JobDescriptionEditor({
  value,
  onChange,
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
    </Card>
  );
}
