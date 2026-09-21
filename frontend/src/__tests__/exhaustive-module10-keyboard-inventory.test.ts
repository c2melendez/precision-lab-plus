import { describe, expect, it } from "vitest";

import { BASIC_V5_ROWS } from "../components/KeyboardBasicPanel";
import {
  CATEGORY_MENUS,
  SYMBOL_CONSTANTS,
  SYMBOL_VARIABLES,
  type KeyDef,
} from "../components/NaturalMathKeyboard";

const allCategoryKeys = Object.values(CATEGORY_MENUS).flatMap((groups) =>
  groups.flatMap((group) => group.keys),
);
const allKeys: KeyDef[] = [
  ...BASIC_V5_ROWS.flat(),
  ...SYMBOL_VARIABLES,
  ...SYMBOL_CONSTANTS,
  ...allCategoryKeys,
];

const ACTION_LABELS = new Set([
  "borrar",
  "borrar todo el campo",
  "insertar el último resultado",
  "calcular",
  "graficar en el plano de Argand",
]);

describe("Suite exhaustiva original — Módulo 10: inventario teclado Plus", () => {
  it("mantiene el inventario V5 esperado por superficie", () => {
    expect(BASIC_V5_ROWS.flat()).toHaveLength(31);
    expect(SYMBOL_VARIABLES).toHaveLength(6);
    expect(SYMBOL_CONSTANTS).toHaveLength(5);
    expect(CATEGORY_MENUS["Trigonométricas"].flatMap(g => g.keys)).toHaveLength(24);
    expect(CATEGORY_MENUS["Álgebra"].flatMap(g => g.keys)).toHaveLength(15);
    expect(CATEGORY_MENUS["Cálculo"].flatMap(g => g.keys)).toHaveLength(16);
    expect(CATEGORY_MENUS["Complejos"].flatMap(g => g.keys)).toHaveLength(15);
  });

  it("toda tecla visible tiene etiqueta y tooltip utilizable", () => {
    for (const key of allKeys) {
      expect(key.ariaLabel.trim(), JSON.stringify(key)).not.toBe("");
      expect((key.description ?? key.ariaLabel).trim(), key.ariaLabel).not.toBe("");
    }
  });

  it("toda tecla matemática activa tiene inserción o acción explícita", () => {
    for (const key of allKeys.filter(k => !k.unavailable)) {
      if (ACTION_LABELS.has(key.ariaLabel)) continue;
      expect(key.insertLatex.trim(), key.ariaLabel).not.toBe("");
    }
  });

  it("Plus conserva como única KeyDef unavailable a Productoria", () => {
    const unavailable = [...new Set(allKeys.filter(k => k.unavailable).map(k => k.ariaLabel))].sort();
    expect(unavailable).toEqual(["productoria"]);
  });

  it("las divergencias Plus activas siguen accesibles", () => {
    const calculus = CATEGORY_MENUS["Cálculo"].flatMap(g => g.keys);
    const complex = CATEGORY_MENUS["Complejos"].flatMap(g => g.keys);
    expect(calculus.find(k => k.ariaLabel === "derivada parcial")?.unavailable).toBeFalsy();
    expect(complex.find(k => k.ariaLabel.startsWith("residuo en un polo"))?.unavailable).toBeFalsy();
    expect(complex.find(k => k.ariaLabel.startsWith("singularidades"))?.unavailable).toBeFalsy();
  });
});
