import { describe, expect, it } from "vitest";
import { latexToBackendSyntax } from "../components/NaturalMathField";

function c(s: string): string {
  return latexToBackendSyntax(s).replace(/\s+/g, "");
}
function noTex(s: string): string {
  const out = c(s);
  expect(out.length).toBeGreaterThan(0);
  expect(out).not.toContain("\\");
  return out;
}

describe("IN625 Parte A / A4 Raíces — UI → backend", () => {
  const cases: Array<[string,string]> = [
    ["EN-RD-01","\\sqrt{4}"],
    ["EN-RD-02","\\sqrt4"],
    ["EN-RD-03","\\sqrt2"],
    ["EN-RD-04","\\sqrt x"],
    ["EN-RD-05","\\sqrt{x}y"],
    ["EN-RD-06","\\sqrt[3]{8}"],
    ["EN-RD-07","\\sqrt[3]{-8}"],
    ["EN-RD-08","\\sqrt[3]4"],
    ["EN-RD-09","\\sqrt[10]{1024}"],
    ["EN-RD-10","\\sqrt[n]{x}"],
    ["EN-RD-11","\\sqrt{\\sqrt{\\sqrt{256}}}"],
    ["EN-RD-12","2\\sqrt{3}"],
    ["EN-RD-13","\\sqrt{2}\\sqrt{3}"],
    ["EN-RD-14","x^{\\frac{1}{2}}"],
    ["EN-RD-15","\\sqrt{-4}"],
  ];
  for (const [id,input] of cases) {
    it(`${id}: elimina TeX residual y conserva estructura`, () => { noTex(input); });
  }

  it("EN-RD-06/08/09/10: raíces n-ésimas convergen a potencia 1/n", () => {
    for (const input of ["\\sqrt[3]{8}","\\sqrt[3]4","\\sqrt[10]{1024}","\\sqrt[n]{x}"]) {
      const out = noTex(input);
      expect(out).toMatch(/\*\*|\^/);
      expect(out).toMatch(/1\//);
    }
  });

  it("EN-RD-11: anidamiento conserva tres niveles", () => {
    const out = noTex("\\sqrt{\\sqrt{\\sqrt{256}}}");
    expect((out.match(/sqrt\(/g) ?? []).length).toBeGreaterThanOrEqual(3);
  });

  it("EN-RD-14: potencia 1/2 sigue siendo potencia explícita", () => {
    expect(noTex("x^{\\frac{1}{2}}")).toMatch(/\*\*|\^/);
  });
});
