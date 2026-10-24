import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { latexToBackendSyntax } from "../components/NaturalMathField";
const row = readFileSync("../qa/certification/syntax309_cases.jsonl", "utf8").trim().split("\n").map(s => JSON.parse(s)).find(r => r.id === "SY-R-08");
describe("SY-R-08 complex binomial conversion", () => {
 it("preserves the original real and imaginary coefficients", () => {
  expect(row.entrada).toBe("1+2i");
  expect(row.esperado).toBe("1+2i");
  const actual = latexToBackendSyntax(row.entrada);
  console.log("SY-R-08 converted", actual);
  expect(actual.trim()).toMatch(/^1\s*\+\s*2\s*\*?\s*i$/);
 });
 it.each([
  ["3-4i", /^3\s*-\s*4\s*\*?\s*i$/],
  ["-2+3i", /^-2\s*\+\s*3\s*\*?\s*i$/],
 ])("preserves both coefficients and signs of %s", (source, expected) => {
  expect(latexToBackendSyntax(source).trim()).toMatch(expected);
 });
});
