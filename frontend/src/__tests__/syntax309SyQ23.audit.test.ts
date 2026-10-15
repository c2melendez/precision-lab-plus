import {readFileSync} from "node:fs";
import {describe,expect,it} from "vitest";
import {latexToBackendSyntax} from "../components/NaturalMathField";
const rows=readFileSync("../qa/certification/syntax309_cases.jsonl","utf8").trim().split("\n").map(s=>JSON.parse(s));
describe("SY-Q-23 real Unicode conversion",()=>{
 it("converts the original Unicode greater-or-equal operator",()=>{
  const row=rows.find(r=>r.id==="SY-Q-23");
  expect(row.entrada).toBe("x≥1");
  expect(row.nota).toContain("Unicode");
  expect(latexToBackendSyntax(row.entrada).replace(/\s/g,"")).toBe("x>=1");
 });
 it("keeps equality and strict comparison distinct",()=>{
  expect(latexToBackendSyntax("1≤x").replace(/\s/g,"")).toBe("1<=x");
  expect(latexToBackendSyntax("x>1").replace(/\s/g,"")).toBe("x>1");
 });
});
