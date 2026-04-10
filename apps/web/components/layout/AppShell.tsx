import { ReactNode } from "react";

import { cn } from "@/lib/utils/cn";
import { FloatingSideBar } from "@/components/layout/FloatingSideBar";

type AppShellProps = {
  title: string;
  description?: string;
  eyebrow?: string;
  actions?: ReactNode;
  children: ReactNode;
  className?: string;
  backHref?: string;
};

export function AppShell({
  title,
  description,
  eyebrow = "Auto HR",
  actions,
  children,
  className,
  backHref = "/jobs",
}: AppShellProps) {
  return (
    <main className="ui-page-shell">
      <div className={cn("mx-auto flex w-full max-w-7xl flex-col gap-8 px-6 py-8 sm:px-8 sm:py-10", className)}>
        <header className="ui-glass-panel rounded-[32px] px-6 py-6 sm:px-7">
          <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
            <div className="max-w-3xl space-y-2">
              <p className="text-xs font-semibold uppercase tracking-[0.24em] text-[var(--foreground-muted)]">
                {eyebrow}
              </p>
              <h1 className="text-3xl font-semibold tracking-tight text-[var(--foreground)] sm:text-4xl">
                {title}
              </h1>
              {description ? (
                <p className="max-w-2xl text-sm leading-7 text-[var(--foreground-soft)] sm:text-base">
                  {description}
                </p>
              ) : null}
            </div>
            {actions ? <div className="flex flex-wrap gap-3">{actions}</div> : null}
          </div>
        </header>

        <div className="flex flex-col gap-6">
          {children}
        </div>
      </div>
      <FloatingSideBar backHref={backHref} />
    </main>
  );
}
