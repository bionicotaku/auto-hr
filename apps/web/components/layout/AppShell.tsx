import { ReactNode } from "react";

import { cn } from "@/lib/utils/cn";

type AppShellProps = {
  title: string;
  description?: string;
  eyebrow?: string;
  actions?: ReactNode;
  children: ReactNode;
  className?: string;
};

export function AppShell({
  title,
  description,
  eyebrow = "Auto HR",
  actions,
  children,
  className,
}: AppShellProps) {
  return (
    <main className="min-h-screen bg-[linear-gradient(180deg,#f4f1eb_0%,#f7f5f0_30%,#fbfaf7_100%)] text-slate-950">
      <div className={cn("mx-auto flex w-full max-w-7xl flex-col gap-8 px-6 py-8 sm:px-8 sm:py-10", className)}>
        <header className="flex flex-col gap-5 border-b border-slate-200/90 pb-6 lg:flex-row lg:items-end lg:justify-between">
          <div className="max-w-3xl space-y-2">
            <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-500">{eyebrow}</p>
            <h1 className="text-3xl font-semibold tracking-tight text-slate-950 sm:text-4xl">{title}</h1>
            {description ? (
              <p className="max-w-2xl text-sm leading-7 text-slate-600 sm:text-base">{description}</p>
            ) : null}
          </div>
          {actions ? <div className="flex flex-wrap gap-3">{actions}</div> : null}
        </header>

        {children}
      </div>
    </main>
  );
}
