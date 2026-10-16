import {readFileSync} from "node:fs";
import {describe,expect,it} from "vitest";
import {latexToBackendSyntax} from "../components/NaturalMathField";
const row=readFileSync("../qa/certification/syntax309_cases.jsonl","utf8").trim().split("\n").map(s=>JSON.parse(s)).find(r=>r.id==="SY-S-06");
describe("SY-S-06 Spanish arctg",()=>{
 it("converts official alias to unary inverse tangent",()=>{
  expect(row.entrada).toBe(String.raw`\operatorname{arctg}1`);
  expect(row.esperado).toBe(String.raw`\frac{\pi}{4}`);
  const expression=latexToBackendSyntax(row.entrada).replace(/\s/g,"");
  expect(expression).toMatch(/^(?:atan|arctan)\(1\)$/);
  expect(expression).not.toContain("arctg");
 });
});
