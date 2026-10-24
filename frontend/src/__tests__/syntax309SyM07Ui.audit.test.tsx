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


describe("SY-M-07 error display and recovery (editor and transport mocks)",()=>{
 it("shows unequal-row error without HTTP and accepts the corrected determinant",async()=>{
  mockedSubmit.mockResolvedValue({success:true,operation:"matrix_determinant",request_id:"fixed",
   result_type:"scalar",result_text:"-2",result_latex:"-2",result_approx:-2,steps:[],
   has_detailed_steps:false,warnings:[],duration_ms:1} as never);
  render(<BasicMode/>);
  const input=screen.getByLabelText("Expresión");
  const form=input.closest("form")!;
  fireEvent.change(input,{target:{value:rows["SY-M-07"].entrada}});
  fireEvent.submit(form);
  expect(await screen.findByRole("alert")).toHaveTextContent(/filas.*longitud/i);
  expect(mockedSubmit).not.toHaveBeenCalled();
  expect(useUIStore.getState().isLoading).toBe(false);
  fireEvent.change(input,{target:{value:String.raw`\det\begin{pmatrix}1&2\\3&4\end{pmatrix}`}});
  fireEvent.submit(form);
  await waitFor(()=>expect(mockedSubmit).toHaveBeenCalledTimes(1));
  expect(mockedSubmit).toHaveBeenCalledWith("/matrix/determinant",{matrix:[["1","2"],["3","4"]]},expect.any(String));
  await waitFor(()=>expect(screen.queryByRole("alert")).not.toBeInTheDocument());
  expect(useUIStore.getState().isLoading).toBe(false);
 });
});
