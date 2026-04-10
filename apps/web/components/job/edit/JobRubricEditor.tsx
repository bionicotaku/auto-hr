import type { ChangeEvent } from "react";

import { Card } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { Textarea } from "@/components/ui/Textarea";
import type { JobRubricDraftItemDto } from "@/lib/api/types";

type JobRubricEditorProps = {
  items: JobRubricDraftItemDto[];
  disabled?: boolean;
  onItemChange: <K extends keyof JobRubricDraftItemDto>(
    index: number,
    field: K,
    value: JobRubricDraftItemDto[K],
  ) => void;
};

function handleNumberChange(event: ChangeEvent<HTMLInputElement>) {
  const raw = event.target.value;
  return raw === "" ? 0 : Number(raw);
}

export function JobRubricEditor({
  items,
  disabled = false,
  onItemChange,
}: JobRubricEditorProps) {
  return (
    <Card className="space-y-4">
      <div className="space-y-2">
        <h2 className="text-lg font-semibold tracking-tight text-slate-950">评估规范</h2>
        <p className="text-sm leading-6 text-slate-600">
          明确评估维度、必须项和评分标准。权重 100 代表必须满足的硬要求。
        </p>
      </div>

      <div className="space-y-4">
        {items.map((item, index) => (
          <div key={`${item.sort_order}-${index}`} className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-4">
            <div className="grid gap-4">
              <div className="grid gap-4 md:grid-cols-[minmax(0,1fr)_88px]">
                <div className="space-y-2">
                  <label className="text-sm font-semibold text-slate-800">评估项</label>
                  <Input
                    value={item.name}
                    onChange={(event) => onItemChange(index, "name", event.target.value)}
                    disabled={disabled}
                  />
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-semibold text-slate-800">权重</label>
                  <Input
                    type="number"
                    step="1"
                    min="1"
                    max="100"
                    value={item.weight_input}
                    onChange={(event) => onItemChange(index, "weight_input", handleNumberChange(event))}
                    disabled={disabled}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-semibold text-slate-800">说明</label>
                <Textarea
                  className="min-h-[120px]"
                  value={item.description}
                  onChange={(event) => onItemChange(index, "description", event.target.value)}
                  disabled={disabled}
                />
              </div>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}
