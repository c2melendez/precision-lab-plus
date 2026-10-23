import { describe, expect, it } from "vitest";
import { splitFreeSystemLatex, splitSystemLatex } from "../components/systemSplit";

describe("splitSystemLatex", () => {
  it("splits a cases environment into equation rows", () => {
    expect(
      splitSystemLatex("\\begin{cases}x+y=1\\\\x-y=0\\end{cases}"),
    ).toEqual(["x+y=1", "x-y=0"]);
  });

  it("splits three-row cases", () => {
    expect(
      splitSystemLatex("\\begin{cases}a=1\\\\b=2\\\\c=3\\end{cases}"),
    ).toEqual(["a=1", "b=2", "c=3"]);
  });

  it("splits aligned environments", () => {
    expect(
      splitSystemLatex("\\begin{aligned}a&=1\\\\b&=2\\end{aligned}"),
    ).toEqual(["a=1", "b=2"]);
  });

  it("requires at least two non-empty rows", () => {
    expect(splitSystemLatex("\\begin{cases}x=1\\end{cases}")).toBeNull();
    expect(splitSystemLatex("\\begin{cases}\\\\x=1\\end{cases}")).toBeNull();
    expect(splitSystemLatex("\\begin{cases}x=1\\\\ \\end{cases}")).toBeNull();
  });

  it("rejects numeric array environments without relations", () => {
    expect(splitSystemLatex("\\begin{array}{cc}1&2\\\\3&4\\end{array}")).toBeNull();
    expect(splitSystemLatex("\\begin{array}{c}1\\\\2\\end{array}")).toBeNull();
    expect(splitSystemLatex("\\begin{array}{cc}a&b\\\\c&d\\end{array}")).toBeNull();
  });

  it("keeps array rows that look like equations", () => {
    expect(
      splitSystemLatex("\\begin{array}{c}x=1\\\\y=2\\end{array}"),
    ).toEqual(["x=1", "y=2"]);
  });

  it("accepts inequality relations in array rows", () => {
    expect(
      splitSystemLatex("\\begin{array}{c}x<1\\\\y>0\\end{array}"),
    ).toEqual(["x<1", "y>0"]);
    expect(
      splitSystemLatex("\\begin{array}{c}x\\leq 1\\\\y\\geq 0\\end{array}"),
    ).toEqual(["x\\leq 1", "y\\geq 0"]);
  });

  it("returns null when there is no system environment", () => {
    expect(splitSystemLatex("x+y=1")).toBeNull();
    expect(splitSystemLatex("")).toBeNull();
    expect(splitSystemLatex("\\begin{matrix}1\\\\2\\end{matrix}")).toBeNull();
  });

  it("strips alignment ampersands from cases rows", () => {
    expect(
      splitSystemLatex("\\begin{cases}x+y&=1\\\\x-y&=0\\end{cases}"),
    ).toEqual(["x+y=1", "x-y=0"]);
  });

  it("ignores column-spec braces on array", () => {
    expect(
      splitSystemLatex("\\begin{array}{rcl}x&=&1\\\\y&=&2\\end{array}"),
    ).toEqual(["x=1", "y=2"]);
  });
});

describe("splitFreeSystemLatex", () => {
  it("splits semicolon-separated equations", () => {
    expect(splitFreeSystemLatex("x+y=1; x-y=0")).toEqual(["x+y=1", "x-y=0"]);
    expect(splitFreeSystemLatex("x=1;y=2")).toEqual(["x=1", "y=2"]);
  });

  it("splits newline-separated equations", () => {
    expect(splitFreeSystemLatex("x=1\ny=2")).toEqual(["x=1", "y=2"]);
    expect(splitFreeSystemLatex("x=1\r\ny=2")).toEqual(["x=1", "y=2"]);
  });

  it("splits top-level comma between two equations", () => {
    expect(splitFreeSystemLatex("x=1, y=2")).toEqual(["x=1", "y=2"]);
  });

  it("does not split commas inside parentheses", () => {
    expect(splitFreeSystemLatex("f(x,y)=1, z=2")).toEqual(["f(x,y)=1", "z=2"]);
  });

  it("splits text{y} conjunction", () => {
    expect(splitFreeSystemLatex("x=1\\text{ y }y=2")).toEqual(["x=1", "y=2"]);
    expect(splitFreeSystemLatex("a=1\\text{y}b=2")).toEqual(["a=1", "b=2"]);
  });

  it("splits bare double-backslash outside environments", () => {
    expect(splitFreeSystemLatex("x=1\\\\y=2")).toEqual(["x=1", "y=2"]);
  });

  it("rejects a single equation", () => {
    expect(splitFreeSystemLatex("x=1")).toBeNull();
    expect(splitFreeSystemLatex("x+y=z")).toBeNull();
  });

  it("rejects empty input", () => {
    expect(splitFreeSystemLatex("   ")).toBeNull();
    expect(splitFreeSystemLatex("")).toBeNull();
  });

  it("rejects three free equations (only pairs)", () => {
    expect(splitFreeSystemLatex("x=1; y=2; z=3")).toBeNull();
  });

  it("rejects rows that are not equations (no single equals)", () => {
    expect(splitFreeSystemLatex("x+y; a+b")).toBeNull();
    expect(splitFreeSystemLatex("x<1; y>0")).toBeNull();
    expect(splitFreeSystemLatex("x==1; y=2")).toBeNull();
  });

  it("rejects free split when a begin environment is present for double-backslash path", () => {
    // double-backslash path is skipped when \\begin{ is present;
    // cases path is handled by splitSystemLatex, not free.
    expect(splitFreeSystemLatex("\\begin{cases}x=1\\\\y=2\\end{cases}")).toBeNull();
  });
});
