import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import UiLabPage from "@/app/ui-lab/page";

describe("UI lab page", () => {
  it("renders the merged canonical showcase with a theme switch", () => {
    render(<UiLabPage />);

    expect(
      screen.getByRole("heading", { name: "Decision Support Glass Preview" }),
    ).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "light" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "dark" })).toBeInTheDocument();
    expect(screen.getByText("Candidate signal table")).toBeInTheDocument();
    expect(screen.getByText("Side-by-side decision bars")).toBeInTheDocument();
  });
});
