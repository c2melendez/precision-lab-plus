import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { latexToBackendSyntax } from "../components/NaturalMathField";
const rows = readFileSync("../qa/certification/syntax309_cases.jsonl", "utf8").trim().split("\n").map(s => JSON.parse(s));
describe("SY-S-17 official plain-text function", () => {
 it("preserves the function and its complete argument", () => {
  const row = rows.find(r => r.id === "SY-S-17");
  expect(row.entrada).toBe("abs(-3)");
  expect(row.esperado).toBe("3");
  expect(latexToBackendSyntax(row.entrada).replace(/\s/g, "")).toBe("abs(-3)");
  expect(latexToBackendSyntax(row.esperado)).toBe("3");
 });
});
