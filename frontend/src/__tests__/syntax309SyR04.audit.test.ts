import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { latexToBackendSyntax } from "../components/NaturalMathField";
const row = readFileSync("../qa/certification/syntax309_cases.jsonl", "utf8").trim().split("\n").map(s => JSON.parse(s)).find(r => r.id === "SY-R-04");
describe("SY-R-04 original inline binding is preserved for HTTP", () => {
 it("preserves body, assignment and official expected without treating con as variables", () => {
  expect(row.entrada).toBe(String.raw`e^{-x^{2}}\ \text{con}\ x=1`);
  expect(row.esperado).toBe("0.3678794412");
  const actual = latexToBackendSyntax(row.entrada);
  console.log("SY-R-04 converted", actual);
  const pieces = actual.split(/\s+con\s+/);
  expect(pieces).toHaveLength(2);
  expect(pieces[0].replace(/\s/g, "")).toBe("(e^(-x^2))");
  expect(pieces[1].replace(/[()\s]/g, "")).toBe("x=1");
 });
 it("keeps the negative exponent and another binding value", () => {
  const actual = latexToBackendSyntax(String.raw`2^{-y^{2}}\ \text{con}\ y=-2`);
  expect(actual).toMatch(/\scon\s/);
  expect(actual.split(/\s+con\s+/)[0].replace(/\s/g, "")).toBe("(2^(-y^2))");
  expect(actual.split(/\s+con\s+/)[1].replace(/[()\s]/g, "")).toBe("y=-2");
 });
});
