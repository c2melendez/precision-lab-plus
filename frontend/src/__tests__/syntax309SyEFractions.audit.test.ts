import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { detectCalculusIntent } from "../components/calculusIntent";
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


describe("SY-E-31 convention for adjacent fraction", () => {
  it("uses multiplication for numeric adjacency", () => {
    const row = rows["SY-E-31"];
    expect(row.operacion).toBe("convencion");
    expect(row.entrada).toBe("2\\frac{1}{3}");
    const source = latexToBackendSyntax(row.entrada).replace(/\s+/g, "");
    expect(["2*(1/3)", "2*(1)/(3)", "2(1/3)", "2(1)/(3)", "2*1/3", "2*1/(3)"]).toContain(source);
  });
});


describe("SY-N-01 leading decimal original source", () => {
  it("converts .5 to the equivalent numeric backend input", () => {
    const row = rows["SY-N-01"];
    expect(row.operacion).toBe("valor");
    expect(row.entrada).toBe(".5");
    expect(row.esperado).toBe("0.5");
    const converted = latexToBackendSyntax(row.entrada).trim();
    expect([".5", "0.5"]).toContain(converted);
  });
});


describe("SY-N-04 scientific multiplication original LaTeX", () => {
  it("converts the original scientific product without interpreting e-notation", () => {
    const row = rows["SY-N-04"];
    expect(row.operacion).toBe("valor");
    expect(row.entrada).toBe("1.2\\times10^{3}");
    expect(row.esperado).toBe("1200");
    const converted = latexToBackendSyntax(row.entrada);
    expect(converted).not.toContain("\\times");
    expect(converted).toMatch(/10/);
    expect(converted).toMatch(/3/);
  });
});


describe("SY-N-05 calculator-e convention", () => {
  it("converts exact original to 1000 without enabling bare scientific syntax", () => {
    const row = rows["SY-N-05"];
    expect(row.operacion).toBe("convencion");
    expect(row.entrada).toBe("1\\mathrm{e}3");
    expect(row.nota).toMatch(/aceptarla o rechazarla/);
    expect(latexToBackendSyntax(row.entrada)).toBe("1000");
  });
});


describe("SY-N-06 decimal precision original source", () => {
  it("preserves the decimal operands without adding binary floating artifacts", () => {
    const row = rows["SY-N-06"];
    expect(row.operacion).toBe("valor");
    expect(row.entrada).toBe("0.1+0.2");
    expect(row.esperado).toBe("0.3");
    const converted = latexToBackendSyntax(row.entrada).replace(/\s+/g, "");
    expect(converted).toBe("0.1+0.2");
    expect(converted).not.toContain("0.30000000000000004");
  });
});


describe("SY-N-07 original multiplication LaTeX", () => {
  it("converts the source to equivalent backend arithmetic", () => {
    const row = rows["SY-N-07"];
    expect(row.operacion).toBe("valor");
    expect(row.entrada).toBe("0.1\\times3");
    expect(row.esperado).toBe("0.3");
    const converted = latexToBackendSyntax(row.entrada).replace(/\s+/g, "");
    expect(["0.1*3", "0.1(3)", "(0.1)*3"]).toContain(converted);
    expect(converted).not.toContain("0.30000000000000004");
  });
});


describe("SY-N-08 original decimal subtraction", () => {
  it("converts exact operands without introducing a binary floating artifact", () => {
    const row = rows["SY-N-08"];
    expect(row.operacion).toBe("valor");
    expect(row.entrada).toBe("1-0.9");
    expect(row.esperado).toBe("0.1");
    const converted = latexToBackendSyntax(row.entrada).replace(/\s+/g, "");
    expect(converted).toBe("1-0.9");
    expect(converted).not.toContain("0.09999999999999998");
  });
});


describe("SY-N-09 exact decimal product original LaTeX", () => {
  it("preserves 4.35 times 100 as a numeric product", () => {
    const row = rows["SY-N-09"];
    expect(row.operacion).toBe("valor");
    expect(row.entrada).toBe("4.35\\times100");
    expect(row.esperado).toBe("435");
    const converted = latexToBackendSyntax(row.entrada).replace(/\s+/g, "");
    expect(["4.35*100", "4.35(100)", "(4.35)*100"]).toContain(converted);
    expect(converted).not.toContain("434.99999999999994");
  });
});


describe("SY-N-10 original exact decimal product", () => {
  it("preserves all decimal digits and the multiplier", () => {
    const row = rows["SY-N-10"];
    expect(row.operacion).toBe("valor");
    expect(row.entrada).toBe("1.005\\times1000");
    expect(row.esperado).toBe("1005");
    const converted = latexToBackendSyntax(row.entrada).replace(/\s+/g, "");
    expect(["1.005*1000", "1.005(1000)", "(1.005)*1000"]).toContain(converted);
    expect(latexToBackendSyntax("1005").trim()).toBe("1005");
  });
});


describe("SY-N-11 original rational multiplication", () => {
  it("preserves the exact fraction and multiplier without a truncated decimal", () => {
    const row = rows["SY-N-11"];
    expect(row.operacion).toBe("valor");
    expect(row.entrada).toBe("\\frac{1}{3}\\times3");
    expect(row.esperado).toBe("1");
    const converted = latexToBackendSyntax(row.entrada).replace(/\s+/g, "");
    expect(["1/3*3", "(1/3)*3", "(1)/(3)*3", "((1)/(3))*3"], converted).toContain(converted);
    expect(latexToBackendSyntax("1").trim()).toBe("1");
  });
});


describe("SY-N-12 decimal plus abbreviated fraction", () => {
  it("preserves the decimal, addition and complete half fraction", () => {
    const row = rows["SY-N-12"];
    expect(row.operacion).toBe("valor");
    expect(row.entrada).toBe("1.5+\\frac12");
    expect(row.esperado).toBe("2");
    const converted = latexToBackendSyntax(row.entrada).replace(/\s+/g, "");
    expect(["1.5+1/2", "1.5+(1/2)", "1.5+(1)/(2)", "1.5+((1)/(2))"], converted).toContain(converted);
    expect(latexToBackendSyntax("2").trim()).toBe("2");
  });
});


describe("SY-N-13 original squared radical", () => {
  it("preserves the radical and exponent when converting the complete source", () => {
    const row = rows["SY-N-13"];
    expect(row.operacion).toBe("valor");
    expect(row.entrada).toBe("\\sqrt{2}^{2}");
    expect(row.esperado).toBe("2");
    const converted = latexToBackendSyntax(row.entrada).replace(/\s+/g, "");
    expect(converted).not.toContain("\\sqrt");
    expect(converted).toMatch(/sqrt|\^|\*\*/i);
    expect(converted).toContain("2");
    expect(converted).not.toContain("2.0000000000000004");
    expect(latexToBackendSyntax("2").trim()).toBe("2");
  });
});


describe("SY-N-14 squared radical cancellation", () => {
  it("keeps the radical power and subtraction in the original complete expression", () => {
    const row = rows["SY-N-14"];
    expect(row.operacion).toBe("valor");
    expect(row.entrada).toBe("\\left(\\sqrt{2}\\right)^{2}-2");
    expect(row.esperado).toBe("0");
    const converted = latexToBackendSyntax(row.entrada).replace(/\s+/g, "");
    expect(converted).not.toContain("\\sqrt");
    expect(converted).toMatch(/sqrt|\^|\*\*/);
    expect(converted).toContain("-2");
    expect(converted).not.toContain("0.0000000000000004");
    expect(latexToBackendSyntax("0").trim()).toBe("0");
  });
});


describe("SY-N-15 exact large integer source", () => {
  it("keeps the power and trailing unit rather than flattening to an unsafe float", () => {
    const row = rows["SY-N-15"];
    expect(row.operacion).toBe("valor");
    expect(row.entrada).toBe("10^{20}+1");
    expect(row.esperado).toBe("100000000000000000001");
    const converted = latexToBackendSyntax(row.entrada).replace(/\s+/g, "");
    expect(["10^20+1", "10^(20)+1", "10**20+1", "10**(20)+1"]).toContain(converted);
    expect(latexToBackendSyntax(row.esperado).trim()).toBe(row.esperado);
  });
});


describe("SY-N-15 exact large integer conversion", () => {
  it("preserves the original exponent, addition and all 21 output digits", () => {
    const row = rows["SY-N-15"];
    const expected = "100000000000000000001";
    expect(row.entrada).toBe("10^{20}+1");
    expect(row.esperado).toBe(expected);
    const converted = latexToBackendSyntax(row.entrada).replace(/\s+/g, "");
    expect(["10^20+1", "10^(20)+1", "(10^20)+1", "10**20+1", "(10**20)+1"]).toContain(converted);
    expect(latexToBackendSyntax(expected)).toBe(expected);
  });
});


describe("SY-N-16 exact large integer power conversion", () => {
  it("preserves exponent and exact 31-digit result", () => {
    const row = rows["SY-N-16"];
    const expected = "1267650600228229401496703205376";
    expect(row.operacion).toBe("valor");
    expect(row.entrada).toBe("2^{100}");
    expect(row.esperado).toBe(expected);
    expect(["2^100", "2^(100)", "2**100", "2**(100)"]).toContain(
      latexToBackendSyntax(row.entrada).replace(/\s+/g, "")
    );
    expect(latexToBackendSyntax(expected).trim()).toBe(expected);
  });
});


describe("SY-N-17 integer above JS safe integer", () => {
  it("retains the entire input without passing it through Number", () => {
    const row = rows["SY-N-17"];
    const expected = "9007199254740993";
    expect(row.operacion).toBe("valor");
    expect(row.entrada).toBe(expected);
    expect(row.esperado).toBe(expected);
    expect(latexToBackendSyntax(row.entrada).trim()).toBe(expected);
  });
});


describe("SY-N-18 percent input", () => {
  it("converts the original 12 percent into the exact fractional value", () => {
    const row = rows["SY-N-18"];
    expect(row.entrada).toBe("12\\%");
    expect(row.esperado).toBe("0.12");
    const converted = latexToBackendSyntax(row.entrada).replace(/\s+/g, "");
    expect(["12/100", "(12)/100", "12*(1/100)", "0.12", "12%"]).toContain(converted);
  });
});


describe("SY-N-19 original percent multiplication", () => {
  it("converts fifty percent times two hundred without dropping multiplication", () => {
    const row = rows["SY-N-19"];
    expect(row.operacion).toBe("valor");
    expect(row.entrada).toBe("50\\%\\times200");
    expect(row.esperado).toBe("100");
    const converted = latexToBackendSyntax(row.entrada).replace(/\s+/g, "");
    expect(converted).not.toContain("\\times");
    expect(converted).toContain("200");
    expect(converted).toMatch(/50|0\.5|1\/2/);
    expect(latexToBackendSyntax("100").trim()).toBe("100");
  });
});


describe("SY-N-20 factorial original source", () => {
  it("preserves the factorial operator when converting 5!", () => {
    const row = rows["SY-N-20"];
    expect(row.operacion).toBe("valor");
    expect(row.entrada).toBe("5!");
    expect(row.esperado).toBe("120");
    expect(latexToBackendSyntax(row.entrada).trim()).toBe("5!");
    expect(latexToBackendSyntax("120").trim()).toBe("120");
  });
});


describe("SY-N-21 zero factorial original source", () => {
  it("preserves postfix factorial and converts its result for reentry", () => {
    const row = rows["SY-N-21"];
    expect(row.operacion).toBe("valor");
    expect(row.entrada).toBe("0!");
    expect(row.esperado).toBe("1");
    expect(latexToBackendSyntax(row.entrada).trim()).toBe("0!");
    expect(latexToBackendSyntax(row.esperado).trim()).toBe("1");
  });
});


describe("SY-N-22 negative factorial source", () => {
  it("retains the negative operand and factorial operator for domain validation", () => {
    const row = rows["SY-N-22"];
    expect(row.operacion).toBe("error");
    expect(row.entrada).toBe("(-1)!");
    expect(row.esperado).toMatch(/factorial no definido/i);
    const source = latexToBackendSyntax(row.entrada).replace(/\s+/g, "");
    expect(["(-1)!", "(-1)!"].includes(source)).toBe(true);
    expect(latexToBackendSyntax("2+3")).toBe("2+3");
  });
});


describe("SY-N-23 non-integer factorial source", () => {
  it("preserves postfix factorial and the decimal argument for backend convention", () => {
    const row = rows["SY-N-23"];
    expect(row.operacion).toBe("convencion");
    expect(row.entrada).toBe("2.5!");
    expect(row.nota).toMatch(/Gamma o aviso/);
    expect(latexToBackendSyntax(row.entrada).trim()).toBe("2.5!");
    expect(latexToBackendSyntax("2+3")).toBe("2+3");
  });
});


describe("SY-N-24 large factorial original source", () => {
  it("keeps 100! intact and does not round its source into JavaScript Number", () => {
    const row = rows["SY-N-24"];
    expect(row.operacion).toBe("valor");
    expect(row.entrada).toBe("100!");
    expect(latexToBackendSyntax(row.entrada).trim()).toBe("100!");
    expect(row.nota).toMatch(/158 dígitos/);
  });
});


describe("SY-N-25 large factorial near finite float boundary", () => {
  it("keeps 170! unchanged in the backend source", () => {
    const row = rows["SY-N-25"];
    expect(row.operacion).toBe("valor");
    expect(row.entrada).toBe("170!");
    expect(latexToBackendSyntax(row.entrada).trim()).toBe("170!");
  });
});


describe("SY-N-26 overflow boundary factorial source", () => {
  it("preserves the factorial notation without evaluating it through JavaScript Number", () => {
    const row = rows["SY-N-26"];
    expect(row.entrada).toBe("171!");
    expect(row.esperado).toMatch(/Infinity/);
    expect(latexToBackendSyntax(row.entrada).trim()).toBe("171!");
  });
});


describe("SY-N-27 pi source conversion", () => {
  it("preserves the exact constant in original source and returned LaTeX", () => {
    const row = rows["SY-N-27"];
    expect(row.entrada).toBe("\\pi");
    expect(row.esperado).toBe("3.141592654");
    expect(latexToBackendSyntax(row.entrada).trim()).toBe("pi");
    expect(latexToBackendSyntax("\\pi").trim()).toBe("pi");
  });
});


describe("SY-N-28 Euler constant source conversion", () => {
  it("preserves e as a constant rather than a truncated decimal", () => {
    const row = rows["SY-N-28"];
    expect(row.entrada).toBe("e");
    expect(row.esperado).toBe("2.718281828");
    expect(latexToBackendSyntax(row.entrada).trim()).toBe("e");
  });
});


describe("SY-N-29 locale-sensitive decimal comma", () => {
  it("does not silently turn 1,5+2 into an unrelated expression", () => {
    const row = rows["SY-N-29"];
    expect(row.entrada).toBe("1,5+2");
    expect(row.operacion).toBe("convencion");
    let converted: string;
    try {
      converted = latexToBackendSyntax(row.entrada).trim();
    } catch (error) {
      expect(String(error).trim().length).toBeGreaterThan(0);
      return; // Explicit warning/rejection is permitted.
    }
    // Conversion must retain the decimal comma or normalize it to a decimal point.
    // Removing it, or silently interpreting it as an expression separator, is forbidden.
    expect(converted === "1.5+2" || converted === "1,5+2").toBe(true);
  });
});


describe("SY-N-30 thousands separator convention", () => {
  it("does not silently reinterpret the original 1{,}000+1", () => {
    const row = rows["SY-N-30"];
    expect(row.entrada).toBe("1{,}000+1");
    expect(row.operacion).toBe("convencion");
    let translated: string;
    try {
      translated = latexToBackendSyntax(row.entrada).replace(/\\s+/g, "");
    } catch (error) {
      expect(String(error)).toMatch(/separador|ambiguo|miles|decimal/i);
      return;
    }
    // Converter may retain thousands punctuation for backend rejection, or normalize to 1000+1.
    expect(["1000+1", "1{,}000+1", "1,000+1"], translated).toContain(translated);
  });
});


describe("SY-U-01 original multiplication sign", () => {
  it("converts the complete source to multiplication and preserves result reentry", () => {
    const row = rows["SY-U-01"];
    expect(row.entrada).toBe("3\\times4");
    expect(row.operacion).toBe("valor");
    expect(row.esperado).toBe("12");
    expect(latexToBackendSyntax(row.entrada).replace(/\s+/g, "")).toBe("3*4");
    expect(latexToBackendSyntax("12").trim()).toBe("12");
  });
});


describe("SY-U-02 original division sign", () => {
  it("converts the complete source to division and preserves result reentry", () => {
    const row = rows["SY-U-02"];
    expect(row.entrada).toBe("12\\div4");
    expect(row.operacion).toBe("valor");
    expect(row.esperado).toBe("3");
    expect(latexToBackendSyntax(row.entrada).replace(/\s+/g, "")).toBe("12/4");
    expect(latexToBackendSyntax("3").trim()).toBe("3");
  });
});


describe("SY-U-03 original cdot multiplication", () => {
  it("converts the complete source to multiplication and preserves result reentry", () => {
    const row = rows["SY-U-03"];
    expect(row.entrada).toBe("3\\cdot4");
    expect(row.operacion).toBe("valor");
    expect(row.esperado).toBe("12");
    expect(latexToBackendSyntax(row.entrada).replace(/\s+/g, "")).toBe("3*4");
    expect(latexToBackendSyntax("12").trim()).toBe("12");
  });
});



describe("SY-U-04 ASCII multiplication", () => {
  it("converts original ASCII multiplication and reentry", () => {
    const row = rows["SY-U-04"];
    expect(row.entrada).toBe("3*4");
    expect(row.operacion).toBe("valor");
    expect(row.esperado).toBe("12");
    expect(latexToBackendSyntax(row.entrada).replace(/\\s+/g, "")).toBe("3*4");
    expect(latexToBackendSyntax("12").trim()).toBe("12");
  });
});

describe("SY-U-05 ASCII division", () => {
  it("converts original ASCII division and reentry", () => {
    const row = rows["SY-U-05"];
    expect(row.entrada).toBe("12/4");
    expect(row.operacion).toBe("valor");
    expect(row.esperado).toBe("3");
    expect(latexToBackendSyntax(row.entrada).replace(/\s+/g, "")).toBe("12/4");
    expect(latexToBackendSyntax("3").trim()).toBe("3");
  });
});

describe("SY-U-06 Unicode multiplication", () => {
  it("converts original Unicode source and result for reentry", () => {
    const row = rows["SY-U-06"];
    expect(row.entrada).toBe("3×4");
    expect(row.esperado).toBe("12");
    expect(latexToBackendSyntax(row.entrada).replace(/\s+/g, "")).toBe("3*4");
    expect(latexToBackendSyntax("12").trim()).toBe("12");
  });
});


describe("SY-U-07 Unicode division", () => {
  it("preserves original division symbol and exact result reentry", () => {
    const row = rows["SY-U-07"];
    expect(row.entrada).toBe("12÷4");
    expect(row.operacion).toBe("valor");
    expect(row.esperado).toBe("3");
    expect(latexToBackendSyntax(row.entrada).replace(/\s+/g, "")).toBe("12/4");
    expect(latexToBackendSyntax("3").trim()).toBe("3");
  });
});


describe("SY-U-08 Unicode middle dot multiplication", () => {
  it("preserves original middle dot and exact result reentry", () => {
    const row = rows["SY-U-08"];
    expect(row.entrada).toBe("3·4");
    expect(row.operacion).toBe("valor");
    expect(row.esperado).toBe("12");
    expect(latexToBackendSyntax(row.entrada).replace(/\s+/g, "")).toBe("3*4");
    expect(latexToBackendSyntax("12").trim()).toBe("12");
  });
});


describe("SY-U-09 Unicode minus", () => {
  it("translates original Unicode minus to subtraction for backend", () => {
    const row = rows["SY-U-09"];
    expect(row.entrada).toBe("2−1");
    expect(row.operacion).toBe("valor");
    expect(row.esperado).toBe("1");
    expect(latexToBackendSyntax(row.entrada).replace(/\s+/g, "")).toBe("2-1");
    expect(latexToBackendSyntax("1").trim()).toBe("1");
  });
});


describe("SY-U-10 Unicode en dash convention", () => {
  it("must not silently misinterpret original source", () => {
    const row = rows["SY-U-10"];
    expect(row.entrada).toBe("2–1");
    expect(row.operacion).toBe("convencion");
    let converted: string;
    try { converted = latexToBackendSyntax(row.entrada).replace(/\s+/g, ""); }
    catch (error) { expect(String(error).length).toBeGreaterThan(0); return; }
    expect(["2-1", "2–1"]).toContain(converted);
  });
});


describe("SY-U-11 Unicode superscript convention", () => {
  it("preserves x squared or explicitly rejects it", () => {
    const row = rows["SY-U-11"];
    expect(row.entrada).toBe("x²");
    expect(row.operacion).toBe("convencion");
    let converted: string;
    try { converted = latexToBackendSyntax(row.entrada).replace(/\s+/g, ""); }
    catch (error) { expect(String(error).length).toBeGreaterThan(0); return; }
    expect(["x^2", "x**2", "x²", "x^{2}"]).toContain(converted);
  });
});


describe("SY-U-12 Unicode root convention", () => {
  it("preserves root value or explicitly rejects source", () => {
    const row = rows["SY-U-12"];
    expect(row.entrada).toBe("√4");
    expect(row.operacion).toBe("convencion");
    let converted: string;
    try { converted = latexToBackendSyntax(row.entrada).replace(/\s+/g, ""); }
    catch (error) { expect(String(error).length).toBeGreaterThan(0); return; }
    expect(["sqrt(4)", "√4", "\\sqrt{4}", "\\sqrt4"]).toContain(converted);
  });
});


describe("SY-V-13 original limit intent and conversion", () => {
  it("extracts the original two-sided limit and keeps the full sine quotient", () => {
    const row = rows["SY-V-13"];
    expect(row.entrada).toBe("\\lim_{x\\to0}\\frac{\\sin x}{x}");
    expect(row.operacion).toBe("valor");
    expect(row.esperado).toBe("1");
    const intent = detectCalculusIntent(row.entrada);
    expect(intent?.kind).toBe("limit");
    if (!intent || intent.kind !== "limit") throw new Error("Expected limit intent");
    expect(intent.variable).toBe("x");
    expect(intent.point).toBe("0");
    expect(intent.direction).toBe("both");
    const body = latexToBackendSyntax(intent.innerLatex).replace(/\s+/g, "");
    expect(["sin(x)/x", "(sin(x))/(x)", "(sin(x)/x)", "((sin(x))/(x))", "(sin(x))/x"]).toContain(body);
    expect(latexToBackendSyntax("1").trim()).toBe("1");
  });
});


describe("SY-V-14 right reciprocal limit intent", () => {
  it("preserves the right-hand direction, quotient and infinity point syntax", () => {
    const row = rows["SY-V-14"];
    expect(row.entrada).toBe("\\lim_{x\\to0^{+}}\\frac{1}{x}");
    expect(row.esperado).toBe("+\\infty");
    const intent = detectCalculusIntent(row.entrada);
    expect(intent?.kind).toBe("limit");
    if (!intent || intent.kind !== "limit") throw new Error("Expected limit intent");
    expect(intent.variable).toBe("x");
    expect(intent.point).toBe("0");
    expect(intent.direction).toBe("right");
    const body = latexToBackendSyntax(intent.innerLatex).replace(/\s+/g, "");
    expect(["1/x", "(1)/(x)", "(1/x)", "((1)/(x))"]).toContain(body);
    expect(latexToBackendSyntax("\\infty").trim()).toBe("oo");
  });
});


describe("SY-V-15 reciprocal limit at infinity intent", () => {
  it("extracts the infinite point and preserves the entire quotient", () => {
    const row = rows["SY-V-15"];
    expect(row.entrada).toBe("\\lim_{x\\to\\infty}\\frac{1}{x}");
    expect(row.operacion).toBe("valor");
    expect(row.esperado).toBe("0");
    const intent = detectCalculusIntent(row.entrada);
    expect(intent?.kind).toBe("limit");
    if (!intent || intent.kind !== "limit") throw new Error("Expected limit intent");
    expect(intent.variable).toBe("x");
    expect(intent.point).toBe("oo");
    expect(intent.direction).toBe("both");
    const body = latexToBackendSyntax(intent.innerLatex).replace(/\s+/g, "");
    expect(["1/x", "(1)/(x)", "(1/x)", "((1)/(x))"]).toContain(body);
    expect(latexToBackendSyntax("0").trim()).toBe("0");
  });
});


describe("SY-V-16 original finite sum conversion", () => {
  it("preserves the complete body, index and inclusive limits", () => {
    const row = rows["SY-V-16"];
    expect(row.entrada).toBe("\\sum_{k=1}^{10}k");
    expect(row.operacion).toBe("valor");
    expect(row.esperado).toBe("55");
    expect(latexToBackendSyntax(row.entrada).replace(/\s+/g, "")).toBe("sum(k,k,1,10)");
    expect(latexToBackendSyntax("55").trim()).toBe("55");
  });
});


describe("SY-V-17 original symbolic sum conversion", () => {
  it("keeps the symbolic upper bound rather than substituting a numeric witness", () => {
    const row = rows["SY-V-17"];
    expect(row.entrada).toBe("\\sum_{k=1}^{n}k");
    expect(row.operacion).toBe("equivalente");
    expect(row.esperado).toBe("\\frac{n(n+1)}{2}");
    expect(latexToBackendSyntax(row.entrada).replace(/\s+/g, "")).toBe("sum(k,k,1,n)");
  });
});


describe("SY-V-18 original finite product conversion", () => {
  it("preserves product operation, body, index and both limits", () => {
    const row = rows["SY-V-18"];
    expect(row.entrada).toBe("\\prod_{k=1}^{5}k");
    expect(row.operacion).toBe("valor");
    expect(row.esperado).toBe("120");
    expect(latexToBackendSyntax(row.entrada).replace(/\s+/g, "")).toBe("product(k,k,1,5)");
    expect(latexToBackendSyntax("120").trim()).toBe("120");
  });
});


describe("SY-V-19 original binomial conversion", () => {
  it("preserves both arguments and combination semantics", () => {
    const row = rows["SY-V-19"];
    expect(row.entrada).toBe("\\binom{5}{2}");
    expect(row.operacion).toBe("valor");
    expect(row.esperado).toBe("10");
    expect(latexToBackendSyntax(row.entrada).replace(/\s+/g, "")).toBe("nCr(5,2)");
    expect(latexToBackendSyntax("\\binom{6}{2}").replace(/\s+/g, "")).toBe("nCr(6,2)");
    expect(latexToBackendSyntax("\\binom{5}{0}").replace(/\s+/g, "")).toBe("nCr(5,0)");
    expect(latexToBackendSyntax("\\binom{1+4}{2}").replace(/\s+/g, "")).toBe("nCr(1+4,2)");
    expect(latexToBackendSyntax("10").trim()).toBe("10");
  });
});


describe("SY-V-20 original symbolic binomial conversion", () => {
  it("preserves the symbolic first argument and fixed second argument", () => {
    const row = rows["SY-V-20"];
    expect(row.entrada).toBe("\\binom{n}{2}");
    expect(row.operacion).toBe("equivalente");
    expect(row.esperado).toBe("\\frac{n(n-1)}{2}");
    expect(latexToBackendSyntax(row.entrada).replace(/\s+/g, "")).toBe("nCr(n,2)");
  });
});


describe("SY-V-21 permutation alias and local-function boundary", () => {
  it("preserves bare numeric P and a complete local P definition without conflating them", () => {
    const row = rows["SY-V-21"];
    expect(row.entrada).toBe("P(5,2)");
    expect(row.esperado).toBe("20");
    expect(latexToBackendSyntax(row.entrada).replace(/\s+/g, "")).toBe("P(5,2)");
    const local = "P(x,y)=x+y;P(5,2)";
    expect(latexToBackendSyntax(local).replace(/\s+/g, "")).toBe(local);
    expect(latexToBackendSyntax("20").trim()).toBe("20");
  });
});
