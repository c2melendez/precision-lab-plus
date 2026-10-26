import { describe, expect, it } from "vitest";
import { latexToBackendSyntax } from "../components/NaturalMathField";
const norm = (s: string) => latexToBackendSyntax(s).replace(/\s+/g, "");

describe("IN625 F2a — Unicode 01..19", () => {
  it("EN-UC-01/02 superíndices", () => {
    expect(norm("x²")).toContain("x^2");
    expect(norm("x³")).toContain("x^3");
    expect(norm("x¹⁰")).toMatch(/x\^\(?10\)?/);
  });
  it("EN-UC-03 exponentes negativos", () => {
    expect(norm("10⁻³")).toMatch(/10\^\(?-3\)?/);
    expect(norm("x⁻¹")).toMatch(/x\^\(?-1\)?/);
  });
  it("EN-UC-04 subíndices", () => {
    expect(norm("x₁")).toMatch(/x_?1/);
    expect(norm("x₁₀")).toMatch(/x_?\(?10\)?/);
  });
  it("EN-UC-05/06/07 raíces", () => {
    expect(norm("√4")).toContain("sqrt");
    expect(norm("√(x+1)")).toContain("sqrt");
    expect(norm("√x+1")).toContain("sqrt");
    expect(norm("∛8")).toContain("8");
    expect(norm("∜16")).toContain("16");
  });
  it("EN-UC-08/09 operadores", () => {
    expect(norm("2×3")).toBe("2*3");
    expect(norm("6÷3")).toBe("6/3");
    for (const s of ["2·3","2⋅3","2∙3","2∗3"]) expect(norm(s)).toBe("2*3");
  });
  it("EN-UC-10/11/12 signos menos", () => {
    expect(norm("5−3")).toBe("5-3");
    for (const s of ["5–3","5—3","5‐3","5‑3"]) expect(norm(s)).toBe("5-3");
    expect(norm("−5")).toBe("-5");
  });
  it("EN-UC-13 fracciones unicode", () => {
    expect(norm("½")).toMatch(/1\/2/);
    expect(norm("¼")).toMatch(/1\/4/);
    expect(norm("¾")).toMatch(/3\/4/);
  });
  it("EN-UC-14 constantes", () => {
    expect(norm("π")).toMatch(/pi/);
    expect(norm("θ")).toMatch(/theta/);
    expect(norm("∞")).toMatch(/inf|oo/);
  });
  it("EN-UC-15 relaciones", () => {
    expect(norm("x≤3")).toContain("<=");
    expect(norm("x≥3")).toContain(">=");
    expect(norm("x≠3")).toContain("!=");
  });
  it("EN-UC-16 ±", () => expect(norm("5±2")).toMatch(/pm|\+\-/));
  it("EN-UC-17 grados", () => {
    expect(norm("30°")).toContain("pi/180");
    expect(norm("sin 30°")).toContain("sin");
  });
  it("EN-UC-18 primas", () => {
    expect(norm("f’(x)")).toContain("f");
    expect(norm("f′(x)")).toContain("f");
  });
  it("EN-UC-19 espacios especiales", () => {
    expect(norm("2\u00A0+\u20093")).toBe("2+3");
    expect(norm("2\u202F+3")).toBe("2+3");
  });
});
