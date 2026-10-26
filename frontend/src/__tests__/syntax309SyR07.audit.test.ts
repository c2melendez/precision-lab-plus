import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { latexToBackendSyntax } from "../components/NaturalMathField";
const row = readFileSync("../qa/certification/syntax309_cases.jsonl", "utf8").trim().split("\n").map(s => JSON.parse(s)).find(r => r.id === "SY-R-07");
describe("SY-R-07 scientific notation conversion", () => {
 it("preserves the original coefficient, multiplication and negative exponent", () => {
  expect(row.entrada).toBe(String.raw`1.5\times10^{-7}`);
  expect(row.esperado).toBe("0.00000015");
  const actual = latexToBackendSyntax(row.entrada);
  console.log("SY-R-07 converted", actual);
  expect(actual.trim()).toMatch(/^1\.5\s*\*\s*10\s*\^\s*(?:\(\s*-7\s*\)|-7)$/);
 });
 it.each([
  [String.raw`2.5\times10^{-6}`, /^2\.5\s*\*\s*10\s*\^\s*(?:\(\s*-6\s*\)|-6)$/],
  [String.raw`-1.5\times10^{-7}`, /^-1\.5\s*\*\s*10\s*\^\s*(?:\(\s*-7\s*\)|-7)$/],
 ])("preserves the full arithmetic structure of %s", (source, expected) => {
  expect(latexToBackendSyntax(source).trim()).toMatch(expected);
 });
});
