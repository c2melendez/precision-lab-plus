import {describe,expect,it} from "vitest";
import {readFileSync} from "node:fs";
import {detectMatrixIntent} from "../components/matrixIntent";
const source=readFileSync("../qa/certification/syntax309_cases.jsonl","utf8");
describe("SY-M-11 explicit matrix-vector dot product",()=>{
 it("extracts the official dot payload",()=>{
  const row=source.trim().split("\n").map(s=>JSON.parse(s)).find(r=>r.id==="SY-M-11");
  expect(row.entrada).toBe("\\langle1,2,3\\rangle\\cdot\\langle4,5,6\\rangle");
  expect(row.operacion).toBe("vectores");
  expect(row.esperado).toBe("32");
  const intent=detectMatrixIntent(row.entrada);
  expect(intent).toEqual({kind:"dot",left:[["1","2","3"]],right:[["4","5","6"]]});
 });
 it("keeps ordinary adjacency as matrix multiplication",()=>{
  expect(detectMatrixIntent(String.raw`\begin{pmatrix}1&2\end{pmatrix}\begin{pmatrix}3\\4\end{pmatrix}`)?.kind).toBe("multiply");
 });
 it("rejects unequal lengths or nonvector matrices",()=>{
  for(const input of [
   String.raw`\begin{pmatrix}1\\2\end{pmatrix}\cdot\begin{pmatrix}3\end{pmatrix}`,
   String.raw`\begin{pmatrix}1&2\\3&4\end{pmatrix}\cdot\begin{pmatrix}1\\2\end{pmatrix}`
  ])expect(()=>detectMatrixIntent(input)).toThrow(/vectores/);
 }); it("validates angle components and paired sized delimiters",()=>{
  expect(detectMatrixIntent(String.raw`\left\langle1,2,3\right\rangle\cdot\left\langle4,5,6\right\rangle`)).toEqual({kind:"dot",left:[["1","2","3"]],right:[["4","5","6"]]});
  expect(()=>detectMatrixIntent(String.raw`\langle1,,3\rangle\cdot\langle4,5,6\rangle`)).toThrow(/componentes/);
  expect(()=>detectMatrixIntent(String.raw`\langle1,2\rangle\cdot\langle4,5,6\rangle`)).toThrow(/misma longitud/);
  expect(detectMatrixIntent(String.raw`\left\langle1,2,3\rangle\cdot\langle4,5,6\rangle`)).toBeNull();
 });

});
