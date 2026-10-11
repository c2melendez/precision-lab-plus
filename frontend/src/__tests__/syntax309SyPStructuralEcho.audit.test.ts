import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
const source = readFileSync("../qa/certification/syntax309_sy_p_cases.jsonl", "utf8");
import { latexToBackendSyntax } from "../components/NaturalMathField";

type Row = { id: string; operacion: string; entrada: string };
const rows: Row[] = source.trim().split("\n").map(line => JSON.parse(line) as Row);
const byId = Object.fromEntries(rows.map(row => [row.id, row]));
const convert = (id: string) => latexToBackendSyntax(byId[id].entrada).replace(/\s+/g, "");

describe("Syntax309 SY-P — Plus frontend conversion structural witnesses", () => {
  it("uses official interpretation rows (including metadata-only 24/25)", () => {
    for (const id of ["SY-P-03", "SY-P-24", "SY-P-25", "SY-P-27", "SY-P-28"]) {
      expect(byId[id]?.operacion).toBe("interpretacion");
    }
  });
  it("SY-P-03: preserves trig function and coefficient in backend input", () => {
    const out = convert("SY-P-03").toLowerCase();
    expect(out).toContain("sin");
    expect(out).toContain("3");
    expect(out).toContain("x");
    expect(out).not.toContain("\\sin");
  });
  it("SY-P-27: preserves coefficient and exponential variable", () => {
    const out = convert("SY-P-27").toLowerCase();
    expect(out).toContain("2");
    expect(out).toContain("e");
    expect(out).toContain("x");
    expect(out).toMatch(/\^|\*\*/);
  });
  it("SY-P-28: preserves independent x and exponent 2", () => {
    const out = convert("SY-P-28").toLowerCase();
    expect(out).toContain("e");
    expect(out).toContain("2");
    expect(out).toContain("x");
    expect(out).toMatch(/\^|\*\*/);
  });

  it("SY-P-24: concatenated xy preserves two operand letters", () => {
    const out = convert("SY-P-24").toLowerCase();
    expect(out).toMatch(/x\s*\*?\s*y/);
    expect(out).not.toMatch(/\bxy\s*\(/);
  });
  it("SY-P-25: concatenated xyz preserves all operand letters in order", () => {
    const out = convert("SY-P-25").toLowerCase();
    expect(out).toMatch(/x\s*\*?\s*y\s*\*?\s*z/);
    expect(out).not.toMatch(/\bxyz\s*\(/);
  });
});
