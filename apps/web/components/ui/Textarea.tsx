import { forwardRef, TextareaHTMLAttributes } from "react";

import { cn } from "@/lib/utils/cn";

export const Textarea = forwardRef<
  HTMLTextAreaElement,
  TextareaHTMLAttributes<HTMLTextAreaElement>
>(function Textarea({ className, ...props }, ref) {
  return (
    <textarea
      ref={ref}
      className={cn(
        "min-h-32 w-full rounded-[24px] border border-[var(--border)] bg-[var(--panel-strong)] px-4 py-3 text-sm leading-7 text-[var(--foreground)] shadow-[var(--shadow-soft)] outline-none transition focus:border-[var(--border-strong)] focus:ring-4 focus:ring-[var(--ring)] motion-reduce:transition-none",
        className,
      )}
      {...props}
    />
  );
});
