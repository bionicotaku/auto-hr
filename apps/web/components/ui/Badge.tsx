import { HTMLAttributes } from "react";

import { cn } from "@/lib/utils/cn";

type BadgeTone = "accent" | "neutral" | "success";

const toneClasses: Record<BadgeTone, string> = {
  accent: "bg-sky-100 text-sky-800 ring-1 ring-sky-200",
  neutral: "bg-slate-100 text-slate-700 ring-1 ring-slate-200",
  success: "bg-emerald-100 text-emerald-800 ring-1 ring-emerald-200",
};

type BadgeProps = HTMLAttributes<HTMLSpanElement> & {
  tone?: BadgeTone;
};

export function Badge({ className, tone = "neutral", ...props }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-xl px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em]",
        toneClasses[tone],
        className,
      )}
      {...props}
    />
  );
}
