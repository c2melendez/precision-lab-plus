import { describe, expect, it } from "vitest";
import { latexToBackendSyntax } from "../components/NaturalMathField";

describe("IN625 E3a — normalización previa al router",()=>{
  it("EN-DI-01 expresión",()=>expect(latexToBackendSyntax("x^{2}-4")).toBe("x^2-4"));
  it("EN-DI-02 ecuación =0",()=>expect(latexToBackendSyntax("x^{2}-4=0")).toContain("="));
  it("EN-DI-03 ecuación x²=4",()=>expect(latexToBackendSyntax("x^{2}=4")).toContain("="));
  it("EN-DI-04 inecuación",()=>expect(latexToBackendSyntax("x^{2}>4")).toContain(">"));
  it("EN-DI-05 valor absoluto <=2",()=>{
    const s=latexToBackendSyntax("\\lvert x-1\\rvert\\leq2");
    expect(s).toMatch(/<=|≤/);
  });
  it("EN-DI-06 conserva cadena estricta",()=>expect(latexToBackendSyntax("3<x<7")).toBe("3<x<7"));
  it("EN-DI-06 conserva cadena cerrada",()=>{
    const s=latexToBackendSyntax("3\\le x\\le7");
    expect(s.replace(/\s/g,"")).toMatch(/^3(?:<=|≤)x(?:<=|≤)7$/);
  });
});
