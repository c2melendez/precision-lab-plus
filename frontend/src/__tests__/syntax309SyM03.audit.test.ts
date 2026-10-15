import {readFileSync} from "node:fs";
import {describe,expect,it} from "vitest";
import {detectMatrixIntent} from "../components/matrixIntent";
const rows=readFileSync("../qa/certification/syntax309_cases.jsonl","utf8").trim().split("\n").map(s=>JSON.parse(s));
describe("SY-M-03 real matrix intent",()=>{
 it("extracts the official determinant payload without losing rows or columns",()=>{
  const row=rows.find(r=>r.id==="SY-M-03");
  expect(row.entrada).toBe(String.raw`\begin{vmatrix}1&2\\3&4\end{vmatrix}`);
  expect(row.operacion).toBe("det");
  expect(row.esperado).toBe("-2");
  expect(detectMatrixIntent(row.entrada)).toEqual({kind:"determinant",matrix:[["1","2"],["3","4"]]});
  expect(row.nota).toContain("vmatrix");
 });
 it("treats bars as determinant without a prefix while brackets remain a literal",()=>{
  const bars=String.raw`\begin{vmatrix}1&2\\3&4\end{vmatrix}`;
  expect(detectMatrixIntent(bars)?.kind).toBe("determinant");
  expect(detectMatrixIntent(bars.replaceAll("vmatrix","bmatrix"))?.kind).toBe("literal");
  expect(detectMatrixIntent(bars+"+1")).toBeNull();
  expect(detectMatrixIntent(bars.replace("\\end{vmatrix}","\\end{pmatrix}"))).toBeNull();
 });
 it("rejects ragged rows inside determinant bars",()=>{
  expect(()=>detectMatrixIntent(String.raw`\begin{vmatrix}1&2\\3\end{vmatrix}`)).toThrow();
 });
});
