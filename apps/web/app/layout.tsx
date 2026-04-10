import type { Metadata } from "next";
import type { ReactNode } from "react";
import Script from "next/script";

import { Providers } from "@/app/providers";
import "@/styles/globals.css";

export const metadata: Metadata = {
  title: "Auto HR",
  description: "招聘工作台",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="zh-CN" suppressHydrationWarning>
      <body suppressHydrationWarning>
        <Script id="theme-init" strategy="beforeInteractive">
          {`(() => {
            const root = document.documentElement;
            const prefersDark =
              typeof window.matchMedia === "function" &&
              window.matchMedia("(prefers-color-scheme: dark)").matches;
            const theme = prefersDark ? "dark" : "light";
            root.dataset.theme = theme;
            root.style.colorScheme = theme;
          })();`}
        </Script>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
