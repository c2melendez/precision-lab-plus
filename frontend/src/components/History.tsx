/**
 * src/components/History.tsx — historial (spec, sección 11): conectado a
 * `useHistoryStore`; "Reusar" pasa por `reuseEntry` (que valida
 * `endpointUrl` contra `KNOWN_ENDPOINTS`, sección 11) antes de reejecutar
 * la llamada.
 */

import { useHistoryStore, type HistoryEntry } from "../store/useHistoryStore";

interface HistoryProps {
  onReuse: (entry: HistoryEntry) => void;
}

export function History({ onReuse }: HistoryProps) {
  const entries = useHistoryStore((state) => state.entries);
  const clearHistory = useHistoryStore((state) => state.clearHistory);


  if (entries.length === 0) {
    return (
      <div className="rounded-xl border border-dashed border-paper-line bg-paper p-6 text-center">
        <p className="text-sm font-medium text-ink">Todavía no hay historial en esta sesión.</p>
        <p className="mt-1 text-xs text-muted">Las operaciones recientes aparecerán aquí y podrás reutilizarlas.</p>
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
        {entries.map((entry: HistoryEntry) => (
          <li
            key={entry.id}
            className="rounded-xl border border-paper-line bg-paper p-3 shadow-sm"
          >
            <div className="flex items-start justify-between gap-3">
              <div className="min-w-0">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="rounded-full bg-marker-soft px-2 py-0.5 text-[10px] font-semibold text-marker-text">
                    {entry.sourceModule ?? "Científica"}
                  </span>
                  <span className="text-[10px] font-medium text-muted">{entry.operation}</span>
                </div>
                <p className="mt-1 break-words text-sm font-medium text-ink">{entry.label}</p>
                {(entry.resultText || entry.resultLatex) && (
                  <p className="mt-1 break-words text-xs text-marker">{entry.resultText ?? entry.resultLatex}</p>
                )}
              </div>
              <time className="shrink-0 text-[10px] text-muted" dateTime={new Date(entry.timestamp).toISOString()}>
                {new Date(entry.timestamp).toLocaleString()}
              </time>
            </div>
            <div className="mt-3 flex justify-end">
              <button
              type="button"
              onClick={() => onReuse(entry)
              aria-label={`Reusar entrada: ${entry.label}`}
                className="rounded-lg border border-paper-line bg-paper-soft px-3 py-1.5 text-xs font-medium text-ink hover:bg-paper-line/40"
              >
                Reusar
              </button>
            </div>
          </li>
        ))}
      </ul>

      {reuseError && (
        <p role="alert" className="text-sm text-red-600">
          {reuseError}
        </p>
      )}

      {(isReusing || reusedResult) && (
        <div className="border-t border-paper-line pt-4">
          <ResultPanel result={reusedResult} isLoading={isReusing} />
        </div>
      )}
    </div>
  );
}
