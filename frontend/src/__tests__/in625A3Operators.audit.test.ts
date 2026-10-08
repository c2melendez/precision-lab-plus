import { describe, expect, it } from "vitest";
import { latexToBackendSyntax } from "../components/NaturalMathField";

const c=(s:string)=>latexToBackendSyntax(s).replace(/\\s+/g,"");
function noTex(s:string){ const out=c(s); expect(out.length).toBeGreaterThan(0); expect(out).not.toContain("\\"); return out; }

describe("IN625 Parte A / A3 Operadores, factorial y relaciones — UI → backend",()=>{
  const simple:Array<[string,string]>=[
    ["EN-OP-01","2\\cdot3"],["EN-OP-02","2\\times3"],["EN-OP-03","2*3"],["EN-OP-04","2\\ast3"],
    ["EN-OP-05","6\\div3"],["EN-OP-06","6/3"],["EN-OP-08","2\\cdot x\\cdot y"],["EN-OP-09","x\\times y"],
    ["EN-OP-11","5\\pm2"],["EN-OP-16a","5!"],["EN-OP-16b","0!"],["EN-OP-17","5!!"],
    ["EN-OP-18","3!^{2}"],["EN-OP-19","-3!"],["EN-OP-20","2^{3!}"],["EN-OP-21","\\binom{5}{2}"],
    ["EN-OP-22","{5\\choose2}"],["EN-OP-23","17\\bmod5"],["EN-OP-24","\\gcd(12,18)"],
  ];
  for(const [id,input] of simple) it(`${id}: elimina TeX residual`,()=>{noTex(input);});

  it("EN-OP-07: 6:3 permanece inequívoco o rechazo posterior explícito",()=>{ expect(c("6:3")).toContain(":"); });
  it("EN-OP-10: producto vectorial queda feature-dependent",()=>{
    const input="\\begin{pmatrix}1\\\\0\\\\0\\end{pmatrix}\\times\\begin{pmatrix}0\\\\1\\\\0\\end{pmatrix}";
    const out=latexToBackendSyntax(input); expect(out.length).toBeGreaterThan(0);
  });

  it("EN-OP-12: <= variants",()=>{ for(const s of ["x\\leq3","x\\le3","x\\leqslant3"]) expect(noTex(s)).toContain("<="); });
  it("EN-OP-13: >= variants",()=>{ for(const s of ["x\\geq3","x\\ge3","x\\geqslant3"]) expect(noTex(s)).toContain(">="); });
  it("EN-OP-14: != variants",()=>{ for(const s of ["x\\neq3","x\\ne3"]) expect(noTex(s)).toMatch(/!=|<>/); });
  it("EN-OP-15: < > variants",()=>{
    expect(noTex("x\\lt3")).toContain("<"); expect(noTex("x\\gt3")).toContain(">");
    expect(noTex("x<3")).toContain("<"); expect(noTex("x>3")).toContain(">");
  });
});
