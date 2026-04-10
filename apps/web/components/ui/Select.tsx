import { forwardRef, SelectHTMLAttributes } from "react";

import { cn } from "@/lib/utils/cn";

export const Select = forwardRef<HTMLSelectElement, SelectHTMLAttributes<HTMLSelectElement>>(
  function Select({ className, children, ...props }, ref) {
    return (
      <select
        ref={ref}
        className={cn(
          "h-11 w-full rounded-[20px] border border-[var(--border)] bg-[var(--panel-strong)] px-4 text-sm text-[var(--foreground)] shadow-[var(--shadow-soft)] outline-none transition focus:border-[var(--border-strong)] focus:ring-4 focus:ring-[var(--ring)] motion-reduce:transition-none",
          className,
        )}
        {...props}
      >
        {children}
      </select>
    );
  },
);
