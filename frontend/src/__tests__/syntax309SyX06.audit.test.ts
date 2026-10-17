import { readFileSync } from "node:fs";
import { expect, it } from "vitest";
import { latexToBackendSyntax } from "../components/NaturalMathField";
const row = readFileSync("../qa/certification/syntax309_cases.jsonl", "utf8")
  .trim().split("\n").map((line) => JSON.parse(line)).find((entry) => entry.id === "SY-X-06");

it("preserves the full10000-character expansion before backend length validation", () => {
  expect(row.entrada).toBe(String.raw`\text{(entrada de 10 000 caracteres)}`);
  expect(row.esperado).toBe("procesada sin bloquear, o rechazada con aviso de longitud");
  const source = "1+".repeat(4999) + "11";
  expect(source).toHaveLength(10000);
  expect(latexToBackendSyntax(source)).toBe(source);
}, 15000);
