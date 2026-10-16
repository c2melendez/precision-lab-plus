import {readFileSync} from "node:fs";
import {describe,expect,it} from "vitest";
import {latexToBackendSyntax} from "../components/NaturalMathField";
const rows=readFileSync("../qa/certification/syntax309_cases.jsonl","utf8").trim().split("\n").map(s=>JSON.parse(s));
describe("SY-S-02 real Spanish tangent conversion",()=>{
 it("maps the whole official argument to tangent, without free alias symbols",()=>{
  const row=rows.find(r=>r.id==="SY-S-02");
  expect(row.entrada).toBe(String.raw`\operatorname{tg}\frac{\pi}{4}`);
  const expression=latexToBackendSyntax(row.entrada).replace(/\s/g,"");
  expect(expression).toBe("tan((pi)/(4))");
  expect(expression).not.toMatch(/tg|operatorname/);
  expect(expression).toContain("pi");
  expect(expression).toContain("4");
  expect(latexToBackendSyntax(row.esperado).replace(/\s/g,"")).toBe("1");
 });
 it("gives the same conversion for explicit grouping",()=>{
  const row=rows.find(r=>r.id==="SY-S-02");
  const grouped=String.raw`\operatorname{tg}\left(\frac{\pi}{4}\right)`;
  expect(latexToBackendSyntax(grouped).replace(/\s/g,"")).toBe(latexToBackendSyntax(row.entrada).replace(/\s/g,""));
 });
});
