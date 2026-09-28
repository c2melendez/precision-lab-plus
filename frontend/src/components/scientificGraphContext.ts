import type { MathResponse } from "../api/client";

/** Datos matemáticos de Científica que sobreviven al cambio de módulo. */
export interface ScientificGraphContext {
  operation: "function" | "derivative" | "integral" | "limit" | "equation" | "system" | "inequality" | "complex" | "ode";
  originalExpression: string;
  inputLatex: string;
  canonicalResult: {
    text: string | null;
    data: MathResponse["result_data"];
  } | null;
  variables: string[];
  metadata: Record<string, unknown>;
  /** null: aún no calculadas; []: dominio confirmado sin restricciones. */
  restrictions: string[] | null;
  visualization: "cartesian-2d" | "number-line" | "region-2d" | "argand" | "advanced";
  graphRequest: { endpoint: "/graph/2d"; payload: { expressions: string[]; variable: string; angle_unit: "rad" | "deg" } } | null;
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
