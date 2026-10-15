import {readFileSync} from "node:fs";
import {describe,expect,it} from "vitest";
import {detectMatrixIntent} from "../components/matrixIntent";
const rows=readFileSync("../qa/certification/syntax309_cases.jsonl","utf8").trim().split("\n").map(s=>JSON.parse(s));
describe("SY-M-04 real matrix intent",()=>{
 it("extracts the official determinant payload without losing rows or columns",()=>{
  const row=rows.find(r=>r.id==="SY-M-04");
  expect(row.entrada).toBe(String.raw`\det\begin{array}{cc}1&2\\3&4\end{array}`);
  expect(row.operacion).toBe("det");
  expect(row.esperado).toBe("-2");
  expect(detectMatrixIntent(row.entrada)).toEqual({kind:"determinant",matrix:[["1","2"],["3","4"]]});
 });
 it("keeps plain arrays as literals and validates the column specification",()=>{
  const array=String.raw`\begin{array}{cc}1&2\\3&4\end{array}`;
  expect(detectMatrixIntent(array)?.kind).toBe("literal");
  expect(detectMatrixIntent("\\det"+array+"+1")).toBeNull();
  expect(()=>detectMatrixIntent("\\det"+array.replace("{cc}","{c}"))).toThrow();
  expect(()=>detectMatrixIntent("\\det"+array.replace("3&4","3"))).toThrow();
  expect(detectMatrixIntent(array.replace("{cc}","{cr}"))?.kind).toBe("literal");
  expect(detectMatrixIntent(array.replace("{cc}","{xx}"))).toBeNull();
  expect(detectMatrixIntent(array.replace("\\end{array}","\\end{pmatrix}"))).toBeNull();
 });
});
