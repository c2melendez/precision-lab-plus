import { describe, expect, it } from "vitest";
import { parseFracLatex, toMixedFracLatex } from "../components/fractionDisplay";

describe("parseFracLatex (formato real de SymPy, verificado contra el paquete)", () => {
  it("fracción positiva simple", () => {
    expect(parseFracLatex("\\frac{57}{2}")).toEqual({ n: 57, d: 2 });
  });

  it("fracción negativa (SymPy agrega un espacio tras el signo)", () => {
    expect(parseFracLatex("- \\frac{57}{2}")).toEqual({ n: -57, d: 2 });
  });

  it("fracción negativa propia", () => {
    expect(parseFracLatex("- \\frac{1}{2}")).toEqual({ n: -1, d: 2 });
  });

  it("devuelve null para algo que no es \\frac{}{}", () => {
    expect(parseFracLatex("\\sqrt{7}")).toBeNull();
    expect(parseFracLatex("42")).toBeNull();
  });

  it("recorta espacios exteriores y conserva el signo sin espacio", () => {
    expect(parseFracLatex("  -\\frac{13}{7}  ")).toEqual({ n: -13, d: 7 });
    expect(parseFracLatex(" \\frac{0}{3} ")).toEqual({ n: 0, d: 3 });
  });

  it.each(["\\frac{3}{0}", "\\frac{x}{2}", "\\frac{3}{-2}", "\\frac{1.5}{2}", "prefix\\frac{3}{2}", "\\frac{3}{2}+1"])
  ("no ofrece una fracción mixta para LaTeX no racional o incompleto: %s", latex => {
    expect(parseFracLatex(latex)).toBeNull();
  });
});

describe("toMixedFracLatex", () => {
  it("fracción impropia positiva -> mixta", () => {
    expect(toMixedFracLatex(57, 2)).toBe("28\\frac{1}{2}");
  });

  it("fracción impropia negativa -> mixta con signo", () => {
    expect(toMixedFracLatex(-57, 2)).toBe("-28\\frac{1}{2}");
  });

  it("6/5 (el caso reportado por el usuario) -> 1 1/5", () => {
    expect(toMixedFracLatex(6, 5)).toBe("1\\frac{1}{5}");
  });

  it("fracción propia -> null (no hay forma mixta distinta)", () => {
    expect(toMixedFracLatex(1, 2)).toBeNull();
    expect(toMixedFracLatex(-1, 2)).toBeNull();
  });

  it("caso límite: numerador igual al denominador (raro, SymPy ya lo simplifica antes)", () => {
    expect(toMixedFracLatex(5, 5)).toBe("1");
  });

  it("conserva enteros negativos y omite la vista mixta para cero", () => {
    expect(toMixedFracLatex(-12, 3)).toBe("-4");
    expect(toMixedFracLatex(0, 3)).toBeNull();
    expect(toMixedFracLatex(7, 3)).toBe("2\\frac{1}{3}");
  });
});
