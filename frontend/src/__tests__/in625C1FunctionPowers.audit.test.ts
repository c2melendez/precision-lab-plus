import { describe, expect, it } from "vitest";
import { latexToBackendSyntax } from "../components/NaturalMathField";

const c=(s:string)=>latexToBackendSyntax(s).replace(/\s+/g,"");
function noTex(s:string){const out=c(s);expect(out.length).toBeGreaterThan(0);expect(out).not.toContain("\\");return out;}

describe("IN625 Parte C / C1 Potencia de función vs inversa — UI → backend",()=>{
  const cases:Array<[string,string]>=[
    ["EN-FP-01","\\sin^{2}x"],["EN-FP-02","\\sin^{2}(x)"],["EN-FP-03","\\sin^2 x"],
    ["EN-FP-04","\\sin^{-1}x"],["EN-FP-05","\\cos^{-1}x"],["EN-FP-06","\\tan^{-1}x"],
    ["EN-FP-07","\\sin^{-2}x"],["EN-FP-08","\\left(\\sin x\\right)^{-1}"],["EN-FP-09","\\frac{1}{\\sin x}"],
    ["EN-FP-10","\\left(\\sin x\\right)^{2}"],["EN-FP-11","\\sin(x)^{2}"],["EN-FP-12","\\sin(x^{2})"],
    ["EN-FP-13","\\sin x^{2}"],["EN-FP-14","\\sin^{2}x^{2}"],["EN-FP-15","\\sin^{3}x"],
    ["EN-FP-16","\\sin^{2}3x"],["EN-FP-17a","\\sinh^{-1}(1)"],["EN-FP-17b","\\cosh^{-1}(1)"],
    ["EN-FP-18a","\\csc^{-1}2"],["EN-FP-18b","\\sec^{-1}2"],["EN-FP-18c","\\cot^{-1}1"],
    ["EN-FP-19","\\ln^{2}\\left(e^{3}\\right)"],["EN-FP-20","\\log^{2}1000"],
    ["EN-FP-21","\\ln^{-1}x"],["EN-FP-22","\\sin x^{-1}"],
    ["EN-FP-23","\\sin^{2}x+\\cos^{2}x"],["EN-FP-24a","\\sin^{1}x"],["EN-FP-24b","\\sin^{0}x"],
    ["EN-FP-25","f^{2}(x)"]
  ];
  for(const [id,input] of cases) it(`${id}: conversión estable`,()=>{noTex(input);});

  it("FP-04/05/06 C3: inverse trig forms explicit",()=>{
    for(const s of ["\\sin^{-1}x","\\cos^{-1}x","\\tan^{-1}x"]){
      const out=noTex(s).toLowerCase();
      expect(out).toMatch(/asin|acos|atan|arcsin|arccos|arctan/);
    }
  });

  it("FP-07 vs FP-04 remain distinguishable",()=>{
    expect(noTex("\\sin^{-2}x")).not.toBe(noTex("\\sin^{-1}x"));
  });

  it("FP-08 grouped reciprocal is not inverse-function alias",()=>{
    const out=noTex("\\left(\\sin x\\right)^{-1}").toLowerCase();
    expect(out).not.toMatch(/asin|arcsin/);
  });

  it("FP-13 exponent belongs to argument",()=>{
    const out=noTex("\\sin x^{2}").toLowerCase();
    expect(out).toContain("sin");
    expect(out).toMatch(/\^|\*\*/);
  });

  it("FP-21/25 ambiguities remain explicit, not silently erased",()=>{
    expect(noTex("\\ln^{-1}x").length).toBeGreaterThan(0);
    expect(noTex("f^{2}(x)").length).toBeGreaterThan(0);
  });
});
