import { describe, expect, it } from "vitest";
import { detectConstrainedEquationIntent, satisfiesConstraint } from "../components/constrainedEquationIntent";

describe("IN625 E3d3 — constrained equation intent", () => {
  it("EN-DI-22 detecta ecuación + condición", () => {
    const intent = detectConstrainedEquationIntent("x^{2}-4=0, x>0");
    expect(intent).toEqual({
      equationLatex: "x^{2}-4=0",
      constraintLatex: "x>0",
      variable: "x",
      operator: ">",
      bound: 0,
    });
    expect(satisfiesConstraint(-2, intent!)).toBe(false);
    expect(satisfiesConstraint(2, intent!)).toBe(true);
  });
});
