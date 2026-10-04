import { describe, expect, it } from "vitest";
import { latexToBackendSyntax } from "../components/NaturalMathField";
const c=(s:string)=>latexToBackendSyntax(s).replace(/\s+/g,"");
describe("IN625 Parte D / D1 Decimales y separadores — UI → backend invariants",()=>{
  it("EN-NM-01 3.5",()=>expect(c("3.5")).toBe("3.5"));
  it("EN-NM-03 .5 -> 0.5",()=>expect(c(".5")).toMatch(/^0?\.5$/));
  it("EN-NM-05 5. -> 5",()=>expect(c("5.")).toMatch(/^5\.?$/));
  it("EN-NM-06 -.5 -> -0.5",()=>expect(c("-.5")).toMatch(/^-0?\.5$/));
  it("EN-NM-07 0.50 valid",()=>expect(c("0.50")).toMatch(/^0\.50?$/));
  it("EN-NM-08 007 remains decimal literal",()=>expect(c("007")).toMatch(/^0*7$/));
  it("EN-NM-09 MathLive explicit decimal comma 3{,}5",()=>expect(c("3{,}5")).toMatch(/^3\.5$/));
  it("EN-NM-12 thin-space thousands",()=>expect(c("1\\,234.56")).toMatch(/^1234\.56$/));
  it("EN-NM-23 malformed 1.2.3 is not collapsed",()=>expect(c("1.2.3")).not.toBe("123"));
  it("EN-NM-24 malformed 3..5 is not collapsed",()=>expect(c("3..5")).not.toBe("35"));
  it("EN-NM-25 grouped thousands by space",()=>expect(c("1 000")).toMatch(/^1000$/));
  it("EN-NM-26 digit space never silently becomes 34",()=>expect(c("3 4")).not.toBe("34"));
});
describe("IN625 D1 — configuración regional/manual",()=>{
  for(const id of ["02","04","10","11","13","14","15","16","17","18","19","20","21","22"]){
    it.todo(`EN-NM-${id} locale/config dependent`);
  }
});
