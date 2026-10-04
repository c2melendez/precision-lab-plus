import { describe, expect, it } from "vitest";
import { detectCalculusIntent } from "../components/calculusIntent";

describe("IN625 E1c — reconocimiento de integrales",()=>{
  it("EN-CA-01 indefinida con \\,dx",()=>expect(detectCalculusIntent("\\int x^{2}\\,dx")).toMatchObject({kind:"integral",variable:"x",lowerBound:null,upperBound:null}));
  it("EN-CA-02 dx sin espacio fino",()=>expect(detectCalculusIntent("\\int x^{2}dx")).toMatchObject({kind:"integral",variable:"x"}));
  it("EN-CA-03 forma compacta",()=>expect(detectCalculusIntent("\\int x^2 dx")).toMatchObject({kind:"integral",variable:"x"}));
  it("EN-CA-04 definida 0..1",()=>expect(detectCalculusIntent("\\int_{0}^{1}x^{2}\\,dx")).toMatchObject({kind:"integral",variable:"x",lowerBound:"0",upperBound:"1"}));
  it("EN-CA-05 límites sin llaves",()=>expect(detectCalculusIntent("\\int_0^1 x^2\\,dx")).toMatchObject({kind:"integral",variable:"x",lowerBound:"0",upperBound:"1"}));
  it("EN-CA-06 definida 0..pi",()=>expect(detectCalculusIntent("\\int_{0}^{\\pi}\\sin x\\,dx")).not.toBeNull());
  it("EN-CA-08 acepta \\mathrm{d}x",()=>expect(detectCalculusIntent("\\int\\frac{1}{x}\\mathrm{d}x")).toMatchObject({kind:"integral",variable:"x"}));
  it("EN-CA-09 acepta \\differentialD x",()=>expect(detectCalculusIntent("\\int\\frac{1}{x}\\differentialD x")).toMatchObject({kind:"integral",variable:"x"}));
  it("EN-CA-10 detecta variable t",()=>expect(detectCalculusIntent("\\int t\\,dt")).toMatchObject({kind:"integral",variable:"t"}));
  it.todo("EN-CA-07 integral impropia: backend actual la marca unsupported en esta fase");
  it.todo("EN-CA-11 integral doble requiere intención estructural múltiple");
});
