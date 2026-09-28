import { describe, expect, it } from "vitest";
import type { components } from "../types/api";
import { graphPreviewGeometry } from "../components/graphPreviewGeometry";

type GraphData = components["schemas"]["GraphData"];

describe("vista previa de curva", () => {
  it("respeta discontinuidades devueltas por el motor y no une puntos a través de ellas", () => {
    const data: GraphData = {
      traces: [{ type: "line", name: "1/x", x: [-1, -0.5, 0, 0.5, 1], y: [-1, -2, null, 2, 1] }],
      x_range: [-1, 1], y_range: [-2, 2], points_truncated: false,
    };
    const geometry = graphPreviewGeometry(data);
    expect(geometry?.paths).toHaveLength(1);
    expect(geometry?.paths[0].match(/M/g)).toHaveLength(2);
    expect(geometry?.zeroX).toBe(160);
    expect(geometry?.zeroY).toBe(60);
  });

  it("no dibuja una curva cuando el motor no aporta rango o puntos válidos", () => {
    const data: GraphData = {
      traces: [{ type: "line", name: "sqrt(-x²)", x: [-1, 0, 1], y: [null, null, null] }],
      x_range: [-1, 1], y_range: null, points_truncated: false,
    };
    expect(graphPreviewGeometry(data)).toBeNull();
  });
});
