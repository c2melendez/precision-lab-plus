import { describe, expect, it } from "vitest";
import type { MathResponse } from "../api/client";
import { algebraTransformationGraphContext, directFunctionGraphContext, derivativeGraphContext, definiteIntegralGraphContext, indefiniteIntegralGraphContext, limitGraphContext, odeGraphContext, systemGraphContext } from "../components/scientificGraphContext";

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

describe("sistema lineal certificado", () => {
  it("conserva ecuaciones y soluciones, y marca solo la intersección calculada", () => {
    const result = { success: true, result_data: [{ text: "x=2, y=1", latex: "x=2,y=1" }],
      system_graph_expressions: ["3 - x", "x - 1"], system_graph_latex: ["3-x", "x-1"],
      system_graph_intersections: [[2, 1]] } as MathResponse;
    const context = systemGraphContext(["x+y=3", "x-y=1"], ["x", "y"], "\\begin{cases}...", result);
    expect(context.graphRequest?.payload.expressions).toEqual(["3 - x", "x - 1"]);
    expect(context.metadata.intersections).toEqual([[2, 1]]);
    expect(context.metadata.equations).toEqual(["x+y=3", "x-y=1"]);
    expect(context.canonicalResult?.data).toEqual(result.result_data);
  });

  it("no envía rectas verticales a un motor y=f(x)", () => {
    const context = systemGraphContext(["x=1", "y=2"], ["x", "y"], "system", {
      success: true, system_graph_expressions: null, system_graph_latex: null,
    } as MathResponse);
    expect(context.graphRequest).toBeNull();
    expect(context.visualization).toBe("advanced");
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

describe("contexto canónico de límite", () => {
  it("conserva punto, dirección y DNE sin inferir laterales desde LaTeX de Resultado", () => {
    const result = { success: true, result_text: "DNE", result_latex: "texto con laterales" } as MathResponse;
    const context = limitGraphContext("1/x", "\\frac{1}{x}", "\\lim_{x\\to0}\\frac{1}{x}", "x", "0", "both", "deg", result, true);
    expect(context.metadata).toMatchObject({ point: "0", direction: "both", bilateralDoesNotExist: true, inputAngleUnit: "deg" });
    expect(context.canonicalResult?.text).toBe("DNE");
    expect(context.graphRequest?.payload).toMatchObject({ expressions: ["1/x"], x_min: -2, x_max: 2, angle_unit: "rad" });
    expect(JSON.stringify(context)).not.toContain("texto con laterales");
  });

  it("encuadra el comportamiento lejano en dirección al infinito", () => {
    const context = limitGraphContext("1/x", "1/x", "límite", "x", "oo", "both", "rad",
      { success: true, result_text: "0" } as MathResponse, true);
    expect(context.graphRequest?.payload).toMatchObject({ x_min: 4, x_max: 20 });
    expect(context.metadata.behavior).toBe("far-field");
  });
});

describe("transformación algebraica y dominio", () => {
  it("grafica una sola curva para dos formas polinómicas con dominio real completo", () => {
    const result = { success: true, result_text: "(x - 2)*(x + 2)", result_latex: "(x-2)(x+2)",
      graph_polynomial_comparison: true } as MathResponse;
    const context = algebraTransformationGraphContext("factor", "x^2-4", "x^2-4", "x", "rad", result);
    expect(context.restrictions).toEqual([]);
    expect(context.graphRequest?.payload.expressions).toEqual(["x^2-4"]);
    expect(context.graphInputLatex).toEqual(["x^2-4"]);
    expect(context.metadata.transformedExpression).toBe("(x - 2)*(x + 2)");
  });

  it("no atribuye dominio real completo a x/x simplificado como 1", () => {
    const result = { success: true, result_text: "1", result_latex: "1",
      graph_polynomial_comparison: false } as MathResponse;
    const context = algebraTransformationGraphContext("simplify", "x/x", "\\frac{x}{x}", "x", "rad", result);
    expect(context.restrictions).toBeNull();
    expect(context.graphRequest).toBeNull();
    expect(context.visualization).toBe("advanced");
  });
});

describe("solución EDO estructurada", () => {
  it("grafica solo el lado derecho de una solución particular", () => {
    const result = { success: true, result_text: "Eq(y(x), exp(x))", result_latex: "y(x)=e^x",
      ode_solution_expression: "exp(x)", ode_solution_latex: "e^{x}" } as MathResponse;
    const context = odeGraphContext("y'=y, y(0)=1", "y'=y, y(0)=1", result);
    expect(context.graphRequest?.payload.expressions).toEqual(["exp(x)"]);
    expect(context.graphInputLatex).toEqual(["e^{x}"]);
    expect(context.canonicalResult?.text).toBe("Eq(y(x), exp(x))");
    expect(context.metadata.kind).toBe("particular");
  });

  it("conserva la familia original y grafica solo tres representantes", () => {
    const result = { success: true, result_text: "Eq(y(x), C1*exp(x))",
      ode_representative_expressions: ["-exp(x)", "0", "exp(x)"],
      ode_representative_latex: ["-e^x", "0", "e^x"] } as MathResponse;
    const context = odeGraphContext("y'=y", "y'=y", result);
    expect(context.graphRequest?.payload.expressions).toEqual(["-exp(x)", "0", "exp(x)"]);
    expect(context.metadata.representativeConstants).toEqual([-1, 0, 1]);
    expect(context.canonicalResult?.text).toContain("C1");
  });

  it("no inventa curvas para una familia de dos parámetros", () => {
    const context = odeGraphContext("y''=-y", "y''=-y", { success: true,
      result_text: "Eq(y(x), C1*sin(x)+C2*cos(x))" } as MathResponse);
    expect(context.graphRequest).toBeNull();
    expect(context.visualization).toBe("advanced");
  });
});
