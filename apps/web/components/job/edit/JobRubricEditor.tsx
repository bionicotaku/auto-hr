import type { ChangeEvent } from "react";

import { Card } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";
import { Textarea } from "@/components/ui/Textarea";
import type { JobRubricItemDto } from "@/lib/api/types";

type JobRubricEditorProps = {
  items: JobRubricItemDto[];
  disabled?: boolean;
  onItemChange: <K extends keyof JobRubricItemDto>(
    index: number,
    field: K,
    value: JobRubricItemDto[K],
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
          <div key={item.id ?? `${item.sort_order}-${index}`} className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-4">
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
                      const nextType = event.target.value as JobRubricItemDto["criterion_type"];
                      onItemChange(index, "criterion_type", nextType);
                      if (nextType === "hard_requirement") {
                        onItemChange(index, "weight_input", 100);
                        onItemChange(index, "weight_normalized", null);
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

              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <label className="text-sm font-semibold text-slate-800">权重输入</label>
                  <Input
                    type="number"
                    step="1"
                    value={item.weight_input}
                    onChange={(event) => onItemChange(index, "weight_input", handleNumberChange(event))}
                    disabled={disabled || item.criterion_type === "hard_requirement"}
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-semibold text-slate-800">标准化权重</label>
                  <Input
                    type="number"
                    step="0.05"
                    value={item.weight_normalized ?? ""}
                    onChange={(event) =>
                      onItemChange(
                        index,
                        "weight_normalized",
                        event.target.value === "" ? null : Number(event.target.value),
                      )
                    }
                    disabled={disabled || item.criterion_type === "hard_requirement"}
                  />
                </div>
              </div>

              <details className="rounded-2xl border border-slate-200 bg-white px-4 py-3">
                <summary className="cursor-pointer text-sm font-semibold text-slate-900">查看详细标准</summary>
                <div className="mt-3 space-y-3 text-sm leading-6 text-slate-600">
                  <div>
                    <p className="font-semibold text-slate-900">评分标准</p>
                    <pre className="mt-1 overflow-x-auto whitespace-pre-wrap rounded-xl bg-slate-50 px-3 py-3 text-xs text-slate-700">
                      {JSON.stringify(item.scoring_standard_json, null, 2)}
                    </pre>
                  </div>
                  <div>
                    <p className="font-semibold text-slate-900">分析提示</p>
                    <p className="mt-1 whitespace-pre-wrap">{item.agent_prompt_text}</p>
                  </div>
                  <div>
                    <p className="font-semibold text-slate-900">证据提取要求</p>
                    <p className="mt-1 whitespace-pre-wrap">{item.evidence_guidance_text}</p>
                  </div>
                </div>
              </details>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}
