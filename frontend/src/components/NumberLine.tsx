import type { components } from "../types/api";

type Interval = components["schemas"]["InequalityInterval"];

/** Recta real a partir de intervalos canónicos; el texto exacto queda en Resultado. */
export function NumberLine({ intervals }: { intervals: Interval[] }) {
  const finite = intervals.flatMap((part) => [part.lower, part.upper])
    .filter((value): value is number => value !== null && value !== undefined && Number.isFinite(value));
  const min = finite.length ? Math.min(...finite) : 0;
  const max = finite.length ? Math.max(...finite) : 0;
  const margin = Math.max(2, (max - min) * 0.3);
  const left = min - margin, right = max + margin;
  const xPixel = (value: number) => 16 + ((value - left) / (right - left)) * 288;

  return (
    <div data-testid="inequality-number-line" role="img"
      aria-label={intervals.length ? "Recta real con intervalos solución y extremos abiertos o cerrados" : "Conjunto solución vacío"}
      className="w-full max-w-xl rounded-lg border border-paper-line bg-paper/50 p-2">
      {intervals.length === 0 ? <p className="py-7 text-center text-xs text-muted">Conjunto solución vacío ∅</p> : (
        <svg viewBox="0 0 320 110" className="h-28 w-full" aria-hidden="true">
          <line x1="12" x2="308" y1="50" y2="50" stroke="currentColor" opacity="0.35" strokeWidth="2" />
          {intervals.map((part, index) => {
            const start = part.lower === null || part.lower === undefined ? 16 : xPixel(part.lower);
            const end = part.upper === null || part.upper === undefined ? 304 : xPixel(part.upper);
            return <g key={index}>
              {start !== end && <line data-testid="inequality-segment" x1={start} x2={end} y1="50" y2="50" stroke="#2862b8" strokeWidth="7" />}
              {part.lower == null
                ? <path d="M13 50 L24 44 L24 56 Z" fill="#2862b8" />
                : <g><circle data-testid="inequality-endpoint" cx={start} cy="50" r="6" fill={part.lower_included ? "#2862b8" : "white"} stroke="#2862b8" strokeWidth="2.5" />
                    <text x={start} y="79" textAnchor="middle" fill="currentColor" fontSize="11">{part.lower_text ?? part.lower}</text></g>}
              {part.upper == null
                ? <path d="M307 50 L296 44 L296 56 Z" fill="#2862b8" />
                : part.upper !== part.lower && <g><circle data-testid="inequality-endpoint" cx={end} cy="50" r="6" fill={part.upper_included ? "#2862b8" : "white"} stroke="#2862b8" strokeWidth="2.5" />
                    <text x={end} y="79" textAnchor="middle" fill="currentColor" fontSize="11">{part.upper_text ?? part.upper}</text></g>}
            </g>;
          })}
        </svg>
      )}
    </div>
  );
}
