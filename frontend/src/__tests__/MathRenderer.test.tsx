import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { MathRenderer, MAX_KATEX_EXPANSIONS } from "../components/MathRenderer";

describe("MathRenderer", () => {
  it("renderiza LaTeX válido vía katex.renderToString (HTML generado por KaTeX)", () => {
    const { container } = render(<MathRenderer latex="x^{2}" />);
    // KaTeX genera sus propios nodos con la clase "katex" — confirma que
    // pasó por su API real, no que se insertó el texto crudo tal cual.
    expect(container.querySelector(".katex")).not.toBeNull();
    expect(container.textContent).not.toBe("x^{2}");
  });

  it("cae a texto plano (fallbackText) si KaTeX no puede parsear el input", () => {
    // En JSX, una cadena literal no procesa secuencias de escape como JS normal.
    render(<MathRenderer latex={"\\notacomando{roto"} fallbackText="texto de respaldo" />);
    expect(screen.getByText("texto de respaldo")).toBeInTheDocument();
  });

  it("cae al propio latex como texto si no hay fallbackText y KaTeX falla", () => {
    // "\\left(" sin su "\\right)" correspondiente es un ParseError real de KaTeX.
    render(<MathRenderer latex={"\\left("} />);
    expect(screen.getByText("\\left(")).toBeInTheDocument();
  });

  it("EN-SG-03: HTML incluido en texto matemático se muestra como texto literal", () => {
    const payload = '<img src=x onerror="alert(1)">';
    const { container } = render(<MathRenderer latex={payload} />);

    // KaTeX debe rechazar esta entrada y MathRenderer debe usar el fallback
    // de texto plano. No debe convertir el contenido suministrado en nodos HTML.
    expect(container.querySelector("img")).toBeNull();
    expect(container.querySelector("svg")).toBeNull();
    expect(container.textContent).toBe(payload);
    expect(screen.getByText(payload)).toBeInTheDocument();
  });

  it("EN-SG-03 (literal original H.2): x^{2}\\text{<b>hola</b>} se muestra sin interpretar HTML", () => {
    const payload = "x^{2}\\text{<b>hola</b>}";
    const { container } = render(<MathRenderer latex={payload} />);

    // Literal de la matriz fuente; el texto interno no debe crear nodos HTML.
    expect(container.querySelector("b")).toBeNull();
    expect(container.querySelector("img, svg, script")).toBeNull();
    expect(container.textContent).toBe(payload);
    expect(screen.getByText(payload)).toBeInTheDocument();
  });

  it.each([
    ["EN-SG-01", "<script>alert(1)</script>"],
    ["EN-SG-02", "<img src=x onerror=alert(1)>"],
  ])("%s: HTML activo se muestra como texto escapado", (_id, payload) => {
    const { container } = render(<MathRenderer latex={payload} />);
    expect(container.querySelector("script, img, svg")).toBeNull();
    expect(container.textContent).toBe(payload);
    expect(screen.getByText(payload)).toBeInTheDocument();
    const root = container.firstElementChild as HTMLElement;
    expect(root.dataset.renderFallback).toBe("markup");
  });

  it("EN-SG-04: href con javascript no produce enlace ejecutable", () => {
    const payload = "\\href{javascript:alert(1)}{x}";
    const { container } = render(<MathRenderer latex={payload} />);
    expect(container.querySelector("a")).toBeNull();
    expect(container.querySelector("script")).toBeNull();
  });

  it.each([
    ["EN-SG-05 url", "\\url{http://example.com}"],
    ["EN-SG-05 includegraphics", "\\includegraphics{x.png}"],
    ["EN-SG-05 htmlClass", "\\htmlClass{a}{x}"],
    ["EN-SG-05 htmlStyle", "\\htmlStyle{color:red}{x}"],
    ["EN-SG-08 input", "\\input{/etc/passwd}"],
    ["EN-SG-08 include", "\\include{x}"],
    ["EN-SG-08 write18", "\\write18{ls}"],
    ["EN-SG-08 openin", "\\openin1=x"],
  ])("%s: la entrada no genera HTML activo ni enlaces ejecutables", (_id, payload) => {
    const { container } = render(<MathRenderer latex={payload} />);
    expect(container.querySelector("script, img, iframe, object, embed")).toBeNull();
    expect(container.querySelector("a")).toBeNull();
  });

  // EN-SG-06 / EN-SG-07: recursion bound + clear fallback (no infinite expansion).
  it.each([
    ["EN-SG-06 recursive def", "\\def\\a{\\a}\\a"],
    ["EN-SG-06 recursive def duplicate", "\\def\\x{\\x\\x}\\x"],
    ["EN-SG-07 recursive newcommand", "\\newcommand{\\a}{\\a}\\a"],
    ["EN-SG-07 catcode", "\\catcode"],
  ])("%s: expansión acotada, fallback literal y señal data-render-fallback=syntax", (_id, payload) => {
    const started = performance.now();
    const { container } = render(<MathRenderer latex={payload} />);
    const elapsed = performance.now() - started;

    expect(elapsed).toBeLessThan(2000);
    expect(MAX_KATEX_EXPANSIONS).toBe(1000);

    const root = container.firstElementChild as HTMLElement;
    expect(root.dataset.renderFallback).toBe("syntax");
    expect(container.querySelector("script, img, svg, a, iframe, object, embed")).toBeNull();
    expect(container.querySelector(".katex")).toBeNull();
    expect(root.textContent).toBe(payload);
  });

  it("EN-SG-07 let: alias de macro no se expande ni ejecuta nada (inert, acotado)", () => {
    const payload = "\\let\\a\\b";
    const started = performance.now();
    const { container } = render(<MathRenderer latex={payload} />);
    expect(performance.now() - started).toBeLessThan(2000);
    expect(container.querySelector("script, img, svg, a, iframe, object, embed")).toBeNull();
    // KaTeX consumes the control sequences and yields an inert empty node:
    // no expansion loop, no error throw, no side effect.
    expect(container.querySelector(".katex")).not.toBeNull();
    expect(container.textContent).toBe("");
  });

  it("EN-SG-06/07 regression: macro finita sigue renderizando (\\def\\a{x}\\a)", () => {
    const { container } = render(<MathRenderer latex={"\\def\\a{x}\\a"} />);
    expect(container.querySelector(".katex")).not.toBeNull();
    expect(container.textContent).toContain("x");
    expect((container.firstElementChild as HTMLElement).dataset.renderFallback).toBeUndefined();
  });
});
