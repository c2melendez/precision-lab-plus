import {readFileSync} from "node:fs";
import {describe,expect,it} from "vitest";
import {latexToBackendSyntax} from "../components/NaturalMathField";
const row=readFileSync("../qa/certification/syntax309_cases.jsonl","utf8").trim().split("\n").map(s=>JSON.parse(s)).find(r=>r.id==="SY-X-03");
describe("SY-X-03 converter does not erase invalid literal backslashes",()=>{
 it("pins the original fixture",()=>{
  expect(row.entrada).toBe("\\".repeat(2));
  expect(row.entrada).toHaveLength(2);
  expect(row.operacion).toBe("error");
  expect(row.esperado).toBe("error claro de sintaxis");
 });
 it.each(["\\".repeat(2),"\\","\n"+"\\".repeat(2)+"\t"])("rejects or preserves invalid syntax %j, then recovers",input=>{
  let actual:string|undefined;
  let failure:any;
  try{actual=latexToBackendSyntax(input);}catch(error){failure=error;}
  console.log("SY-X-03 CONVERTER",JSON.stringify({input,actual,error:failure?.message}));
  if(failure){
   expect(failure.message).toMatch(/sintaxis|carácter|comando|interpretar|barra/i);
   expect(failure.message).not.toMatch(/vacía|antes de calcular/i);
  }else{
   expect(actual?.trim()).not.toBe("");
   expect(actual).toMatch(/\\/);
  }
  expect(latexToBackendSyntax("\\ ".repeat(4))).toBe("");
  expect(latexToBackendSyntax("2+3").replace(/\s/g,"")).toBe("2+3");
 });
});
