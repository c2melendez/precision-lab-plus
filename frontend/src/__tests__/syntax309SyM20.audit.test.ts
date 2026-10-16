import {readFileSync} from "node:fs";
import {describe,expect,it} from "vitest";
import {detectMatrixIntent} from "../components/matrixIntent";
const rows=readFileSync("../qa/certification/syntax309_cases.jsonl","utf8").trim().split("\n").map(s=>JSON.parse(s));
describe("SY-M-20 real scalar matrix intent",()=>{
 it("extracts the official scalar and matrix",()=>{
  const row=rows.find(r=>r.id==="SY-M-20");
  expect(row.entrada).toBe(String.raw`2\begin{pmatrix}1&2\\3&4\end{pmatrix}`);
  expect(detectMatrixIntent(row.entrada)).toEqual({kind:"scale",scalar:"2",matrix:[["1","2"],["3","4"]]});
  expect(detectMatrixIntent(row.esperado)).toEqual({kind:"literal",matrix:[["2","4"],["6","8"]]});
 });
 it("preserves signed fractions and rejects nonfinite or extra input",()=>{
  const matrix=String.raw`\begin{pmatrix}1&2\\3&4\end{pmatrix}`;
  expect(detectMatrixIntent(String.raw`-\frac{1}{2}`+matrix)?.kind).toBe("scale");
  expect(()=>detectMatrixIntent("1/0"+matrix)).toThrow(/finito/);
  expect(detectMatrixIntent("2"+matrix+"x")).toBeNull();
  expect(detectMatrixIntent("2x")).toBeNull();
 });
});
