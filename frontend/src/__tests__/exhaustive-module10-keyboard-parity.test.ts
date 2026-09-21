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
  it("todo KeyDef visible tiene etiqueta y las teclas semánticas tienen tooltip descriptivo", () => {
    const missing: string[] = [];
    for (const key of allKeys) {
      expect(key.ariaLabel.trim()).not.toBe("");
      if (!structuralLabels.has(key.ariaLabel) && !key.description?.trim()) missing.push(key.ariaLabel);
    }
    expect(missing).toEqual([]);
  });

  it("Productoria Π cumple el requisito actualizado: activa y con plantilla real", () => {
    const product = keyByLabel("productoria");
    expect(product).toBeDefined();
    expect(product?.unavailable).toBeFalsy();
    expect(product?.insertLatex.trim()).not.toBe("");
  });

  it("normaliza grados y DMS a radianes", () => {
    expect(latexToBackendSyntax("90°")).toMatch(/90.*pi.*180/);
    expect(latexToBackendSyntax("45°30′")).toMatch(/45.*30.*60.*pi.*180/);
    expect(latexToBackendSyntax("45°30′15″")).toMatch(/45.*30.*60.*15.*3600.*pi.*180/);
  });

  it("normaliza inversas trigonométricas y logaritmo con base desde la plantilla real", () => {
    expect(latexToBackendSyntax("\\sin^{-1}\\left(0.5\\right)")).toMatch(/^(?:asin|arcsin)\(0\.5\)$/);
    expect(latexToBackendSyntax("\\csc^{-1}\\left(2\\right)")).toMatch(/^(?:acsc|arccsc)\(2\)$/);
    expect(latexToBackendSyntax("\\log_{2}\\left(8\\right)")).toBe("log(8,2)");
  });

  it("normaliza funciones \mathrm usadas por teclas Álgebra/Complejos como identificadores únicos", () => {
    expect(latexToBackendSyntax("\\mathrm{sign}\\left(-4\\right)")).toBe("sign(-4)");
    expect(latexToBackendSyntax("\\mathrm{root}\\left(27,3\\right)")).toBe("root(27,3)");
    expect(latexToBackendSyntax("\\mathrm{log}\\left(-1\\right)")).toBe("log(-1)");
  });

  it("la tecla porcentaje conserva semántica de porcentaje, no módulo", () => {
    const normalized = latexToBackendSyntax("50\\%");
    expect(normalized).not.toContain("%");
    expect(normalized).toMatch(/50.*100/);
  });

  it("la tecla ± normaliza a la operación dedicada pm()", () => {
    expect(latexToBackendSyntax("\\pm\\left(5\\right)")).toBe("pm(5)");
  });

  it("las únicas divergencias unavailable aceptadas en Plus no incluyen Productoria", () => {
    const unavailable = allKeys.filter((k) => k.unavailable).map((k) => k.ariaLabel);
    expect(unavailable).not.toContain("productoria");
    expect(unavailable).not.toContain("derivada parcial");
    expect(unavailable).not.toContain("residuo en un polo (funciones racionales)");
    expect(unavailable).not.toContain("singularidades (funciones racionales)");
  });
});
