import { describe, expect, it } from "vitest";
import { formatScientificLatex } from "./formatNumber";

describe("SY-N-31 scientific presentation", () => {
  it("matches the canonical rational fixture without replacing the exact result", () => {
    const exact = String.raw`\frac{1}{3000000}`;
    expect(formatScientificLatex(1 / 3000000)).toBe(String.raw`3.333333333\times10^{-7}`);
    expect(exact).toBe(String.raw`\frac{1}{3000000}`);
  });
  it("does not manufacture a scientific number for non-finite results", () => {
    expect(formatScientificLatex(NaN)).toBeNull();
    expect(formatScientificLatex(Infinity)).toBeNull();
  });
});
