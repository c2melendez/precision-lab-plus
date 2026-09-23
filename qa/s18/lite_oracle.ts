import fs from "node:fs";
import {
  derivative,
  evaluate,
  indefiniteIntegral,
  solveEquation,
  substituteAndFloat,
  toDecimalApprox,
  toLatex,
} from "../../lite/src/engine/algebriteClient.ts";
import { parseExpression } from "../../lite/src/engine/parsing/index.ts";

type Request =
  | { op: "eval"; expr: string }
  | { op: "derivativeOfIntegral"; expr: string; variable?: string }
  | { op: "rootsResiduals"; expr: string; variable?: string }
  | { op: "roundtrip"; expr: string; variable?: string; samples: number[] };

function numericFromAlgebrite(expr: string): number {
  const raw = evaluate(expr);
  const decimal = toDecimalApprox(raw);
  const candidate = (decimal ?? raw).replace("…", "");
  const value = Number(candidate);
  if (!Number.isFinite(value)) {
    throw new Error(`Resultado Lite no numérico para "${expr}": ${raw}`);
  }
  return value;
}

function evalUserExpression(expr: string): number {
  const parsed = parseExpression(expr, "RAD");
  return numericFromAlgebrite(parsed.algebrite);
}

function derivativeOfIntegral(expr: string, variable: string): string {
  const parsed = parseExpression(expr, "RAD");
  const anti = indefiniteIntegral(parsed.algebrite, variable);
  return derivative(anti, variable);
}

function rootsResiduals(expr: string, variable: string) {
  const parsed = parseExpression(expr, "RAD");
  const roots = solveEquation(parsed.algebrite, variable);
  return roots.map((root) => {
    const raw = substituteAndFloat(parsed.algebrite, variable, root).replace(/\.\.\.$/, "");
    const residual = Number(raw);
    if (!Number.isFinite(residual)) {
      throw new Error(`Residual Lite no numérico para raíz ${root}: ${raw}`);
    }
    return { root, residual };
  });
}

function roundtrip(expr: string, variable: string, samples: number[]) {
  const first = parseExpression(expr, "RAD").algebrite;
  const latex = toLatex(first);
  const second = parseExpression(latex, "RAD").algebrite;
  const values = samples.map((x) => {
    const before = Number(substituteAndFloat(first, variable, String(x)).replace(/\.\.\.$/, ""));
    const after = Number(substituteAndFloat(second, variable, String(x)).replace(/\.\.\.$/, ""));
    if (!Number.isFinite(before) || !Number.isFinite(after)) {
      throw new Error(`Round-trip no numérico para ${expr} en ${variable}=${x}`);
    }
    return { x, before, after };
  });
  return { first, latex, second, values };
}

const input = fs.readFileSync(0, "utf8");
const requests = JSON.parse(input) as Request[];
const results = requests.map((request) => {
  switch (request.op) {
    case "eval":
      return { ok: true, value: evalUserExpression(request.expr) };
    case "derivativeOfIntegral":
      return {
        ok: true,
        expression: derivativeOfIntegral(request.expr, request.variable ?? "x"),
      };
    case "rootsResiduals":
      return {
        ok: true,
        roots: rootsResiduals(request.expr, request.variable ?? "x"),
      };
    case "roundtrip":
      return {
        ok: true,
        ...roundtrip(request.expr, request.variable ?? "x", request.samples),
      };
  }
});
process.stdout.write(JSON.stringify(results));
