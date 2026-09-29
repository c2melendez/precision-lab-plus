import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { InequalityRegion } from "../components/InequalityRegion";

const boundaries = [
  { a: 1, b: 0, c: 0, operator: ">", label: "x>0" },
  { a: 0, b: 1, c: 0, operator: ">=", label: "y>=0" },
  { a: 1, b: 1, c: 4, operator: "<", label: "x+y<4" },
];

describe("región factible B7", () => {
  it("sombrea solo la intersección y distingue fronteras estrictas", () => {
    render(<InequalityRegion boundaries={boundaries} polygon={[[0, 0], [4, 0], [0, 4]]}
      viewport={[-3, 7, -3, 7]} kind="bounded" />);
    expect(screen.getByTestId("feasible-region")).toHaveAttribute("points");
    const lines = screen.getAllByTestId("inequality-boundary");
    expect(lines).toHaveLength(3);
    expect(lines[0]).toHaveAttribute("stroke-dasharray", "6 5");
    expect(lines[1]).not.toHaveAttribute("stroke-dasharray");
    expect(lines[2]).toHaveAttribute("stroke-dasharray", "6 5");
  });

  it("no pinta región cuando la intersección está vacía", () => {
    render(<InequalityRegion boundaries={boundaries.slice(0, 1)} polygon={[]}
      viewport={[-4, 4, -4, 4]} kind="empty" />);
    expect(screen.queryByTestId("feasible-region")).toBeNull();
    expect(screen.getByText(/Región vacía/)).toBeInTheDocument();
  });

  it("dibuja un rayo con origen hueco y sin relleno de área", () => {
    render(<InequalityRegion boundaries={[
      { a: 1, b: 0, c: 0, operator: ">=", label: "x>=0" },
      { a: 1, b: 0, c: 0, operator: "<=", label: "x<=0" },
      { a: 0, b: 1, c: 0, operator: ">", label: "y>0" },
    ]} polygon={[[0, 0], [0, 4]]} viewport={[-4, 4, -4, 4]} kind="unbounded" />);
    expect(screen.queryByTestId("feasible-region")).toBeNull();
    expect(screen.getByTestId("feasible-line")).toBeInTheDocument();
    expect(screen.getByTestId("feasible-endpoint")).toHaveAttribute("fill", "white");
    expect(screen.getByTestId("feasible-continuation")).toBeInTheDocument();
  });

  it("marca el punto factible incluido", () => {
    render(<InequalityRegion boundaries={[
      { a: 1, b: 0, c: 1, operator: ">=", label: "x>=1" },
      { a: 1, b: 0, c: 1, operator: "<=", label: "x<=1" },
      { a: 0, b: 1, c: 2, operator: ">=", label: "y>=2" },
      { a: 0, b: 1, c: 2, operator: "<=", label: "y<=2" },
    ]} polygon={[[1, 2]]} viewport={[-3, 5, -2, 6]} kind="bounded" />);
    expect(screen.queryByTestId("feasible-region")).toBeNull();
    expect(screen.getByTestId("feasible-endpoint")).toHaveAttribute("fill", "#174a9c");
  });
});
