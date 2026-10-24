import { describe, expect, it } from "vitest";
import { splitSystemLatex } from "../components/systemSplit";

const expected=["x+y=3","x-y=1"];

describe("IN625 E2b — sistemas equivalentes",()=>{
  it("EN-MT-11 cases",()=>expect(splitSystemLatex("\\begin{cases}x+y=3\\\\x-y=1\\end{cases}")).toEqual(expected));
  it("EN-MT-12 aligned ignora &",()=>expect(splitSystemLatex("\\begin{aligned}x+y&=3\\\\x-y&=1\\end{aligned}")).toEqual(expected));
  it("EN-MT-13 array equivalente",()=>expect(splitSystemLatex("\\begin{array}{l}x+y=3\\\\x-y=1\\end{array}")).toEqual(expected));
});
