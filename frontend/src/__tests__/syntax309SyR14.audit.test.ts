import {readFileSync} from "node:fs";
import {describe,expect,it} from "vitest";
import {latexToBackendSyntax} from "../components/NaturalMathField";
const row=readFileSync("../qa/certification/syntax309_cases.jsonl","utf8").trim().split("\n").map(s=>JSON.parse(s)).find(r=>r.id==="SY-R-14");
describe("SY-R-14 converter preserves absolute value and signed binding",()=>{
 it("pins the official fixture and exposes the HTTP witness",()=>{
  expect(row.entrada).toBe(String.raw`\left\lvert x\right\rvert\ \text{con}\ x=-4`);
  expect(row.esperado).toBe("4");
  const actual=latexToBackendSyntax(row.entrada);
  console.log("SY-R-14 HTTP WITNESS",actual);
  const pieces=actual.split(/\s+con\s+/);
  expect(pieces).toHaveLength(2);
  expect(pieces[0].replace(/[()\s]/g,"")).toBe("absx");
  expect(pieces[1].replace(/[()\s]/g,"")).toBe("x=-4");
 });
 it.each([
  [String.raw`\left\lvert y\right\rvert\ \text{con}\ y=-7`,"absy","y=-7"],
  [String.raw`\left\lvert x\right\rvert+x\ \text{con}\ x=-4`,"absx+x","x=-4"],
  [String.raw`\left\lvert x\right\rvert+x\ \text{con}\ x=4`,"absx+x","x=4"],
 ])("retains operator and sign in %s",(source,body,binding)=>{
  const pieces=latexToBackendSyntax(source).split(/\s+con\s+/);
  expect(pieces).toHaveLength(2);
  expect(pieces[0].replace(/[()\s]/g,"")).toBe(body);
  expect(pieces[1].replace(/[()\s]/g,"")).toBe(binding);
 });
});
