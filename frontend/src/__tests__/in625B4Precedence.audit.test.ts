import { describe, expect, it } from "vitest";
import { latexToBackendSyntax } from "../components/NaturalMathField";

const c=(s:string)=>latexToBackendSyntax(s).replace(/\s+/g,"");
function noTex(s:string){ const out=c(s); expect(out.length).toBeGreaterThan(0); expect(out).not.toContain("\\"); return out; }

describe("IN625 Parte B / B4 Precedencia y signos — UI → backend",()=>{
  const cases:Array<[string,string]>=[
    ["EN-PR-01","2+3\\cdot4"],["EN-PR-02","(2+3)\\cdot4"],["EN-PR-03","8/2/2"],["EN-PR-04","8/2*4"],
    ["EN-PR-05","2-3-4"],["EN-PR-06","2*3^2"],["EN-PR-07","2-(-3)"],["EN-PR-08","2--3"],
    ["EN-PR-09","2+-3"],["EN-PR-10","2*-3"],["EN-PR-11","2++3"],["EN-PR-12","--x"],
    ["EN-PR-13","-2^{-2}"],["EN-PR-14","1-1+1"]
  ];
  for(const [id,input] of cases) it(`${id}: conversión estable sin TeX residual`,()=>{ noTex(input); });

  it("PR-01/02 conservan agrupación y producto",()=>{
    expect(noTex("2+3\\cdot4")).toMatch(/\*|×/);
    const out=noTex("(2+3)\\cdot4"); expect(out).toContain("("); expect(out).toContain(")");
  });
  it("PR-03/04 conservan orden textual de / y *",()=>{
    expect(noTex("8/2/2")).toContain("/");
    const out=noTex("8/2*4"); expect(out).toContain("/"); expect(out).toContain("*");
  });
  it("PR-08 doble menos no se pierde silenciosamente",()=>{
    const out=noTex("2--3"); expect(out).not.toBe("2-3");
  });
  it("PR-13 conserva signo externo y exponente negativo",()=>{
    const out=noTex("-2^{-2}"); expect(out.startsWith("-")).toBe(true); expect(out).toMatch(/\^|\*\*/);
  });
});
