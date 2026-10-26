import {readFileSync} from "node:fs";
import {describe,expect,it} from "vitest";
import {detectMatrixIntent} from "../components/matrixIntent";
const rows=readFileSync("../qa/certification/syntax309_cases.jsonl","utf8").trim().split("\n").map(s=>JSON.parse(s));
describe("SY-M-18 real transpose intent",()=>{
 it("extracts the official transpose and distinguishes a positive power",()=>{
  const row=rows.find(r=>r.id==="SY-M-18");
  expect(row.entrada).toBe(String.raw`\begin{pmatrix}1&2\\3&4\end{pmatrix}^{T}`);
  expect(row.operacion).toBe("matriz");
  expect(detectMatrixIntent(row.entrada)).toEqual({kind:"transpose",matrix:[["1","2"],["3","4"]]});
  expect(detectMatrixIntent(row.entrada.replace("^{T}","^{2}"))?.kind).toBe("power");
 });
});
