import {readFileSync} from "node:fs";
import {describe,expect,it} from "vitest";
import {latexToBackendSyntax} from "../components/NaturalMathField";
const row=readFileSync("../qa/certification/syntax309_cases.jsonl","utf8").trim().split("\n").map(s=>JSON.parse(s)).find(r=>r.id==="SY-X-02");
describe("SY-X-02 converter preserves spacing-only emptiness",()=>{
 it("pins the raw fixture",()=>{
  expect(row.entrada).toBe("\\ ".repeat(4));
  expect(row.operacion).toBe("error");
  expect(row.esperado).toBe("igual que la entrada vacía");
 });
 it.each(["\\ ".repeat(4)," \t\n",String.raw`\ `])("converts %j to the empty HTTP witness and recovers",input=>{
  const actual=latexToBackendSyntax(input);
  console.log("SY-X-02 CONVERTER",JSON.stringify({input,actual}));
  expect(actual).toBe("");
  expect(latexToBackendSyntax(String.raw`2\ +\ 3`).replace(/\s/g,"")).toBe("2+3");
  expect(latexToBackendSyntax(input)).toBe("");
 });
});
