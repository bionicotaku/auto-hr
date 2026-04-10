import { HTMLAttributes } from "react";

import { cn } from "@/lib/utils/cn";

export function Spinner({ className, ...props }: HTMLAttributes<HTMLSpanElement>) {
  return (
    <span
      className={cn(
        "inline-block h-5 w-5 animate-spin rounded-full border-2 border-[var(--border)] border-t-[var(--foreground)]",
        className,
      )}
      {...props}
    />
  );
}
