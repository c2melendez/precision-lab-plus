/**
 * src/components/GraphViewer.tsx — visor de gráficas 2D (spec, sección
 * 11): import DINÁMICO de Plotly (nunca en el bundle principal — solo se
 * carga cuando este componente realmente se monta, vía `React.lazy` en
 * `GraphMode.tsx`), botón "Descargar PNG" con `Plotly.toImage()`.
 */

import { useEffect, useRef, useState } from "react";

import type { components } from "../types/api";
import { integralRegionSegments, limitApproachSeries } from "./graphPreviewGeometry";

type GraphData = components["schemas"]["GraphData"];

// Tipo mínimo del módulo Plotly que realmente usamos — evita depender de
// toda la superficie de @types/plotly.js en la firma pública de este
// archivo, pero sigue tipado (no `any`).
interface PlotlyModule {
  newPlot: (
    div: HTMLElement,
    data: unknown[],
    layout: Record<string, unknown>,
    config?: Record<string, unknown>,
  ) => Promise<unknown>;
  toImage: (
    div: HTMLElement,
    opts: { format: string; width: number; height: number },
  ) => Promise<string>;
  purge: (div: HTMLElement) => void;
}

// Fase D (spec UX estilo ClassCalc §6): colores explícitos por curva, en
// vez del ciclo de color por defecto de Plotly — para que coincidan con
// los puntos de color del sidebar de expresiones en GraphMode.tsx.
// Fase T, Módulo T0: este archivo ya no declara su propia copia de
// CURVE_COLORS — nada la importaba desde aquí (verificado antes de
// quitarla), y la fuente única ahora es useGraphColorPaletteStore.ts,
// que no depende de este archivo ni de Plotly, así que no reintroduce
// el problema de bundle eager que motivó la duplicación original. El
// color de cada curva sigue llegando por el prop `colors` de
// `<GraphViewer>`, sin cambios en ese contrato.

function traceToPlotly(trace: GraphData["traces"][number], color?: string, breakAtX?: number) {
  if (trace.type === "surface") {
    return {
      x: trace.x,
      y: trace.y,
      z: trace.z,
      type: "surface" as const,
      name: trace.name,
      colorscale: "Viridis" as const,
      showscale: false,
    };
  }
  // Fase F (spec_edo_complejos_tooltips.md §3.4, Módulo F3): "point"
  // (Argand) -- mismo type "scatter" que una curva, pero mode:"markers"
  // en vez de "lines" (Plotly lo soporta nativamente, sin dependencia
  // nueva, tal como preveía el spec). NO reutiliza mode:"lines" con un
  // solo punto -- eso conecta con nada y Plotly lo dibuja invisible.
  if (trace.type === "point") {
    return {
      x: trace.x,
      y: trace.y,
      type: "scatter" as const,
      mode: "markers" as const,
      name: trace.name,
      marker: color ? { color, size: 10 } : { size: 10 },
    };
  }
  const x: Array<number | null> = [];
  const y: Array<number | null> = [];
  trace.x.forEach((value, index) => {
    if (breakAtX !== undefined && index > 0 && trace.x[index - 1] <= breakAtX && value > breakAtX) {
      x.push(null);
      y.push(null);
    }
    x.push(value);
    y.push(trace.y[index] ?? null);
  });
  return {
    x,
    y,
    type: "scatter" as const,
    mode: "lines" as const,
    name: trace.name,
    line: color ? { color } : undefined,
    connectgaps: false, // los `null` (discontinuidades, sección 10) cortan la línea
  };
}

function isSurface(data: GraphData): boolean {
  return data.traces.some((trace) => trace.type === "surface");
}

interface GraphViewerProps {
  data: GraphData;
  /** Colores por índice de traza, alineados con los puntos del sidebar
   * de expresiones (spec §6). Opcional — sin esto, Plotly usa su propio
   * ciclo de color por defecto (comportamiento anterior, sin cambios). */
  colors?: string[];
  integralBounds?: [number, number];
  limitFocus?: { point: string; direction: "both" | "left" | "right" };
  systemIntersections?: number[][];
}

export default function GraphViewer({ data, colors, integralBounds, limitFocus, systemIntersections }: GraphViewerProps) {
  const lowerBound = integralBounds?.[0];
  const upperBound = integralBounds?.[1];
  const limitPoint = limitFocus?.point;
  const limitDirection = limitFocus?.direction;
  const containerRef = useRef<HTMLDivElement | null>(null);
  const plotlyRef = useRef<PlotlyModule | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [downloadError, setDownloadError] = useState<string | null>(null);

  useEffect(() => {
    const container = containerRef.current;
    if (container === null) return;
    const safeContainer: HTMLDivElement = container;

    let cancelled = false;

    async function render(): Promise<void> {
      try {
        const plotlyModule = (await import("plotly.js-dist-min")) as unknown as {
          default: PlotlyModule;
        };
        const Plotly = plotlyModule.default;
        if (cancelled) return;
        plotlyRef.current = Plotly;

        const region = lowerBound !== undefined && upperBound !== undefined
          ? integralRegionSegments(data, lowerBound, upperBound) : null;
        const regionTraces = region ? ([
          { pieces: region.positive, name: "Aporte positivo", color: "rgba(22,134,93,0.35)" },
          { pieces: region.negative, name: "Aporte negativo", color: "rgba(195,74,74,0.35)" },
        ]).filter(({ pieces }) => pieces.length > 0).map(({ pieces, name, color }) => ({
          type: "scatter", mode: "lines", fill: "tozeroy", fillcolor: color,
          line: { width: 0 }, hoverinfo: "skip", showlegend: true, name,
          x: pieces.flatMap(([a, , b]) => [a, b, null]),
          y: pieces.flatMap(([, ya, , yb]) => [ya, yb, null]),
        })) : [];
        const approach = limitPoint && limitDirection ? limitApproachSeries(data, limitPoint, limitDirection) : null;
        const approachTraces = approach ? ([
          { samples: approach.left, name: "Aproximación izquierda", color: "#2862b8" },
          { samples: approach.right, name: "Aproximación derecha", color: "#b65d20" },
        ]).filter(({ samples }) => samples.some(Boolean)).map(({ samples, name, color }) => ({
          type: "scatter", mode: "lines", name, connectgaps: false,
          x: samples.map((sample) => sample?.[0] ?? null),
          y: samples.map((sample) => sample?.[1] ?? null),
          line: { color, width: 4 },
        })) : [];
        const finiteLimitPoint = limitPoint && limitPoint !== "oo" && limitPoint !== "-oo"
          && Number.isFinite(Number(limitPoint)) ? Number(limitPoint) : null;

        await Plotly.newPlot(
          safeContainer,
          [...regionTraces, ...data.traces.map((trace, i) => traceToPlotly(trace, colors?.[i], finiteLimitPoint ?? undefined)), ...approachTraces,
            ...(systemIntersections?.length ? [{ type: "scatter", mode: "markers", name: "Intersección común",
              x: systemIntersections.map(([x]) => x), y: systemIntersections.map(([, y]) => y),
              marker: { color: "#16865d", size: 11, line: { color: "white", width: 2 } } }] : [])],
          isSurface(data)
            ? {
                scene: {
                  xaxis: { title: { text: "x" } },
                  yaxis: { title: { text: "y" } },
                  zaxis: { title: { text: "z" } },
                },
                paper_bgcolor: "transparent",
                font: { color: "#1C1F26" },
                margin: { t: 20, r: 20, b: 20, l: 20 },
              }
            : {
                xaxis: { range: data.x_range, title: { text: data.x_axis_label ?? "x" } },
                yaxis: data.y_range
                  ? { range: region
                    ? [Math.min(0, data.y_range[0]), Math.max(0, data.y_range[1])]
                    : data.y_range, title: { text: data.y_axis_label ?? "y" } }
                  : { title: { text: data.y_axis_label ?? "y" } },
                shapes: [...[lowerBound, upperBound].filter((bound): bound is number => bound !== undefined),
                  ...(finiteLimitPoint !== null ? [finiteLimitPoint] : [])].map((bound) => ({
                  type: "line", x0: bound, x1: bound, y0: 0, y1: 1,
                  yref: "paper", line: { color: "#747b87", width: 1, dash: "dot" },
                })),
                paper_bgcolor: "transparent",
                plot_bgcolor: "transparent",
                font: { color: "#1C1F26" },
                margin: { t: 20, r: 20, b: 40, l: 50 },
              },
          { responsive: true, displaylogo: false },
        );
      } catch {
        if (!cancelled) {
          setLoadError("No se pudo cargar el visor de gráficas.");
        }
      }
    }

    void render();

    return () => {
      cancelled = true;
      if (plotlyRef.current) {
        plotlyRef.current.purge(safeContainer);
      }
    };
  }, [data, colors, lowerBound, upperBound, limitPoint, limitDirection, systemIntersections]);

  async function handleDownloadPng(): Promise<void> {
    if (!containerRef.current || !plotlyRef.current) return;
    try {
      const url = await plotlyRef.current.toImage(containerRef.current, {
        format: "png",
        width: 900,
        height: 600,
      });
      const link = document.createElement("a");
      link.href = url;
      link.download = "grafica.png";
      link.click();
    } catch {
      setDownloadError("No se pudo generar la imagen PNG.");
    }
  }

  if (loadError) {
    return (
      <p role="alert" className="text-sm text-red-600">
        {loadError}
      </p>
    );
  }

  return (
    <div className="space-y-2">
      {data.points_truncated && (
        <p className="text-xs text-amber-600">
          ⚠ Se redujo la densidad de muestreo respecto a lo solicitado.
        </p>
      )}
      <div
        ref={containerRef}
        role="img"
        aria-label="Gráfica de las expresiones ingresadas"
        className="h-96 w-full rounded border border-paper-line"
      />
      <div className="flex items-center gap-2">
        <button
          type="button"
          onClick={handleDownloadPng}
          aria-label="Descargar gráfica como PNG"
          className="rounded border border-paper-line px-3 py-1 text-xs text-muted hover:bg-paper-line/40"
        >
          Descargar PNG
        </button>
        {downloadError && (
          <span role="alert" className="text-xs text-red-600">
            {downloadError}
          </span>
        )}
      </div>
    </div>
  );
}
