"use client";

import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";

export const PRESET_CANDIDATE_TAGS = ["制造业经验", "管理经验", "本地候选人", "高匹配", "需要复核"];

type CandidateListToolbarProps = {
  sort: "score_desc" | "score_asc" | "created_at_desc" | "created_at_asc";
  status: "all" | "pending" | "in_progress" | "rejected" | "offer_sent" | "hired";
  selectedTags: string[];
  query: string;
  availableTags: string[];
  onSortChange: (value: CandidateListToolbarProps["sort"]) => void;
  onStatusChange: (value: CandidateListToolbarProps["status"]) => void;
  onQueryChange: (value: string) => void;
  onToggleTag: (tag: string) => void;
};

const statusOptions = [
  { value: "all", label: "全部状态" },
  { value: "pending", label: "待处理" },
  { value: "in_progress", label: "正在推进" },
  { value: "rejected", label: "已拒绝" },
  { value: "offer_sent", label: "已发 offer" },
  { value: "hired", label: "已入职" },
] as const;

const sortOptions = [
  { value: "score_desc", label: "总分从高到低" },
  { value: "score_asc", label: "总分从低到高" },
  { value: "created_at_desc", label: "最新添加优先" },
  { value: "created_at_asc", label: "最早添加优先" },
] as const;

export function CandidateListToolbar({
  sort,
  status,
  selectedTags,
  query,
  availableTags,
  onSortChange,
  onStatusChange,
  onQueryChange,
  onToggleTag,
}: CandidateListToolbarProps) {
  const mergedTags = [...new Set([...PRESET_CANDIDATE_TAGS, ...availableTags])];

  return (
    <div className="space-y-4 rounded-[28px] border border-[var(--border)] bg-[var(--panel-strong)] p-6 shadow-[var(--shadow-card)] backdrop-blur-xl">
      <div className="space-y-1">
        <p className="text-xs font-semibold uppercase tracking-[0.24em] text-[var(--foreground-muted)]">
          Candidate filters
        </p>
        <p className="text-sm leading-6 text-[var(--foreground-soft)]">
          在页面内即时调整搜索、排序、状态与标签，不影响 URL。
        </p>
      </div>

      <div className="grid gap-3 lg:grid-cols-[1.2fr_0.8fr_0.8fr]">
        <Input
          aria-label="搜索候选人"
          placeholder="搜索姓名或 AI 摘要"
          value={query}
          onChange={(event) => onQueryChange(event.target.value)}
        />
        <Select aria-label="候选人排序" value={sort} onChange={(event) => onSortChange(event.target.value as CandidateListToolbarProps["sort"])}>
          {sortOptions.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </Select>
        <Select
          aria-label="候选人状态筛选"
          value={status}
          onChange={(event) => onStatusChange(event.target.value as CandidateListToolbarProps["status"])}
        >
          {statusOptions.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </Select>
      </div>

      <div className="flex flex-wrap gap-2">
        {mergedTags.map((tag) => {
          const selected = selectedTags.includes(tag);
          return (
            <button
              key={tag}
              type="button"
              className={`cursor-pointer rounded-full px-3 py-2 text-sm font-medium transition-colors duration-200 ease-out motion-reduce:transition-none ${
                selected
                  ? "bg-[var(--accent)] text-[var(--accent-contrast)]"
                  : "border border-[var(--border)] bg-[var(--panel-muted)] text-[var(--foreground-soft)] hover:bg-[var(--panel-strong)]"
              }`}
              onClick={() => onToggleTag(tag)}
            >
              {tag}
            </button>
          );
        })}
      </div>
    </div>
  );
}
