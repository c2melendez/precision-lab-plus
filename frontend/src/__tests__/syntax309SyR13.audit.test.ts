import {readFileSync} from "node:fs";
import {describe,expect,it} from "vitest";
import {latexToBackendSyntax} from "../components/NaturalMathField";
const row=readFileSync("../qa/certification/syntax309_cases.jsonl","utf8").trim().split("\n").map(s=>JSON.parse(s)).find(r=>r.id==="SY-R-13");
describe("SY-R-13 converter retains cube-root index and binding",()=>{
 it("pins the fixture and exposes the exact HTTP witness",()=>{
  expect(row.entrada).toBe(String.raw`\sqrt[3]{x}\ \text{con}\ x=27`);
  expect(row.esperado).toBe("3");
  const actual=latexToBackendSyntax(row.entrada);
  console.log("SY-R-13 HTTP WITNESS",actual);
  expect(actual.replace(/\s/g,"")).toBe("((x)**(1/(3)))conx=(27)");
 });
 it.each([
  [String.raw`\sqrt[3]{x}\ \text{con}\ x=8`,"x","8"],
  [String.raw`\sqrt[3]{y}\ \text{con}\ y=64`,"y","64"],
 ])("preserves changed source %s",(source,variable,value)=>{
  const pieces=latexToBackendSyntax(source).split(/\s+con\s+/);
  expect(pieces).toHaveLength(2);
  expect(pieces[0].replace(/[()\s]/g,"")).toBe(variable+"**1/3");
  expect(pieces[1].replace(/[()\s]/g,"")).toBe(variable+"="+value);
 });
});
