import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { BasicMode } from "../components/BasicMode";
import { callApi } from "../api/client";

vi.mock("../api/client", () => ({ callApi: vi.fn() }));
vi.mock("../components/NaturalMathField", () => ({
  NaturalMathField: ({ latex, onLatexChange, ariaLabel }: { latex: string; onLatexChange: (s: string) => void; ariaLabel: string }) => (
    <input aria-label={ariaLabel} value={latex} onChange={(e) => onLatexChange(e.target.value)} />
  ),
  latexToBackendSyntax: (latex: string) => latex.trim(),
}));

beforeEach(() => {
  vi.mocked(callApi).mockReset();
  vi.mocked(callApi).mockResolvedValue({ success: true, operation: "partial_fractions", request_id: "pf", steps: [], has_detailed_steps: false, warnings: [], duration_ms: 1 } as never);
});

describe("Algebra114 AS-PF-01 scientific UI wiring", () => {
  it("routes selected fraction decomposition to the registered HTTP endpoint", async () => {
    render(<BasicMode />);
    fireEvent.change(screen.getByLabelText("Expresión"), { target: { value: "(3*x+5)/((x+1)*(x+2))" } });
    fireEvent.click(screen.getByRole("checkbox", { name: "Descomponer en fracciones parciales" }));
    fireEvent.submit(screen.getByRole("button", { name: "Evaluar" }).closest("form")!);
    await waitFor(() => expect(callApi).toHaveBeenCalledWith("/partial-fractions", { expression: "(3*x+5)/((x+1)*(x+2))" }, expect.objectContaining({ signal: expect.any(AbortSignal) })));
  });
});
