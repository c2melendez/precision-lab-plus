import { describe, expect, it } from "vitest";

import { BASIC_V5_ROWS } from "../components/KeyboardBasicPanel";
import {
  CATEGORY_MENUS,
  SYMBOL_CONSTANTS,
  SYMBOL_VARIABLES,
} from "../components/NaturalMathKeyboard";

const basicKeys = BASIC_V5_ROWS.flat();
const byLabel = (label: string) => basicKeys.find((key) => key.ariaLabel === label);

describe("paridad de especificación del teclado V5 de Plus", () => {
  it("B6 mantiene edición/ejecución en el núcleo y mueve lo contextual", () => {
    expect(byLabel("borrar")).toBeDefined();
    expect(byLabel("borrar todo el campo")).toBeDefined();
    expect(byLabel("insertar el último resultado")).toBeDefined();
    expect(byLabel("igual")?.insertLatex).toBe("=");
    expect(byLabel("calcular")?.insertLatex).toBe("");

    for (const moved of [
      "grados minutos segundos",
      "prima",
      "menor que",
      "mayor que",
      "menor o igual que",
      "mayor o igual que",
    ]) {
      expect(byLabel(moved)).toBeUndefined();
    }

    const units = CATEGORY_MENUS["Unidades"].flatMap((group) => group.keys);
    expect(units.find((key) => key.ariaLabel === "grados minutos segundos")?.insertLatex).toBe("#0°#1′#2″");
    expect(units.find((key) => key.ariaLabel === "prima")?.insertLatex).toBe("'");

    const algebra = CATEGORY_MENUS["Álgebra"].flatMap((group) => group.keys);
    expect(algebra.find((key) => key.ariaLabel === "menor que")?.insertLatex).toBe("<");
    expect(algebra.find((key) => key.ariaLabel === "mayor que")?.insertLatex).toBe(">");
    expect(algebra.find((key) => key.ariaLabel === "menor o igual que")?.insertLatex).toBe("\\le");
    expect(algebra.find((key) => key.ariaLabel === "mayor o igual que")?.insertLatex).toBe("\\ge");
  });

  it("no duplica variables ni constantes en Básico", () => {
    for (const label of ["variable x", "variable y", "variable z", "pi", "e", "número imaginario"]) {
      expect(byLabel(label)).toBeUndefined();
    }
  });

  it("separa Phi angular y phi áureo", () => {
    expect(SYMBOL_VARIABLES.find((key) => key.ariaLabel === "Phi mayúscula")?.insertLatex).toBe("\\Phi");
    expect(SYMBOL_CONSTANTS.find((key) => key.ariaLabel === "número áureo phi")?.insertLatex).toBe(
      "\\frac{1+\\sqrt{5}}{2}",
    );
  });

  it("mantiene la paridad Plus: ∂/∂x y Π activas", () => {
    const calculus = CATEGORY_MENUS["Cálculo"].flatMap((group) => group.keys);
    const partial = calculus.find((key) => key.ariaLabel === "derivada parcial");
    const product = calculus.find((key) => key.ariaLabel === "productoria");

    expect(partial?.unavailable).toBeFalsy();
    expect(partial?.insertLatex).toBe("\\frac{\\partial}{\\partial x}\\left(#0\\right)");
    expect(product?.unavailable).toBeFalsy();
    expect(product?.insertLatex).toContain("\\prod");
  });

  it("reincorpora sgn(a) y mod(a,b) en Álgebra", () => {
    const algebra = CATEGORY_MENUS["Álgebra"].flatMap((group) => group.keys);
    expect(algebra.find((key) => key.ariaLabel === "signo de a")?.insertLatex).toContain("sign");
    expect(algebra.find((key) => key.ariaLabel === "módulo o residuo")?.insertLatex).toContain("mod");
  });
  it("B6 congela el núcleo permanente y exige tooltip real", () => {
    expect(BASIC_V5_ROWS.map((row) => row.map((key) => String(key.glyph)))).toEqual([
      ["7", "8", "9", "(", ")", "⌫"],
      ["4", "5", "6", "×", "÷", "%"],
      ["1", "2", "3", "+", "−", "."],
      ["0", "ANS", "DEL", "=", "Enter"],
    ]);
    expect(basicKeys).toHaveLength(23);
    for (const key of basicKeys) {
      expect(key.description, `tooltip faltante en ${key.ariaLabel}`).toBeTruthy();
    }
    expect(byLabel("calcular")?.glyph).toBe("Enter");
  });

});
