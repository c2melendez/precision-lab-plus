import { describe, expect, it } from "vitest";
import { convert } from "../utils/unitConversion";

describe("unitConversion mutation-oriented asserts", () => {
  it("length identity and linear scale are exact", () => {
    expect(convert("length", 1, "m", "m")).toBe(1);
    expect(convert("length", 2, "km", "m")).toBe(2000);
    expect(convert("length", 1000, "mm", "m")).toBe(1);
    expect(convert("length", 1, "in", "m")).toBeCloseTo(0.0254, 12);
  });

  it("mass and time reject inverted arithmetic", () => {
    expect(convert("mass", 2, "kg", "g")).toBe(2000);
    expect(convert("mass", 1, "lb", "kg")).toBeCloseTo(0.45359237, 12);
    expect(convert("time", 2, "h", "s")).toBe(7200);
    expect(convert("time", 1, "min", "s")).toBe(60);
  });

  it("storage base-1000 paths are exact integers", () => {
    expect(convert("storage", 1, "kb", "byte")).toBe(1000);
    expect(convert("storage", 1, "mb", "kb")).toBe(1000);
    expect(convert("storage", 8, "bit", "byte")).toBe(1);
    expect(convert("storage", 1, "byte", "bit")).toBe(8);
  });

  it("temperature formulas are exact at anchors", () => {
    expect(convert("temperature", 0, "c", "f")).toBe(32);
    expect(convert("temperature", 32, "f", "c")).toBe(0);
    expect(convert("temperature", 0, "c", "k")).toBeCloseTo(273.15, 12);
    expect(convert("temperature", 273.15, "k", "c")).toBeCloseTo(0, 12);
    expect(convert("temperature", -40, "c", "f")).toBe(-40);
    expect(convert("temperature", 25, "c", "c")).toBe(25);
  });

  it("invalid units throw with a non-empty diagnostic message", () => {
    expect(() => convert("length", 1, "bogus", "m")).toThrow(/Unidad desconocida/);
    expect(() => convert("length", 1, "m", "bogus")).toThrow(/Unidad desconocida/);
    expect(() => convert("temperature", 1, "bogus", "c")).toThrow(/Unidad de temperatura desconocida/);
    expect(() => convert("temperature", 1, "c", "bogus")).toThrow(/Unidad de temperatura desconocida/);
  });

  it("pressure energy power force sample conversions", () => {
    expect(convert("pressure", 1, "atm", "pa")).toBe(101325);
    expect(convert("energy", 1, "kwh", "j")).toBe(3_600_000);
    expect(convert("power", 1, "kw", "w")).toBe(1000);
    expect(convert("force", 1, "kgf", "n")).toBeCloseTo(9.80665, 12);
  });
});
