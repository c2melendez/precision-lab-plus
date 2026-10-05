import { describe, expect, it } from "vitest";
import { splitFreeSystemLatex } from "../components/systemSplit";
import { latexToBackendSyntax } from "../components/NaturalMathField";

const variants=[
  "x+y=3\\\\x-y=1",
  "x+y=3,\\ x-y=1",
  "x+y=3;\\ x-y=1",
  "x+y=3\\text{ y }x-y=1",
  "x+y=3\nx-y=1",
];

describe("IN625 E3b — sistemas libres",()=>{
  it.each(variants)("separa dos ecuaciones: %s",(input)=>{
    expect(splitFreeSystemLatex(input)).toEqual(["x+y=3","x-y=1"]);
  });

  it("normaliza ambas filas para /solve/system",()=>{
    for(const input of variants){
      expect(splitFreeSystemLatex(input)!.map(latexToBackendSyntax)).toEqual(["x+y=3","x-y=1"]);
    }
  });
});
