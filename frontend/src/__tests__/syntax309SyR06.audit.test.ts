import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { latexToBackendSyntax } from "../components/NaturalMathField";
const row = readFileSync("../qa/certification/syntax309_cases.jsonl", "utf8").trim().split("\n").map(s => JSON.parse(s)).find(r => r.id === "SY-R-06");
describe("SY-R-06 natural logarithm conversion", () => {
 it("preserves the untouched official source and its natural base", () => {
  expect(row.entrada).toBe(String.raw`\ln\left(2\right)`);
  expect(row.esperado).toBe("0.6931471806");
  const actual = latexToBackendSyntax(row.entrada);
  console.log("SY-R-06 converted", actual);
  expect(actual.trim()).toMatch(/^ln\s*\(\s*2\s*\)$/);
 });
 it.each([
  [String.raw`\ln\left(3\right)`, /^ln\s*\(\s*3\s*\)$/],
  [String.raw`\log\left(2\right)`, /^log\s*\(\s*2\s*\)$/],
 ])("keeps the function identifier of %s intact", (source, expected) => {
  expect(latexToBackendSyntax(source).trim()).toMatch(expected);
 });
});
