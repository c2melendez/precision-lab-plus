import { describe, expect, it } from "vitest";
import { isKnownEndpoint } from "../api/endpoints";
import type { OperationType } from "../api/client";

describe("Algebra114 AS-PF-01 HTTP frontend contract", () => {
  it("exposes partial fractions in the approved API whitelist and operation type", () => {
    expect(isKnownEndpoint("/partial-fractions")).toBe(true);
    const operation: OperationType = "partial_fractions";
    expect(operation).toBe("partial_fractions");
  });
});
