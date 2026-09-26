import { describe, expect, it } from "vitest";

import { getAvailableResultFormats } from "../components/resultFormatPolicy";

describe("S26 Bloque 4 — política de formatos de resultado", () => {
  it("mantiene Exacto como formato base", () => {
    expect(getAvailableResultFormats({
      hasExact: true,
      hasDecimal: false,
      hasFraction: false,
      hasDms: false,
    })).toEqual(["exact"]);
  });

  it("habilita Decimal y Científica solo con valor numérico", () => {
    expect(getAvailableResultFormats({
      hasExact: true,
      hasDecimal: true,
      hasFraction: false,
      hasDms: false,
    })).toEqual(["exact", "dec", "scn"]);
  });

  it("habilita Fracción solo con forma racional exacta", () => {
    expect(getAvailableResultFormats({
      hasExact: true,
      hasDecimal: true,
      hasFraction: true,
      hasDms: false,
    })).toEqual(["exact", "dec", "frac", "scn"]);
  });

  it("habilita DMS solo para salida angular aplicable", () => {
    expect(getAvailableResultFormats({
      hasExact: true,
      hasDecimal: true,
      hasFraction: false,
      hasDms: true,
    })).toEqual(["exact", "dec", "scn", "dms"]);
  });
});
