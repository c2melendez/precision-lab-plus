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
