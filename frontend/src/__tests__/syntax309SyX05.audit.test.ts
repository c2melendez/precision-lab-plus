import { readFileSync } from "node:fs";
import { expect, it } from "vitest";
import { latexToBackendSyntax } from "../components/NaturalMathField";

const row = readFileSync("../qa/certification/syntax309_cases.jsonl", "utf8")
  .trim().split("\n").map((line) => JSON.parse(line)).find((entry) => entry.id === "SY-X-05");

it("pins the descriptive fixture and expands exactly30 actual grouping levels", () => {
  expect(row.entrada).toBe(String.raw`\underbrace{(\cdots((1))\cdots)}_{30\text{ niveles}}`);
  expect(row.esperado).toBe("1");
  expect("(".repeat(30) + "1" + ")".repeat(30)).toHaveLength(61);
});

it.each(["1", "7", "2+3"])("preserves the30-level input %s through the converter", (inner) => {
  const source = "(".repeat(30) + inner + ")".repeat(30);
  expect(latexToBackendSyntax(source).replace(/\s/g, "")).toBe(source);
});
