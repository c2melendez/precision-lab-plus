import { describe, expect, it } from "vitest";
import { latexToBackendSyntax } from "../components/NaturalMathField";
const n=(s:string)=>latexToBackendSyntax(s).replace(/\s+/g,"");

describe("IN625 F3a — ASCII/Python básico 01..10",()=>{
  it("EN-AS-01/02 potencias ASCII/Python",()=>{
    expect(n("x^2+1")).toMatch(/x\^\(?2\)?\+1/);
    expect(()=>n("x**2+1")).not.toThrow();
  });
  it("EN-AS-03 sqrt",()=>expect(n("sqrt(16)")).toContain("sqrt"));
  it("EN-AS-04 potencias parentizadas",()=>{
    expect(n("2^(10)")).toMatch(/2\^\(?10\)?/);
    expect(n("2^(-1)")).toMatch(/2\^\(?-1\)?/);
  });
  it("EN-AS-05/06 expresiones exponenciales",()=>{
    expect(n("x^(1/2)")).toMatch(/x\^/);
    expect(n("e^(-x^2)")).toContain("e");
  });
  it("EN-AS-07 constantes ascii",()=>{
    expect(n("pi")).toMatch(/pi/);
    for(const s of ["inf","oo","infinity"]) expect(()=>n(s)).not.toThrow();
  });
  it("EN-AS-08 logs básicos",()=>{
    expect(n("ln(1)")).toMatch(/ln|log/);
    expect(n("log(100)")).toMatch(/log/);
  });
  it("EN-AS-09 log base segundo argumento",()=>{
    expect(n("log(100,10)")).toMatch(/log/);
    expect(n("log(8,2)")).toMatch(/log/);
  });
  it("EN-AS-10 log10/log2",()=>{
    expect(n("log10(1000)")).toMatch(/log/);
    expect(()=>n("log2(8)")).not.toThrow();
  });
});
