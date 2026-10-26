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


describe("SY-M-14 local declarations route (editor/transport mocks)",()=>{
 it("sends the declared vectors to the dot endpoint",async()=>{
  mockedSubmit.mockResolvedValue({success:true,operation:"matrix_operation",request_id:"dot14",
   result_type:"scalar",result_text:"32",result_latex:"32",result_approx:32,steps:[],
   has_detailed_steps:false,warnings:[],duration_ms:1} as never);
  render(<BasicMode/>);
  const input=screen.getByLabelText("Expresión");
  fireEvent.change(input,{target:{value:rows["SY-M-14"].entrada}});
  fireEvent.submit(input.closest("form")!);
  await waitFor(()=>expect(mockedSubmit).toHaveBeenCalledTimes(1));
  expect(mockedSubmit).toHaveBeenCalledWith("/matrix/operations",{operation:"dot",matrix_a:[["1","2","3"]],matrix_b:[["4","5","6"]]},expect.any(String));
  await waitFor(()=>expect(useUIStore.getState().isLoading).toBe(false));
  expect(screen.queryByRole("alert")).not.toBeInTheDocument();
 });
});
