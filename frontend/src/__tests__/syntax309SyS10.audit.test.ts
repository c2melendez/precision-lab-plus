import {readFileSync} from "node:fs";
import {describe,expect,it} from "vitest";
import {latexToBackendSyntax} from "../components/NaturalMathField";
const row=readFileSync("../qa/certification/syntax309_cases.jsonl","utf8").trim().split("\n").map(s=>JSON.parse(s)).find(r=>r.id==="SY-S-10");
describe("SY-S-10 argsenh",()=>{
 it("normalizes Spanish hyperbolic sine with its unit argument",()=>{
  expect(row.entrada).toBe(String.raw`\operatorname{argsenh}1`);
  expect(row.esperado).toBe("0.881373587");
  const converted=latexToBackendSyntax(row.entrada).replace(/\s/g,"");
  expect(converted).toMatch(/^asinh\(?1\)?$/);
  expect(converted).not.toContain("argsenh");
 });
});
