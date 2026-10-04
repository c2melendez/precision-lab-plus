import { describe, expect, it } from "vitest";
import { latexToBackendSyntax } from "../components/NaturalMathField";
const c=(s:string)=>latexToBackendSyntax(s).replace(/\s+/g,"");

describe("IN625 Parte D / D2 Notación científica y porcentaje — UI→backend",()=>{
  it("EN-CI-01 ×10^3",()=>expect(c("1.5\\times10^{3}")).toMatch(/1\.5\*10\^3|1500/));
  it("EN-CI-02 ·10^3",()=>expect(c("1.5\\cdot10^{3}")).toMatch(/1\.5\*10\^3|1500/));
  it("EN-CI-03 negative exponent",()=>expect(c("1.5\\times10^{-3}")).toMatch(/1\.5\*10\^-?3|0\.0015/));
  it("EN-CI-05 lowercase e notation preserved",()=>expect(c("1.5e3").toLowerCase()).toMatch(/1\.5e\+?3|1500/));
  it("EN-CI-06 2e3",()=>expect(c("2e3").toLowerCase()).toMatch(/2e\+?3|2000/));
  it("EN-CI-07 signed E notation preserved",()=>{
    expect(c("1e-3").toLowerCase()).toMatch(/1e-3|0\.001/);
    expect(c("1E+3").toLowerCase()).toMatch(/1e\+3|1000/);
  });
  it("EN-CI-08 chained scientific expression stable",()=>expect(c("2\\times10^{-3}\\times3\\times10^{2}")).toContain("10"));
  it("EN-CI-09 huge positive exponent never becomes Infinity",()=>expect(c("1\\times10^{400}")).not.toMatch(/Infinity/i));
  it("EN-CI-10 huge negative exponent never becomes zero",()=>expect(c("1\\times10^{-400}")).not.toBe("0"));
  it("EN-PC-01 50%",()=>expect(c("50\\%")).toMatch(/50\/100|0\.5|1\/2/));
  it("EN-PC-02 15%",()=>expect(c("15\\%")).toMatch(/15\/100|0\.15|3\/20/));
  it("EN-PC-03 plain 15%",()=>expect(c("15%")).toMatch(/15\/100|0\.15|3\/20/));
  it("EN-PC-04 200·15%",()=>expect(c("200\\cdot15\\%")).toMatch(/200.*15\/100|30/));
  it("EN-PC-05 C7 additive percent",()=>expect(c("100+15\\%")).toMatch(/100\+15\/100|100\.15/));
  it("EN-PC-06 explicit commercial increase",()=>expect(c("100\\cdot\\left(1+15\\%\\right)")).toMatch(/100.*1\+15\/100|115/));
  it("EN-PC-07 percent boundaries",()=>{
    expect(c("0.5\\%")).toMatch(/0\.5\/100|0\.005/);
    expect(c("100\\%")).toMatch(/100\/100|1/);
  });
  it("EN-PC-08 symbolic percent",()=>expect(c("x\\%")).toMatch(/x\/100/));
  it.todo("EN-PC-09 7%3 ambiguous postfix percent requires UI warning/error verification");
  it.todo("EN-CI-04 Avogadro-sized exact rendering requires backend/display verification");
});
