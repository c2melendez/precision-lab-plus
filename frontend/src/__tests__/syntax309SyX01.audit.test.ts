import {readFileSync} from "node:fs";
import {describe,expect,it} from "vitest";
import {latexToBackendSyntax} from "../components/NaturalMathField";
const row=readFileSync("../qa/certification/syntax309_cases.jsonl","utf8").trim().split("\n").map(s=>JSON.parse(s)).find(r=>r.id==="SY-X-01");
describe("SY-X-01 converter keeps empty input empty and recovers",()=>{
 it("pins the fixture as a description of an empty field",()=>{
  expect(row.entrada).toBe("*(vacía)*");
  expect(row.operacion).toBe("error");
  expect(row.esperado).toBe('sin cambios o aviso "entrada vacía"; sin error interno');
 });
 it("does not fabricate an expression or retain the previous conversion",()=>{
  for(let pass=0;pass<2;pass++){
   expect(latexToBackendSyntax("")).toBe("");
   expect(latexToBackendSyntax("2+3").replace(/\s/g,"")).toBe("2+3");
  }
  expect(latexToBackendSyntax("")).toBe("");
 });
});
