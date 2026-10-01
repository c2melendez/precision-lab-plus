import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { NumberLine } from "../components/NumberLine";

describe("recta real B7", () => {
  it("diferencia visualmente extremo abierto y cerrado", () => {
    const { rerender } = render(<NumberLine intervals={[{ lower: 0, upper: null,
      lower_text: "0", lower_included: false, upper_included: false }]} />);
    expect(screen.getByTestId("inequality-endpoint")).toHaveAttribute("fill", "white");
    rerender(<NumberLine intervals={[{ lower: 0, upper: null,
      lower_text: "0", lower_included: true, upper_included: false }]} />);
    expect(screen.getByTestId("inequality-endpoint")).toHaveAttribute("fill", "#2862b8");
  });

  it("muestra dos intervalos separados y el conjunto vacío", () => {
    const { rerender } = render(<NumberLine intervals={[
      { lower: null, upper: -1, upper_text: "-1", lower_included: false, upper_included: true },
      { lower: 1, upper: null, lower_text: "1", lower_included: true, upper_included: false },
    ]} />);
    expect(screen.getAllByTestId("inequality-segment")).toHaveLength(2);
    rerender(<NumberLine intervals={[]} />);
    expect(screen.getByText(/Conjunto solución vacío/)).toBeInTheDocument();
  });
});
