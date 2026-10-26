import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, expect, it, vi } from "vitest";

vi.mock("../api/client", () => ({ callApi: vi.fn() }));
vi.mock("../components/NaturalMathField", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../components/NaturalMathField")>();
  return {
    ...actual,
    // jsdom only: real converter retained; native MathLive is covered by Playwright.
    NaturalMathField: ({ latex, onLatexChange, ariaLabel }: {
      latex: string; onLatexChange(value: string): void; ariaLabel: string;
    }) => <input aria-label={ariaLabel} value={latex} onChange={(event) => onLatexChange(event.target.value)} />,
  };
});

import { BasicMode } from "../components/BasicMode";
import { callApi } from "../api/client";
import { useUIStore } from "../store/useUIStore";
const mockedCallApi = vi.mocked(callApi);

beforeEach(() => {
  mockedCallApi.mockReset();
  useUIStore.setState({ activeMode: "basic", isLoading: false });
  mockedCallApi.mockResolvedValue({
    success: true, operation: "evaluate", request_id: "recovery", result_text: "5", result_latex: "5",
    result_approx: 5, steps: [], has_detailed_steps: false, warnings: [], duration_ms: 1,
  } as never);
});

it("SY-X-03 converts rejection into a readable alert without HTTP and permits recovery", async () => {
  render(<BasicMode />);
  const input = screen.getByLabelText("Expresión");
  const form = screen.getByRole("button", { name: "Evaluar" }).closest("form")!;
  fireEvent.change(input, { target: { value: "\\\\" } });
  fireEvent.submit(form);
  expect(await screen.findByRole("alert")).toHaveTextContent("Sintaxis incompleta");
  expect(mockedCallApi).not.toHaveBeenCalled();
  fireEvent.change(input, { target: { value: "2+3" } });
  fireEvent.submit(form);
  await waitFor(() => expect(mockedCallApi).toHaveBeenCalledWith("/evaluate",
    { expression: "2+3", angle_unit: "rad" }, expect.objectContaining({ signal: expect.any(AbortSignal) })));
  await waitFor(() => expect(screen.queryByRole("alert")).not.toBeInTheDocument());
});
