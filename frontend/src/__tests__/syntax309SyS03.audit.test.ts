import {readFileSync} from "node:fs";
import {describe,expect,it} from "vitest";
import {latexToBackendSyntax} from "../components/NaturalMathField";
const rows=readFileSync("../qa/certification/syntax309_cases.jsonl","utf8").trim().split("\n").map(s=>JSON.parse(s));
describe("SY-S-03 Spanish cotangent alias",()=>{
 it("binds whole official fractional argument",()=>{
  const row=rows.find(r=>r.id==="SY-S-03");
  expect(row.entrada).toBe(String.raw`\operatorname{ctg}\frac{\pi}{4}`);
  expect(row.esperado).toBe("1");
  expect(latexToBackendSyntax(row.entrada).replace(/\s/g,"")).toBe("cot((pi)/(4))");
 });
 it("converts grouped equivalent consistently",()=>{
  const official=String.raw`\operatorname{ctg}\frac{\pi}{4}`;
  const grouped=String.raw`\operatorname{ctg}\left(\frac{\pi}{4}\right)`;
  expect(latexToBackendSyntax(grouped).replace(/\s/g,"")).toBe(latexToBackendSyntax(official).replace(/\s/g,""));
 });
});