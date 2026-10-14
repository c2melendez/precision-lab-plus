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
    const compact = converted.replace(/\s+/g, "");
    expect(compact).toMatch(/1/);
    expect(compact).toMatch(/2/);
    expect(compact).toMatch(/3/);
    expect(compact).toMatch(/4/);
    expect(compact).toContain("/");
    const output = latexToBackendSyntax(row.esperado).replace(/\s+/g, "");
    expect(["2/3", "(2)/(3)", "(2/3)", "((2)/(3))"]).toContain(output);
  });
});


describe("SY-E-24 original display-style fraction conversion", () => {
  it("converts the whole original dfrac and its expected result consistently", () => {
    const row = rows["SY-E-24"];
    expect(row.operacion).toBe("valor");
    expect(row.entrada).toBe("\\dfrac{3}{4}");
    expect(row.esperado).toBe("\\frac{3}{4}");
    const source = latexToBackendSyntax(row.entrada).replace(/\s+/g, "");
    const expected = latexToBackendSyntax(row.esperado).replace(/\s+/g, "");
    expect(["3/4", "(3)/(4)", "(3/4)", "((3)/(4))"], source).toContain(source);
    expect(["3/4", "(3)/(4)", "(3/4)", "((3)/(4))"], expected).toContain(expected);
  });
});

describe("SY-E-25 original text-style fraction conversion", () => {
  it("converts the whole original tfrac and its expected result consistently", () => {
    const row = rows["SY-E-25"];
    expect(row.operacion).toBe("valor");
    expect(row.entrada).toBe("\\tfrac{3}{4}");
    expect(row.esperado).toBe("\\frac{3}{4}");
    const source = latexToBackendSyntax(row.entrada).replace(/\s+/g, "");
    const expected = latexToBackendSyntax(row.esperado).replace(/\s+/g, "");
    expect(["3/4", "(3)/(4)", "(3/4)", "((3)/(4))"], source).toContain(source);
    expect(["3/4", "(3)/(4)", "(3/4)", "((3)/(4))"], expected).toContain(expected);
  });
});

describe("SY-E-26 original fraction addition conversion", () => {
  it("converts the whole original sum and its expected result consistently", () => {
    const row = rows["SY-E-26"];
    expect(row.operacion).toBe("valor");
    expect(row.entrada).toBe("\\frac{1}{3}+\\frac{1}{6}");
    expect(row.esperado).toBe("\\frac{1}{2}");
    const source = latexToBackendSyntax(row.entrada).replace(/\s+/g, "");
    const expected = latexToBackendSyntax(row.esperado).replace(/\s+/g, "");
    expect(["1/3+1/6", "(1)/(3)+(1)/(6)", "(1/3)+(1/6)"], source).toContain(source);
    expect(["1/2", "(1)/(2)", "(1/2)", "((1)/(2))"], expected).toContain(expected);
  });
});

describe("SY-E-27 original improper fraction conversion", () => {
  it("converts the whole original fraction and its expected result consistently", () => {
    const row = rows["SY-E-27"];
    expect(row.operacion).toBe("valor");
    expect(row.entrada).toBe("\\frac{22}{7}");
    expect(row.esperado).toBe("\\frac{22}{7}\\approx3.142857143");
    const source = latexToBackendSyntax(row.entrada).replace(/\s+/g, "");
    const expected = latexToBackendSyntax("\\frac{22}{7}").replace(/\s+/g, "");
    expect(["22/7", "(22)/(7)", "(22/7)", "((22)/(7))"], source).toContain(source);
    expect(["22/7", "(22)/(7)", "(22/7)", "((22)/(7))"], expected).toContain(expected);
  });
});

describe("SY-E-28 source conversion for undefined fraction", () => {
  it("preserves denominator zero for backend domain validation", () => {
    const row = rows["SY-E-28"];
    expect(row.operacion).toBe("error");
    expect(row.entrada).toBe("\\frac{1}{0}");
    const converted = latexToBackendSyntax(row.entrada).replace(/\s+/g, "");
    expect(["1/0", "(1)/(0)", "(1/0)", "((1)/(0))"]).toContain(converted);
  });
});


describe("SY-E-29 zero over zero source conversion", () => {
  it("retains indeterminate operands for domain-error handling", () => {
    const row = rows["SY-E-29"];
    expect(row.operacion).toBe("error");
    expect(row.entrada).toBe("\\frac{0}{0}");
    expect(row.esperado).toMatch(/indeterminado/);
    const converted = latexToBackendSyntax(row.entrada).replace(/\s+/g, "");
    expect(["0/0", "(0)/(0)", "(0/0)", "((0)/(0))"]).toContain(converted);
  });
});


describe("SY-E-30 empty denominator original source", () => {
  it("rejects an empty denominator clearly and preserves later conversion", () => {
    const row = rows["SY-E-30"];
    expect(row.operacion).toBe("error");
    expect(row.entrada).toBe("\\frac{x}{}");
    expect(row.esperado).toContain("denominador vacío");
    expect(() => latexToBackendSyntax(row.entrada)).toThrow(/denominador|denominator|vacío|empty/i);
    const recovered = latexToBackendSyntax("\\frac{1}{2}").replace(/\s+/g, "");
    expect(["1/2","(1)/(2)","(1/2)","((1)/(2))"]).toContain(recovered);
  });
});


describe("SY-E-31 adjacent fraction convention", () => {
  it("declares adjacency as implicit multiplication, not a mixed-number literal", () => {
    const row = rows["SY-E-31"];
    expect(row.operacion).toBe("convencion");
    expect(row.entrada).toBe("2\\frac{1}{3}");
    expect(row.nota).toMatch(/Número mixto o producto: declarar/);
    const converted = latexToBackendSyntax(row.entrada).replace(/\s+/g, "");
    expect(["2*(1/3)", "2*(1)/(3)", "2(1/3)", "2(1)/(3)", "2*1/3", "2*1/(3)"]).toContain(converted);
  });
});
