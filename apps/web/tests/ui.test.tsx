import { render, screen } from "@testing-library/react";

import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";
import { Spinner } from "@/components/ui/Spinner";
import { Textarea } from "@/components/ui/Textarea";

describe("UI primitives", () => {
  it("renders the core primitives with consistent semantics", () => {
    render(
      <Card>
        <Badge>Demo</Badge>
        <Input placeholder="role title" />
        <Textarea placeholder="write details" />
        <Select defaultValue="all">
          <option value="all">All</option>
        </Select>
        <Button>Save</Button>
        <Spinner aria-label="loading" />
      </Card>,
    );

    expect(screen.getByText("Demo")).toBeInTheDocument();
    expect(screen.getByPlaceholderText("role title")).toBeInTheDocument();
    expect(screen.getByPlaceholderText("write details")).toBeInTheDocument();
    expect(screen.getByDisplayValue("All")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Save" })).toBeInTheDocument();
    expect(screen.getByLabelText("loading")).toBeInTheDocument();
  });
});
