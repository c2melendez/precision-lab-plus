import {readFileSync} from "node:fs";
import {describe,expect,it} from "vitest";
import {detectMatrixIntent} from "../components/matrixIntent";
const rows=readFileSync("../qa/certification/syntax309_cases.jsonl","utf8").trim().split("\n").map(s=>JSON.parse(s));
describe("SY-M-19 real transpose intent",()=>{
 it("extracts the official transpose and distinguishes a positive power",()=>{
  const row=rows.find(r=>r.id==="SY-M-19");
  expect(row.entrada).toBe(String.raw`\begin{pmatrix}1&2\\3&4\end{pmatrix}^{\top}`);
  expect(row.operacion).toBe("matriz");
  expect(detectMatrixIntent(row.entrada)).toEqual({kind:"transpose",matrix:[["1","2"],["3","4"]]});
  expect(detectMatrixIntent(row.entrada.replace("^{\\top}","^{2}"))?.kind).toBe("power");
 });
 it("accepts unbraced top and rejects extended or incomplete commands",()=>{
  const matrix=String.raw`\begin{pmatrix}1&2\\3&4\end{pmatrix}`;
  expect(detectMatrixIntent(matrix+String.raw`^\top`)?.kind).toBe("transpose");
  for(const suffix of [String.raw`^{\top`,String.raw`^{\top}x`,String.raw`^\topology`])expect(detectMatrixIntent(matrix+suffix)).toBeNull();
 });
});
