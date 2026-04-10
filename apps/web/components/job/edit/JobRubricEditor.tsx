import type { ChangeEvent } from "react";

import { Card } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";
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
        <p className="text-sm leading-6 text-slate-600">明确评估维度、必须项和评分标准。</p>
      </div>

      <div className="space-y-4">
        {items.map((item, index) => (
          <div key={`${item.sort_order}-${index}`} className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-4">
            <div className="grid gap-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <label className="text-sm font-semibold text-slate-800">评估项名称</label>
                  <Input
                    value={item.name}
                    onChange={(event) => onItemChange(index, "name", event.target.value)}
                    disabled={disabled}
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-semibold text-slate-800">类型</label>
                  <Select
                    value={item.criterion_type}
                    onChange={(event) => {
                      const nextType = event.target.value as JobRubricDraftItemDto["criterion_type"];
                      onItemChange(index, "criterion_type", nextType);
                      if (nextType === "hard_requirement") {
                        onItemChange(index, "weight_input", 100);
                      }
                    }}
                    disabled={disabled}
                  >
                    <option value="weighted">加权项</option>
                    <option value="hard_requirement">必须项</option>
                  </Select>
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

              <div className="grid gap-4 md:grid-cols-1">
                <div className="space-y-2">
                  <label className="text-sm font-semibold text-slate-800">权重输入</label>
                  <Input
                    type="number"
                    step="1"
                    value={item.weight_input}
                    onChange={(event) => onItemChange(index, "weight_input", handleNumberChange(event))}
                    disabled={disabled || item.criterion_type === "hard_requirement"}
                  />
                  <p className="text-xs leading-5 text-slate-500">
                    标准化权重会在后端自动计算，不需要手动填写。
                  </p>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}
