import { describe, expect, it } from "vitest";
import { detectCalculusIntent } from "../components/calculusIntent";

describe("IN625 E1a — reconocimiento de derivadas naturales",()=>{
  it("EN-CA-12 d/dx x^2",()=>{
    expect(detectCalculusIntent("\\frac{d}{dx}x^{2}")).toEqual({
      kind:"derivative", variable:"x", order:1, innerLatex:"x^{2}"
    });
  });
  it("EN-CA-13 d/dx (x^2)",()=>{
    expect(detectCalculusIntent("\\frac{d}{dx}\\left(x^{2}\\right)")).toEqual({
      kind:"derivative", variable:"x", order:1, innerLatex:"x^{2}"
    });
  });
  it("EN-CA-14 d/dx sin x",()=>{
    expect(detectCalculusIntent("\\frac{d}{dx}\\sin x")).toEqual({
      kind:"derivative", variable:"x", order:1, innerLatex:"\\sin x"
    });
  });
  it.todo("EN-CA-15 dy/dx aislada conserva intención, no fracción y/x");
  it.todo("EN-CA-16 d²y/dx² conserva intención de segunda derivada");
  it.todo("EN-CA-17 primas de orden 1–4");
  it.todo("EN-CA-18 macros \\prime equivalentes");
  it.todo("EN-CA-19 parcial: frac{partial f}{partial x} y partial_x f");
});
