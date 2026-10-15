import {readFileSync} from "node:fs";
import {describe,expect,it} from "vitest";
import {latexToBackendSyntax} from "../components/NaturalMathField";
const rows=readFileSync("../qa/certification/syntax309_cases.jsonl","utf8").trim().split("\n").map(s=>JSON.parse(s));
describe("SY-Q-20 real source conversion",()=>{
 it("keeps the source as a bare expression until equation intent is explicit",()=>{
  const row=rows.find(r=>r.id==="SY-Q-20");
  expect(row.entrada).toBe(String.raw`x^{2}-4`);
  const converted=latexToBackendSyntax(row.entrada);
  expect(converted).not.toContain("=");
  expect(converted.replace(/\*\*/g,"^").replace(/[()\s]/g,"")).toBe("x^2-4");
 });
 it("preserves visible explicit zero on equation conversion",()=>{
  const converted=latexToBackendSyntax(rows.find(r=>r.id==="SY-Q-20").entrada+"=0");
  expect(converted.split("=")).toHaveLength(2);
  expect(converted.split("=")[1].trim()).toBe("0");
 });
});
