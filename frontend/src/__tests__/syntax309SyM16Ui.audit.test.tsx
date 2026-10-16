import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
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


describe("SY-M-16 declared type routing (editor/transport mocks)",()=>{
 it("requires the unbound type, then chooses matrix and scalar endpoints",async()=>{
  render(<BasicMode/>);
  const input=screen.getByLabelText("Expresión");
  const base=rows["SY-M-16"].entrada;
  const submit=(value:string)=>{
   fireEvent.change(input,{target:{value}});
   fireEvent.submit(input.closest("form")!);
  };
  submit(base);
  expect(await screen.findByRole("alert")).toHaveTextContent(/tipo.*matriz.*determinante.*escalar/);
  expect(mockedSubmit).not.toHaveBeenCalled();
  submit(base+String.raw`\ \text{con}\ A=\begin{pmatrix}1&2\\3&4\end{pmatrix}`);
  await waitFor(()=>expect(mockedSubmit).toHaveBeenCalledTimes(1));
  expect(mockedSubmit.mock.calls[0].slice(0,2)).toEqual(["/matrix/determinant",{matrix:[["1","2"],["3","4"]]}]);
  await waitFor(()=>expect(useUIStore.getState().isLoading).toBe(false));
  submit(base+String.raw`\ \text{con}\ A=-3`);
  await waitFor(()=>expect(mockedSubmit).toHaveBeenCalledTimes(2));
  expect(mockedSubmit.mock.calls[1][0]).toBe("/evaluate");
  expect(mockedSubmit.mock.calls[1][1]).toMatchObject({expression:"abs(-3)"});
  await waitFor(()=>expect(useUIStore.getState().isLoading).toBe(false));
 });
});
