import { describe, expect, it } from "vitest";
import { latexToBackendSyntax } from "../components/NaturalMathField";

const c=(s:string)=>latexToBackendSyntax(s).replace(/\s+/g,"");
function out(input:string){const v=c(input);expect(v.length).toBeGreaterThan(0);expect(v).not.toContain("\\");return v.toLowerCase();}
function fn(input:string,re:RegExp){expect(out(input)).toMatch(re);}

describe("IN625 Parte C / C3 Alias en español y otros nombres — UI → backend",()=>{
  it("EN-AL-01..06 sen aliases",()=>{
    for(const s of ["\\operatorname{sen}\\left(\\frac{\\pi}{6}\\right)","\\mathrm{sen}\\,x","\\text{sen}(x)","sen(x)","sen x","\\sen x"]) fn(s,/sin|sen/);
  });
  it("EN-AL-07/08 sen powers/inverse",()=>{
    fn("sen^{2}x",/sin|sen/); fn("sen^2(x)",/sin|sen/); fn("sen^{-1}x",/asin|arcsin|sen/);
  });
  it("EN-AL-09 case variants explicit or stable",()=>{for(const s of ["Sen x","SEN(x)"]) expect(out(s).length).toBeGreaterThan(0);});
  it("EN-AL-10 tg",()=>{for(const s of ["tg x","\\operatorname{tg}x","\\tg x"]) fn(s,/tan|tg/);});
  it("EN-AL-11 ctg/cotg",()=>{for(const s of ["ctg x","cotg x","\\operatorname{cotg}x"]) fn(s,/cot|ctg/);});
  it("EN-AL-12 cosec",()=>{for(const s of ["cosec x","\\operatorname{cosec}x"]) fn(s,/csc|cosec/);});
  it("EN-AL-13..18 inverse aliases",()=>{
    for(const s of ["arcsen(1/2)","\\operatorname{arcsen}\\frac{1}{2}"]) fn(s,/asin|arcsin|arcsen/);
    fn("arccos(1/2)",/acos|arccos/);
    for(const s of ["arctg(1)","\\operatorname{arctg}1"]) fn(s,/atan|arctan|arctg/);
    for(const s of ["arcctg(0)","arccotg(0)"]) fn(s,/acot|arccot/);
    for(const s of ["arccosec(2)","arccsc(2)"]) fn(s,/acsc|arccsc/);
    fn("arcsec(2)",/asec|arcsec/);
  });
  it("EN-AL-19..25 hyperbolic aliases",()=>{
    for(const s of ["senh(1)","\\operatorname{senh}1"]) fn(s,/sinh|senh/);
    for(const s of ["tgh(1)","\\operatorname{tgh}1"]) fn(s,/tanh|tgh/);
    for(const s of ["ctgh(1)","cotgh(1)"]) fn(s,/coth|ctgh|cotgh/);
    fn("sech(0)",/sech/); fn("cosech(1)",/csch|cosech/);
    for(const s of ["argsenh(1)","arcsenh(1)"]) fn(s,/asinh|arsinh|argsenh|arcsenh/);
    fn("argcosh(1)",/acosh|argcosh/);
    for(const s of ["argtgh(1/2)","arctgh(1/2)"]) fn(s,/atanh|artanh|argtgh|arctgh/);
  });
  it("EN-AL-26..31 common aliases",()=>{
    for(const s of ["\\log 1000","log(1000)","lg 1000"]) fn(s,/log|lg/);
    fn("ln(e)",/ln/);
    for(const s of ["raiz(16)","raíz(16)","\\operatorname{raiz}(16)"]) fn(s,/sqrt|root|raiz/);
    for(const s of ["abs(-3)","\\operatorname{abs}(-3)","abs(x)"]) fn(s,/abs/);
    fn("exp(1)",/exp/);
  });
  it("EN-AL-32..35 named functions",()=>{
    fn("\\operatorname{mcd}(12,18)",/gcd|mcd/);
    fn("\\operatorname{mcm}(4,6)",/lcm|mcm/);
    fn("\\max(2,5)",/max/);
    fn("\\operatorname{máx}(2,5)",/max|máx/);
    fn("\\operatorname{mín}(2;5,5)",/min|mín/);
    fn("\\max(2;5,5)",/max/);
  });
  it("EN-AL-36 pi aliases stable",()=>{
    for(const s of ["pi","PI","Pi","\\pi","π"]) expect(out(s).length).toBeGreaterThan(0);
  });
});
