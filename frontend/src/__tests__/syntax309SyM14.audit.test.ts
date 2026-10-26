import {describe,expect,it} from "vitest";
import {readFileSync} from "node:fs";
import {detectMatrixIntent} from "../components/matrixIntent";
import {splitFreeSystemLatex} from "../components/systemSplit";
const source=readFileSync("../qa/certification/syntax309_cases.jsonl","utf8");
const official="\\vec{u}\\cdot\\vec{v}\\ \\text{con}\\ \\vec{u}=(1,2,3),\\ \\vec{v}=(4,5,6)";
describe("SY-M-14 locally declared vectors",()=>{
 it("reads the official source as local vector data and computes 32",()=>{
  const row=source.trim().split("\n").map(s=>JSON.parse(s)).find(r=>r.id==="SY-M-14");
  expect(row.entrada).toBe(official);
  expect(row.operacion).toBe("vectores");
  expect(row.esperado).toBe("32");
  expect(splitFreeSystemLatex(row.entrada)).toBeNull();
  const intent=detectMatrixIntent(row.entrada);
  expect(intent).toEqual({kind:"dot",left:[["1","2","3"]],right:[["4","5","6"]]});
 });
 it("uses current declarations and leaves no persistent named values",()=>{
  expect(detectMatrixIntent(official.replace("(4,5,6)","(0,1,0)"))).toEqual({kind:"dot",left:[["1","2","3"]],right:[["0","1","0"]]});
  expect(detectMatrixIntent(String.raw`\vec{u}\cdot\vec{v}`)).toBeNull();
  expect(splitFreeSystemLatex("x=1,y=2")).toEqual(["x=1","y=2"]);
 });
 it("rejects duplicate, missing and unequal declarations",()=>{
  expect(()=>detectMatrixIntent(official.replace("\\vec{v}=(4,5,6)","\\vec{u}=(4,5,6)"))).toThrow(/nombres distintos/);
  expect(()=>detectMatrixIntent(official.replace("\\vec{v}=(4,5,6)","\\vec{w}=(4,5,6)"))).toThrow(/Faltan/);
  expect(()=>detectMatrixIntent(official.replace("(4,5,6)","(4,5)"))).toThrow(/misma longitud/);
 });
});
