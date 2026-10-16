import {describe,expect,it} from "vitest";
import {readFileSync} from "node:fs";
import {detectMatrixIntent} from "../components/matrixIntent";
const source=readFileSync("../qa/certification/syntax309_cases.jsonl","utf8");
const original=String.raw`\left\lvert A\right\rvert`;
describe("SY-M-16 bars resolve by declared local type",()=>{
 it("asks for a type for the official unbound name",()=>{
  const row=source.trim().split("\n").map(s=>JSON.parse(s)).find(r=>r.id==="SY-M-16");
  expect(row.entrada).toBe(original);
  expect(row.operacion).toBe("convencion");
  expect(row.esperado).toContain("si es escalar");
  expect(()=>detectMatrixIntent(original)).toThrow(/tipo.*matriz.*determinante.*escalar.*valor absoluto/);
 });
 it("selects operations from local matrix and scalar types",()=>{
  expect(detectMatrixIntent(original+String.raw`\ \text{con}\ A=\begin{pmatrix}1&2\\3&4\end{pmatrix}`)).toEqual({kind:"determinant",matrix:[["1","2"],["3","4"]]});
  expect(detectMatrixIntent(original+String.raw`\ \text{con}\ A=-3`)).toEqual({kind:"absolute",scalar:"-3"});
  expect(()=>detectMatrixIntent(original)).toThrow(/tipo/);
 });
 it("rejects a different declared name and preserves ordinary numeric abs routing",()=>{
  expect(()=>detectMatrixIntent(original+String.raw`\ \text{con}\ B=-3`)).toThrow(/nombre/);
  expect(detectMatrixIntent(String.raw`\left\lvert-3\right\rvert`)).toBeNull();
 });
});
