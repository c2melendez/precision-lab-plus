import { describe, expect, it } from "vitest";
import { splitFreeSystemLatex, splitSystemLatex } from "../components/systemSplit";

describe("splitSystemLatex", () => {
  it("splits a cases environment into equation rows", () => {
    expect(
      splitSystemLatex("\\begin{cases}x+y=1\\\\x-y=0\\end{cases}"),
    ).toEqual(["x+y=1", "x-y=0"]);
  });

  it("splits aligned environments", () => {
    expect(
      splitSystemLatex("\\begin{aligned}a&=1\\\\b&=2\\end{aligned}"),
    ).toEqual(["a=1", "b=2"]);
  });

  it("requires at least two non-empty rows", () => {
    expect(splitSystemLatex("\\begin{cases}x=1\\end{cases}")).toBeNull();
    expect(splitSystemLatex("\\begin{cases}\\\\x=1\\end{cases}")).toBeNull();
  });

  it("rejects numeric array environments without relations", () => {
    expect(splitSystemLatex("\\begin{array}{cc}1&2\\\\3&4\\end{array}")).toBeNull();
    expect(splitSystemLatex("\\begin{array}{c}1\\\\2\\end{array}")).toBeNull();
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
  });

  it("returns null when there is no system environment", () => {
    expect(splitSystemLatex("x+y=1")).toBeNull();
    expect(splitSystemLatex("")).toBeNull();
  });

  it("strips alignment ampersands from cases rows", () => {
    expect(
      splitSystemLatex("\\begin{cases}x+y&=1\\\\x-y&=0\\end{cases}"),
    ).toEqual(["x+y=1", "x-y=0"]);
  });
});

describe("splitFreeSystemLatex", () => {
  it("splits semicolon-separated equations", () => {
    expect(splitFreeSystemLatex("x+y=1; x-y=0")).toEqual(["x+y=1", "x-y=0"]);
  });

  it("splits newline-separated equations", () => {
    expect(splitFreeSystemLatex("x=1\ny=2")).toEqual(["x=1", "y=2"]);
  });

  it("splits top-level comma between two equations", () => {
    expect(splitFreeSystemLatex("x=1, y=2")).toEqual(["x=1", "y=2"]);
  });

  it("splits text{y} conjunction", () => {
    expect(splitFreeSystemLatex("x=1\\text{ y }y=2")).toEqual(["x=1", "y=2"]);
  });

  it("rejects a single equation", () => {
    expect(splitFreeSystemLatex("x=1")).toBeNull();
  });

  it("rejects empty input", () => {
    expect(splitFreeSystemLatex("   ")).toBeNull();
    expect(splitFreeSystemLatex("")).toBeNull();
  });

  it("rejects three free equations (only pairs)", () => {
    expect(splitFreeSystemLatex("x=1; y=2; z=3")).toBeNull();
  });
});
