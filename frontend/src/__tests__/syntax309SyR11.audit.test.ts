import {describe,expect,it} from "vitest";
import {readFileSync} from "node:fs";
import {detectMatrixIntent} from "../components/matrixIntent";
const fixture=readFileSync("../qa/certification/syntax309_cases.jsonl","utf8");
const source=String.raw`\begin{pmatrix}-2&1\\\frac{3}{2}&-\frac{1}{2}\end{pmatrix}`;
const b=[[1,2],[3,4]];
const identity=[[2,0],[0,2]];
function numeratorOverTwo(cell:string):number {
 const f=/^(-?)\\frac\{(\d+)\}\{2\}$/.exec(cell);
 if(f)return (f[1]==="-"?-1:1)*Number(f[2]);
 if(!/^-?\d+$/.test(cell))throw Error("non-rational matrix cell: "+cell);
 return 2*Number(cell);
}
function product(a:number[][],c:number[][]):number[][] {
 return a.map(row=>c[0].map((_,j)=>row.reduce((sum,value,k)=>sum+value*c[k][j],0)));
}
describe("SY-R-11 official matrix inverse, exact integer-scaled oracle",()=>{
 it("preserves all source cells and proves both orders yield identity",()=>{
  const row=fixture.trim().split("\n").map(s=>JSON.parse(s)).find(r=>r.id==="SY-R-11");
  expect(row.entrada).toBe(source); expect(row.esperado).toContain("identidad");
  const parsed=detectMatrixIntent(row.entrada);
  expect(parsed?.kind).toBe("literal");
  if(!parsed||parsed.kind!=="literal")throw Error("matrix intent missing");
  const a=parsed.matrix.map(r=>r.map(numeratorOverTwo));
  expect(a).toEqual([[-4,2],[3,-1]]);
  expect(product(a,b)).toEqual(identity);
  expect(product(b,a)).toEqual(identity);
 });
 it("fails exact identity when a sign or numerator changes",()=>{
  expect(product([[-4,2],[3,1]],b)).not.toEqual(identity);
  expect(product([[-4,2],[2,-1]],b)).not.toEqual(identity);
 });
});
