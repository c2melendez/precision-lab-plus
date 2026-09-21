import { describe, expect, it } from "vitest";

import { BASIC_V5_ROWS } from "../components/KeyboardBasicPanel";
import {
  CATEGORY_MENUS,
  SYMBOL_CONSTANTS,
  SYMBOL_VARIABLES,
  type KeyDef,
} from "../components/NaturalMathKeyboard";
import { latexToBackendSyntax } from "../components/NaturalMathField";

const allKeys: KeyDef[] = [
  ...BASIC_V5_ROWS.flat(),
  ...SYMBOL_VARIABLES,
  ...SYMBOL_CONSTANTS,
  ...Object.values(CATEGORY_MENUS).flatMap((groups) => groups.flatMap((group) => group.keys)),
];
const keyByLabel = (label: string) => allKeys.find((key) => key.ariaLabel === label);

const structuralLabels = new Set([
  ...Array.from({ length: 10 }, (_, n) => String(n)),
  "paréntesis izquierdo", "paréntesis derecho", "punto decimal",
  "sumar", "restar", "multiplicar", "dividir",
  "menor que", "mayor que", "menor o igual que", "mayor o igual que", "igual",
  "borrar", "borrar todo el campo", "insertar el último resultado", "calcular",
]);

describe("Suite exhaustiva original — Módulo 10: teclado ↔ motor (Plus frontend)", () => {
  it("inventario: etiquetas y tooltips semánticos", () => {
    const missing: string[] = [];
    for (const key of allKeys) {
      expect(key.ariaLabel.trim()).not.toBe("");
      if (!structuralLabels.has(key.ariaLabel) && !key.description?.trim()) missing.push(key.ariaLabel);
    }
    expect(missing).toEqual([]);
  });

  it("Productoria Π cumple el requisito actualizado", () => {
    const product = keyByLabel("productoria");
    expect(product).toBeDefined();
    expect(product?.unavailable).toBeFalsy();
    expect(product?.insertLatex.trim()).not.toBe("");
  });

  it("grados y DMS se normalizan", () => {
    expect(latexToBackendSyntax("90°")).toMatch(/90.*pi.*180/);
    expect(latexToBackendSyntax("45°30′")).toMatch(/45.*30.*60.*pi.*180/);
    expect(latexToBackendSyntax("45°30′15″")).toMatch(/45.*30.*60.*15.*3600.*pi.*180/);
  });

  it.each([
    ["sin inversa", "\\sin^{-1}\\left(0.5\\right)", /^(?:asin|arcsin)\(0\.5\)$/],
    ["cos inversa", "\\cos^{-1}\\left(0.5\\right)", /^(?:acos|arccos)\(0\.5\)$/],
    ["tan inversa", "\\tan^{-1}\\left(1\\right)", /^(?:atan|arctan)\(1\)$/],
    ["csc inversa", "\\csc^{-1}\\left(2\\right)", /^(?:acsc|arccsc)\(2\)$/],
    ["sec inversa", "\\sec^{-1}\\left(2\\right)", /^(?:asec|arcsec)\(2\)$/],
    ["cot inversa", "\\cot^{-1}\\left(1\\right)", /^(?:acot|arccot)\(1\)$/],
  ] as const)("normalización real: %s", (_label, latex, expected) => {
    expect(latexToBackendSyntax(latex)).toMatch(expected);
  });

  it("logaritmo con base real", () => {
    expect(latexToBackendSyntax("\\log_{2}\\left(8\\right)")).toBe("log(8,2)");
  });

  it.each([
    ["sign", "\\mathrm{sign}\\left(-4\\right)", "sign(-4)"],
    ["root complejo", "\\mathrm{root}\\left(27,3\\right)", "root(27,3)"],
    ["Log complejo", "\\mathrm{log}\\left(-1\\right)", "log(-1)"],
  ] as const)("normalización mathrm: %s", (_label, latex, expected) => {
    expect(latexToBackendSyntax(latex)).toBe(expected);
  });

  it("porcentaje conserva semántica de porcentaje", () => {
    const normalized = latexToBackendSyntax("50\\%");
    expect(normalized).not.toContain("%");
    expect(normalized).toMatch(/50.*100/);
  });

  it("± se normaliza a pm()", () => {
    expect(latexToBackendSyntax("\\pm\\left(5\\right)")).toBe("pm(5)");
  });

  it("Plus mantiene activas parcial/Res/Sing y Productoria debe dejar de ser unavailable", () => {
    const unavailable = allKeys.filter((k) => k.unavailable).map((k) => k.ariaLabel);
    for (const label of [
      "productoria",
      "derivada parcial",
      "residuo en un polo (funciones racionales)",
      "singularidades (funciones racionales)",
    ]) expect(unavailable).not.toContain(label);
  });
});
