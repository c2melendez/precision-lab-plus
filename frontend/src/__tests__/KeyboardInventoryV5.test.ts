import { describe, expect, it } from "vitest";

import { BASIC_V5_ROWS } from "../components/KeyboardBasicPanel";
import {
  CATEGORY_MENUS,
  SYMBOL_CONSTANTS,
  SYMBOL_VARIABLES,
  type KeyDef,
} from "../components/NaturalMathKeyboard";

const EDITOR_ACTIONS = new Set([
  "borrar",
  "borrar todo el campo",
  "insertar el último resultado",
  "calcular",
  "graficar en el plano de Argand",
]);

const allKeyboardKeys: KeyDef[] = [
  ...BASIC_V5_ROWS.flat(),
  ...SYMBOL_VARIABLES,
  ...SYMBOL_CONSTANTS,
  ...Object.values(CATEGORY_MENUS).flatMap((groups) =>
    groups.flatMap((group) => group.keys),
  ),
];

const functionalKeys = allKeyboardKeys.filter(
  (key) => !key.unavailable && !EDITOR_ACTIONS.has(key.ariaLabel),
);

describe("inventario estructural del teclado V5 de Plus", () => {
  it("contiene definiciones en Básico, variables, constantes y categorías", () => {
    expect(BASIC_V5_ROWS).toHaveLength(4);
    expect(SYMBOL_VARIABLES.length).toBeGreaterThan(0);
    expect(SYMBOL_CONSTANTS.length).toBeGreaterThan(0);

    for (const groups of Object.values(CATEGORY_MENUS)) {
      expect(groups.length).toBeGreaterThan(0);
      expect(groups.flatMap((group) => group.keys).length).toBeGreaterThan(0);
    }
  });

  it("mantiene ocho columnas lógicas por fila en Básico", () => {
    expect(BASIC_V5_ROWS[0]).toHaveLength(8);
    expect(BASIC_V5_ROWS[1]).toHaveLength(8);
    expect(BASIC_V5_ROWS[2]).toHaveLength(8);
    expect(BASIC_V5_ROWS[3]).toHaveLength(7);
  });

  it("no deja teclas sin etiqueta accesible ni descripción utilizable", () => {
    for (const key of allKeyboardKeys) {
      expect(key.ariaLabel.trim()).not.toBe("");
      expect((key.description ?? key.ariaLabel).trim()).not.toBe("");
    }
  });

  it("no marca disponible una tecla matemática sin inserción", () => {
    for (const key of functionalKeys) {
      expect(key.insertLatex.trim(), key.ariaLabel).not.toBe("");
    }
  });

  it("mantiene vacías las inserciones de capacidades declaradas no disponibles", () => {
    for (const key of allKeyboardKeys.filter((item) => item.unavailable)) {
      expect(key.insertLatex, key.ariaLabel).toBe("");
    }
  });

  it("mantiene activas productoria y derivada parcial de Plus", () => {
    const calculus = CATEGORY_MENUS["Cálculo"].flatMap((group) => group.keys);
    const product = calculus.find((key) => key.ariaLabel === "productoria");
    const partial = calculus.find((key) => key.ariaLabel === "derivada parcial");

    expect(product?.unavailable).toBeFalsy();
    expect(product?.insertLatex).toBe("\\prod_{#0}^{#1}#2");
    expect(partial?.unavailable).toBeFalsy();
  });
});
