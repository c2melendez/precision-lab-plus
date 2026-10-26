import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { readFileSync } from "node:fs";
import { BasicMode } from "../components/BasicMode";
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


describe("SY-M-13 local canonical basis display (editor mock)",()=>{
 it("shows the coordinates without calling HTTP",async()=>{
  render(<BasicMode/>);
  const input=screen.getByLabelText("Expresión");
  fireEvent.change(input,{target:{value:rows["SY-M-13"].entrada}});
  fireEvent.submit(input.closest("form")!);
  const notices = await screen.findAllByText(/Coordenadas en la base canónica: \(1, 2, -1\)\./);
  expect(notices[0]).toBeVisible();
  expect(mockedSubmit).not.toHaveBeenCalled();
  expect(useUIStore.getState().isLoading).toBe(false);
 });
});
