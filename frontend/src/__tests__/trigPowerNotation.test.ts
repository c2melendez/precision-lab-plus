import { expect, it } from "vitest";
import { latexToBackendSyntax } from "../components/NaturalMathField";

it.each([
  "\\sin^{3}\\left(x\\right)",
  "\\sin\\left(x\\right)^{3}",
  "\\cos^{5}\\left(2x\\right)",
])("accepts trig powers in the editor: %s", (latex) => {
  expect(latexToBackendSyntax(latex)).toMatch(/(?:sin|cos)\s*\(?\s*(?:\^\s*\d+\s*\(.*\)|\(.*\)\s*\^\s*\d+)/);
});
