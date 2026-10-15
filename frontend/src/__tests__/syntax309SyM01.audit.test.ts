import {readFileSync} from "node:fs";
import {describe,expect,it} from "vitest";
import {detectMatrixIntent} from "../components/matrixIntent";
const rows=readFileSync("../qa/certification/syntax309_cases.jsonl","utf8").trim().split("\n").map(s=>JSON.parse(s));
describe("SY-M-01 real matrix intent",()=>{
 it("extracts the official determinant payload without losing rows or columns",()=>{
  const row=rows.find(r=>r.id==="SY-M-01");
  expect(row.entrada).toBe(String.raw`\det\begin{pmatrix}1&2\\3&4\end{pmatrix}`);
  expect(row.operacion).toBe("det");
  expect(row.esperado).toBe("-2");
  expect(detectMatrixIntent(row.entrada)).toEqual({kind:"determinant",matrix:[["1","2"],["3","4"]]});
  expect(detectMatrixIntent(row.entrada.replace("\\det",""))).toEqual({kind:"literal",matrix:[["1","2"],["3","4"]]});
 });
 it("rejects ragged rows",()=>{
  expect(()=>detectMatrixIntent(String.raw`\det\begin{pmatrix}1&2\\3\end{pmatrix}`)).toThrow();
 });
});
