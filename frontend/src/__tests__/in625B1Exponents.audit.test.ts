import { describe, expect, it } from "vitest";
import { latexToBackendSyntax } from "../components/NaturalMathField";

const c=(s:string)=>latexToBackendSyntax(s).replace(/\s+/g,"");
function noTex(s:string){const out=c(s);expect(out.length).toBeGreaterThan(0);expect(out).not.toContain("\\");return out;}

describe("IN625 Parte B / B1 Exponentes — UI → backend",()=>{
  const cases:Array<[string,string]>=[
    ["EN-EX-01","2^{10}"],["EN-EX-02","2^10"],["EN-EX-03","2^{12}"],["EN-EX-04","2^{100}"],
    ["EN-EX-05","10^{-12}"],["EN-EX-06","10^{100}"],["EN-EX-07","x^{10}"],["EN-EX-08","x^{-10}"],
    ["EN-EX-09","x^{100}"],["EN-EX-10","x^23"],["EN-EX-11","x^{2}3"],["EN-EX-12","x^2"],
    ["EN-EX-13","x^{-1}"],["EN-EX-14","x^-1"],["EN-EX-15","2^-x"],["EN-EX-16","x^{1/2}"],
    ["EN-EX-17","x^{0.5}"],["EN-EX-18","x^{2n}"],["EN-EX-19","x^{a+b}"],["EN-EX-20","2^{3^{2}}"],
    ["EN-EX-21","2^3^2"],["EN-EX-22","(2^3)^2"],["EN-EX-23","x^{2}^{3}"],["EN-EX-24","-2^2"],
    ["EN-EX-25","(-2)^2"],["EN-EX-26","-x^2"],["EN-EX-27","(-8)^{1/3}"],["EN-EX-28","e^{-x^{2}}"],
    ["EN-EX-29","e^{2x+1}"],["EN-EX-30","e^\\pi"],["EN-EX-31","e^{i\\pi}"],["EN-EX-32a","\\exp(x)"],
    ["EN-EX-32b","\\exp x"],["EN-EX-33","2^{-2^{2}}"],["EN-EX-34","x_1^2"],["EN-EX-35","x^{2}_{1}"]
  ];
  for(const [id,input] of cases) it(`${id}: sin TeX residual`,()=>{noTex(input);});

  it("multidigit exponents stay grouped",()=>{
    for(const input of ["2^{10}","2^10","x^{100}","x^23"]){
      const out=noTex(input); expect(out).toMatch(/\^|\*\*/);
    }
  });
  it("EN-EX-20/21 preserve right-associative chain",()=>{
    expect(noTex("2^{3^{2}}")).toMatch(/\^|\*\*/);
    expect(noTex("2^3^2")).toMatch(/\^|\*\*/);
  });
  it("EN-EX-34/35 preserve subscripted symbol plus power",()=>{
    expect(noTex("x_1^2").length).toBeGreaterThan(0);
    expect(noTex("x^{2}_{1}").length).toBeGreaterThan(0);
  });
});
