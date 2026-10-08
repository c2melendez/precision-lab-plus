import { describe, expect, it } from "vitest";
import { detectRelationIntent } from "../components/relationIntent";

describe("IN625 E3d2 — identities are not relations", () => {
  it.each([
    ["1=1"],
    ["2=3"],
    ["x=x"],
    ["x+1=x"],
    ["\\sin^{2}(x)+\\cos^{2}(x)=1"],
    ["(x+1)^{2}=x^{2}+2x+1"],
  ])("%s remains an algebraic equation", (input) => {
    expect(detectRelationIntent(input)).toBeNull();
  });
});
