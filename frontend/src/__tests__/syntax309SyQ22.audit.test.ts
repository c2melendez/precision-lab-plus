import {readFileSync} from "node:fs";
import {describe,expect,it} from "vitest";
import {latexToBackendSyntax} from "../components/NaturalMathField";
const rows=readFileSync("../qa/certification/syntax309_cases.jsonl","utf8").trim().split("\n").map(s=>JSON.parse(s));
describe("SY-Q-22 real ASCII conversion",()=>{
 it("preserves both characters of the original <= operator",()=>{
  const row=rows.find(r=>r.id==="SY-Q-22");
  expect(row.entrada).toBe("x<=2");
  expect(row.nota).toContain("ASCII");
  expect(latexToBackendSyntax(row.entrada).replace(/\s/g,"")).toBe("x<=2");
 });
 it("keeps equality and strict comparison distinct",()=>{
  expect(latexToBackendSyntax("x=2").replace(/\s/g,"")).toBe("x=2");
  expect(latexToBackendSyntax("x<2").replace(/\s/g,"")).toBe("x<2");
 });
});
