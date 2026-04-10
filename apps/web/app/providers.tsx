"use client";

import {
  PropsWithChildren,
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import { QueryClientProvider } from "@tanstack/react-query";

import { createQueryClient } from "@/lib/query/client";

type ThemeMode = "light" | "dark";

type ThemeControllerValue = {
  theme: ThemeMode;
  toggleTheme: () => void;
};

const ThemeControllerContext = createContext<ThemeControllerValue | null>(null);

function getSystemTheme(): ThemeMode {
  if (typeof window !== "undefined" && typeof window.matchMedia === "function") {
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }
  return "light";
}

function getInitialTheme(): ThemeMode {
  if (typeof document !== "undefined") {
    const currentTheme = document.documentElement.dataset.theme;
    if (currentTheme === "light" || currentTheme === "dark") {
      return currentTheme;
    }
  }

  return getSystemTheme();
}

export function Providers({ children }: PropsWithChildren) {
  const [queryClient] = useState(() => createQueryClient());
  const [systemTheme, setSystemTheme] = useState<ThemeMode>(getInitialTheme);
  const [themeOverride, setThemeOverride] = useState<ThemeMode | null>(null);

  const theme = themeOverride ?? systemTheme;

  useEffect(() => {
    const mediaQuery = typeof window.matchMedia === "function"
      ? window.matchMedia("(prefers-color-scheme: dark)")
      : null;

    if (!mediaQuery) {
      return;
    }

    const activeMediaQuery = mediaQuery;

    function syncSystemTheme(event?: MediaQueryListEvent) {
      setSystemTheme((event?.matches ?? activeMediaQuery.matches) ? "dark" : "light");
    }

    syncSystemTheme();
    activeMediaQuery.addEventListener("change", syncSystemTheme);

    return () => {
      activeMediaQuery.removeEventListener("change", syncSystemTheme);
    };
  }, []);

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    document.documentElement.style.colorScheme = theme;
  }, [theme]);

  const themeController = useMemo<ThemeControllerValue>(
    () => ({
      theme,
      toggleTheme: () => {
        setThemeOverride((currentTheme) => {
          if (currentTheme) {
            return currentTheme === "dark" ? "light" : "dark";
          }
          return systemTheme === "dark" ? "light" : "dark";
        });
      },
    }),
    [systemTheme, theme],
  );

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeControllerContext.Provider value={themeController}>
        {children}
      </ThemeControllerContext.Provider>
    </QueryClientProvider>
  );
}

export function useThemeController() {
  const context = useContext(ThemeControllerContext);

  if (!context) {
    throw new Error("useThemeController must be used within Providers");
  }

  return context;
}
