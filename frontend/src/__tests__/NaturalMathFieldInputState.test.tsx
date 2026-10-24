import {act, render} from "@testing-library/react";
import {beforeAll, expect, it, vi} from "vitest";
vi.mock("mathlive",()=>({}));
import {NaturalMathField} from "../components/NaturalMathField";

beforeAll(()=>{
  // Only the custom-element shell is simulated; the React input handler is real.
  if(!customElements.get("math-field")){
    customElements.define("math-field",class extends HTMLElement{
      value="";
      setValue(value:string){this.value=value;}
    });
  }
  Object.defineProperty(window,"mathVirtualKeyboard",{configurable:true,value:{hide:vi.fn()}});
});

it("notifies clearing after a controlled value changed from the initial empty string",()=>{
  const changed=vi.fn();
  const view=render(<NaturalMathField latex="" onLatexChange={changed} ariaLabel="Entrada"/>);
  view.rerender(<NaturalMathField latex="5" onLatexChange={changed} ariaLabel="Entrada"/>);
  const field=view.container.querySelector("math-field") as HTMLElement & {value:string};
  expect(field.value).toBe("5");
  act(()=>{field.value="";field.dispatchEvent(new Event("input",{bubbles:true}));});
  expect(changed).toHaveBeenLastCalledWith("");
});
