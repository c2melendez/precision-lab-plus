import {readFileSync} from "node:fs";
import {describe,expect,it} from "vitest";
import {latexToBackendSyntax} from "../components/NaturalMathField";
const rows=readFileSync("../qa/certification/syntax309_cases.jsonl","utf8").trim().split("\n").map(s=>JSON.parse(s));
describe("SY-S-01 real Spanish sine conversion",()=>{
 it("maps the whole official argument to sine, without free alias symbols",()=>{
  const row=rows.find(r=>r.id==="SY-S-01");
  expect(row.entrada).toBe(String.raw`\operatorname{sen}\frac{\pi}{6}`);
  const expression=latexToBackendSyntax(row.entrada).replace(/\s/g,"");
  expect(expression).toBe("sin((pi)/(6))");
  expect(expression).not.toMatch(/sen|operatorname/);
  expect(expression).toContain("pi");
  expect(expression).toContain("6");
  expect(latexToBackendSyntax(row.esperado).replace(/\s/g,"")).toMatch(/1.*\/.*2/);
 });
 it("gives the same conversion for explicit grouping",()=>{
  const row=rows.find(r=>r.id==="SY-S-01");
  const grouped=String.raw`\operatorname{sen}\left(\frac{\pi}{6}\right)`;
  expect(latexToBackendSyntax(grouped).replace(/\s/g,"")).toBe(latexToBackendSyntax(row.entrada).replace(/\s/g,""));
 });
});
