import { describe, expect, it } from "vitest";
import { latexToBackendSyntax } from "./NaturalMathField";

describe("SY-X-04: 500 explicit x addends", () => {
  it("preserves all 500 addends rather than pre-simplifying to 500*x", () => {
    const source = Array(500).fill("x").join("+");
    expect(source).toHaveLength(999);
    const converted = latexToBackendSyntax(source);
    const normalized = converted.replace(/\s+/g, "");
    expect(normalized).toBe(source);
    expect(normalized.split("+")).toHaveLength(500);
  });

  it("preserves whitespace-separated addends without truncation", () => {
    const value = Array(500).fill("x").join(" + ");
    const actual = latexToBackendSyntax(value);
    const compact = actual.replace(/\s+/g, "");
    expect(compact).toBe(Array(500).fill("x").join("+"));
  });

  it("does not retain a previous long input after converting a shorter expression", () => {
    const source = Array(500).fill("x").join("+");
    latexToBackendSyntax(source);
    expect(latexToBackendSyntax("2+3").replace(/\s+/g, "")).toBe("2+3");
  });
});
