/**
 * src/components/MatrixMode.tsx — modo Matrices (spec, sección 11):
 * selector de dimensión NxM para A y B, inputs de texto con validación,
 * conectado a `POST /matrix/operations`.
 */

import { useState, type FormEvent } from "react";

import type { MathResponse } from "../api/client";
import { submitAndRecord } from "../api/submitWithHistory";

const submitMatrices = (endpoint: Parameters<typeof submitAndRecord>[0], payload: Record<string, unknown>, label: string) =>
  submitAndRecord(endpoint, payload, label, "Matrices");
import { useUIStore } from "../store/useUIStore";
import { ResultPanel } from "./ResultPanel";

type Operation =
  | "add"
  | "subtract"
  | "multiply"
  | "kronecker"
  | "transpose"
  | "determinant"
  | "inverse"
  | "power"
  | "eigen"
  | "ref"
  | "rref"
  | "dot"
  | "cross"
  | "norm"
  | "trace"
  | "rank";

const OPERATION_LABELS: Record<Operation, string> = {
  add: "Suma (A + B)",
  subtract: "Resta (A − B)",
  multiply: "Multiplicación (A × B)",
  kronecker: "Kronecker (A ⊗ B)",
  transpose: "Transposición (Aᵀ)",
  determinant: "Determinante (|A|)",
  inverse: "Inversa (A⁻¹)",
  power: "Potencia (Aⁿ)",
  eigen: "Eigenvalores y eigenvectores",
  ref: "Forma escalonada (ref)",
  rref: "Forma escalonada reducida (rref)",
  // P5 (spec v2 §6): A y B son vectores (matriz 1xn o nx1) en estas 3.
  dot: "Producto punto (A · B)",
  cross: "Producto cruz (A ⨯ B)",
  norm: "Norma / magnitud (‖A‖)",
  // Módulo L0 (spec_graficacion_matrices_estadistica_unidades.md, sección 5).
  trace: "Traza (tr A)",
  rank: "Rango (rango A)",
};

const NEEDS_MATRIX_B: ReadonlySet<Operation> = new Set(["add", "subtract", "multiply", "kronecker", "dot", "cross"]);
const NEEDS_EXPONENT: ReadonlySet<Operation> = new Set(["power"]);

function emptyMatrix(rows: number, cols: number): string[][] {
  return Array.from({ length: rows }, () => Array.from({ length: cols }, () => ""));
}

function resizeMatrix(matrix: string[][], rows: number, cols: number): string[][] {
  return Array.from({ length: rows }, (_, r) =>
    Array.from({ length: cols }, (_, c) => matrix[r]?.[c] ?? ""),
  );
}

interface MatrixGridProps {
  label: string;
  matrix: string[][];
  rows: number;
  cols: number;
  onDimensionsChange: (rows: number, cols: number) => void;
  onCellChange: (row: number, col: number, value: string) => void;
}

function Stepper({ label, value, onChange }: { label: string; value: number; onChange: (n: number) => void }) {
  return (
    <label className="flex items-center gap-1.5 text-xs text-muted">
      {label}
      <button
        type="button"
        onClick={() => onChange(Math.max(1, value - 1))}
        aria-label={`Reducir ${label}`}
        className="h-5 w-5 rounded-full bg-paper-line/60 text-ink hover:bg-paper-line"
      >
        −
      </button>
      <span className="w-4 text-center font-mono text-ink">{value}</span>
      <button
        type="button"
        onClick={() => onChange(Math.min(6, value + 1))}
        aria-label={`Aumentar ${label}`}
        className="h-5 w-5 rounded-full bg-paper-line/60 text-ink hover:bg-paper-line"
      >
        +
      </button>
    </label>
  );
}

function MatrixGrid({
  label,
  matrix,
  rows,
  cols,
  onDimensionsChange,
  onCellChange,
}: MatrixGridProps) {
  return (
    <section aria-label={label} className="space-y-3 rounded-xl border border-paper-line bg-paper p-3">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div>
          <h3 className="text-sm font-semibold text-ink">{label}</h3>
          <p className="text-[11px] text-muted">{rows} × {cols}</p>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <Stepper label="Filas" value={rows} onChange={(n) => onDimensionsChange(n, cols)} />
          <Stepper label="Col" value={cols} onChange={(n) => onDimensionsChange(rows, n)} />
        </div>
      </div>
      <div className="max-w-full overflow-x-auto pb-1">
        <div
          role="group"
          aria-label={`Celdas de ${label}`}
          className="inline-grid min-w-max gap-1 rounded-lg bg-paper-soft p-2"
          style={{ gridTemplateColumns: `repeat(${cols}, minmax(0, 1fr))` }}
        >
          {matrix.map((row, r) =>
            row.map((cell, c) => (
              <input
                key={`${r}-${c}`}
                aria-label={`${label} celda fila ${r + 1} columna ${c + 1}`}
                value={cell}
                onChange={(e) => onCellChange(r, c, e.target.value)}
                className="w-12 rounded-md border border-paper-line bg-paper px-1.5 py-1.5 text-center text-sm text-ink sm:w-14"
              />
            )),
          )}
        </div>
      </div>
    </section>
  );
}

export function MatrixMode() {
  const [operation, setOperation] = useState<Operation>("add");
  const [rowsA, setRowsA] = useState(2);
  const [colsA, setColsA] = useState(2);
  const [matrixA, setMatrixA] = useState<string[][]>(emptyMatrix(2, 2));
  const [rowsB, setRowsB] = useState(2);
  const [colsB, setColsB] = useState(2);
  const [matrixB, setMatrixB] = useState<string[][]>(emptyMatrix(2, 2));
  const [exponent, setExponent] = useState("2");
  const [validationError, setValidationError] = useState<string | null>(null);
  const [lastResult, setLastResult] = useState<MathResponse | null>(null);

  const setLoading = useUIStore((state) => state.setLoading);
  const setErrorMessage = useUIStore((state) => state.setErrorMessage);
  const isLoading = useUIStore((state) => state.isLoading);

  function handleDimensionsA(rows: number, cols: number): void {
    setRowsA(rows);
    setColsA(cols);
    setMatrixA((current) => resizeMatrix(current, rows, cols));
  }

  function handleDimensionsB(rows: number, cols: number): void {
    setRowsB(rows);
    setColsB(cols);
    setMatrixB((current) => resizeMatrix(current, rows, cols));
  }

  function hasEmptyCell(matrix: string[][]): boolean {
    return matrix.some((row) => row.some((cell) => cell.trim() === ""));
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();

    if (hasEmptyCell(matrixA)) {
      setValidationError("Todas las celdas de la matriz A deben tener un valor.");
      return;
    }
    if (NEEDS_MATRIX_B.has(operation) && hasEmptyCell(matrixB)) {
      setValidationError("Todas las celdas de la matriz B deben tener un valor.");
      return;
    }
    if (NEEDS_EXPONENT.has(operation) && (exponent.trim() === "" || !/^-?\d+$/.test(exponent.trim()))) {
      setValidationError("El exponente debe ser un número entero.");
      return;
    }
    setValidationError(null);

    setLoading(true);
    setErrorMessage(null);
    try {
      let result: MathResponse;
      const label = `Matriz A ${rowsA}x${colsA} — ${OPERATION_LABELS[operation]}`;

      if (
        operation === "add" ||
        operation === "subtract" ||
        operation === "multiply" ||
        operation === "kronecker" ||
        operation === "dot" ||
        operation === "cross"
      ) {
        result = await submitMatrices(
          "/matrix/operations",
          { operation, matrix_a: matrixA, matrix_b: matrixB },
          `Matrices ${rowsA}x${colsA} ${operation} ${rowsB}x${colsB}`,
        );
      } else if (operation === "transpose") {
        result = await submitMatrices("/matrix/transpose", { matrix: matrixA }, label);
      } else if (operation === "determinant") {
        result = await submitMatrices("/matrix/determinant", { matrix: matrixA }, label);
      } else if (operation === "inverse") {
        result = await submitMatrices("/matrix/inverse", { matrix: matrixA }, label);
      } else if (operation === "ref") {
        result = await submitMatrices("/matrix/ref", { matrix: matrixA }, label);
      } else if (operation === "rref") {
        result = await submitMatrices("/matrix/rref", { matrix: matrixA }, label);
      } else if (operation === "norm") {
        result = await submitMatrices("/matrix/norm", { matrix: matrixA }, label);
      } else if (operation === "trace") {
        result = await submitMatrices("/matrix/trace", { matrix: matrixA }, label);
      } else if (operation === "rank") {
        result = await submitMatrices("/matrix/rank", { matrix: matrixA }, label);
      } else if (operation === "power") {
        result = await submitMatrices(
          "/matrix/power",
          { matrix: matrixA, exponent: Number(exponent) },
          `${label} (n=${exponent})`,
        );
      } else {
        result = await submitMatrices("/matrix/eigen", { matrix: matrixA }, label);
      }

      setLastResult(result);
      if (!result.success) {
        setErrorMessage(result.error_message ?? "Ocurrió un error.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} aria-labelledby="matrix-mode-heading" className="mx-auto grid w-full max-w-[1376px] gap-4 lg:grid-cols-[minmax(0,1.15fr)_minmax(320px,0.85fr)] lg:items-start">
      <section aria-label="Entrada de matrices" className="space-y-4 rounded-xl border border-paper-line bg-paper-soft p-4 shadow-sm">
        <div className="flex flex-wrap items-start justify-between gap-3 border-b border-paper-line pb-3">
          <div>
            <h2 id="matrix-mode-heading" className="text-base font-semibold text-ink">
              Matrices
            </h2>
            <p className="mt-0.5 text-xs text-muted">Define dimensiones, valores y operación</p>
          </div>
          <span className="rounded-full border border-paper-line bg-paper px-2.5 py-1 text-[11px] text-muted">
            Hasta 6×6
          </span>
        </div>

        <div className="rounded-xl border border-paper-line bg-paper p-3">
          <label htmlFor="matrix-operation" className="block text-xs font-semibold uppercase tracking-[0.14em] text-muted">
            Operación
          </label>
          <select
            id="matrix-operation"
            value={operation}
            onChange={(e) => setOperation(e.target.value as Operation)}
            className="mt-2 w-full rounded-lg border border-paper-line bg-paper-soft px-3 py-2 text-sm"
          >
            {(Object.keys(OPERATION_LABELS) as Operation[]).map((op) => (
              <option key={op} value={op}>
                {OPERATION_LABELS[op]}
              </option>
            ))}
          </select>
        </div>

        <MatrixGrid
          label="Matriz A"
          matrix={matrixA}
          rows={rowsA}
          cols={colsA}
          onDimensionsChange={handleDimensionsA}
          onCellChange={(r, c, value) =>
            setMatrixA((current) =>
              current.map((row, i) =>
                i === r ? row.map((cell, j) => (j === c ? value : cell)) : row,
              ),
            )
          }
        />

        {NEEDS_EXPONENT.has(operation) && (
          <div className="space-y-1">
            <label htmlFor="matrix-exponent" className="block text-sm text-muted">
              Exponente (entero, de -10 a 10)
            </label>
            <input
              id="matrix-exponent"
              type="text"
              inputMode="numeric"
              value={exponent}
              onChange={(e) => setExponent(e.target.value)}
              className="w-24 rounded border border-paper-line bg-paper-soft px-2 py-1 text-sm"
            />
          </div>
        )}

        {NEEDS_MATRIX_B.has(operation) && (
          <MatrixGrid
            label="Matriz B"
            matrix={matrixB}
            rows={rowsB}
            cols={colsB}
            onDimensionsChange={handleDimensionsB}
            onCellChange={(r, c, value) =>
              setMatrixB((current) =>
                current.map((row, i) =>
                  i === r ? row.map((cell, j) => (j === c ? value : cell)) : row,
                ),
              )
            }
          />
        )}

        {validationError && (
          <p role="alert" className="text-sm text-red-600">
            {validationError}
          </p>
        )}

        <button
          type="submit"
          className="w-full rounded-lg bg-graph px-4 py-2.5 text-sm font-semibold text-white hover:bg-graph/90"
        >
          Calcular
        </button>
      </section>

      <section aria-label="Resultado de matrices" className="min-w-0 rounded-xl border border-paper-line bg-paper p-4 shadow-sm">
        <div className="mb-3 border-b border-paper-line pb-3">
          <h3 className="text-xs font-semibold uppercase tracking-[0.14em] text-muted">Resultado</h3>
          <p className="mt-0.5 text-[11px] text-muted">Resultado de la operación seleccionada</p>
        </div>
        <ResultPanel result={lastResult} isLoading={isLoading} />
      </section>
    </form>
  );
}
