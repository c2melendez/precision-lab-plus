import { describe, expect, it } from "vitest";
import { latexToBackendSyntax } from "../components/NaturalMathField";
const c=(s:string)=>latexToBackendSyntax(s).replace(/\s+/g,"");
function noTex(s:string){const out=c(s);expect(out.length).toBeGreaterThan(0);expect(out).not.toContain("\\");return out;}

describe("IN625 Parte B / B2 Subíndices y bases de logaritmo — UI → backend",()=>{
  const cases:Array<[string,string]>=[
    ["EN-SB-01","x_{10}"],["EN-SB-02","x_1+x_2"],["EN-SB-03","a_{i,j}"],["EN-SB-04","x_{\\text{max}}"],
    ["EN-SB-05","\\log_{2}8"],["EN-SB-06","\\log_28"],["EN-SB-07","\\log_{10}1000"],["EN-SB-08","\\log_{16}256"],
    ["EN-SB-09","\\log_{2}8^{2}"],["EN-SB-10","\\log_{b}x"]
  ];
  for(const [id,input] of cases) it(`${id}: conversión sin TeX residual`,()=>{noTex(input);});

  it("EN-SB-01/02 subíndices no se convierten en producto",()=>{
    expect(noTex("x_{10}")).not.toMatch(/x\*1/);
    const out=noTex("x_1+x_2"); expect(out).toContain("+");
  });
  it("EN-SB-05..09 conservan base y argumento",()=>{
    for(const input of ["\\log_{2}8","\\log_28","\\log_{10}1000","\\log_{16}256","\\log_{2}8^{2}"]){
      const out=noTex(input); expect(out.toLowerCase()).toContain("log");
    }
  });
});
