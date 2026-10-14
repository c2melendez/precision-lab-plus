import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { latexToBackendSyntax } from "../components/NaturalMathField";

const rows = Object.fromEntries(readFileSync("../qa/certification/syntax309_cases.jsonl", "utf8").trim().split("\n").map(line => {
  const row = JSON.parse(line);
  return [row.id, row];
}));

describe("Syntax309 SY-E-11..13 original source before Plus conversion", () => {
  it("rejects an ungrouped double superscript with a clear error", () => {
    const row = rows["SY-E-11"];
    expect(row.operacion).toBe("error");
    expect(row.entrada).toBe("x^{2}^{3}");
    expect(() => latexToBackendSyntax(row.entrada)).toThrowError(/superíndice|exponente/i);
  });
  it.each(["SY-E-09", "SY-E-10"])("%s preserves explicit grouping", id => {
    expect(() => latexToBackendSyntax(rows[id].entrada)).not.toThrow();
  });
  it.each(["x^{2} ^{3}", "x^{2^{3}}^{4}", "x^{y^{2}^{3}}"])("rejects repeated superscripts in %s", input => {
    expect(() => latexToBackendSyntax(input)).toThrowError(/superíndice|exponente/i);
  });

  it("SY-E-12: rejects the official empty exponent with a clear error", () => {
    const row = rows["SY-E-12"];
    expect(row.operacion).toBe("error");
    expect(row.entrada).toBe("x^{}");
    expect(() => latexToBackendSyntax(row.entrada)).toThrowError(/vacío|vacio|exponente/i);
  });
  it("SY-E-13: rejects the official exponent without a base", () => {
    const row = rows["SY-E-13"];
    expect(row.operacion).toBe("error");
    expect(row.entrada).toBe("^{2}");
    expect(() => latexToBackendSyntax(row.entrada)).toThrowError(/base|operando|izquierdo/i);
  });
  it.each(["x^{0}", "2^{0}", "x^{-1}", "2^{3^{2}}", "(x^{2})^{3}"])("preserves the valid exponent %s", input => {
    expect(() => latexToBackendSyntax(input)).not.toThrow();
  });

});
