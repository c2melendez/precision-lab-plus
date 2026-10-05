import { describe, expect, it } from "vitest";
import { latexToBackendSyntax } from "../components/NaturalMathField";

describe("IN625 F1 — texto pegado", () => {
  it.each([
    ["EN-PG-01", "$x^{2}+1$"],
    ["EN-PG-02", "$$x^{2}+1$$"],
    ["EN-PG-03", "\\(x^{2}+1\\)"],
    ["EN-PG-04", "\\[x^{2}+1\\]"],
    ["EN-PG-05a", "\\begin{equation}x^{2}+1\\end{equation}"],
    ["EN-PG-05b", "\\begin{align*}x^{2}+1\\end{align*}"],
    ["EN-PG-06", "{\\displaystyle x^{2}+1}"],
    ["EN-PG-08", "x^{2}\\,+\\,1"],
    ["EN-PG-09", "x^{2}+1 \\,"],
    ["EN-PG-12", "x^{2}+1\n"],
    ["EN-PG-13", "x+1\\\\"],
    ["EN-PG-14a", "x^{2}+1\\tag{1}"],
    ["EN-PG-14b", "x^{2}+1\\label{eq:1}"],
  ])("%s limpia ruido no semántico", (_id, input) => {
    const out = latexToBackendSyntax(input);
    expect(out.replace(/\s+/g, "")).toBe("x^2+1");
  });

  it.each([
    ["EN-PG-07a", "\\displaystyle\\frac{1}{2}"],
    ["EN-PG-07b", "\\textstyle\\frac{1}{2}"],
  ])("%s conserva la fracción", (_id, input) => {
    expect(latexToBackendSyntax(input).replace(/\s+/g, "")).toMatch(/1\/2|\(1\)\/\(2\)/);
  });

  it.each([
    ["EN-PG-10", "x^{2}+1."],
    ["EN-PG-11", "x^{2}+1,"],
    ["EN-PG-15", "x^{2}+1\\quad\\text{(ver ejercicio 3)}"],
  ])("%s no debe incorporar texto editorial como variables", (_id, input) => {
    const out = latexToBackendSyntax(input);
    expect(out).not.toMatch(/ver\s*ejercicio/i);
  });
});
