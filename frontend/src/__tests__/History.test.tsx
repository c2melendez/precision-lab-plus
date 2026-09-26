import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { History } from "../components/History";
import { useHistoryStore, type HistoryEntry } from "../store/useHistoryStore";

beforeEach(() => {
  useHistoryStore.setState({ entries: [] });
});

function renderHistory(onReuse = vi.fn<(entry: HistoryEntry) => void>()) {
  render(<History onReuse={onReuse} />);
  return onReuse;
}

describe("History", () => {
  it("muestra el mensaje vacío cuando no hay entradas", () => {
    renderHistory();
    expect(screen.getByText(/no hay historial/)).toBeInTheDocument();
  });

  it("Reusar entrega la entrada al shell para volver al módulo de origen", () => {
    useHistoryStore.getState().addEntry({
      sourceModule: "Científica",
      operation: "derivative",
      endpointUrl: "/derivative",
      requestPayload: { expression: "x**2", variable: "x", order: 1 },
      inputText: "x^2",
      label: "d/dx [x**2]",
      hasDetailedSteps: true,
      warnings: [],
    });

    const onReuse = renderHistory();
    fireEvent.click(screen.getByRole("button", { name: /Reusar entrada/ }));

    expect(onReuse).toHaveBeenCalledTimes(1);
    expect(onReuse.mock.calls[0]?.[0].sourceModule).toBe("Científica");
    expect(onReuse.mock.calls[0]?.[0].requestPayload).toEqual({
      expression: "x**2",
      variable: "x",
      order: 1,
    });
  });

  it("muestra el módulo y el nombre natural de la operación", () => {
    useHistoryStore.setState({
      entries: [
        {
          id: "matrix-1",
          sourceModule: "Matrices",
          operation: "matrix_determinant",
          endpointUrl: "/matrix/determinant",
          requestPayload: { matrix: [[1, 2], [3, 4]] },
          label: "det(A)",
          resultText: "-2",
          hasDetailedSteps: false,
          warnings: [],
          timestamp: Date.now(),
        },
        {
          id: "stats-1",
          sourceModule: "Estadística",
          operation: "statistics_descriptive",
          endpointUrl: "/statistics/descriptive",
          requestPayload: { values: [1, 2, 3], stat: "mean" },
          label: "Media(1,2,3)",
          resultText: "2",
          hasDetailedSteps: false,
          warnings: [],
          timestamp: Date.now() - 1,
        },
      ],
    });

    renderHistory();
    expect(screen.getByText("Matrices")).toBeInTheDocument();
    expect(screen.getByText("Determinante")).toBeInTheDocument();
    expect(screen.getByText("Estadística")).toBeInTheDocument();
    expect(screen.getByText("Estadística descriptiva")).toBeInTheDocument();
    expect(screen.queryByText("matrix_determinant")).not.toBeInTheDocument();
    expect(screen.queryByText("statistics_descriptive")).not.toBeInTheDocument();
  });

  it("muestra los valores guardados de las matrices", () => {
    useHistoryStore.setState({
      entries: [
        {
          id: "matrix-values",
          sourceModule: "Matrices",
          operation: "matrix_operation",
          endpointUrl: "/matrix/operations",
          requestPayload: {
            operation: "multiply",
            matrix_a: [[1, 2], [3, 4]],
            matrix_b: [[5, 6], [7, 8]],
          },
          label: "A × B",
          resultText: "[[19,22],[43,50]]",
          hasDetailedSteps: false,
          warnings: [],
          timestamp: Date.now(),
        },
      ],
    });

    renderHistory();
    expect(screen.getByText("A =")).toBeInTheDocument();
    expect(screen.getByText("B =")).toBeInTheDocument();
    for (const value of ["1", "2", "3", "4", "5", "6", "7", "8"]) {
      expect(screen.getAllByText(value).length).toBeGreaterThan(0);
    }
  });

  it("normaliza sintaxis backend a formato matemático natural en Científica", () => {
    useHistoryStore.setState({
      entries: [
        {
          id: "natural-science",
          sourceModule: "Científica",
          operation: "evaluate",
          endpointUrl: "/evaluate",
          requestPayload: { expression: "sin((pi)/(4))+sqrt2" },
          inputText: "sin((pi)/(4))+sqrt2",
          label: "sin((pi)/(4))+sqrt2",
          resultLatex: "sin((pi)/(4))+sqrt2",
          resultText: "sin((pi)/(4))+sqrt2",
          hasDetailedSteps: false,
          warnings: [],
          timestamp: Date.now(),
        },
      ],
    });

    render(<History onReuse={vi.fn()} />);
    const resultLabel = screen.getByText("Resultado");
    const resultRow = resultLabel.parentElement;
    if (!(resultRow instanceof HTMLElement)) throw new Error("No se encontró la fila de resultado");
    const visibleMath = resultRow.querySelector(".katex-html");
    if (!(visibleMath instanceof HTMLElement)) throw new Error("No se encontró la salida visual de KaTeX");
    expect(visibleMath.textContent).not.toContain("sqrt2");
    expect(visibleMath.textContent).not.toContain("pi");
    expect(visibleMath.textContent).toContain("π");
  });

  it("muestra fecha y hora del resultado", () => {
    const timestamp = new Date(2026, 8, 25, 20, 16, 21).getTime();
    useHistoryStore.setState({
      entries: [
        {
          id: "dated-1",
          sourceModule: "Gráficas",
          operation: "graph_2d",
          endpointUrl: "/graph/2d",
          requestPayload: { expressions: ["1/x"], variable: "x" },
          label: "1/x",
          hasDetailedSteps: false,
          warnings: [],
          timestamp,
        },
      ],
    });

    renderHistory();
    const time = document.querySelector("time");
    if (!(time instanceof HTMLTimeElement)) throw new Error("No se encontró el elemento time del historial");
    expect(time).toHaveAttribute("dateTime", new Date(timestamp).toISOString());
    expect(time.textContent).toMatch(/\d{2}\/\d{2}\/\d{4}/);
    expect(time.textContent).toMatch(/\d{2}:\d{2}/);
  });

  it("Borrar historial vacía la lista", () => {
    useHistoryStore.getState().addEntry({
      sourceModule: "Científica",
      operation: "evaluate",
      endpointUrl: "/evaluate",
      requestPayload: { expression: "1+1" },
      label: "1+1",
      hasDetailedSteps: false,
      warnings: [],
    });

    renderHistory();
    fireEvent.click(screen.getByRole("button", { name: "Borrar historial" }));
    expect(screen.getByText(/no hay historial/)).toBeInTheDocument();
  });
});
