import {readFileSync} from "node:fs";
import {describe,expect,it} from "vitest";
import {detectMatrixIntent} from "../components/matrixIntent";
import {latexToBackendSyntax} from "../components/NaturalMathField";
const rows=readFileSync("../qa/certification/syntax309_cases.jsonl","utf8").trim().split("\n").map(s=>JSON.parse(s));
describe("SY-M-09 matrix and real cell conversion",()=>{
 it("converts each cell of the official original source",()=>{
  const row=rows.find(r=>r.id==="SY-M-09");
  expect(row.entrada).toBe(String.raw`\det\begin{pmatrix}\frac12&\sqrt2\\\pi&e\end{pmatrix}`);
  const intent=detectMatrixIntent(row.entrada);
  if(!intent||intent.kind!=="determinant")throw Error("missing determinant");
  const cells=intent.matrix.map(row=>row.map(cell=>latexToBackendSyntax(cell).replace(/\s/g,"")));
  expect(cells).toEqual([["(1)/(2)","sqrt(2)"],["pi","e"]]);
 });
});
