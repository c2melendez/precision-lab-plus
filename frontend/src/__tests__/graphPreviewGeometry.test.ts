import { describe, expect, it } from "vitest";
import type { components } from "../types/api";
import { graphPreviewGeometry, integralRegionGeometry } from "../components/graphPreviewGeometry";

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

describe("región de integral definida", () => {
  const data: GraphData = {
    traces: [{ type: "line", name: "x", x: [-2, -1, 0, 1, 2], y: [-2, -1, 0, 1, 2] }],
    x_range: [-2, 2], y_range: [-2, 2], points_truncated: false,
  };

  it("recorta el tramo y separa los signos al cruzar el eje", () => {
    const geometry = graphPreviewGeometry(data, true)!;
    const region = integralRegionGeometry(data, -0.5, 1.5, geometry)!;
    expect(region.positivePath).toContain("Z");
    expect(region.negativePath).toContain("Z");
    expect(region.lowerX).toBeCloseTo(geometry.projectX(-0.5));
    expect(region.upperX).toBeCloseTo(geometry.projectX(1.5));
  });

  it("invierte el signo cuando se invierten los límites", () => {
    const geometry = graphPreviewGeometry(data, true)!;
    const forward = integralRegionGeometry(data, 0, 2, geometry)!;
    const reverse = integralRegionGeometry(data, 2, 0, geometry)!;
    expect(forward.positivePath).toContain("Z");
    expect(forward.negativePath).toBe("");
    expect(reverse.positivePath).toBe("");
    expect(reverse.negativePath).toContain("Z");
  });
});
