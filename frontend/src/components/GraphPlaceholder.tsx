/**
 * B7 — vista previa ligera de Científica.
 *
 * Este componente NO analiza matemática por sí mismo. Recibe un estado
 * semántico del orquestador y ofrece el puente explícito al módulo
 * Gráficas cuando existe contexto reutilizable.
 */
import { useEffect, useState } from "react";
import { callApi, type MathResponse } from "../api/client";
import { graphPreviewGeometry, integralRegionGeometry, limitApproachGeometry } from "./graphPreviewGeometry";
import type { ScientificGraphContext } from "./scientificGraphContext";
import { NumberLine } from "./NumberLine";
import { InequalityRegion } from "./InequalityRegion";

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
    const request = (context?.operation === "function" || context?.operation === "derivative" || context?.operation === "integral" || context?.operation === "limit" || context?.operation === "simplify" || context?.operation === "factor" || context?.operation === "ode" || context?.operation === "system") && context.canonicalResult
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
  const finiteLimitPoint = context?.operation === "limit"
    && context.metadata.point !== "oo" && context.metadata.point !== "-oo"
    && Number.isFinite(Number(context.metadata.point)) ? Number(context.metadata.point) : undefined;
  const geometry = preview?.success && preview.graph_data
    ? graphPreviewGeometry(preview.graph_data, definite, finiteLimitPoint) : null;
  const region = definite && geometry && preview?.graph_data
    ? integralRegionGeometry(preview.graph_data, Number(context?.metadata.lowerBound), Number(context?.metadata.upperBound), geometry)
    : null;
  const approach = context?.operation === "limit" && geometry && preview?.graph_data
    ? limitApproachGeometry(preview.graph_data, String(context.metadata.point),
      context.metadata.direction as "both" | "left" | "right", geometry) : null;

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
        {state === "available" && context?.visualization === "region-2d" ? (
          <>
            <InequalityRegion boundaries={context.metadata.constraints as NonNullable<MathResponse["inequality_constraints"]>}
              polygon={context.metadata.polygon as number[][]} viewport={context.metadata.viewport as number[]}
              kind={String(context.metadata.kind)} />
            <p className="text-[11px] text-muted">{context.metadata.kind === "empty" ? "Región factible vacía" : context.metadata.kind === "bounded" ? "Región factible acotada" : "Región factible no acotada"}. Frontera discontinua: excluida; continua: incluida.</p>
          </>
        ) : state === "available" && context?.visualization === "number-line" ? (
          <>
            <NumberLine intervals={context.metadata.intervals as NonNullable<MathResponse["inequality_intervals"]>} />
            <p className="text-[11px] text-muted">Conjunto solución: {context.canonicalResult?.text ?? "—"}. Los extremos huecos se excluyen; los rellenos se incluyen.</p>
          </>
        ) : (state === "available" || (state === "advanced" && context?.graphRequest)) ? (
          <>
            <div
              role="img"
              aria-label={geometry
                ? `Vista previa de ${context?.operation === "derivative" ? "función y derivada" : definite ? "integrando y región con signo" : context?.operation === "integral" ? "integrando y antiderivada" : context?.operation === "limit" ? "aproximación al límite" : "función"} de ${context?.variables[0] ?? "x"}`
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
                  {approach?.pointX !== null && approach?.pointX !== undefined && <line x1={approach.pointX} x2={approach.pointX} y1="0" y2="120" stroke="#9b6a18" strokeDasharray="3 3" opacity="0.7" />}
                  {geometry.paths.map((path, index) => <path key={index} d={path} fill="none"
                    stroke={context?.operation === "system" ? ["#2862b8", "#b65d20"][(context.metadata.componentIndices as number[] | null)?.[index] ?? index] : context?.operation === "ode" && context.metadata.kind === "one-parameter-family"
                      ? ["#2862b8", "#737b89", "#b65d20"][index] : "currentColor"}
                    opacity={context?.operation !== "ode" && context?.operation !== "function" && index === 0 ? 0.5 : 1}
                    strokeWidth={context?.operation !== "ode" && context?.operation !== "function" && index === 0 ? 1.5 : 2.5}
                    vectorEffect="non-scaling-stroke" />)}
                  {context?.operation === "system" && (context.metadata.intersections as number[][]).map(([x, y], index) =>
                    Number.isFinite(x) && Number.isFinite(y) && x >= preview!.graph_data!.x_range[0]
                    && x <= preview!.graph_data!.x_range[1] && y >= preview!.graph_data!.y_range![0]
                    && y <= preview!.graph_data!.y_range![1]
                      ? <circle key={index} data-testid="system-intersection" cx={geometry.projectX(x)}
                        cy={geometry.projectY(y)} r="4" fill="#16865d" stroke="white" strokeWidth="1.5" /> : null)}
                  {approach?.leftPath && <path data-testid="limit-left-approach" d={approach.leftPath} fill="none" stroke="#2862b8" strokeWidth="3" vectorEffect="non-scaling-stroke" />}
                  {approach?.rightPath && <path data-testid="limit-right-approach" d={approach.rightPath} fill="none" stroke="#b65d20" strokeWidth="3" vectorEffect="non-scaling-stroke" />}
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
                : context?.operation === "limit"
                ? `${context.metadata.point === "oo" || context.metadata.point === "-oo"
                  ? `Comportamiento hacia ${context.metadata.point === "oo" ? "+∞" : "−∞"}`
                  : `Aproximación ${context.metadata.direction === "left" ? "por la izquierda" : context.metadata.direction === "right" ? "por la derecha" : "por ambos lados"} a ${context.metadata.point}`}${context.metadata.bilateralDoesNotExist ? "; los límites laterales difieren" : ""}. Resultado: ${context.canonicalResult?.text ?? "—"}.`
                : context?.operation === "simplify" || context?.operation === "factor"
                ? `Curva de la expresión original; forma ${context.operation === "simplify" ? "simplificada" : "factorizada"} conservada en Resultado. Ambas formas son polinomios con dominio real completo.`
                : context?.operation === "ode"
                ? context.metadata.kind === "particular"
                  ? "Solución particular y(x) obtenida de la EDO; se grafica la solución, no la ecuación diferencial original."
                  : "Tres miembros representativos de la familia de soluciones (C₁=−1, 0, 1); el resultado conserva la constante arbitraria."
                : context?.operation === "system"
                ? context.metadata.coincident ? "Las ecuaciones coinciden: una curva representa infinitas soluciones."
                  : (context.metadata.intersections as number[][]).length
                    ? "Curvas componentes y sus intersecciones comunes marcadas en verde."
                    : "Curvas componentes sin intersección común; el sistema no tiene solución."
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
          <p className="max-w-md text-xs leading-relaxed text-muted">{message ?? ((context?.operation === "simplify" || context?.operation === "factor") && !context.graphRequest
            ? "Esta transformación requiere comprobar restricciones de dominio antes de comparar gráficas."
            : context?.operation === "ode" && !context.graphRequest
              ? "Esta familia necesita una vista avanzada para elegir sus parámetros antes de graficarla."
              : context?.operation === "system" && !context.graphRequest
                ? "Este sistema requiere una representación implícita o de más dimensiones en Gráficas."
                : context?.operation === "inequality" && context.visualization === "advanced"
                  ? "La región requiere una representación especializada para conservar exactamente sus fronteras."
              : STATE_COPY[state])}</p>
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
