import {readFileSync} from "node:fs";
import {describe,expect,it} from "vitest";
import {detectMatrixIntent} from "../components/matrixIntent";
const rows=readFileSync("../qa/certification/syntax309_cases.jsonl","utf8").trim().split("\n").map(s=>JSON.parse(s));
describe("SY-M-05 real matrix intent",()=>{
 it("extracts the official determinant payload without losing rows or columns",()=>{
  const row=rows.find(r=>r.id==="SY-M-05");
  expect(row.entrada).toBe(String.raw`\det\left[\begin{matrix}1&2\\3&4\end{matrix}\right]`);
  expect(row.operacion).toBe("det");
  expect(row.esperado).toBe("-2");
  expect(detectMatrixIntent(row.entrada)).toEqual({kind:"determinant",matrix:[["1","2"],["3","4"]]});
 });
 it("requires matching external brackets and preserves matrix literal intent",()=>{
  const wrapped=String.raw`\left[\begin{matrix}1&2\\3&4\end{matrix}\right]`;
  expect(detectMatrixIntent(wrapped)).toEqual({kind:"literal",matrix:[["1","2"],["3","4"]]});
  expect(detectMatrixIntent("\\det"+wrapped+"+1")).toBeNull();
  expect(detectMatrixIntent(wrapped.replace("\\right]","\\right)"))).toBeNull();
  expect(detectMatrixIntent(wrapped.replace("\\right]",""))).toBeNull();
  expect(detectMatrixIntent(wrapped.replace("\\end{matrix}","\\end{pmatrix}"))).toBeNull();
  expect(()=>detectMatrixIntent("\\det"+wrapped.replace("3&4","3"))).toThrow();
 });
});
