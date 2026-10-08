import { describe, expect, it } from "vitest";
import { latexToBackendSyntax } from "../components/NaturalMathField";

const cases: Array<[string, string]> = [
  ["EN-FR-01", "\\frac{1}{2}"],
  ["EN-FR-02", "\\dfrac{1}{2}"],
  ["EN-FR-03", "\\tfrac{1}{2}"],
  ["EN-FR-04", "\\cfrac{1}{2}"],
  ["EN-FR-05", "{1\\over 2}"],
  ["EN-FR-06", "1/2"],
  ["EN-FR-07", "\\frac{x+1}{x-1}"],
  ["EN-FR-08", "(x+1)/(x-1)"],
  ["EN-FR-09", "x+1\\over x-1"],
  ["EN-FR-10", "\\frac12"],
  ["EN-FR-11", "\\frac1x"],
  ["EN-FR-12", "\\frac{12}3"],
  ["EN-FR-13", "\\frac123"],
  ["EN-FR-14", "\\frac{\\frac{1}{2}}{3}"],
  ["EN-FR-15", "\\frac{1}{\\frac{1}{2}}"],
  ["EN-FR-16", "\\frac{1}{\\frac{1}{x}+\\frac{1}{y}}"],
  ["EN-FR-17", "\\frac{1}{2}x"],
  ["EN-FR-18", "\\frac{1}{2x}"],
  ["EN-FR-19", "\\frac{a}{b}\\frac{c}{d}"],
  ["EN-FR-20", "x+1/x-1"],
  ["EN-FR-21", "\\frac{2}{3}+\\frac{3}{4}"],
  ["EN-FR-22", "\\frac{1.5}{2}"],
  ["EN-FR-23", "\\frac{\\pi}{2}"],
  ["EN-FR-24", "\\frac{\\sqrt{2}}{2}"],
];

describe("IN625 Parte A / A1 Fracciones — conversión UI → backend", () => {
  for (const [id, input] of cases) {
    it(`${id}: produce sintaxis backend no vacía y sin macros TeX residuales`, () => {
      const out = latexToBackendSyntax(input);
      expect(out.trim().length).toBeGreaterThan(0);
      expect(out).not.toContain("\\");
    });
  }

  it("EN-FR-01..06 convergen semánticamente a una mitad", () => {
    for (const input of [
      "\\frac{1}{2}",
      "\\dfrac{1}{2}",
      "\\tfrac{1}{2}",
      "\\cfrac{1}{2}",
      "{1\\over 2}",
      "1/2",
    ]) {
      const compact = latexToBackendSyntax(input).replace(/\\s+/g, "");
      expect(["(1)/(2)", "1/2"]).toContain(compact);
    }
  });

  it("EN-FR-09 conserva el agrupamiento global de \\over", () => {
    const compact = latexToBackendSyntax("x+1\\over x-1").replace(/\\s+/g, "");
    expect(["(x+1)/(x-1)", "(x+1)/(x-1)"]).toContain(compact);
  });

  it("EN-FR-13 no absorbe 3 en el denominador de \\frac123", () => {
    const compact = latexToBackendSyntax("\\frac123").replace(/\\s+/g, "");
    expect(compact).not.toContain("(23)");
    expect(compact).not.toBe("123");
    expect(compact).toContain("3");
  });
});
