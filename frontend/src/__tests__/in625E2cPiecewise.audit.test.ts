import { describe, expect, it } from "vitest";
import { detectPiecewiseIntent } from "../components/piecewiseIntent";
import { splitSystemLatex } from "../components/systemSplit";

describe("IN625 E2c — función a trozos",()=>{
  const input="\\begin{cases}x^{2}&x<0\\\\x&x\\geq0\\end{cases}";

  it("EN-MT-14 reconoce piecewise antes de sistema",()=>{
    expect(detectPiecewiseIntent(input)).toEqual({
      kind:"piecewise",
      branches:[
        {expressionLatex:"x^{2}",conditionLatex:"x<0"},
        {expressionLatex:"x",conditionLatex:"x\\geq0"},
      ],
    });
  });

  it("el detector de sistema por sí solo no define la prioridad del router",()=>{
    expect(splitSystemLatex(input)).not.toBeNull();
    expect(detectPiecewiseIntent(input)).not.toBeNull();
  });
});
