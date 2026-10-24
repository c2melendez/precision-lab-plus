import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { latexToBackendSyntax } from "../components/NaturalMathField";
const rows = readFileSync("../qa/certification/syntax309_cases.jsonl", "utf8").trim().split("\n").map(s => JSON.parse(s));
describe("SY-S-20 explicit degrees preserve sine argument", () => {
 it("translates the official source to a single radians conversion", () => {
  const row = rows.find(r => r.id === "SY-S-20");
  expect(row.entrada).toBe("sen(30°)");
  expect(row.esperado).toBe(String.raw`\frac{1}{2}`);
  const actual = latexToBackendSyntax(row.entrada).replace(/\s/g, "");
  console.log("SY-S-20 actual translation", actual);
  expect(actual).toBe("sin(((30)*pi/180))");
  expect((actual.match(/pi/g) ?? []).length).toBe(1);
 });
 it.each([
  String.raw`\operatorname{sen}\left(30^{\circ}\right)`,
  String.raw`\operatorname{sen}\left(30^\circ\right)`,
  String.raw`\operatorname{sen}\left(30\degree\right)`,
 ])("agrees with native degree serialization %s", source => {
  expect(latexToBackendSyntax(source).replace(/\s/g, "")).toBe("sin(((30)*pi/180))");
 });
});
