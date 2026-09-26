/**
 * src/components/ResultPanel.tsx — panel de resultado (spec, sección 11).
 *
 * `has_detailed_steps: false` se muestra como "procedimiento resumido"
 * (nunca como ausencia de resultado — el resultado sigue siendo válido).
 * `warnings` siempre visibles. "Copiar resultado"/"Copiar como LaTeX"
 * (deshabilitado si `result_latex` es `null`). Notación científica para
 * `result_approx` extremo. `aria-live`/`aria-label` para accesibilidad.
 */

import { useState } from "react";

import type { EquationSolution, MathResponse } from "../api/client";
import { formatResultApprox } from "./formatNumber";
import { parseFracLatex, toMixedFracLatex } from "./fractionDisplay";
import { MathRenderer } from "./MathRenderer";
import { StepList } from "./StepList";
import { decimalDegreesToDms, isInverseTrigAngleExpression, parseDecimalDegreesInput } from "./dmsDisplay";
import { ResultFormatSelector, type ResultFormatId } from "./ResultFormatSelector";
import { getAvailableResultFormats } from "./resultFormatPolicy";

// Fase 2.5 (bug reportado por el usuario): antes se mostraban SIEMPRE
// "exacto" (result_latex) y "≈ aproximado" (result_approx) juntos, sin
// forma de pedir notación científica ni saber si el resultado exacto ya
// es una fracción. Se agrega un selector de 4 formatos, mismo criterio
// que ya usa Lite (dec/frac/scn/exacto) — con una diferencia importante:
// acá NO hay una capa de fracciones propia como fractions.ts en Lite, así
// que "frac" nunca INVENTA una fracción a partir de un decimal
// aproximado (sería fabricar precisión falsa) — solo muestra
// result_latex cuando SymPy ya lo devolvió como \frac{...}{...} de
// forma exacta; si no, dice explícitamente que no aplica.
type AnswerFormat = ResultFormatId;

function isFractionLatex(latex: string | null | undefined): boolean {
  return latex !== null && latex !== undefined && latex.includes("\\frac");
}

interface ResultPanelProps {
  result: MathResponse | null;
  isLoading: boolean;
  inputLatex?: string;
  angleUnit?: "rad" | "deg";
}

async function copyToClipboard(text: string): Promise<boolean> {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch {
    return false;
  }
}

function CopyButton({ text, label }: { text: string | null; label: string }) {
  const [justCopied, setJustCopied] = useState(false);

  async function handleClick(): Promise<void> {
    if (text === null) return;
    const ok = await copyToClipboard(text);
    if (ok) {
      setJustCopied(true);
      setTimeout(() => setJustCopied(false), 1500);
    }
  }

  return (
    <button
      type="button"
      onClick={handleClick}
      disabled={text === null}
      className="rounded border border-paper-line px-3 py-1 text-xs text-muted hover:bg-paper-line/40 disabled:cursor-not-allowed disabled:opacity-40"
    >
      {justCopied ? "¡Copiado!" : label}
    </button>
  );
}

function isMatrixData(
  data: MathResponse["result_data"],
  resultType: MathResponse["result_type"],
): data is string[][] {
  return resultType === "matrix" && Array.isArray(data);
}

function isEquationSolutionData(
  data: MathResponse["result_data"],
  resultType: MathResponse["result_type"],
): data is EquationSolution[] {
  return resultType === "equation_solutions" && Array.isArray(data);
}

function MatrixResult({ matrix }: { matrix: string[][] }) {
  return (
    <div className="overflow-x-auto">
      <table className="border-separate border-spacing-1">
        <tbody>
          {matrix.map((row, r) => (
            <tr key={r}>
              {row.map((cell, c) => (
                <td
                  key={c}
                  className="min-w-[3rem] rounded border border-paper-line bg-paper px-3 py-2 text-center text-base text-ink"
                >
                  {cell}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function SolutionListResult({ solutions }: { solutions: EquationSolution[] }) {
  if (solutions.length === 0) {
    return <p className="text-sm text-muted">El sistema no tiene solución.</p>;
  }
  return (
    <ul className="space-y-2">
      {solutions.map((solution, index) => (
        <li key={index} className="a11y-scale-result-lg text-ink">
          <MathRenderer latex={solution.latex} fallbackText={solution.text} />
          {solution.is_complex && <span className="ml-2 text-xs text-muted">(compleja)</span>}
        </li>
      ))}
    </ul>
  );
}

export function ResultPanel({ result, isLoading, inputLatex = "", angleUnit = "rad" }: ResultPanelProps) {
  const [format, setFormat] = useState<AnswerFormat>("exact");
  // Modo fracción propia/impropia (pedido explícito) — mismo criterio
  // que el toggle equivalente en Lite: default mixta cuando corresponde,
  // el usuario puede pedir la impropia.
  const [showMixed, setShowMixed] = useState(true);
  const explicitDegreeInput = parseDecimalDegreesInput(inputLatex);
  const inverseAngleResult = angleUnit === "deg" && isInverseTrigAngleExpression(inputLatex);
  const inverseDegrees = inverseAngleResult && result?.result_approx != null && Number.isFinite(Number(result.result_approx))
    ? Number(result.result_approx)
    : null;
  const dmsDegrees = explicitDegreeInput ?? inverseDegrees;
  const dmsValue = dmsDegrees === null ? null : decimalDegreesToDms(dmsDegrees);
  const exactLatex = inverseAngleResult && result?.result_latex
    ? `{${result.result_latex}}^{\\circ}`
    : result?.result_latex;

  if (isLoading) {
    return (
      <div role="status" aria-live="polite" className="text-sm text-muted">
        Calculando…
      </div>
    );
  }

  if (result === null) {
    return (
      <p className="text-sm text-muted">
        Introduce una expresión y envía el formulario para ver el resultado aquí.
      </p>
    );
  }

  if (!result.success) {
    return (
      <div role="alert" aria-live="assertive" className="text-sm text-red-600">
        <p className="font-medium">{result.error_code}</p>
        <p>{result.error_message}</p>
      </div>
    );
  }

  const matrixData = isMatrixData(result.result_data, result.result_type) ? result.result_data : null;
  const solutionData = isEquationSolutionData(result.result_data, result.result_type)
    ? result.result_data
    : null;
  const approxText = result.result_approx != null ? formatResultApprox(result.result_approx) : null;
  const copyText = result.result_text ?? approxText;
  const parsedFraction = isFractionLatex(result.result_latex) ? parseFracLatex(result.result_latex!) : null;
  const mixedLatex = parsedFraction ? toMixedFracLatex(parsedFraction.n, parsedFraction.d) : null;
  const numericApprox = result.result_approx != null ? Number(result.result_approx) : NaN;
  const hasNumericApprox = Number.isFinite(numericApprox);
  const availableFormats = getAvailableResultFormats({
    hasExact: Boolean(result.result_latex ?? result.result_text),
    hasDecimal: hasNumericApprox,
    hasFraction: Boolean(parsedFraction),
    hasDms: Boolean(dmsValue),
  }) as AnswerFormat[];
  const activeFormat = availableFormats.includes(format) ? format : (availableFormats[0] ?? "exact");

  return (
    <div aria-live="polite" className="space-y-4 fade-in">
      {matrixData && (
        <section aria-label="Resultado estructurado" className="space-y-3">
          <div className="flex items-center justify-between gap-3">
            <p className="text-xs font-semibold uppercase tracking-[0.14em] text-muted">Resultado</p>
            <span className="rounded-md bg-paper-line/50 px-2 py-1 text-[11px] font-medium text-muted">Matriz</span>
          </div>
          <div className="min-h-14 rounded-xl border border-paper-line bg-paper px-4 py-3">
            <MatrixResult matrix={matrixData} />
          </div>
        </section>
      )}
      {solutionData && (
        <section aria-label="Resultado estructurado" className="space-y-3">
          <div className="flex items-center justify-between gap-3">
            <p className="text-xs font-semibold uppercase tracking-[0.14em] text-muted">Resultado</p>
            <span className="rounded-md bg-paper-line/50 px-2 py-1 text-[11px] font-medium text-muted">Soluciones</span>
          </div>
          <div className="min-h-14 rounded-xl border border-paper-line bg-paper px-4 py-3">
            <SolutionListResult solutions={solutionData} />
          </div>
        </section>
      )}

      {!matrixData && !solutionData && (result.result_latex || result.result_text) && (
        <div className="space-y-3">
          <div className="flex items-center justify-between gap-3">
            <p className="text-xs font-semibold uppercase tracking-[0.14em] text-muted">Resultado</p>
            {!result.has_detailed_steps && (
              <span className="rounded-md bg-paper-line/50 px-2 py-1 text-[11px] font-medium text-muted">
                Resumen
              </span>
            )}
          </div>

          <div className="min-h-14 rounded-xl border border-paper-line bg-paper px-4 py-3">
            {(() => {
            if (activeFormat === "dms" && dmsValue) {
              return <MathRenderer latex={dmsValue.latex} fallbackText={dmsValue.text} className="a11y-scale-result-lg" />;
            }
            if (activeFormat === "dec") {
              return approxText ? (
                <p className="a11y-scale-result-lg text-ink">{approxText}{inverseAngleResult ? "°" : ""}</p>
              ) : (
                <p className="text-sm text-muted">No hay aproximación decimal disponible.</p>
              );
            }
            if (activeFormat === "scn") {
              const n = result.result_approx != null ? Number(result.result_approx) : NaN;
              return Number.isFinite(n) ? (
                <p className="a11y-scale-result-lg text-ink">{n.toExponential(6)}{inverseAngleResult ? "°" : ""}</p>
              ) : (
                <p className="text-sm text-muted">No hay un valor numérico para notación científica.</p>
              );
            }
            if (activeFormat === "frac") {
              // No se fabrica una fracción a partir de un decimal
              // aproximado — solo se muestra cuando SymPy ya la dio
              // exacta (ver isFractionLatex arriba).
              if (!isFractionLatex(result.result_latex)) {
                return <p className="text-sm text-muted">El resultado no es una fracción exacta.</p>;
              }
              const rawDisplayLatex = mixedLatex && showMixed ? mixedLatex : result.result_latex!;
              const displayLatex = inverseAngleResult ? `{${rawDisplayLatex}}^{\\circ}` : rawDisplayLatex;
              return (
                <MathRenderer
                  latex={displayLatex}
                  fallbackText={result.result_text ?? undefined}
                  className="a11y-scale-result-lg"
                />
              );
            }
            // "exact": comportamiento original, sin cambios (salvo
            // Módulo R0: a11y-scale-result-lg reemplaza a text-lg).
            return exactLatex ? (
              <MathRenderer
                latex={exactLatex}
                fallbackText={result.result_text ?? undefined}
                className="a11y-scale-result-lg"
              />
            ) : (
              <p className="a11y-scale-result-lg text-ink">{result.result_text}</p>
            );
            })()}
          {/* Fracción exacta (arriba) y decimal (abajo) mostrados juntos —
              nunca uno oculta al otro (sección 9: fracciones + su
              equivalente decimal) — solo en el formato "exact", que es el
              que ya traía este comportamiento antes de Fase 2.5. */}
            {activeFormat === "exact" && approxText && approxText !== result.result_text && (
              <p className="mt-1 text-sm text-muted">≈ {approxText}{inverseAngleResult ? "°" : ""}</p>
            )}
          </div>

          <div className="flex flex-wrap items-center justify-between gap-2">
            <ResultFormatSelector
              formats={availableFormats}
              value={activeFormat}
              onChange={setFormat}
            />

            {activeFormat === "frac" && mixedLatex && (
              <button
                type="button"
                onClick={() => setShowMixed((v) => !v)}
                className="min-h-8 rounded-full px-2 text-xs text-muted underline decoration-dotted hover:text-marker"
              >
                {showMixed ? "ver como impropia" : "ver como mixta"}
              </button>
            )}
          </div>
        </div>
      )}

      {!result.has_detailed_steps && (
        <p className="rounded-lg border border-paper-line bg-paper px-3 py-2 text-xs text-muted">
          Procedimiento resumido: este resultado no incluye desglose paso a paso.
        </p>
      )}

      {result.warnings.length > 0 && (
        <ul className="space-y-1 text-xs text-amber-600">
          {result.warnings.map((warning, index) => (
            <li key={index}>⚠ {warning}</li>
          ))}
        </ul>
      )}

      {(copyText || result.result_latex) && (
        <div className="flex gap-2">
          <CopyButton text={copyText ?? null} label="Copiar resultado" />
          <CopyButton text={result.result_latex ?? null} label="Copiar como LaTeX" />
        </div>
      )}

      {result.has_detailed_steps && (
        <section className="border-t border-paper-line pt-4" aria-label="Pasos">
          <div className="mb-3 flex items-center justify-between">
            <h3 className="text-sm font-semibold text-ink">Pasos</h3>
            <span className="text-xs text-muted">{result.steps.length} {result.steps.length === 1 ? "paso" : "pasos"}</span>
          </div>
          <StepList steps={result.steps} />
        </section>
      )}
    </div>
  );
}
