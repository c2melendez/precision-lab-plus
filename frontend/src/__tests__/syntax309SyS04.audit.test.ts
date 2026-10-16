import {readFileSync} from "node:fs";
import {describe,expect,it} from "vitest";
import {latexToBackendSyntax} from "../components/NaturalMathField";
const rows=readFileSync("../qa/certification/syntax309_cases.jsonl","utf8").trim().split("\n").map(s=>JSON.parse(s));
describe("SY-S-04 Spanish cosecant alias",()=>{
 it("binds whole official fractional argument",()=>{
  const row=rows.find(r=>r.id==="SY-S-04");
  expect(row.entrada).toBe(String.raw`\operatorname{cosec}\frac{\pi}{6}`);
  expect(row.esperado).toBe("2");
  expect(latexToBackendSyntax(row.entrada).replace(/\s/g,"")).toBe("csc((pi)/(6))");
 });
 it("converts grouped equivalent consistently",()=>{
  const official=String.raw`\operatorname{cosec}\frac{\pi}{6}`;
  const grouped=String.raw`\operatorname{cosec}\left(\frac{\pi}{6}\right)`;
  expect(latexToBackendSyntax(grouped).replace(/\s/g,"")).toBe(latexToBackendSyntax(official).replace(/\s/g,""));
 });
});