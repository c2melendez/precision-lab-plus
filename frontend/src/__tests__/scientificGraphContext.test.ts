import { describe, expect, it } from "vitest";
import type { MathResponse } from "../api/client";
import { directFunctionGraphContext } from "../components/scientificGraphContext";

describe("contexto canónico de función directa", () => {
  it("conserva la expresión de entrada y el resultado del motor, sin leer texto visual", () => {
    const result = {
      success: true,
      result_text: "x**2 + 1",
      result_latex: "x^{2}+1",
      result_data: null,
    } as MathResponse;
    const context = directFunctionGraphContext("x**2+1", "x", "deg", result, "x^2+1");

    expect(context.originalExpression).toBe("x**2+1");
    expect(context.inputLatex).toBe("x^2+1");
    expect(context.canonicalResult).toEqual({ text: "x**2 + 1", data: null });
    expect(context.graphRequest).toEqual({
      endpoint: "/graph/2d",
      payload: { expressions: ["x**2+1"], variable: "x", angle_unit: "deg" },
    });
    expect(JSON.stringify(context)).not.toContain("x^{2}");
  });

  it("representa una función aún no evaluada sin inventar un resultado", () => {
    const context = directFunctionGraphContext("y**2", "y", "rad", null, "y^2");
    expect(context.canonicalResult).toBeNull();
    expect(context.variables).toEqual(["y"]);
    expect(context.graphRequest?.payload.variable).toBe("y");
  });
});
