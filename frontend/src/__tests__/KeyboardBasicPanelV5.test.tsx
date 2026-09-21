import { act, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { KeyboardBasicPanel } from "../components/KeyboardBasicPanel";

function makeField() {
  return {
    focus: vi.fn(),
    insert: vi.fn(),
    executeCommand: vi.fn(),
    setValue: vi.fn(),
  };
}

describe("KeyboardBasicPanel V5", () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("mantiene el inventario básico acordado y usa Enter en doble columna", () => {
    render(<KeyboardBasicPanel field={makeField() as never} onSubmit={vi.fn()} lastAnswerLatex={null} />);

    for (const name of [
      "borrar",
      "borrar todo el campo",
      "insertar el último resultado",
      "grados minutos segundos",
      "prima",
      "menor que",
      "mayor que",
      "menor o igual que",
      "mayor o igual que",
      "igual",
      "calcular",
    ]) {
      expect(screen.getByRole("button", { name })).toBeInTheDocument();
    }

    expect(screen.getByRole("button", { name: "calcular" })).toHaveClass("col-span-2");
  });

  it("= inserta igualdad sin ejecutar; Enter es la única tecla que ejecuta", () => {
    const field = makeField();
    const onSubmit = vi.fn();
    render(<KeyboardBasicPanel field={field as never} onSubmit={onSubmit} lastAnswerLatex={null} />);

    fireEvent.click(screen.getByRole("button", { name: "igual" }));
    expect(field.insert).toHaveBeenCalledWith("=");
    expect(onSubmit).not.toHaveBeenCalled();

    fireEvent.click(screen.getByRole("button", { name: "calcular" }));
    expect(onSubmit).toHaveBeenCalledTimes(1);
  });

  it("ANS inserta el último resultado y no ejecuta el cálculo", () => {
    const field = makeField();
    const onSubmit = vi.fn();
    render(
      <KeyboardBasicPanel
        field={field as never}
        onSubmit={onSubmit}
        lastAnswerLatex="\\frac{3}{2}"
      />,
    );

    fireEvent.click(screen.getByRole("button", { name: "insertar el último resultado" }));
    expect(field.focus).toHaveBeenCalled();
    expect(field.insert).toHaveBeenCalledWith("\\frac{3}{2}");
    expect(onSubmit).not.toHaveBeenCalled();
  });

  it("ANS avisa cuando todavía no existe resultado previo", () => {
    const field = makeField();
    render(<KeyboardBasicPanel field={field as never} onSubmit={vi.fn()} lastAnswerLatex={null} />);

    fireEvent.click(screen.getByRole("button", { name: "insertar el último resultado" }));
    expect(screen.getByText("Sin resultado previo todavía.")).toBeInTheDocument();
    expect(field.insert).not.toHaveBeenCalled();

    act(() => {
      vi.advanceTimersByTime(2500);
    });
    expect(screen.queryByText("Sin resultado previo todavía.")).not.toBeInTheDocument();
  });

  it("DEL limpia todo y backspace solo borra hacia atrás", () => {
    const field = makeField();
    render(<KeyboardBasicPanel field={field as never} onSubmit={vi.fn()} lastAnswerLatex={null} />);

    fireEvent.click(screen.getByRole("button", { name: "borrar" }));
    expect(field.executeCommand).toHaveBeenCalledWith("deleteBackward");

    fireEvent.click(screen.getByRole("button", { name: "borrar todo el campo" }));
    expect(field.setValue).toHaveBeenCalledWith("");
  });
});
