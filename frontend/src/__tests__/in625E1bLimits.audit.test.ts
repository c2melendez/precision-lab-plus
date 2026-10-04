import { describe, expect, it } from "vitest";
import { detectCalculusIntent } from "../components/calculusIntent";

describe("IN625 E1b — reconocimiento de límites",()=>{
  const core={kind:"limit" as const,variable:"x",innerLatex:"\\frac{\\sin x}{x}",direction:"both" as const};
  it("EN-CA-20 x->0",()=>expect(detectCalculusIntent("\\lim_{x\\to0}\\frac{\\sin x}{x}")).toEqual({...core,point:"0"}));
  it("EN-CA-21 acepta \\rightarrow",()=>expect(detectCalculusIntent("\\lim_{x\\rightarrow0}\\frac{\\sin x}{x}")).toEqual({...core,point:"0"}));
  it("EN-CA-22 lateral derecho",()=>expect(detectCalculusIntent("\\lim_{x\\to0^{+}}\\frac{1}{x}")).toEqual({
    kind:"limit",variable:"x",point:"0",innerLatex:"\\frac{1}{x}",direction:"right"
  }));
  it("EN-CA-23 lateral izquierdo sin llaves",()=>expect(detectCalculusIntent("\\lim_{x\\to0^-}\\frac{1}{x}")).toEqual({
    kind:"limit",variable:"x",point:"0",innerLatex:"\\frac{1}{x}",direction:"left"
  }));
  it("EN-CA-24 infinito",()=>expect(detectCalculusIntent("\\lim_{x\\to\\infty}\\frac{1}{x}")).toEqual({
    kind:"limit",variable:"x",point:"oo",innerLatex:"\\frac{1}{x}",direction:"both"
  }));
  it("EN-CA-25 tolera \\displaystyle",()=>expect(detectCalculusIntent("\\displaystyle\\lim_{x\\to0}\\frac{\\sin x}{x}")).toEqual({...core,point:"0"}));
});
