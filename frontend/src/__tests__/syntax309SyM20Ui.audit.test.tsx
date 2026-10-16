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


describe("SY-M-20 scalar route (editor and transport mocked)",()=>{
 it.each([
  ["2", "2", [["2","4"],["6","8"]]],
  [String.raw`-\frac{1}{2}`, "-1/2", [["-1/2","-1"],["-3/2","-2"]]],
 ])("sends %s as an exact diagonal product",async(prefix,scalar,expected)=>{
  mockedSubmit.mockResolvedValue({success:true,operation:"matrix_operation",request_id:"scale20",
   result_type:"matrix",result_data:expected,result_text:"matrix",result_latex:"matrix",steps:[],
   has_detailed_steps:false,warnings:[],duration_ms:1} as never);
  render(<BasicMode/>);
  const input=screen.getByLabelText("Expresión");
  const latex=rows["SY-M-20"].entrada.replace(/^2/,prefix);
  fireEvent.change(input,{target:{value:latex}});
  fireEvent.submit(input.closest("form")!);
  await waitFor(()=>expect(mockedSubmit).toHaveBeenCalledTimes(1));
  expect(mockedSubmit).toHaveBeenCalledWith("/matrix/operations",
   {operation:"multiply",matrix_a:[[scalar,"0"],["0",scalar]],matrix_b:[["1","2"],["3","4"]]},latex);
  await waitFor(()=>expect(useUIStore.getState().isLoading).toBe(false));
  expect(screen.queryByRole("alert")).not.toBeInTheDocument();
 });
});
