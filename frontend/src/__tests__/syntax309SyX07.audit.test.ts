import { readFileSync } from "node:fs";
import { expect, it } from "vitest";
import { latexToBackendSyntax } from "../components/NaturalMathField";
const row = readFileSync("../qa/certification/syntax309_cases.jsonl", "utf8")
  .trim().split("\n").map((line) => JSON.parse(line)).find((entry) => entry.id === "SY-X-07");
it("pins the infinity-minus-infinity fixture and preserves its indeterminacy", () => {
  expect(row.entrada).toBe(String.raw`\infty-\infty`);
  expect(row.esperado).toBe("indeterminado: error claro");
  expect(() => latexToBackendSyntax(row.entrada)).toThrow(/indeterminad/i);
  expect(latexToBackendSyntax("2+3")).toBe("2+3");
});

it.each(["oo-oo", "∞-∞", "(oo)-(oo)", "(-oo)-(-oo)"])("rejects explicit infinite witness %s", (source) => {
  expect(() => latexToBackendSyntax(source)).toThrow(/indeterminad/i);
});

it.each(["3-3", "3-2"])("retains finite subtraction %s", (source) => {
  expect(latexToBackendSyntax(source)).toBe(source);
});
