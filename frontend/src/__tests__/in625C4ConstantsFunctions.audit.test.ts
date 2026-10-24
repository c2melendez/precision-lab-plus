import { describe, expect, it } from "vitest";
import { latexToBackendSyntax } from "../components/NaturalMathField";
const c=(s:string)=>latexToBackendSyntax(s).replace(/\s+/g,"");
function stable(s:string){const o=c(s);expect(o.length).toBeGreaterThan(0);expect(o).not.toContain("\\");return o;}

describe("IN625 Parte C / C4 Constantes, variables y funciones definidas — UI → backend",()=>{
  const cases=[
    "e^{x}","\\mathrm{e}^{x}","\\exponentialE^{x}","i^{2}","\\imaginaryI^{2}","\\mathrm{i}^{2}",
    "\\sum_{i=1}^{3}i^{2}","\\theta^{2}","2\\theta","\\sin\\theta","\\lambda x","\\alpha\\beta",
    "\\Delta x","dx","\\mathrm{x}+1","\\overline{3+4i}","f(x)=x^{2}+1","f(2)","g(x)=f(x)+1","g(2)",
    "h(t)=3t","h(2)","f'(x)","\\gamma+1","\\Gamma(5)","\\beta+\\zeta","\\Lambda+1","\\infty",
    "E+1","I+1","N+1","S+1","Q+1"
  ];
  for(const input of cases) it(input,()=>{stable(input);});
});
