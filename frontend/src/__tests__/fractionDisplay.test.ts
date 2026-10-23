import { describe, expect, it } from "vitest";
import { parseFracLatex, toMixedFracLatex } from "../components/fractionDisplay";

describe("parseFracLatex", () => {
  it("parses a positive improper fraction from SymPy latex", () => {
    expect(parseFracLatex("\\frac{57}{2}")).toEqual({ n: 57, d: 2 });
  });

  it("parses a negative fraction with the SymPy space after the sign", () => {
    expect(parseFracLatex("- \\frac{57}{2}")).toEqual({ n: -57, d: 2 });
  });

  it("parses a negative fraction without the space", () => {
    expect(parseFracLatex("-\\frac{3}{4}")).toEqual({ n: -3, d: 4 });
  });

  it("parses a proper positive fraction", () => {
    expect(parseFracLatex("\\frac{1}{2}")).toEqual({ n: 1, d: 2 });
  });

  it("trims surrounding whitespace", () => {
    expect(parseFracLatex("  \\frac{5}{3}  ")).toEqual({ n: 5, d: 3 });
  });

  it("rejects non-fraction latex", () => {
    expect(parseFracLatex("2")).toBeNull();
    expect(parseFracLatex("\\frac{a}{b}")).toBeNull();
    expect(parseFracLatex("")).toBeNull();
    expect(parseFracLatex("\\frac{1}{2} + 1")).toBeNull();
  });

  it("rejects division by zero", () => {
    expect(parseFracLatex("\\frac{1}{0}")).toBeNull();
  });
});

describe("toMixedFracLatex", () => {
  it("returns null for a proper fraction", () => {
    expect(toMixedFracLatex(3, 4)).toBeNull();
    expect(toMixedFracLatex(-1, 5)).toBeNull();
    expect(toMixedFracLatex(0, 2)).toBeNull();
  });

  it("converts an improper fraction to mixed form", () => {
    expect(toMixedFracLatex(57, 2)).toBe("28\\frac{1}{2}");
    expect(toMixedFracLatex(5, 3)).toBe("1\\frac{2}{3}");
  });

  it("preserves the negative sign on mixed form", () => {
    expect(toMixedFracLatex(-57, 2)).toBe("-28\\frac{1}{2}");
    expect(toMixedFracLatex(-5, 3)).toBe("-1\\frac{2}{3}");
  });

  it("collapses exact whole numbers", () => {
    expect(toMixedFracLatex(8, 2)).toBe("4");
    expect(toMixedFracLatex(-9, 3)).toBe("-3");
    expect(toMixedFracLatex(0, 1)).toBeNull();
  });

  it("boundary where abs(n) equals d becomes whole number 1", () => {
    expect(toMixedFracLatex(4, 4)).toBe("1");
    expect(toMixedFracLatex(-4, 4)).toBe("-1");
  });
});
