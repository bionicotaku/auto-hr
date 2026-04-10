"use client";

import { useRouter } from "next/navigation";

import { useThemeController } from "@/app/providers";
import { Button } from "@/components/ui/Button";

type FloatingSideBarProps = {
  backHref: string;
};

export function FloatingSideBar({ backHref }: FloatingSideBarProps) {
  const router = useRouter();
  const { theme, toggleTheme } = useThemeController();
  const isDark = theme === "dark";

  return (
    <div className="pointer-events-none fixed bottom-5 right-5 z-50 sm:bottom-7 sm:right-7">
      <div className="ui-glass-panel-strong pointer-events-auto flex flex-col gap-2 rounded-full p-2 shadow-[var(--shadow-shell)]">
        <Button
          aria-label="返回上一页"
          className="h-12 w-12 rounded-full p-0"
          variant="secondary"
          onClick={() => {
            router.push(backHref);
          }}
        >
          <BackIcon />
        </Button>
        <Button
          aria-label={isDark ? "切换到浅色模式" : "切换到深色模式"}
          className="h-12 w-12 rounded-full p-0"
          variant="ghost"
          onClick={toggleTheme}
        >
          {isDark ? <SunIcon /> : <MoonIcon />}
        </Button>
      </div>
    </div>
  );
}

function BackIcon() {
  return (
    <svg
      aria-hidden="true"
      className="h-[22px] w-[22px]"
      fill="none"
      viewBox="0 0 24 24"
    >
      <path
        d="M15 18L9 12L15 6"
        stroke="currentColor"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth="2.2"
      />
    </svg>
  );
}

function SunIcon() {
  return (
    <svg
      aria-hidden="true"
      className="h-[22px] w-[22px]"
      fill="none"
      viewBox="0 0 24 24"
    >
      <circle cx="12" cy="12" r="4.6" stroke="currentColor" strokeWidth="2" />
      <path
        d="M12 2.75V5.25M12 18.75V21.25M21.25 12H18.75M5.25 12H2.75M18.54 5.46L16.77 7.23M7.23 16.77L5.46 18.54M18.54 18.54L16.77 16.77M7.23 7.23L5.46 5.46"
        stroke="currentColor"
        strokeLinecap="round"
        strokeWidth="2"
      />
    </svg>
  );
}

function MoonIcon() {
  return (
    <svg
      aria-hidden="true"
      className="h-[22px] w-[22px]"
      fill="none"
      viewBox="0 0 24 24"
    >
      <path
        d="M19.5 14.5A7.5 7.5 0 0 1 9.5 4.5A8.5 8.5 0 1 0 19.5 14.5Z"
        stroke="currentColor"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth="2"
      />
    </svg>
  );
}
