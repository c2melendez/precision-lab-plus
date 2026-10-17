import { expect, it } from "vitest";
import { latexToBackendSyntax } from "../components/NaturalMathField";
it("preserves negative square roots for the existing complex-capable evaluator", () => {
  expect(latexToBackendSyntax(String.raw`\sqrt{-1}`)).toBe("sqrt(-1)");
  expect(latexToBackendSyntax("i")).toBe("i");
  expect(latexToBackendSyntax("i^2")).toBe("i^2");
  expect(latexToBackendSyntax(String.raw`\sqrt{-4}`)).toBe("sqrt(-4)");
});
