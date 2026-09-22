import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { StepList } from "../components/StepList";

describe("Suite exhaustiva original — Módulo 14: texto natural visible", () => {
  it("StepList no renderiza identificadores técnicos de ninguna familia con pasos", () => {
    const steps = [
      {
        index: 1,
        title: "Regla de la potencia",
        rule: "PowerRule",
        description: "Se deriva la potencia respecto de x.",
        latex_before: "x^3",
        latex_after: "3x^2",
      },
      {
        index: 2,
        title: "Integral de potencia",
        rule: "ChainRule",
        description: "Se aplica la regla de integración correspondiente.",
        latex_before: "x^2",
        latex_after: "\\frac{x^3}{3}",
      },
      {
        index: 3,
        title: "Fórmula general",
        rule: "QuadraticFormula",
        description: "Se calculan las soluciones de la ecuación.",
        latex_before: "x^2-5x+6=0",
        latex_after: "x=2,3",
      },
      {
        index: 4,
        title: "Celda (1,1)",
        rule: "MatrixMultiply",
        description: "Se multiplican fila y columna.",
        latex_before: "A\\cdot B",
        latex_after: "19",
      },
      {
        index: 5,
        title: "Eliminación por filas",
        rule: "RowElimination",
        description: "Se elimina el término bajo el pivote.",
        latex_before: "F_2",
        latex_after: "F_2-3F_1",
      },
    ] as any;

    render(<StepList steps={steps} />);

    for (const natural of [
      "Regla de la potencia",
      "Integral de potencia",
      "Fórmula general",
      "Celda (1,1)",
      "Eliminación por filas",
    ]) {
      expect(screen.getByText(natural)).toBeInTheDocument();
    }

    for (const technical of [
      "PowerRule",
      "ChainRule",
      "QuadraticFormula",
      "MatrixMultiply",
      "RowElimination",
    ]) {
      expect(screen.queryByText(technical)).not.toBeInTheDocument();
    }
  });
});
