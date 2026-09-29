import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { CircleInequality } from "../components/CircleInequality";

const circle = {
  center_x: 2, center_y: -1, radius: 3,
  center_x_exact: "2", center_y_exact: "-1", radius_exact: "3",
  inside: true, boundary_included: false,
};

describe("inecuación circular B7", () => {
  it("rellena solo el interior y excluye el borde estricto", () => {
    render(<CircleInequality circle={circle} />);
    expect(screen.getByTestId("circle-interior-region")).toBeInTheDocument();
    expect(screen.queryByTestId("circle-exterior-region")).toBeNull();
    expect(screen.getByTestId("circle-boundary")).toHaveAttribute("stroke-dasharray", "6 5");
    expect(screen.getByRole("img")).toHaveAttribute("aria-label", expect.stringContaining("centro (2, -1)"));
  });

  it("rellena el exterior e incluye el borde", () => {
    render(<CircleInequality circle={{ ...circle, inside: false, boundary_included: true }} />);
    expect(screen.queryByTestId("circle-interior-region")).toBeNull();
    expect(screen.getByTestId("circle-exterior-region")).toHaveAttribute("fill-rule", "evenodd");
    expect(screen.getByTestId("circle-boundary")).not.toHaveAttribute("stroke-dasharray");
  });
});
