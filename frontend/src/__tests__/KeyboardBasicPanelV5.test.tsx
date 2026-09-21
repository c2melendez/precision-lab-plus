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

    const equal = screen.getByRole("button", { name: "igual" });
    fireEvent.pointerDown(equal);
    fireEvent.pointerUp(equal);
    expect(field.insert).toHaveBeenCalledWith("=");
    expect(onSubmit).not.toHaveBeenCalled();

    const enter = screen.getByRole("button", { name: "calcular" });
    fireEvent.pointerDown(enter);
    fireEvent.pointerUp(enter);
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

    const ans = screen.getByRole("button", { name: "insertar el último resultado" });
    fireEvent.pointerDown(ans);
    fireEvent.pointerUp(ans);
    expect(field.focus).toHaveBeenCalled();
    expect(field.insert).toHaveBeenCalledWith("\\frac{3}{2}");
    expect(onSubmit).not.toHaveBeenCalled();
  });

  it("ANS avisa cuando todavía no existe resultado previo", () => {
    const field = makeField();
    render(<KeyboardBasicPanel field={field as never} onSubmit={vi.fn()} lastAnswerLatex={null} />);

    const ans = screen.getByRole("button", { name: "insertar el último resultado" });
    fireEvent.pointerDown(ans);
    fireEvent.pointerUp(ans);
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

    const backspace = screen.getByRole("button", { name: "borrar" });
    fireEvent.pointerDown(backspace);
    fireEvent.pointerUp(backspace);
    expect(field.executeCommand).toHaveBeenCalledWith("deleteBackward");

    const del = screen.getByRole("button", { name: "borrar todo el campo" });
    fireEvent.pointerDown(del);
    fireEvent.pointerUp(del);
    expect(field.setValue).toHaveBeenCalledWith("");
  });
});
