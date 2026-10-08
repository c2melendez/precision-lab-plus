import { describe, expect, it } from "vitest";
import { latexToBackendSyntax } from "../components/NaturalMathField";
const c=(s:string)=>latexToBackendSyntax(s).replace(/\s+/g,"");

describe("IN625 D3 — L1 preservación exacta de entrada",()=>{
  it("EN-PN-01 decimal expression preserved",()=>expect(c("0.1+0.2")).toContain("0.1"));
  it("EN-PN-03 4.35 is not rounded at UI boundary",()=>expect(c("4.35\\cdot100")).toContain("4.35"));
  it("EN-PN-04 1.005 is not rounded at UI boundary",()=>expect(c("1.005\\cdot1000")).toContain("1.005"));
  it("EN-PN-08 >2^53 integer preserved",()=>expect(c("9007199254740993")).toContain("9007199254740993"));
  it("EN-PN-10 20-digit integer preserved",()=>expect(c("99999999999999999999+1")).toContain("99999999999999999999"));
  it("EN-PN-11 30-digit integer preserved",()=>expect(c("123456789012345678901234567890")).toContain("123456789012345678901234567890"));
  it("EN-PN-12 25-digit decimal payload preserved",()=>expect(c("0.1234567890123456789012345\\cdot10^{25}")).toContain("0.1234567890123456789012345"));
  it("EN-PN-18 extreme exponents preserved",()=>expect(c("10^{400}\\cdot10^{-400}")).toContain("400"));
  it("EN-PN-19 2^-1074 preserved",()=>expect(c("2^{-1074}")).toContain("1074"));
  it("EN-PN-20 2^1024 preserved",()=>expect(c("2^{1024}")).toContain("1024"));
  it.todo("EN-PN-15..17 repeating decimals require explicit L1 syntax contract");
});
