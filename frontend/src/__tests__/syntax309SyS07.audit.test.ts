import {readFileSync} from "node:fs";
import {describe,expect,it} from "vitest";
import {latexToBackendSyntax} from "../components/NaturalMathField";
const row=readFileSync("../qa/certification/syntax309_cases.jsonl","utf8").trim().split("\n").map(s=>JSON.parse(s)).find(r=>r.id==="SY-S-07");
describe("SY-S-07 Spanish arcctg",()=>{
 it("converts official scalar alias as one inverse cotangent",()=>{
  expect(row.entrada).toBe(String.raw`\operatorname{arcctg}1`);
  expect(row.esperado).toBe(String.raw`\frac{\pi}{4}`);
  const result=latexToBackendSyntax(row.entrada).replace(/\s/g,"");
  expect(result).toMatch(/^(?:acot|arccot|atan\(1\)|atan\(1\/1\))\(?(?:1)?\)?$/);
  expect(result).not.toContain("arcctg");
 });
});
