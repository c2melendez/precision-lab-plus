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


describe("SY-M-15 error display and recovery (editor and transport mocks)",()=>{
 it("shows the cross-product clarification without HTTP and accepts explicit vectors",async()=>{
  mockedSubmit.mockResolvedValue({success:true,operation:"matrix_operation",request_id:"fixed",
   result_type:"scalar",result_text:"32",result_latex:"32",result_approx:32,steps:[],
   has_detailed_steps:false,warnings:[],duration_ms:1} as never);
  render(<BasicMode/>);
  const input=screen.getByLabelText("Expresión");
  const form=input.closest("form")!;
  fireEvent.change(input,{target:{value:rows["SY-M-15"].entrada}});
  fireEvent.submit(form);
  expect(await screen.findByRole("alert")).toHaveTextContent(/producto cruz.*3D.*componentes/);
  expect(mockedSubmit).not.toHaveBeenCalled();
  expect(useUIStore.getState().isLoading).toBe(false);
  fireEvent.change(input,{target:{value:String.raw`\langle1,2,3\rangle\cdot\langle4,5,6\rangle`}});
  fireEvent.submit(form);
  await waitFor(()=>expect(mockedSubmit).toHaveBeenCalledTimes(1));
  expect(mockedSubmit).toHaveBeenCalledWith("/matrix/operations",{operation:"dot",matrix_a:[["1","2","3"]],matrix_b:[["4","5","6"]]},expect.any(String));
  await waitFor(()=>expect(screen.queryByRole("alert")).not.toBeInTheDocument());
  expect(useUIStore.getState().isLoading).toBe(false);
 });
});
