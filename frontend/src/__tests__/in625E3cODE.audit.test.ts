import { describe, expect, it } from "vitest";
import { detectCalculusIntent } from "../components/calculusIntent";

describe("IN625 E3c — ODE intent", () => {
  it("EN-DI-12: y'=y", () => {
    expect(detectCalculusIntent("y'=y")).toEqual({ kind: "ode", cleanedExpression: "y'=y" });
  });

  it("EN-DI-13: y''+y=0", () => {
    expect(detectCalculusIntent("y''+y=0")).toEqual({ kind: "ode", cleanedExpression: "y''+y=0" });
  });

  it("EN-DI-14: dy/dx=y", () => {
    expect(detectCalculusIntent("\\frac{dy}{dx}=y")).toEqual({ kind: "ode", cleanedExpression: "y'=y" });
  });
});
