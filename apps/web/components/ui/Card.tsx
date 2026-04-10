import { HTMLAttributes } from "react";

import { cn } from "@/lib/utils/cn";

export function Card({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "rounded-[28px] border border-white/70 bg-white/80 p-6 shadow-[0_20px_48px_rgba(15,23,42,0.10)] backdrop-blur",
        className,
      )}
      {...props}
    />
  );
}
