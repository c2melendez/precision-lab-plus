import { describe, expect, it } from "vitest";

import { BASIC_V5_ROWS } from "../components/KeyboardBasicPanel";
import { latexToBackendSyntax } from "../components/NaturalMathField";
import {
  CATEGORY_MENUS,
  SYMBOL_CONSTANTS,
  SYMBOL_VARIABLES,
} from "../components/NaturalMathKeyboard";

const basicKeys = BASIC_V5_ROWS.flat();
const byLabel = (label: string) => basicKeys.find((key) => key.ariaLabel === label);

describe("paridad de especificación del teclado V5 de Plus", () => {
  it("concentra controles en Básico y deja = como inserción", () => {
    expect(byLabel("borrar")).toBeDefined();
    expect(byLabel("borrar todo el campo")).toBeDefined();
    expect(byLabel("insertar el último resultado")).toBeDefined();
    expect(byLabel("grados minutos segundos")?.insertLatex).toBe("#0°#1′#2″");
    expect(byLabel("prima")?.insertLatex).toBe("'");
    expect(byLabel("menor que")?.insertLatex).toBe("<");
    expect(byLabel("mayor que")?.insertLatex).toBe(">");
    expect(byLabel("menor o igual que")?.insertLatex).toBe("\\le");
    expect(byLabel("mayor o igual que")?.insertLatex).toBe("\\ge");
    expect(byLabel("igual")?.insertLatex).toBe("=");
    expect(byLabel("calcular")?.insertLatex).toBe("");
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
    expect(product?.insertLatex).toBe("\\prod_{#0}^{#1}#2");
  });

  it("reincorpora sgn(a) y mod(a,b) en Álgebra", () => {
    const algebra = CATEGORY_MENUS["Álgebra"].flatMap((group) => group.keys);
    expect(algebra.find((key) => key.ariaLabel === "signo de a")?.insertLatex).toContain("sign");
    expect(algebra.find((key) => key.ariaLabel === "módulo o residuo")?.insertLatex).toContain("mod");
  });
});


describe("regresiones Track D de normalización LaTeX → backend", () => {
  it("normaliza logaritmo con base", () => {
    expect(latexToBackendSyntax("\\log_{2}\\left(8\\right)")).toBe("log(8,2)");
  });

  it("normaliza raíz de índice editable", () => {
    expect(latexToBackendSyntax("\\sqrt[3]{8}")).toMatch(/(?:\(8\)\*\*\(1\/\(3\)\)|root\(8,3\))/);
  });

  it("preserva porcentaje y más/menos con semántica de calculadora", () => {
    expect(latexToBackendSyntax("50%")).toMatch(/50.*\/.*100/);
    expect(latexToBackendSyntax("\\pm\\left(5\\right)")).toBe("pm(5)");
  });

  it("normaliza sumatoria y productoria finitas del teclado", () => {
    expect(latexToBackendSyntax("\\sum_{i=1}^{5}i")).toBe("sum(i,i,1,5)");
    expect(latexToBackendSyntax("\\prod_{i=1}^{5}i")).toBe("product(i,i,1,5)");
  });
});
