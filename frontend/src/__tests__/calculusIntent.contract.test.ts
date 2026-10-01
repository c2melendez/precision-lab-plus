import { describe, expect, it } from "vitest";
import { detectCalculusIntent } from "../components/calculusIntent";

describe("Natural calculus request contracts", () => {
  it.each([
    [String.raw`\frac{d^3}{dt^3}\left(t^5\right)`, { kind: "derivative", variable: "t", order: 3, innerLatex: "t^5" }],
    [String.raw`\frac{d^{4}}{dz^{4}}z^6`, { kind: "derivative", variable: "z", order: 4, innerLatex: "z^6" }],
    [String.raw`\frac{d^5}{du^5}\left(u^7\right)`, { kind: "derivative", variable: "u", order: 5, innerLatex: "u^7" }],
    [String.raw`\left.\frac{d}{dt}t^3\right\rvert_{t=2}`, { kind: "derivative", variable: "t", order: 1, innerLatex: "t^3", evaluationPoint: "2" }],
    [String.raw`\frac{\partial}{\partial t}\left(t^2z\right)`, { kind: "partialDerivative", variable: "t", innerLatex: "t^2z" }],
    [String.raw`\int_{\frac{-\pi}{2}}^{\frac{\pi}{4}}\sin t\,dt`, { kind: "integral", variable: "t", lowerBound: String.raw`\frac{-\pi}{2}`, upperBound: String.raw`\frac{\pi}{4}`, innerLatex: String.raw`\sin t` }],
    [String.raw`\int_{0}^{\frac{1}{2}}\frac{dt}{1+t^2}`, { kind: "integral", variable: "t", lowerBound: "0", upperBound: String.raw`\frac{1}{2}`, innerLatex: String.raw`\frac{1}{1+t^2}` }],
    [String.raw`\int z^3\,dz,\quad z>0`, { kind: "integral", variable: "z", lowerBound: null, upperBound: null, innerLatex: "z^3" }],
    [String.raw`\lim_{t\to-\infty}t^2`, { kind: "limit", variable: "t", point: "-oo", innerLatex: "t^2", direction: "both" }],
    [String.raw`\lim_{t\to\infty^{+}}t^2`, { kind: "limit", variable: "t", point: "oo", innerLatex: "t^2", direction: "right" }],
    [String.raw`\lim_{z\to 2^{-}}\frac{1}{z-2}`, { kind: "limit", variable: "z", point: "2", innerLatex: String.raw`\frac{1}{z-2}`, direction: "left" }],
    [String.raw` \mathrm{Res}\left(root(z,3), z=1\right) `, { kind: "residue", expressionLatex: "root(z,3)", pointLatex: "1" }],
    [String.raw`\mathrm{Res}\left(\frac{1}{z^2}, z = -2\right)`, { kind: "residue", expressionLatex: String.raw`\frac{1}{z^2}`, pointLatex: "-2" }],
    [String.raw`\mathrm{Sing}\left( \frac{1}{z(z-1)} \right)`, { kind: "singularities", expressionLatex: String.raw`\frac{1}{z(z-1)}` }],
  ])("extracts the complete dedicated request for %s", (latex, expected) => {
    expect(detectCalculusIntent(latex as string)).toEqual(expected);
  });

  it.each([
    String.raw`\mathrm{Res}\left(root(z,3)\right)`,
    String.raw`\mathrm{Res}\left(z^-2, x=0\right)`,
    String.raw`\mathrm{Res}\left(z^-2, z=\right)`,
    String.raw`\frac{d^6}{dt^6}\left(t^8\right)`,
    String.raw`\frac{d^0}{dt^0}\left(t\right)`,
    String.raw`\left.\frac{d}{dt}t^2\right\rvert_{x=0}`,
    String.raw`\frac{\partial}{\partial z}\left(\right)`,
    String.raw`\frac{\partial}{\partial z}\left(z^2\right)+1`,
    "xy'=2x",
    "y'",
    "",
  ])("does not send an incomplete or mismatched request for %s", latex => {
    expect(detectCalculusIntent(latex)).toBeNull();
  });
});
