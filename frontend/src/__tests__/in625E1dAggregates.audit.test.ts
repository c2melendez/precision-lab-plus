import { describe, expect, it } from "vitest";
import { latexToBackendSyntax } from "../components/NaturalMathField";

const c=(s:string)=>latexToBackendSyntax(s).replace(/\s+/g,"");

describe("IN625 E1d — UI→backend de sumatorias/productorias",()=>{
  it("EN-CA-26 sum k=1..10",()=>expect(c("\\sum_{k=1}^{10}k")).toBe("sum(k,k,1,10)"));
  it("EN-CA-28 sum k^2=1..10",()=>expect(c("\\sum_{k=1}^{10}k^{2}")).toMatch(/^sum\(.*k.*2.*,k,1,10\)$/));
  it("EN-CA-30 prod k=1..5",()=>expect(c("\\prod_{k=1}^{5}k")).toBe("product(k,k,1,5)"));
  it.todo("EN-CA-27 upper bound n requires symbolic aggregate support");
  it.todo("EN-CA-29 infinity requires series support");
  it.todo("EN-CA-31 evaluation bar requires structural support");
  it.todo("EN-CA-32 10^9 upper bound requires closed-form optimization");
});
