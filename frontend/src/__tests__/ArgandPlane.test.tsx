import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { ArgandPlane, argandGraphData } from "../components/ArgandPlane";

describe("plano complejo B7", () => {
  it("muestra puntos independientes con ejes Re e Im", () => {
    const points = [{ re: 0, im: 1, label: "I" }, { re: 0, im: -1, label: "-I" }];
    render(<ArgandPlane points={points} />);
    expect(screen.getAllByTestId("complex-point")).toHaveLength(2);
    expect(screen.getByTestId("complex-argand")).toHaveAttribute("aria-label", expect.stringContaining("Re e Im"));
    const graph = argandGraphData(points);
    expect(graph.traces.map((trace) => trace.type)).toEqual(["point", "point"]);
    expect(graph.x_axis_label).toBe("Re");
    expect(graph.y_axis_label).toBe("Im");
  });
});
