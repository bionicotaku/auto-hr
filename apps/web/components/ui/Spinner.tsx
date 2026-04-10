import { HTMLAttributes } from "react";

import { cn } from "@/lib/utils/cn";

export function Spinner({ className, ...props }: HTMLAttributes<HTMLSpanElement>) {
  return (
    <span
      className={cn(
        "inline-block h-5 w-5 animate-spin rounded-full border-2 border-slate-200 border-t-emerald-600",
        className,
      )}
      {...props}
    />
  );
}
