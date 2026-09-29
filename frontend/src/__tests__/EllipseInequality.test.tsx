import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { EllipseInequality } from "../components/EllipseInequality";

const ellipse = {
  center_x: 2, center_y: -1, radius_x: 3, radius_y: 2,
  center_x_exact: "2", center_y_exact: "-1", radius_x_exact: "3", radius_y_exact: "2",
  inside: true, boundary_included: false,
};

describe("inecuación elíptica B7", () => {
  it("dibuja interior y frontera excluida con radios distintos", () => {
    render(<EllipseInequality ellipse={ellipse} />);
    const region = screen.getByTestId("ellipse-interior-region");
    expect(Number(region.getAttribute("rx"))).toBeGreaterThan(Number(region.getAttribute("ry")));
    expect(screen.getByTestId("ellipse-boundary")).toHaveAttribute("stroke-dasharray", "6 5");
    expect(screen.getByRole("img")).toHaveAttribute("aria-label", expect.stringContaining("centro (2, -1)"));
  });

  it("dibuja exterior con hueco y frontera incluida", () => {
    render(<EllipseInequality ellipse={{ ...ellipse, inside: false, boundary_included: true }} />);
    expect(screen.queryByTestId("ellipse-interior-region")).toBeNull();
    expect(screen.getByTestId("ellipse-exterior-region")).toHaveAttribute("fill-rule", "evenodd");
    expect(screen.getByTestId("ellipse-boundary")).not.toHaveAttribute("stroke-dasharray");
  });
});
