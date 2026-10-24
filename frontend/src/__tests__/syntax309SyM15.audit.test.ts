import {describe,expect,it} from "vitest";
import {readFileSync} from "node:fs";
import {detectMatrixIntent} from "../components/matrixIntent";
const source=readFileSync("../qa/certification/syntax309_cases.jsonl","utf8");
describe("SY-M-15 named vector cross convention",()=>{
 it("declares cross-product semantics and missing components for the official source",()=>{
  const row=source.trim().split("\n").map(s=>JSON.parse(s)).find(r=>r.id==="SY-M-15");
  expect(row.entrada).toBe(String.raw`\vec{u}\times\vec{v}`);
  expect(row.operacion).toBe("convencion");
  expect(row.esperado).toContain("producto cruz");
  expect(row.nota).toContain("producto cruz");
  expect(()=>detectMatrixIntent(row.entrada)).toThrow(/producto cruz.*3D.*componentes/);
 });
 it("does not reinterpret ordinary scalar multiplication",()=>{
  expect(detectMatrixIntent(String.raw`2\times3`)).toBeNull();
  expect(()=>detectMatrixIntent(String.raw`\vec{a}\ \times\ \vec{b}`)).toThrow(/producto cruz/);
 });
});
