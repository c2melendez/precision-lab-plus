import { describe, expect, it } from "vitest";
import { detectMatrixIntent } from "../components/matrixIntent";

describe("IN625 E2a — reconocimiento de matrices y vectores",()=>{
  const m="\\begin{pmatrix}1&2\\\\3&4\\end{pmatrix}";
  it("EN-MT-01 pmatrix 2x2",()=>expect(detectMatrixIntent(m)).toEqual({kind:"literal",matrix:[["1","2"],["3","4"]]}));
  it("EN-MT-02 bmatrix equivalente",()=>expect(detectMatrixIntent("\\begin{bmatrix}1&2\\\\3&4\\end{bmatrix}")).toEqual({kind:"literal",matrix:[["1","2"],["3","4"]]}));
  it("EN-MT-03 vmatrix implica determinante",()=>expect(detectMatrixIntent("\\begin{vmatrix}1&2\\\\3&4\\end{vmatrix}")).toMatchObject({kind:"determinant"}));
  it("EN-MT-04 det pmatrix",()=>expect(detectMatrixIntent("\\det"+m)).toMatchObject({kind:"determinant"}));
  it("EN-MT-05 inversa",()=>expect(detectMatrixIntent(m+"^{-1}")).toMatchObject({kind:"inverse"}));
  it("EN-MT-06 potencia matricial",()=>expect(detectMatrixIntent(m+"^{2}")).toEqual({kind:"power",matrix:[["1","2"],["3","4"]],exponent:2}));
  it("EN-MT-07 T significa transpuesta",()=>expect(detectMatrixIntent(m+"^{T}")).toMatchObject({kind:"transpose"}));
  it("EN-MT-08 producto matriz-vector",()=>expect(detectMatrixIntent(m+"\\begin{pmatrix}1\\\\1\\end{pmatrix}")).toMatchObject({kind:"multiply"}));
  it("EN-MT-09 vector columna 3x1",()=>expect(detectMatrixIntent("\\begin{pmatrix}1\\\\2\\\\3\\end{pmatrix}")).toEqual({kind:"literal",matrix:[["1"],["2"],["3"]]}));
  it("EN-MT-10 filas desiguales -> error claro",()=>expect(()=>detectMatrixIntent("\\begin{pmatrix}1&2\\\\3\\end{pmatrix}")).toThrow(/misma longitud/));
});
