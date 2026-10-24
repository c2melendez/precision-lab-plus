import { describe, expect, it } from "vitest";
import { latexToBackendSyntax } from "../components/NaturalMathField";
const norm = (s: string) => latexToBackendSyntax(s).replace(/\s+/g, "");

describe("IN625 F2b — Unicode 20..26", () => {
  it("EN-UC-20 invisibles", () => {
    for (const s of ["x\u200B^{2}", "x\uFEFF^{2}", "x\u00AD^{2}"]) {
      expect(norm(s)).toMatch(/x\^\(?2\)?/);
    }
  });

  it("EN-UC-21 cirílico х", () => {
    expect(norm("х+1")).toBe("x+1");
  });

  it("EN-UC-22 letras matemáticas", () => {
    expect(norm("𝑓(𝑥)=𝑥²")).toMatch(/f\(x\)=x\^\(?2\)?/);
  });

  it("EN-UC-23 ancho completo", () => {
    expect(norm("（x＋1）²")).toMatch(/\(x\+1\)\^\(?2\)?/);
    expect(norm("１２３")).toBe("123");
  });

  it("EN-UC-24 e/i matemáticas", () => {
    expect(norm("ⅇ^x")).toContain("e^x");
    expect(norm("ⅈ")).toBe("i");
  });

  it("EN-UC-25 integral unicode compacta", () => {
    expect(norm("∫₀¹x²dx")).toMatch(/integral|int/);
  });

  it.each(["x+1😀","x+漢"])("EN-UC-26 rechaza carácter inesperado: %s", (input) => {
    expect(() => latexToBackendSyntax(input)).toThrow(/Carácter inesperado.*U\+/);
  });
});
