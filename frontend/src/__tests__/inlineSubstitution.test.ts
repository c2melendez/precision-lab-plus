import { describe, expect, it } from "vitest";

import { extractInlineSubstitution } from "../components/inlineSubstitution";

describe("extractInlineSubstitution", () => {
  it("separa una raíz cúbica y su vínculo inline", () => {
    expect(extractInlineSubstitution("\\sqrt[3]{x}\\ \\text{con}\\ x=27")).toEqual({
      expressionLatex: "\\sqrt[3]{x}",
      variable: "x",
      valueLatex: "27",
    });
  });

  it("conserva valores negativos y expresiones compuestas con valor absoluto", () => {
    expect(extractInlineSubstitution("\\left\\lvert x\\right\\rvert+x\\ \\text{con}\\ x=-4")).toEqual({
      expressionLatex: "\\left\\lvert x\\right\\rvert+x",
      variable: "x",
      valueLatex: "-4",
    });
  });

  it("acepta la variante \\mathrm{con}", () => {
    expect(extractInlineSubstitution("x+1\\mathrm{con}x=3")).toEqual({
      expressionLatex: "x+1",
      variable: "x",
      valueLatex: "3",
    });
  });

  it("no interpreta ecuaciones ordinarias ni vínculos incompletos como sustituciones", () => {
    expect(extractInlineSubstitution("2x+3=7")).toBeNull();
    expect(extractInlineSubstitution("x\\text{con}x=")).toBeNull();
    expect(extractInlineSubstitution("x\\text{con}x=2=y")).toBeNull();
  });
});
