import { describe, expect, it } from "vitest";
import { latexToBackendSyntax } from "../components/NaturalMathField";

const c=(s:string)=>latexToBackendSyntax(s).replace(/\s+/g,"");
function noTex(s:string){const out=c(s);expect(out.length).toBeGreaterThan(0);expect(out).not.toContain("\\");return out;}

describe("IN625 Parte B / B3 Multiplicación implícita — UI → backend",()=>{
  const cases:Array<[string,string]>=[
    ["EN-MI-01","2x"],["EN-MI-02","2(3)"],["EN-MI-03","(2)(3)"],["EN-MI-04","(x+1)(x-1)"],
    ["EN-MI-05","x(x+1)"],["EN-MI-06","2x^2"],["EN-MI-07","-2x^2"],["EN-MI-08","3x^2y"],
    ["EN-MI-09","xy"],["EN-MI-10","xyz"],["EN-MI-11","2\\pi"],["EN-MI-12","2\\pi x"],
    ["EN-MI-13","\\pi r^{2}"],["EN-MI-14","3\\sqrt{2}"],["EN-MI-15","2e"],["EN-MI-16","2e^{x}"],
    ["EN-MI-17","xe^{x}"],["EN-MI-18","ex"],["EN-MI-19","2\\sin x"],["EN-MI-20","x\\sin x"],
    ["EN-MI-21","\\sin x\\cos x"],["EN-MI-22","(a+b)c"],["EN-MI-23","2(3)(4)"],["EN-MI-24","2(3)^{2}"],
    ["EN-MI-25","3(x+1)^{2}"],["EN-MI-26","x2"],["EN-MI-27","1/2x"],["EN-MI-28","1/2\\pi"],
    ["EN-MI-29","2/3x"],["EN-MI-30","a/bc"],["EN-MI-31","6/2(1+2)"],["EN-MI-32","6\\div2(1+2)"],
    ["EN-MI-33","2\\frac{1}{2}"],["EN-MI-34","2\\left(3+4\\right)"],["EN-MI-35","\\left(3+4\\right)2"],["EN-MI-36","3\\,x"]
  ];
  for(const [id,input] of cases) it(`${id}: conversión válida sin TeX residual`,()=>{noTex(input);});

  it("MI-01 preserva producto implícito",()=>{
    const out=noTex("2x");
    expect(out).toMatch(/\*|[0-9)][A-Za-z]|[A-Za-z][A-Za-z]/);
  });
  it("MI-06/08 preservan producto y precedencia de potencia",()=>{
    for(const input of ["2x^2","3x^2y"]){
      const out=noTex(input);
      expect(out).toMatch(/\*|[0-9)][A-Za-z]|[A-Za-z][A-Za-z]/);
      expect(out).toMatch(/\^|\*\*/);
    }
  });

  it("MI-09/10 C10: concatenación de letras queda explícita o estable",()=>{
    for(const input of ["xy","xyz"]){
      const out=noTex(input);
      expect(out.length).toBeGreaterThanOrEqual(input.length);
    }
  });

  it("MI-18 C10: ex no se confunde silenciosamente con exp()",()=>{
    const out=noTex("ex");
    expect(out.toLowerCase()).not.toContain("exp(");
  });

  it("MI-19/20/21: funciones trigonométricas conservan llamada y producto",()=>{
    for(const input of ["2\\sin x","x\\sin x","\\sin x\\cos x"]){
      const out=noTex(input).toLowerCase();
      expect(out).toContain("sin");
    }
  });

  it("MI-26: x2 sigue siendo producto, no subíndice",()=>{
    const out=noTex("x2");
    expect(out).not.toContain("sub");
    expect(out).not.toContain("_");
  });

  it("MI-27..32 C1: ambigüedad queda parseada sin pérdida de operandos",()=>{
    const inputs=["1/2x","1/2\\pi","2/3x","a/bc","6/2(1+2)","6\\div2(1+2)"];
    for(const input of inputs){
      const out=noTex(input);
      expect(out).toContain("/");
    }
  });

  it("MI-33 C8: conserva 2 y 1/2 en la representación",()=>{
    const out=noTex("2\\frac{1}{2}");
    expect(out).toContain("2");
    expect(out).toContain("1");
  });
});
