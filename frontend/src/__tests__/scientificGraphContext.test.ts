import { describe, expect, it } from "vitest";
import type { MathResponse } from "../api/client";
import { directFunctionGraphContext, derivativeGraphContext, definiteIntegralGraphContext, indefiniteIntegralGraphContext } from "../components/scientificGraphContext";

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

describe("contexto canónico de integral indefinida", () => {
  it("grafica C=0 desde campos estructurados y conserva +C en Resultado", () => {
    const result = {
      success: true,
      result_text: "x**3/3 + C",
      result_latex: "\\frac{x^{3}}{3} + C",
      antiderivative_expression: "x**3/3",
      antiderivative_latex: "\\frac{x^{3}}{3}",
    } as MathResponse;
    const context = indefiniteIntegralGraphContext("x^2", "x^2", "\\int x^2\\,dx", "x", "rad", result, true);
    expect(context.canonicalResult?.text).toBe("x**3/3 + C");
    expect(context.metadata).toMatchObject({ kind: "indefinite", visualConstant: 0 });
    expect(context.graphRequest?.payload.expressions).toEqual(["x^2", "x**3/3"]);
    expect(context.graphInputLatex).toEqual(["x^2", "\\frac{x^{3}}{3}"]);
  });

  it("usa la semántica en radianes del endpoint aunque la UI esté en grados", () => {
    const result = {
      success: true, result_text: "-cos(x) + C",
      antiderivative_expression: "-cos(x)", antiderivative_latex: "-\\cos(x)",
    } as MathResponse;
    const context = indefiniteIntegralGraphContext("sin(x)", "\\sin(x)", "\\int\\sin(x)\\,dx", "x", "deg", result, true);
    expect(context.graphRequest?.payload.angle_unit).toBe("rad");
    expect(context.metadata.inputAngleUnit).toBe("deg");
  });

  it("no usa el texto mostrado para deducir una antiderivada ausente", () => {
    const result = { success: true, result_text: "x**3/3 + C", result_latex: "\\frac{x^3}{3}+C" } as MathResponse;
    const context = indefiniteIntegralGraphContext("x^2", "x^2", "integral", "x", "rad", result, true);
    expect(context.graphRequest).toBeNull();
    expect(context.visualization).toBe("advanced");
  });
});

describe("contexto canónico de derivada", () => {
  it("transfiere original y resultado del motor con orden y variable", () => {
    const result = {
      success: true, result_text: "2*x", result_latex: "2 x", result_data: null,
    } as MathResponse;
    const context = derivativeGraphContext("x^2+1", "x^2+1", "\\frac{d}{dx}\\left(x^2+1\\right)", "x", 1, "rad", result, true);
    expect(context.canonicalResult?.text).toBe("2*x");
    expect(context.graphRequest?.payload.expressions).toEqual(["x^2+1", "2*x"]);
    expect(context.graphInputLatex).toEqual(["x^2+1", "2 x"]);
    expect(context.metadata).toEqual({ order: 1, angleUnit: "rad", inputAngleUnit: "rad" });
  });

  it("no ofrece una curva cartesiana cuando el resultado depende de otro parámetro", () => {
    const result = { success: true, result_text: "2*a*x", result_latex: "2 a x" } as MathResponse;
    const context = derivativeGraphContext("a*x^2", "a x^2", "derivada", "x", 1, "rad", result, false);
    expect(context.visualization).toBe("advanced");
    expect(context.graphRequest).toBeNull();
  });
});

describe("contexto canónico de integral definida", () => {
  it("mantiene límites, orientación y valor exacto sin deducir el área del muestreo", () => {
    const result = { success: true, result_text: "-8/3", result_data: null } as MathResponse;
    const context = definiteIntegralGraphContext("x^2", "x^2", "\\int_{2}^{0}x^2\\,dx", "x", "2", "0", "rad", result, true);
    expect(context.metadata).toMatchObject({ kind: "definite", lowerBound: "2", upperBound: "0", orientation: -1 });
    expect(context.canonicalResult?.text).toBe("-8/3");
    expect(context.graphRequest?.payload).toMatchObject({ expressions: ["x^2"], variable: "x", x_min: -1, x_max: 3 });
    expect(context.graphInputLatex).toEqual(["x^2"]);
  });
});
