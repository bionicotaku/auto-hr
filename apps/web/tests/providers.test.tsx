import { useQueryClient } from "@tanstack/react-query";
import { fireEvent, render, screen } from "@testing-library/react";

import { Providers, useThemeController } from "@/app/providers";

function QueryClientProbe() {
  const queryClient = useQueryClient();

  return <p>{queryClient ? "query-client-ready" : "missing-query-client"}</p>;
}

function ThemeControllerProbe() {
  const { theme, toggleTheme } = useThemeController();

  return (
    <>
      <p>{theme}</p>
      <button type="button" onClick={toggleTheme}>
        toggle-theme
      </button>
    </>
  );
}

describe("Providers", () => {
  it("exposes a query client to descendants", () => {
    render(
      <Providers>
        <QueryClientProbe />
      </Providers>,
    );

    expect(screen.getByText("query-client-ready")).toBeInTheDocument();
  });

  it("lets descendants toggle the current session theme", () => {
    document.documentElement.dataset.theme = "light";

    render(
      <Providers>
        <ThemeControllerProbe />
      </Providers>,
    );

    expect(screen.getByText("light")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "toggle-theme" }));

    expect(screen.getByText("dark")).toBeInTheDocument();
    expect(document.documentElement.dataset.theme).toBe("dark");
  });
});
