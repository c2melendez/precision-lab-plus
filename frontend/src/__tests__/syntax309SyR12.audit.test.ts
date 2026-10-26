import {readFileSync} from "node:fs";
import {describe,expect,it} from "vitest";
import {latexToBackendSyntax} from "../components/NaturalMathField";
const row=readFileSync("../qa/certification/syntax309_cases.jsonl","utf8").trim().split("\n").map(s=>JSON.parse(s)).find(r=>r.id==="SY-R-12");
describe("SY-R-12 official prose-only input rejection",()=>{
 it("pins the normative case",()=>{
  expect(row.entrada).toBe(String.raw`\text{no existe}`);
  expect(row.operacion).toBe("error");
  expect(row.esperado).toContain("error claro");
 });
 it.each([String.raw`\text{no existe}`,"no existe",String.raw`\mathrm{no existe}`])("rejects invalid source %s",(source)=>{
  expect(()=>latexToBackendSyntax(source)).toThrow(/Entrada no matemática/);
 });
});