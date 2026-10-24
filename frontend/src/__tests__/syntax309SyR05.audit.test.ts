import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { latexToBackendSyntax } from "../components/NaturalMathField";
const row = readFileSync("../qa/certification/syntax309_cases.jsonl", "utf8").trim().split("\n").map(s => JSON.parse(s)).find(r => r.id === "SY-R-05");
describe("SY-R-05 original arsinh alias", () => {
 it("converts the untouched official source to the known asinh HTTP witness", () => {
  expect(row.entrada).toBe(String.raw`\operatorname{arsinh}\left(1\right)`);
  expect(row.esperado).toBe("0.881373587");
  const actual = latexToBackendSyntax(row.entrada);
  console.log("SY-R-05 converted", actual);
  expect(actual.trim()).toMatch(/^asinh\s*\(\s*1\s*\)$/);
 });
 it.each(["-1", "2"])("preserves another argument %s", value => {
  const actual = latexToBackendSyntax(String.raw`\operatorname{arsinh}\left(` + value + String.raw`\right)`);
  expect(actual.trim()).toMatch(new RegExp("^asinh\\s*\\(\\s*" + value + "\\s*\\)$"));
 });
});
