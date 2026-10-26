import { describe, expect, it } from "vitest";
import { latexToBackendSyntax } from "../components/NaturalMathField";
const n=(s:string)=>latexToBackendSyntax(s).replace(/\s+/g,"");

describe("IN625 F3c — SymPy y relaciones 18..26",()=>{
  it("EN-AS-18 sympy latex polynomial",()=>{
    expect(n("x^{2} + 2 x + 1")).toMatch(/x\^\(?2\)?\+2\*?x\+1/);
  });
  it("EN-AS-19 sympy sin latex",()=>{
    expect(n("\\sin{\\left(x \\right)}")).toContain("sin");
  });
  it("EN-AS-20 operatorname asin/acos/atan",()=>{
    expect(n("\\operatorname{asin}{\\left(x \\right)}")).toMatch(/asin|arcsin/);
    expect(n("\\operatorname{acos}{\\left(x \\right)}")).toMatch(/acos|arccos/);
    expect(n("\\operatorname{atan}{\\left(x \\right)}")).toMatch(/atan|arctan/);
  });
  it("EN-AS-21 x!=3 no factorial",()=>{
    const out=n("x!=3");
    expect(out).toContain("!=");
  });
  it("EN-AS-22 <= >=",()=>{
    expect(n("x<=3")).toContain("<=");
    expect(n("x>=3")).toContain(">=");
  });
  it("EN-AS-23 <> -> !=",()=>expect(n("x<>3")).toContain("!="));
  it("EN-AS-24 == -> =",()=>expect(n("x==3")).toContain("="));
  it("EN-AS-25 lim external syntax",()=>{
    expect(()=>n("lim(x->0, sin(x)/x)")).not.toThrow();
  });
  it("EN-AS-26 sympy log latex",()=>{
    expect(n("\\log{\\left(x \\right)}")).toMatch(/log/);
  });
});
