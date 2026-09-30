import { expect, it } from "vitest";
import { latexToBackendSyntax } from "../components/NaturalMathField";

it.each([
  "\\sin^{3}\\left(x\\right)",
  "\\sin\\left(x\\right)^{3}",
  "\\cos^{5}\\left(2x\\right)",
])("accepts trig powers in the editor: %s", (latex) => {
  const converted = latexToBackendSyntax(latex).replace(/\s+/g, "");
  expect(converted).toMatch(/sin|cos/);
  expect(converted.includes("^") || converted.includes("**")).toBe(true);
});
