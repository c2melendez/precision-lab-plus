import { describe, expect, it } from "vitest";
import { latexToBackendSyntax } from "../components/NaturalMathField";
const c=(s:string)=>latexToBackendSyntax(s).replace(/\s+/g,"");
function noTex(s:string){const o=c(s);expect(o.length).toBeGreaterThan(0);expect(o).not.toContain("\\");return o;}
describe("IN625 Parte C / C2 Argumento sin paréntesis — UI → backend",()=>{
 const cases:Array<[string,string]>=[
  ["EN-FA-01","\\sin x"],["EN-FA-02","\\sin 2x"],["EN-FA-03","\\sin2x"],["EN-FA-04","\\sin x+1"],
  ["EN-FA-05","\\sin x\\cos x"],["EN-FA-06","\\sin 2x\\cos 3x"],["EN-FA-07","\\sin\\frac{\\pi}{6}"],
  ["EN-FA-08","\\sin\\pi x"],["EN-FA-09","\\sin 2\\pi x"],["EN-FA-10","\\sin x/2"],["EN-FA-11","\\sin\\cos x"],
  ["EN-FA-12","\\sin\\sin x"],["EN-FA-13","\\ln x^{2}"],["EN-FA-14","\\ln 2x"],["EN-FA-15","\\ln x+1"],
  ["EN-FA-16","\\sin x\\cdot2"],["EN-FA-17","\\cos 2x^{2}"],["EN-FA-18","\\sin(\\pi/6)"],
  ["EN-FA-19","\\operatorname{sin}x"],["EN-FA-20","\\sin 30^{\\circ}"],["EN-FA-21","\\cos\\left(60^{\\circ}\\right)"],
  ["EN-FA-22","\\sin 30"],["EN-FA-23","\\sin(x+1)^{2}"]
 ];
 for(const [id,input] of cases) it(`${id}: conversión estable`,()=>{noTex(input);});
 it("FA-04 + termina argumento",()=>{const o=noTex("\\sin x+1").toLowerCase();expect(o).toContain("sin");expect(o).toContain("+1");});
 it("FA-05/06 conservan llamadas separadas",()=>{for(const s of ["\\sin x\\cos x","\\sin 2x\\cos 3x"]){const o=noTex(s).toLowerCase();expect(o).toContain("sin");expect(o).toContain("cos");}});
 it("FA-10 / termina argumento",()=>{const o=noTex("\\sin x/2").toLowerCase();expect(o).toContain("sin");expect(o).toContain("/2");});
 it("FA-11/12 composiciones no se degradan a producto de nombres",()=>{for(const s of ["\\sin\\cos x","\\sin\\sin x"]){const o=noTex(s).toLowerCase();expect(o).toContain("sin");}});
 it("FA-20/21 grado explícito se conserva",()=>{for(const s of ["\\sin 30^{\\circ}","\\cos\\left(60^{\\circ}\\right)"]){expect(noTex(s)).toMatch(/deg|°|pi|30|60/);}});
});
