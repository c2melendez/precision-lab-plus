import {readFileSync} from "node:fs";
import {expect,it} from "vitest";
import {latexToBackendSyntax} from "../components/NaturalMathField";
const row=readFileSync("../qa/certification/syntax309_cases.jsonl","utf8").trim().split("\n").map(s=>JSON.parse(s)).find(r=>r.id==="SY-X-17");
it("rejects the original shell escape before MathLive can turn it into a product",()=>{
  expect(row.entrada).toBe(String.raw`\write18{ls}`);
  expect(row.esperado).toBe("ignorado o rechazado; sin ejecución");
  expect(()=>latexToBackendSyntax(row.entrada)).toThrow(/Comando.*no permitido/i);
  expect(latexToBackendSyntax("2+3").replace(/\s/g,"")).toBe("2+3");
});
