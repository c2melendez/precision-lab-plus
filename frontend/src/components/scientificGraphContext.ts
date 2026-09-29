import type { MathResponse } from "../api/client";

/** Datos matemáticos de Científica que sobreviven al cambio de módulo. */
export interface ScientificGraphContext {
  operation: "function" | "derivative" | "integral" | "limit" | "simplify" | "factor" | "equation" | "system" | "inequality" | "complex" | "ode";
  originalExpression: string;
  inputLatex: string;
  graphInputLatex: string[] | null;
  canonicalResult: {
    text: string | null;
    data: MathResponse["result_data"];
  } | null;
  variables: string[];
  metadata: Record<string, unknown>;
  /** null: aún no calculadas; []: dominio confirmado sin restricciones. */
  restrictions: string[] | null;
  visualization: "cartesian-2d" | "number-line" | "region-2d" | "argand" | "advanced";
  graphRequest: { endpoint: "/graph/2d" | "/solve/system"; payload: {
    expressions?: string[]; variable?: string; angle_unit?: "rad" | "deg";
    equations?: string[]; variables?: string[]; x_min?: number; x_max?: number;
  } } | null;
}

export function directFunctionGraphContext(
  expression: string,
  variable: string,
  angleUnit: "rad" | "deg",
  result: MathResponse | null,
  inputLatex: string,
): ScientificGraphContext {
  return {
    operation: "function",
    originalExpression: expression,
    inputLatex,
    graphInputLatex: [inputLatex],
    canonicalResult: result?.success
      ? { text: result.result_text ?? null, data: result.result_data ?? null }
      : null,
    variables: [variable],
    metadata: { angleUnit },
    restrictions: null,
    visualization: "cartesian-2d",
    graphRequest: {
      endpoint: "/graph/2d",
      payload: { expressions: [expression], variable, angle_unit: angleUnit },
    },
  };
}

export function derivativeGraphContext(
  expression: string,
  innerLatex: string,
  inputLatex: string,
  variable: string,
  order: number,
  angleUnit: "rad" | "deg",
  result: MathResponse,
  graphable: boolean,
): ScientificGraphContext {
  const derived = result.success ? result.result_text?.trim() : null;
  const canGraph = graphable && Boolean(derived) && Boolean(result.result_latex);
  return {
    operation: "derivative",
    originalExpression: expression,
    inputLatex,
    graphInputLatex: canGraph ? [innerLatex, result.result_latex!] : null,
    canonicalResult: result.success
      ? { text: derived ?? null, data: result.result_data ?? null } : null,
    variables: [variable],
    metadata: { order, angleUnit: "rad", inputAngleUnit: angleUnit },
    restrictions: null,
    visualization: canGraph ? "cartesian-2d" : "advanced",
    graphRequest: canGraph ? {
      endpoint: "/graph/2d",
      payload: { expressions: [expression, derived!], variable, angle_unit: "rad" },
    } : null,
  };
}

export function indefiniteIntegralGraphContext(
  expression: string,
  innerLatex: string,
  inputLatex: string,
  variable: string,
  angleUnit: "rad" | "deg",
  result: MathResponse,
  graphable: boolean,
): ScientificGraphContext {
  const antiderivative = result.antiderivative_expression?.trim();
  const canGraph = result.success && graphable && Boolean(antiderivative) && Boolean(result.antiderivative_latex);
  return {
    operation: "integral",
    originalExpression: expression,
    inputLatex,
    graphInputLatex: canGraph ? [innerLatex, result.antiderivative_latex!] : null,
    canonicalResult: result.success
      ? { text: result.result_text ?? null, data: result.result_data ?? null } : null,
    variables: [variable],
    metadata: { kind: "indefinite", visualConstant: 0, angleUnit: "rad", inputAngleUnit: angleUnit },
    restrictions: null,
    visualization: canGraph ? "cartesian-2d" : "advanced",
    graphRequest: canGraph ? {
      endpoint: "/graph/2d",
      payload: { expressions: [expression, antiderivative!], variable, angle_unit: "rad" },
    } : null,
  };
}

export function definiteIntegralGraphContext(
  expression: string,
  innerLatex: string,
  inputLatex: string,
  variable: string,
  lowerBound: string,
  upperBound: string,
  angleUnit: "rad" | "deg",
  result: MathResponse,
  graphable: boolean,
): ScientificGraphContext {
  const lower = Number(lowerBound);
  const upper = Number(upperBound);
  const validBounds = Number.isFinite(lower) && Number.isFinite(upper)
    && Math.abs(lower) <= 1e6 && Math.abs(upper) <= 1e6;
  const span = Math.abs(upper - lower);
  const margin = Math.max(span * 0.25, 1);
  const canGraph = result.success && graphable && validBounds;
  return {
    operation: "integral",
    originalExpression: expression,
    inputLatex,
    graphInputLatex: canGraph ? [innerLatex] : null,
    canonicalResult: result.success
      ? { text: result.result_text ?? null, data: result.result_data ?? null } : null,
    variables: [variable],
    metadata: { kind: "definite", lowerBound, upperBound, orientation: upper >= lower ? 1 : -1,
      angleUnit: "rad", inputAngleUnit: angleUnit },
    restrictions: null,
    visualization: canGraph ? "cartesian-2d" : "advanced",
    graphRequest: canGraph ? {
      endpoint: "/graph/2d",
      payload: { expressions: [expression], variable, angle_unit: "rad",
        x_min: Math.min(lower, upper) - margin, x_max: Math.max(lower, upper) + margin },
    } : null,
  };
}

export function limitGraphContext(
  expression: string,
  innerLatex: string,
  inputLatex: string,
  variable: string,
  point: string,
  direction: "both" | "left" | "right",
  angleUnit: "rad" | "deg",
  result: MathResponse,
  graphable: boolean,
): ScientificGraphContext {
  const finitePoint = Number(point);
  const isInfinite = point === "oo" || point === "-oo";
  const validPoint = isInfinite || (point.trim() !== "" && Number.isFinite(finitePoint) && Math.abs(finitePoint) <= 1e6);
  const span = isInfinite ? 16 : Math.max(2, Math.abs(finitePoint) * 0.25);
  const xMin = point === "oo" ? 4 : point === "-oo" ? -20 : finitePoint - span;
  const xMax = point === "oo" ? 20 : point === "-oo" ? -4 : finitePoint + span;
  const canGraph = result.success && graphable && validPoint;
  return {
    operation: "limit",
    originalExpression: expression,
    inputLatex,
    graphInputLatex: canGraph ? [innerLatex] : null,
    canonicalResult: result.success ? { text: result.result_text ?? null, data: result.result_data ?? null } : null,
    variables: [variable],
    metadata: { point, direction, angleUnit: "rad", inputAngleUnit: angleUnit,
      behavior: isInfinite ? "far-field" : "near-point", bilateralDoesNotExist: result.result_text === "DNE" },
    restrictions: null,
    visualization: canGraph ? "cartesian-2d" : "advanced",
    graphRequest: canGraph ? { endpoint: "/graph/2d", payload: {
      expressions: [expression], variable, angle_unit: "rad", x_min: xMin, x_max: xMax,
    } } : null,
  };
}

export function algebraTransformationGraphContext(
  operation: "simplify" | "factor",
  expression: string,
  inputLatex: string,
  variable: string | null,
  angleUnit: "rad" | "deg",
  result: MathResponse,
): ScientificGraphContext {
  const safe = result.success && result.graph_polynomial_comparison === true
    && variable !== null && Boolean(result.result_text) && Boolean(result.result_latex);
  return {
    operation,
    originalExpression: expression,
    inputLatex,
    graphInputLatex: safe ? [inputLatex] : null,
    canonicalResult: result.success ? { text: result.result_text ?? null, data: result.result_data ?? null } : null,
    variables: variable ? [variable] : [],
    metadata: { angleUnit, transformedExpression: result.result_text ?? null,
      transformedLatex: result.result_latex ?? null, polynomialDomainCertified: safe },
    restrictions: safe ? [] : null,
    visualization: safe ? "cartesian-2d" : "advanced",
    graphRequest: safe ? { endpoint: "/graph/2d", payload: {
      expressions: [expression], variable, angle_unit: angleUnit,
    } } : null,
  };
}

export function odeGraphContext(
  expression: string,
  inputLatex: string,
  result: MathResponse,
): ScientificGraphContext {
  const particular = result.ode_solution_expression && result.ode_solution_latex;
  const family = result.ode_representative_expressions?.length === 3
    && result.ode_representative_latex?.length === 3;
  const graphExpressions = particular ? [result.ode_solution_expression!] : family
    ? result.ode_representative_expressions! : null;
  const graphLatex = particular ? [result.ode_solution_latex!] : family
    ? result.ode_representative_latex! : null;
  const canGraph = result.success && Boolean(graphExpressions) && Boolean(graphLatex);
  return {
    operation: "ode",
    originalExpression: expression,
    inputLatex,
    graphInputLatex: canGraph ? graphLatex : null,
    canonicalResult: result.success ? { text: result.result_text ?? null, data: result.result_data ?? null } : null,
    variables: ["x"],
    metadata: { kind: particular ? "particular" : family ? "one-parameter-family" : "advanced-family",
      representativeConstants: family ? [-1, 0, 1] : null, angleUnit: "rad" },
    restrictions: null,
    visualization: canGraph ? "cartesian-2d" : "advanced",
    graphRequest: canGraph ? { endpoint: "/graph/2d", payload: {
      expressions: graphExpressions!, variable: "x", angle_unit: "rad",
    } } : null,
  };
}

export function systemGraphContext(
  equations: string[], variables: string[], inputLatex: string, result: MathResponse,
): ScientificGraphContext {
  const expressions = result.system_graph_expressions;
  const latex = result.system_graph_latex;
  const graphable = result.success && variables.length === 2 && variables[0] === "x"
    && variables[1] === "y" && Boolean(expressions?.length) && expressions?.length === latex?.length;
  const verticalGraph = result.success && variables.length === 2 && variables[0] === "x"
    && variables[1] === "y" && Boolean(result.graph_data?.traces.length);
  const intersectionX = result.system_graph_intersections?.[0]?.[0];
  const centerOnIntersection = Number.isFinite(intersectionX) && Math.abs(intersectionX!) <= 1e6
    && Math.abs(intersectionX!) > 8;
  const nonlinearXs = result.system_graph_component_indices
    ? (result.system_graph_intersections ?? []).map(([x]) => x).filter((x) => Number.isFinite(x) && Math.abs(x) <= 1e6)
    : [];
  const nonlinearSpan = nonlinearXs.length
    ? Math.max(1, Math.max(...nonlinearXs) - Math.min(...nonlinearXs)) : 0;
  return {
    operation: "system",
    originalExpression: equations.join(" ; "),
    inputLatex,
    graphInputLatex: graphable ? latex! : verticalGraph ? equations : null,
    canonicalResult: result.success ? { text: result.result_text ?? null, data: result.result_data ?? null } : null,
    variables,
    metadata: { equations, intersections: result.system_graph_intersections ?? [],
      coincident: result.system_graph_coincident === true,
      componentIndices: result.system_graph_component_indices ?? null, angleUnit: "rad" },
    restrictions: null,
    visualization: graphable || verticalGraph ? "cartesian-2d" : "advanced",
    graphRequest: verticalGraph ? { endpoint: "/solve/system", payload: { equations, variables } }
      : graphable ? { endpoint: "/graph/2d", payload: {
      expressions: expressions!, variable: "x", angle_unit: "rad",
      ...(nonlinearXs.length ? { x_min: Math.min(...nonlinearXs) - nonlinearSpan,
        x_max: Math.max(...nonlinearXs) + nonlinearSpan }
        : centerOnIntersection ? { x_min: intersectionX! - 10, x_max: intersectionX! + 10 } : {}),
    } } : null,
  };
}

export function inequalityGraphContext(
  expression: string, variable: string, inputLatex: string, result: MathResponse,
): ScientificGraphContext {
  const intervals = result.inequality_intervals;
  const graphable = result.success && intervals != null;
  return {
    operation: "inequality", originalExpression: expression, inputLatex,
    graphInputLatex: null,
    canonicalResult: result.success ? { text: result.result_text ?? null, data: result.result_data ?? null } : null,
    variables: [variable],
    metadata: { intervals: intervals ?? null, solutionLatex: result.result_latex ?? null,
      angleUnit: "rad" },
    restrictions: null,
    visualization: graphable ? "number-line" : "advanced",
    graphRequest: null,
  };
}
