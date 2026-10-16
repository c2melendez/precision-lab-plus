import {readFileSync} from "node:fs";
import {describe,expect,it} from "vitest";
import {detectMatrixIntent} from "../components/matrixIntent";
const rows=readFileSync("../qa/certification/syntax309_cases.jsonl","utf8").trim().split("\n").map(s=>JSON.parse(s));
describe("SY-M-17 real inverse intent",()=>{
 it("extracts the official inverse and distinguishes a positive power",()=>{
  const row=rows.find(r=>r.id==="SY-M-17");
  expect(row.entrada).toBe(String.raw`\begin{pmatrix}1&2\\3&4\end{pmatrix}^{-1}`);
  expect(row.operacion).toBe("inversa");
  expect(detectMatrixIntent(row.entrada)).toEqual({kind:"inverse",matrix:[["1","2"],["3","4"]]});
  expect(detectMatrixIntent(row.entrada.replace("^{-1}","^{2}"))?.kind).toBe("power");
 });
});
