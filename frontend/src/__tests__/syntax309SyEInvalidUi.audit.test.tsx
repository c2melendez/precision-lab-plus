import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { readFileSync } from "node:fs";
import { BasicMode } from "../components/BasicMode";
import { SimpleBasicMode } from "../components/SimpleBasicMode";
import { submitAndRecord } from "../api/submitWithHistory";
import { useUIStore } from "../store/useUIStore";

// Only the editor rendering is mocked. Source validation and conversion remain real.
vi.mock("../components/NaturalMathField", async importOriginal => {
  const actual = await importOriginal<typeof import("../components/NaturalMathField")>();
  return {
    ...actual,
    NaturalMathField: ({ latex, onLatexChange, ariaLabel }: {
      latex: string; onLatexChange: (value: string) => void; ariaLabel: string;
    }) => <input aria-label={ariaLabel} value={latex}
      onChange={event => onLatexChange(event.target.value)} />,
  };
});
vi.mock("../api/submitWithHistory", () => ({ submitAndRecord: vi.fn() }));

const rows = Object.fromEntries(readFileSync("../qa/certification/syntax309_cases.jsonl", "utf8").trim().split("\n").map(line => {
  const row = JSON.parse(line);
  return [row.id, row];
}));
const mockedSubmit = vi.mocked(submitAndRecord);
beforeEach(() => {
  mockedSubmit.mockReset();
  useUIStore.setState({ activeMode: "basic", isLoading: false, lastErrorMessage: null });
  mockedSubmit.mockResolvedValue({
    success: true, operation: "evaluate", request_id: "recovered",
    result_text: "5", result_latex: "5", result_approx: 5,
    steps: [], has_detailed_steps: false, warnings: [], duration_ms: 1,
  } as never);
});
afterEach(cleanup);

for (const [label, Component] of [["Scientific", BasicMode], ["Simple", SimpleBasicMode]] as const) {
  describe(label + " exponent error display and recovery (editor mock)", () => {
    it.each(["SY-E-11", "SY-E-12", "SY-E-13"])("%s shows an error without HTTP and recovers", async id => {
      render(<Component />);
      const input = screen.getByLabelText("Expresión");
      const form = input.closest("form")!;
      fireEvent.change(input, { target: { value: rows[id].entrada } });
      fireEvent.submit(form);
      expect(await screen.findByRole("alert")).toHaveTextContent(/superíndice|exponente|base/i);
      expect(mockedSubmit).not.toHaveBeenCalled();
      expect(useUIStore.getState().isLoading).toBe(false);

      fireEvent.change(input, { target: { value: "2+3" } });
      fireEvent.submit(form);
      await waitFor(() => expect(mockedSubmit).toHaveBeenCalledTimes(1));
      expect(mockedSubmit).toHaveBeenCalledWith(
        "/evaluate", expect.objectContaining({ expression: "2+3" }), expect.any(String),
        ...(label === "Scientific" ? [expect.anything()] : []),
      );
      await waitFor(() => expect(screen.queryByRole("alert")).not.toBeInTheDocument());
      await waitFor(() => expect(useUIStore.getState().isLoading).toBe(false));
    });
  });
}
