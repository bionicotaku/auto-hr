import { HTMLAttributes } from "react";

import { cn } from "@/lib/utils/cn";

type CardProps = HTMLAttributes<HTMLDivElement> & {
  tone?: "default" | "muted";
};

export function Card({ className, tone = "default", ...props }: CardProps) {
  return (
    <div
      className={cn(
        "rounded-[28px] border p-6 backdrop-blur-xl",
        tone === "default"
          ? "border-[var(--border)] bg-[var(--panel-strong)] shadow-[var(--shadow-card)]"
          : "border-[var(--border)] bg-[var(--panel-muted)] shadow-[var(--shadow-soft)]",
        className,
      )}
      {...props}
    />
  );
}
