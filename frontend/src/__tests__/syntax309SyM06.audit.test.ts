import {readFileSync} from "node:fs";
import {describe,expect,it} from "vitest";
import {detectMatrixIntent} from "../components/matrixIntent";
const rows=readFileSync("../qa/certification/syntax309_cases.jsonl","utf8").trim().split("\n").map(s=>JSON.parse(s));
describe("SY-M-06 real matrix intent",()=>{
 it("extracts the official determinant payload without losing rows or columns",()=>{
  const row=rows.find(r=>r.id==="SY-M-06");
  expect(row.entrada).toBe(String.raw`\det[[1,2],[3,4]]`);
  expect(row.operacion).toBe("det");
  expect(row.esperado).toBe("-2");
  expect(detectMatrixIntent(row.entrada)).toEqual({kind:"determinant",matrix:[["1","2"],["3","4"]]});
 });
 it("parses sized numeric lists without executing expressions",()=>{
  expect(detectMatrixIntent("[[1,2],[3,4]]")).toEqual({kind:"literal",matrix:[["1","2"],["3","4"]]});
  expect(detectMatrixIntent(String.raw`\det\left[\left[1,2\right],\left[3,4\right]\right]`)).toEqual({kind:"determinant",matrix:[["1","2"],["3","4"]]});
  expect(()=>detectMatrixIntent("\\det[[1,2],[3]]")).toThrow();
  for(const bad of ["\\det[[1,2],[3,4]","\\det[[1,2],[3,4]]+1","\\det[[x,2],[3,4]]","\\det[[1,2],[3,alert(1)]]","\\det[[1,,2],[3,4]]"]) {
   expect(detectMatrixIntent(bad)).toBeNull();
  }
 });
});
