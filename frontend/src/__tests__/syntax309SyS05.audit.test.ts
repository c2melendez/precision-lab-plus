import {readFileSync} from "node:fs";
import {describe,expect,it} from "vitest";
import {latexToBackendSyntax} from "../components/NaturalMathField";
const row=readFileSync("../qa/certification/syntax309_cases.jsonl","utf8").trim().split("\n").map(s=>JSON.parse(s)).find(r=>r.id==="SY-S-05");
describe("SY-S-05 arcsen exact fractional argument",()=>{
 it("converts official alias to one arcsin argument",()=>{
  expect(row.entrada).toBe(String.raw`\operatorname{arcsen}\frac{1}{2}`);
  expect(row.esperado).toBe(String.raw`\frac{\pi}{6}`);
  expect(latexToBackendSyntax(row.entrada).replace(/\s/g,"")).toBe("arcsin((1)/(2))");
 });
 it("preserves grouped equivalent",()=>{
  expect(latexToBackendSyntax(String.raw`\operatorname{arcsen}\left(\frac{1}{2}\right)`).replace(/\s/g,""))
    .toBe(latexToBackendSyntax(row.entrada).replace(/\s/g,""));
 });
});