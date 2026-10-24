import {readFileSync} from "node:fs";
import {describe,expect,it} from "vitest";
import {latexToBackendSyntax} from "../components/NaturalMathField";
const rows=readFileSync("../qa/certification/syntax309_cases.jsonl","utf8").trim().split("\n").map(s=>JSON.parse(s));
describe("SY-Q-21 real leq conversion",()=>{
 it("keeps the non-strict operator from the official source",()=>{
  const row=rows.find(r=>r.id==="SY-Q-21");
  expect(row.entrada).toBe("x\\leq2");
  expect(latexToBackendSyntax(row.entrada).replace(/\s/g,"")).toBe("x<=2");
 });
 it("does not turn strict or reversed comparisons into equality",()=>{
  expect(latexToBackendSyntax("x<2").replace(/\s/g,"")).toBe("x<2");
  expect(latexToBackendSyntax("2\\geq x").replace(/\s/g,"")).toBe("2>=x");
 });
});
