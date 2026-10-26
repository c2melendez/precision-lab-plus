import { describe, expect, it } from "vitest";
import { latexToBackendSyntax } from "../components/NaturalMathField";

function compact(input: string): string {
  return latexToBackendSyntax(input).replace(/\\s+/g, "");
}

function expectNoTeX(input: string): string {
  const out = compact(input);
  expect(out.length).toBeGreaterThan(0);
  expect(out).not.toContain("\\");
  return out;
}

describe("IN625 Parte A / A2 Delimitadores y valor absoluto — UI → backend", () => {
  const noResidualCases: Array<[string, string]> = [
    ["EN-DL-01", "\\left(x+1\\right)^{2}"],
    ["EN-DL-02", "\\left[x+1\\right]^{2}"],
    ["EN-DL-04", "\\bigl(x+1\\bigr)^{2}"],
    ["EN-DL-05", "\\Bigl(\\frac{1}{2}\\Bigr)^{3}"],
    ["EN-DL-06", "\\mleft(x+1\\mright)^{2}"],
    ["EN-DL-07", "((x))"],
    ["EN-DL-08", "\\left(2+3\\right)\\left(4-1\\right)"],
    ["EN-DL-09", "\\left(\\frac{1}{2}\\right)^{-2}"],
    ["EN-DL-10", "\\lvert x-1\\rvert"],
    ["EN-DL-11", "|x-1|"],
    ["EN-DL-12", "\\left| x-1 \\right|"],
    ["EN-DL-13", "||x|-1|"],
    ["EN-DL-14", "\\lvert\\lvert x\\rvert-1\\rvert"],
    ["EN-DL-15", "\\lvert x\\rvert\\lvert y\\rvert"],
    ["EN-DL-17", "\\lceil 2.1\\rceil"],
  ];

  for (const [id, input] of noResidualCases) {
    it(`${id}: elimina macros TeX residuales`, () => { expectNoTeX(input); });
  }

  it("EN-DL-01/02/04/06 convergen a agrupación equivalente", () => {
    for (const input of [
      "\\left(x+1\\right)^{2}",
      "\\left[x+1\\right]^{2}",
      "\\bigl(x+1\\bigr)^{2}",
      "\\mleft(x+1\\mright)^{2}",
    ]) {
      const out = expectNoTeX(input);
      expect(out).toContain("x+1");
      expect(out).toMatch(/\^/);
    }
  });

  it("EN-DL-10/11/12 convergen a abs(...)", () => {
    for (const input of ["\\lvert x-1\\rvert", "|x-1|", "\\left| x-1 \\right|"]) {
      expect(expectNoTeX(input)).toContain("abs(");
    }
  });

  it("EN-DL-13/14 preservan valor absoluto anidado", () => {
    for (const input of ["||x|-1|", "\\lvert\\lvert x\\rvert-1\\rvert"]) {
      const out = expectNoTeX(input);
      expect((out.match(/abs\(/g) ?? []).length).toBeGreaterThanOrEqual(2);
    }
  });

  it("EN-DL-15 conserva el producto de dos valores absolutos", () => {
    const out = expectNoTeX("\\lvert x\\rvert\\lvert y\\rvert");
    expect((out.match(/abs\(/g) ?? []).length).toBeGreaterThanOrEqual(2);
  });

  it("EN-DL-16 floor: ambas entradas quedan sin TeX residual", () => {
    expectNoTeX("\\lfloor 2.7\\rfloor");
    expectNoTeX("\\lfloor -2.5\\rfloor");
  });

  // EN-DL-18/19: intervalos; EN-DL-20: norma matricial.
  // Se reservan para observación L2/feature-dependent.
});
