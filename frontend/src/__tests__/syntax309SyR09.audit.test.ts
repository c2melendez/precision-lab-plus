import {readFileSync} from "node:fs";
import {describe, expect, it} from "vitest";
import {latexToBackendSyntax} from "../components/NaturalMathField";
import {detectCalculusIntent} from "../components/calculusIntent";
const row = readFileSync("../qa/certification/syntax309_cases.jsonl","utf8").trim().split("\n").map(s=>JSON.parse(s)).find(r=>r.id==="SY-R-09");
describe("SY-R-09 original antiderivative and derivative routing", () => {
 it.each([["x",3],["y",4]])("preserves the complete %s polynomial and C", (variable, power) => {
  const source = String.raw`\frac{` + variable + "^{" + power + "}}{" + power + "}+C";
  if(variable==="x") {expect(row.entrada).toBe(source); expect(row.esperado).toBe("al derivar da `x^{2}`");}
  const actual = latexToBackendSyntax(source).replace(/\s/g,"");
  console.log("SY-R-09 converted",actual);
  const term = variable+"^"+power;
  expect(actual).toBe("("+term+")/("+power+")+C");
 });
 it("extracts explicit x and the full unchanged antiderivative body", () => {
  const intent = detectCalculusIntent(String.raw`\frac{d}{dx}\left(` + row.entrada + String.raw`\right)`);
  expect(intent).toEqual({kind:"derivative", variable:"x", order:1, innerLatex:row.entrada});
 });
});
