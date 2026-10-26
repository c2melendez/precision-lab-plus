import { readFileSync } from "node:fs";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, expect, it, vi } from "vitest";

vi.mock("../api/client", () => ({ callApi: vi.fn() }));
vi.mock("../components/NaturalMathField", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../components/NaturalMathField")>();
  return { ...actual, NaturalMathField: ({ latex, onLatexChange, ariaLabel }: {
    latex: string; onLatexChange(value: string): void; ariaLabel: string;
  }) => <input aria-label={ariaLabel} value={latex} onChange={(event) => onLatexChange(event.target.value)} /> };
});

import { BasicMode } from "../components/BasicMode";
import { callApi } from "../api/client";
import { useUIStore } from "../store/useUIStore";
const call = vi.mocked(callApi);
const canonical = readFileSync("../qa/certification/syntax309_cases.jsonl", "utf8")
  .trim().split("\n").map((line) => JSON.parse(line)).find((row) => row.id === "SY-R-13").entrada;

beforeEach(() => {
  call.mockReset();
  useUIStore.setState({ activeMode: "basic", isLoading: false });
  call.mockResolvedValue({ success: true, operation: "evaluate", request_id: "unit-only",
    result_text: "3", result_latex: "3", result_approx: 3, steps: [],
    has_detailed_steps: false, warnings: [], duration_ms: 1 } as never);
});

// jsdom field shell and API mock only: actual conversion and BasicMode routing.
// Native MathLive and HTTP response correctness are independently covered by E2E.
it.each([
  [canonical, "/evaluate", "expression", "((x)**(1/(3))) con x=(27)"],
  [String.raw`\sqrt[3]{y}\ \text{con}\ y=64`, "/evaluate", "expression", "((y)**(1/(3))) con y=(64)"],
  [String.raw`\left\lvert x\right\rvert\ \text{con}\ x=-4`, "/evaluate", "expression", "abs(-4)"],
  [String.raw`\left\lvert y\right\rvert\ \text{con}\ y=-7`, "/evaluate", "expression", "abs(-7)"],
  [String.raw`\left\lvert x\right\rvert+x\ \text{con}\ x=-4`, "/evaluate", "expression", "(abs(x)+x) con x=(-4)"],
  [String.raw`\left\lvert x\right\rvert+x\ \text{con}\ x=4`, "/evaluate", "expression", "(abs(x)+x) con x=(4)"],
  ["x+1=4", "/solve", "equation", "x+1=4"],
  ["x<4", "/inequality", "inequality", "x<4"],
])("routes source %s without mistaking a binding for an equation", async (source, endpoint, key, converted) => {
  render(<BasicMode />);
  fireEvent.change(screen.getByLabelText("Expresión"), { target: { value: source } });
  fireEvent.submit(screen.getByRole("button", { name: "Evaluar" }).closest("form")!);
  await waitFor(() => expect(call).toHaveBeenCalledTimes(1));
  expect(call.mock.calls[0][0]).toBe(endpoint);
  expect(call.mock.calls[0][1]).toHaveProperty(key, converted);
});
