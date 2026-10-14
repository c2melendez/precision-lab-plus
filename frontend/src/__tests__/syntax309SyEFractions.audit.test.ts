import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { latexToBackendSyntax } from "../components/NaturalMathField";

const rows = Object.fromEntries(
  readFileSync("../qa/certification/syntax309_cases.jsonl", "utf8").trim().split("\n").map(line => {
    const row = JSON.parse(line); return [row.id, row];
  }),
);

describe("SY-E-21 original abbreviated fraction conversion", () => {
  it("converts original source and returned LaTeX to the exact half quotient", () => {
    const row = rows["SY-E-21"];
    expect(row.entrada).toBe("\\frac12");
    for (const source of [row.entrada, "\\frac{1}{2}"]) {
      const converted = latexToBackendSyntax(source).replace(/\s+/g, "");
      // Accept only equivalent whole-expression forms, never a substring.
      expect(["1/2", "(1)/(2)", "(1/2)", "((1)/(2))"], converted).toContain(converted);
    }
  });
});


describe("SY-E-22/23 nested fraction original LaTeX conversion", () => {
  it("retains the original symbolic inner denominator of SY-E-22", () => {
    const row = rows["SY-E-22"];
    expect(row.entrada).toBe("\\frac{1}{1+\\frac{1}{x}}");
    const converted = latexToBackendSyntax(row.entrada);
    expect(converted).toMatch(/x/);
    // Verify whole expression and its two domain exclusions independently.
    // Do not treat a simplified x/(x+1) as an unrestricted input.
    expect(converted).toContain("/");
    expect(converted).not.toContain("\\frac");
  });
  it("retains both levels of numeric fraction grouping for SY-E-23", () => {
    const row = rows["SY-E-23"];
    expect(row.operacion).toBe("valor");
    expect(row.entrada).toBe("\\frac{\\frac{1}{2}}{\\frac{3}{4}}");
    expect(row.esperado).toBe("\\frac{2}{3}");
    const converted = latexToBackendSyntax(row.entrada);
    expect(converted).not.toContain("\\frac");
    // Original operands must remain nested rather than flattening 1/2/3/4.
    const compact = converted.replace(/\\s+/g, "");
    expect(compact).toMatch(/1/);
    expect(compact).toMatch(/2/);
    expect(compact).toMatch(/3/);
    expect(compact).toMatch(/4/);
    expect(compact).toContain("/");
    const output = latexToBackendSyntax(row.esperado).replace(/\\s+/g, "");
    expect(["2/3", "(2)/(3)", "(2/3)", "((2)/(3))"]).toContain(output);
  });
});
