import { useQueryClient } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";

import { Providers } from "@/app/providers";

function QueryClientProbe() {
  const queryClient = useQueryClient();

  return <p>{queryClient ? "query-client-ready" : "missing-query-client"}</p>;
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
});
