import { HTMLAttributes } from "react";

import { cn } from "@/lib/utils/cn";

type BadgeTone =
  | "accent"
  | "neutral"
  | "success"
  | "warning"
  | "danger"
  | "mint"
  | "lime"
  | "blue"
  | "amber"
  | "orange"
  | "red";

const toneClasses: Record<BadgeTone, string> = {
  accent: "bg-[var(--badge-blue-bg)] text-[var(--badge-blue-text)]",
  neutral: "bg-[var(--panel-muted)] text-[var(--foreground-soft)] ring-1 ring-[var(--border)]",
  success: "bg-[var(--badge-mint-bg)] text-[var(--badge-mint-text)]",
  warning: "bg-[var(--badge-amber-bg)] text-[var(--badge-amber-text)]",
  danger: "bg-[var(--badge-red-bg)] text-[var(--badge-red-text)]",
  mint: "bg-[var(--badge-mint-bg)] text-[var(--badge-mint-text)]",
  lime: "bg-[var(--badge-lime-bg)] text-[var(--badge-lime-text)]",
  blue: "bg-[var(--badge-blue-bg)] text-[var(--badge-blue-text)]",
  amber: "bg-[var(--badge-amber-bg)] text-[var(--badge-amber-text)]",
  orange: "bg-[var(--badge-orange-bg)] text-[var(--badge-orange-text)]",
  red: "bg-[var(--badge-red-bg)] text-[var(--badge-red-text)]",
};

type BadgeProps = HTMLAttributes<HTMLSpanElement> & {
  tone?: BadgeTone;
};

export function Badge({ className, tone = "neutral", ...props }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold",
        toneClasses[tone],
        className,
      )}
      {...props}
    />
  );
}
