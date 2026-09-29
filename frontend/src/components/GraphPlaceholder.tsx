/**
 * B7 — vista previa ligera de Científica.
 *
 * Este componente NO analiza matemática por sí mismo. Recibe un estado
 * semántico del orquestador y ofrece el puente explícito al módulo
 * Gráficas cuando existe contexto reutilizable.
 */
import { useEffect, useState } from "react";
import { callApi, type MathResponse } from "../api/client";
import { graphPreviewGeometry, integralRegionGeometry } from "./graphPreviewGeometry";
import type { ScientificGraphContext } from "./scientificGraphContext";

export type ScientificGraphState =
  | "empty"
  | "available"
  | "not-needed"
  | "advanced"
  | "unavailable";

interface GraphPlaceholderProps {
  canGraph?: boolean;
  onGraph?: () => void;
  state?: ScientificGraphState;
  message?: string;
  context?: ScientificGraphContext | null;
}

const STATE_COPY: Record<Exclude<ScientificGraphState, "available">, string> = {
  empty: "Escribe o resuelve una expresión para preparar una vista previa.",
  "not-needed": "Representación gráfica no necesaria. El resultado no requiere una gráfica para su interpretación.",
  advanced: "Esta operación requiere una representación más avanzada. Puedes continuar el análisis en Gráficas.",
  unavailable: "No hay una representación gráfica útil disponible para esta operación.",
};

export function GraphPlaceholder({
  canGraph = false,
  onGraph,
  state = canGraph ? "available" : "empty",
  message,
  context,
}: GraphPlaceholderProps) {
  const canOpenGraphing = Boolean(onGraph) && canGraph && (state === "available" || state === "advanced");
  const [preview, setPreview] = useState<MathResponse | null>(null);
  const [isPreviewLoading, setPreviewLoading] = useState(false);

  useEffect(() => {
    const request = (context?.operation === "function" || context?.operation === "derivative" || context?.operation === "integral") && context.canonicalResult
      ? context.graphRequest : null;
    setPreview(null);
    if (!request) {
      setPreviewLoading(false);
      return;
    }
    let cancelled = false;
    setPreviewLoading(true);
    void callApi(request.endpoint, request.payload).then((response) => {
      if (!cancelled) {
        setPreview(response);
        setPreviewLoading(false);
      }
    });
    return () => { cancelled = true; };
  }, [context]);

  const definite = context?.operation === "integral" && context.metadata.kind === "definite";
  const geometry = preview?.success && preview.graph_data
    ? graphPreviewGeometry(preview.graph_data, definite) : null;
  const region = definite && geometry && preview?.graph_data
    ? integralRegionGeometry(preview.graph_data, Number(context?.metadata.lowerBound), Number(context?.metadata.upperBound), geometry)
    : null;

  return (
    <section
      data-testid="scientific-graph"
      aria-label="Vista previa de gráfica"
      className="flex min-h-[110px] flex-1 flex-col rounded-xl border border-paper-line bg-paper-soft/60"
    >
      <div className="flex items-center justify-between border-b border-paper-line px-4 py-2.5">
        <p className="text-xs font-semibold uppercase tracking-[0.14em] text-muted">Vista previa de gráfica</p>
        <span className="text-[10px] font-medium text-muted">Científica</span>
      </div>

      <div className="flex flex-1 flex-col items-center justify-center gap-3 px-4 py-6 text-center">
        {(state === "available" || (state === "advanced" && context?.graphRequest)) ? (
          <>
            <div
              role="img"
              aria-label={geometry
                ? `Vista previa de ${context?.operation === "derivative" ? "función y derivada" : definite ? "integrando y región con signo" : context?.operation === "integral" ? "integrando y antiderivada" : "función"} de ${context?.variables[0] ?? "x"}`
                : "Vista previa pendiente de renderizado contextual"}
              className="grid h-24 w-full max-w-md place-items-center overflow-hidden rounded-lg border border-paper-line bg-paper/50"
            >
              {geometry ? (
                <svg data-testid="scientific-preview-plot" viewBox="0 0 320 120" preserveAspectRatio="none" className="h-full w-full text-graph" aria-hidden="true">
                  {geometry.zeroX !== null && <line x1={geometry.zeroX} x2={geometry.zeroX} y1="0" y2="120" stroke="currentColor" opacity="0.2" />}
                  {geometry.zeroY !== null && <line x1="0" x2="320" y1={geometry.zeroY} y2={geometry.zeroY} stroke="currentColor" opacity="0.2" />}
                  {region?.positivePath && <path data-testid="integral-positive-region" d={region.positivePath} fill="#16865d" opacity="0.35" />}
                  {region?.negativePath && <path data-testid="integral-negative-region" d={region.negativePath} fill="#c34a4a" opacity="0.35" />}
                  {region && [region.lowerX, region.upperX].map((x, index) => <line key={index} x1={x} x2={x} y1="0" y2="120" stroke="currentColor" strokeDasharray="3 3" opacity="0.4" />)}
                  {geometry.paths.map((path, index) => <path key={index} d={path} fill="none" stroke="currentColor" opacity={context?.operation !== "function" && index === 0 ? 0.5 : 1} strokeWidth={context?.operation !== "function" && index === 0 ? 1.5 : 2.5} vectorEffect="non-scaling-stroke" />)}
                </svg>
              ) : (
                <span className="text-[11px] text-muted">
                  {isPreviewLoading ? "Preparando vista previa…" : preview && !preview.success
                    ? "Vista previa no disponible para esta función" : preview?.success
                      ? "No hay curva real visible en este rango" : "Vista previa contextual"}
                </span>
              )}
            </div>
            <p className="max-w-md text-[11px] text-muted">
              {definite
                ? `Región con signo de ${context?.metadata.lowerBound} a ${context?.metadata.upperBound}; verde suma, rojo resta${Number(context?.metadata.orientation) < 0 ? " (sentido inverso)" : ""}. Valor exacto: ${context?.canonicalResult?.text ?? "—"}.`
                : context?.operation === "integral"
                ? "Integrando y antiderivada representativa (C=0 solo en la gráfica); el resultado conserva +C."
                : context?.operation === "derivative"
                ? `Función original y derivada de orden ${context.metadata.order} respecto de ${context.variables[0]}.`
                : context?.operation === "function"
                ? `Función de ${context.variables[0]} preparada para Gráficas${context.canonicalResult ? " con resultado conservado" : ""}.`
                : "La vista ampliada conserva la expresión y el contexto matemático de la operación."}
            </p>
          </>
        ) : (
          <p className="max-w-md text-xs leading-relaxed text-muted">{message ?? STATE_COPY[state]}</p>
        )}

        {canOpenGraphing && (
          <button
            type="button"
            onClick={onGraph}
            className="rounded-md bg-marker px-3 py-1.5 text-xs font-semibold text-chrome hover:bg-marker/90"
          >
            Abrir en Gráficas
          </button>
        )}
      </div>
    </section>
  );
}
