import {readFileSync} from "node:fs";
import {describe,expect,it} from "vitest";
import {latexToBackendSyntax} from "../components/NaturalMathField";
const row=readFileSync("../qa/certification/syntax309_cases.jsonl","utf8").trim().split("\n").map(s=>JSON.parse(s)).find(r=>r.id==="SY-R-10");
describe("SY-R-10 whole quotient power conversion",()=>{
 it.each([
  [String.raw`\left(\frac{x+1}{x-1}\right)^{2}`,"(x+1)/(x-1)"],
  [String.raw`\left(\frac{y+2}{y-2}\right)^{2}`,"(y+2)/(y-2)"],
  [String.raw`\left(\frac{2x+1}{x-1}\right)^{2}`,"(2x+1)/(x-1)"],
 ])("preserves the full squared base of %s",(source,body)=>{
  if(body==="(x+1)/(x-1)") {expect(row.entrada).toBe(source); expect(row.esperado).toBe(String.raw`\frac{(x+1)^{2}}{(x-1)^{2}}`);}
  const actual=latexToBackendSyntax(source).replace(/\s/g,"");
  console.log("SY-R-10 converted",actual);
  expect(["("+body+")^2","("+body+")^(2)"]).toContain(actual);
 });
});
