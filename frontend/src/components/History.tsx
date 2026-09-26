import { MathRenderer } from "./MathRenderer";
import { useHistoryStore, type HistoryEntry } from "../store/useHistoryStore";

interface HistoryProps {
  onReuse: (entry: HistoryEntry) => void;
}

const OPERATION_LABELS: Record<string, string> = {
  evaluate: "Cálculo",
  solve: "Resolver ecuación",
  inequality: "Resolver inecuación",
  derivative: "Derivada",
  partial_derivative: "Derivada parcial",
  integral: "Integral",
  limit: "Límite",
  ode: "Ecuación diferencial",
  matrix_operation: "Operación de matrices",
  matrix_determinant: "Determinante",
  matrix_inverse: "Matriz inversa",
  matrix_transpose: "Matriz transpuesta",
  matrix_rank: "Rango de matriz",
  matrix_ref: "Forma escalonada",
  matrix_rref: "Forma escalonada reducida",
  matrix_trace: "Traza",
  statistics_descriptive: "Estadística descriptiva",
  statistics_combinatorics: "Combinatoria",
  statistics_correlation: "Correlación",
  graph_2d: "Gráfica 2D",
  graph_3d: "Gráfica 3D",
  graph_parametric: "Gráfica paramétrica",
  graph_polar: "Gráfica polar",
};

function naturalOperation(operation: string): string {
  if (OPERATION_LABELS[operation]) return OPERATION_LABELS[operation];
  return operation
    .replace(/[_-]+/g, " ")
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

function formatDateTime(timestamp: number): { date: string; time: string } {
  const date = new Date(timestamp);
  return {
    date: date.toLocaleDateString(undefined, { day: "2-digit", month: "2-digit", year: "numeric" }),
    time: date.toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit", second: "2-digit" }),
  };
}

function extractMatrices(payload: Record<string, unknown>): Array<{ name: string; values: unknown[][] }> {
  const labels: Record<string, string> = {
    matrix: "A",
    matrix_a: "A",
    matrix_b: "B",
  };
  return Object.entries(payload)
    .filter(([, value]) => Array.isArray(value) && (value as unknown[]).every((row) => Array.isArray(row)))
    .map(([key, value], index) => ({
      name: labels[key] ?? String.fromCharCode(65 + index),
      values: value as unknown[][],
    }));
}

function parseMatrixResult(entry: HistoryEntry): unknown[][] | null {
  if (Array.isArray(entry.resultData) && entry.resultData.every((row) => Array.isArray(row))) {
    return entry.resultData as unknown[][];
  }
  const value = entry.resultText ?? entry.resultLatex ?? "";
  try {
    const parsed = JSON.parse(value);
    if (Array.isArray(parsed) && parsed.every((row) => Array.isArray(row))) return parsed as unknown[][];
  } catch {
    // Puede venir como LaTeX.
  }
  const match = value.match(/\\begin\{(?:bmatrix|pmatrix|matrix)\}([\s\S]*?)\\end\{(?:bmatrix|pmatrix|matrix)\}/);
  if (!match) return null;
  return match[1]
    .split(/\\\\/)
    .map((row) => row.split("&").map((cell) => cell.trim()))
    .filter((row) => row.length > 0);
}

function MatrixGridPreview({ name, values }: { name: string; values: unknown[][] }) {
  return (
    <div className="flex items-center gap-2">
      <span className="text-xs font-semibold text-muted">{name} =</span>
      <div className="rounded-lg border border-paper-line bg-paper-soft px-2 py-1">
        {values.map((row, rowIndex) => (
          <div key={rowIndex} className="grid grid-flow-col auto-cols-min justify-center gap-2 font-mono text-xs text-ink">
            {row.map((value, columnIndex) => <span key={columnIndex}>{String(value)}</span>)}
          </div>
        ))}
      </div>
    </div>
  );
}

function MatrixPayload({ payload }: { payload: Record<string, unknown> }) {
  const matrices = extractMatrices(payload);
  if (matrices.length === 0) return null;
  return (
    <div className="mt-2 flex flex-wrap gap-3">
      {matrices.map(({ name, values }) => (
        <MatrixGridPreview key={name} name={name} values={values} />
      ))}
    </div>
  );
}

function normalizeBackendMathForDisplay(value: string): string {
  const trimmed = value.trim();
  if (!trimmed) return "";
  // Si ya contiene comandos LaTeX, se conserva tal cual.
  if (/\\[a-zA-Z]+/.test(trimmed)) return trimmed;

  let out = trimmed
    .replace(/\bpi\b/g, "\\pi")
    .replace(/\binfinity\b|\binf\b/g, "\\infty")
    .replace(/\bsqrt\s*\(([^()]+)\)/g, "\\sqrt{$1}")
    .replace(/\bsqrt\s*([A-Za-z0-9.]+)/g, "\\sqrt{$1}")
    .replace(/\b(sin|cos|tan|sec|csc|cot|ln|log|exp)\s*\(/g, (_match, fn: string) => `\\${fn}\\left(`);

  // Fracciones backend simples: (a)/(b) -> \\frac{a}{b}.
  // Se ejecuta varias veces para cubrir fracciones anidadas sencillas.
  for (let i = 0; i < 3; i += 1) {
    const next = out.replace(/\(([^()]+)\)\s*\/\s*\(([^()]+)\)/g, "\\frac{$1}{$2}");
    if (next === out) break;
    out = next;
  }

  // Cierra los \\left( introducidos arriba.
  const opens = (out.match(/\\left\(/g) ?? []).length;
  const closes = (out.match(/\\right\)/g) ?? []).length;
  if (opens > closes) {
    out += "\\right)".repeat(opens - closes);
  }

  return out;
}

function MathOrText({ latex, text, className }: { latex?: string; text?: string; className?: string }) {
  const raw = latex ?? text ?? "";
  if (!raw) return null;

  const normalized = normalizeBackendMathForDisplay(raw);
  const shouldRenderMath =
    Boolean(latex) ||
    /\\[a-zA-Z]+|[{}^_]/.test(normalized) ||
    /[+\-*/=()]/.test(normalized);

  return shouldRenderMath
    ? <MathRenderer latex={normalized} fallbackText={text ?? raw} className={className} />
    : <span className={className}>{raw}</span>;
}

export function History({ onReuse }: HistoryProps) {
  const entries = useHistoryStore((state) => state.entries);
  const clearHistory = useHistoryStore((state) => state.clearHistory);

  if (entries.length === 0) {
    return (
      <div className="rounded-xl border border-dashed border-paper-line bg-paper p-6 text-center">
        <p className="text-sm font-medium text-ink">Todavía no hay cálculos guardados.</p>
        <p className="mt-1 text-xs text-muted">Los cálculos que guardes aparecerán aquí, del más reciente al más antiguo.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-end">
        <button
          type="button"
          onClick={clearHistory}
          aria-label="Borrar historial"
          className="rounded-lg border border-paper-line bg-paper px-3 py-2 text-xs font-medium text-ink hover:bg-paper-line/40"
        >
          Borrar historial
        </button>
      </div>

      <ul className="space-y-2">
        {entries.map((entry) => {
          const when = formatDateTime(entry.timestamp);
          const matrices = extractMatrices(entry.requestPayload);
          const matrixResult = entry.sourceModule === "Matrices" ? parseMatrixResult(entry) : null;
          return (
            <li key={entry.id} className="rounded-xl border border-paper-line bg-paper p-3 shadow-sm">
              <div className="flex items-start justify-between gap-4">
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="rounded-full bg-marker-soft px-2 py-0.5 text-[10px] font-semibold text-marker-text">
                      {entry.sourceModule ?? "Científica"}
                    </span>
                    <span className="text-[11px] font-medium text-muted">{naturalOperation(entry.operation)}</span>
                  </div>

                  {matrices.length > 0 ? (
                    <>
                      <p className="mt-2 text-sm font-medium text-ink">{entry.label}</p>
                      <MatrixPayload payload={entry.requestPayload} />
                    </>
                  ) : (
                    <div className="mt-2 text-sm font-medium text-ink">
                      <MathOrText latex={entry.inputText} text={entry.label} className="text-sm font-medium text-ink" />
                    </div>
                  )}

                  {(entry.resultText || entry.resultLatex || matrixResult) && (
                    matrixResult ? (
                      <div className="mt-3">
                        <MatrixGridPreview name="Resultado" values={matrixResult} />
                      </div>
                    ) : (
                      <div className="mt-2 flex flex-wrap items-baseline gap-2">
                        <span className="text-[10px] font-semibold uppercase tracking-wide text-muted">Resultado</span>
                        <MathOrText
                          latex={entry.resultLatex}
                          text={entry.resultText}
                          className="text-sm font-medium text-marker-text"
                        />
                      </div>
                    )
                  )}
                </div>

                <div className="flex shrink-0 flex-col items-end gap-2">
                  <time className="text-right text-[10px] leading-4 text-muted" dateTime={new Date(entry.timestamp).toISOString()}>
                    <span className="block">{when.date}</span>
                    <span className="block">{when.time}</span>
                  </time>
                  <button
                    type="button"
                    onClick={() => onReuse(entry)}
                    aria-label={`Reusar entrada: ${entry.label}`}
                    className="rounded-lg border border-paper-line bg-paper-soft px-3 py-1.5 text-xs font-medium text-ink hover:bg-paper-line/40"
                  >
                    Reusar
                  </button>
                </div>
              </div>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
