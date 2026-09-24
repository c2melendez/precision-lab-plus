/**
 * src/App.tsx — layout base + selector de modos + historial (spec,
 * sección 11, Módulo 12).
 *
 * Accesibilidad final (Módulo 12): skip-link al contenido principal,
 * `aria-current` en el modo activo, `aria-expanded` en el toggle de
 * historial, foco visible (`focus-visible:outline`) en todos los
 * controles interactivos añadidos aquí.
 */

import { useState } from "react";

import { BasicMode } from "./components/BasicMode";
import { SimpleBasicMode } from "./components/SimpleBasicMode";
import { DerivativeMode } from "./components/DerivativeMode";
import { EquationMode } from "./components/EquationMode";
import { ErrorBoundary } from "./components/ErrorBoundary";
import { GraphMode } from "./components/GraphMode";
import { History } from "./components/History";
import { HistoryDrawer } from "./components/HistoryDrawer";
import { IntegralMode } from "./components/IntegralMode";
import { LimitMode } from "./components/LimitMode";
import { MatrixMode } from "./components/MatrixMode";
import { StatisticsMode } from "./components/StatisticsMode";
import { SystemMode } from "./components/SystemMode";
import { UnitsMode } from "./components/UnitsMode";
import { GeometryMode } from "./components/GeometryMode";
import { AjustesPopover } from "./components/AjustesPopover";
import { KeyboardDock } from "./components/KeyboardDock";
import { ProjectBrand } from "./components/ProjectBrand";
import { ModeIcon, type ModeIconName } from "./components/ModeIcon";
import { useUIStore, type CalculatorMode } from "./store/useUIStore";
import { useLayoutModeStore } from "./store/useLayoutModeStore";
import { useMinWidthMediaQuery, FLOATING_MIN_WIDTH_PX } from "./hooks/useMinWidthMediaQuery";

const MODE_LABELS: Record<CalculatorMode, string> = {
  basic: "Científica",
  simple: "Basic",
  derivative: "Derivada",
  integral: "Integral",
  equation: "Ecuación",
  system: "Sistemas",
  matrix: "Matrices",
  graph: "Gráficas",
  limit: "Límite",
  statistics: "Estadística",
  geometry: "Geometría",
  units: "Unidades",
};

// Punto 4 del rediseño de teclado (pedido de Carlos): Derivada/Integral/
// Ecuación/Sistema ya no deben verse en el frontend — su función quedó
// cubierta por el router de Fase 1/2 dentro de "Científica" (ecuación/
// sistema/derivada/integral, todo en una sola pantalla vía
// calculusIntent.ts + submitCalculus). Los modos en sí NO se eliminan
// (siguen existiendo, siguen siendo válidos si algo interno navega ahí,
// ej. antes onGoToDerivative), solo se les quita la pestaña visible.
// Límite sigue el mismo criterio desde que se creó: el router también lo
// detecta ahora (ver calculusIntent.ts), así que tampoco ocupa un lugar
// en la navegación principal.
//
// P6 (spec v2 §7): "statistics" nueva, visible.
// P7 (spec v2 §8): "units" nueva, visible — con esto queda el orden
// final de §9 (previo al Módulo 5): Científica · Basic · Matrices ·
// Gráficas · Estadística · Unidades.
//
// Módulo 5 (hoja-de-ruta-visual.md §5 / spec §3): mismo tratamiento para
// "simple" (Basic) — confirmado por el usuario. Verificado: a diferencia
// de precision-lab-lite, SimpleKeyboard.tsx (Full) no tiene ninguna
// función propia sin equivalente (solo dígitos/paréntesis/AC/⌫/⏎, todo
// cubierto por BasicMode) — acá la eliminación no deja nada huérfano.
const VISIBLE_MODES: CalculatorMode[] = ["basic", "matrix", "graph", "statistics", "geometry", "units"];

const MODE_ICONS: Partial<Record<CalculatorMode, ModeIconName>> = {
  basic: "scientific",
  matrix: "matrix",
  graph: "graph",
  statistics: "statistics",
  geometry: "geometry",
  units: "units",
};

function ActiveModeForm({ mode }: { mode: CalculatorMode }) {
  switch (mode) {
    case "basic":
      return <BasicMode />;
    case "simple":
      return <SimpleBasicMode />;
    case "derivative":
      return <DerivativeMode />;
    case "integral":
      return <IntegralMode />;
    case "equation":
      return <EquationMode />;
    case "system":
      return <SystemMode />;
    case "matrix":
      return <MatrixMode />;
    case "graph":
      return <GraphMode />;
    case "statistics":
      return <StatisticsMode />;
    case "geometry":
      return <GeometryMode />;
    case "units":
      return <UnitsMode />;
    case "limit":
      return <LimitMode />;
  }
}

export default function App() {
  const activeMode = useUIStore((state) => state.activeMode);
  const setActiveMode = useUIStore((state) => state.setActiveMode);
  const lastErrorMessage = useUIStore((state) => state.lastErrorMessage);
  const [showHistory, setShowHistory] = useState(false);
  // Módulo P3: sin dock fijo en "stacked" (KeyboardDock retorna null ahí).
  // Módulo P4: tampoco hay dock fijo en "floating" cuando el viewport es
  // lo bastante ancho (el teclado vive en su FloatingWindow) — pero SÍ lo
  // hay si Flotante degrada a Enfoque en viewport angosto, por eso se usa
  // el mismo hook que KeyboardDock.tsx, no basta con mirar el string de
  // layoutMode.
  const layoutMode = useLayoutModeStore((s) => s.layoutMode);
  const isFloatingWideEnough = useMinWidthMediaQuery(FLOATING_MIN_WIDTH_PX);
  const hasFixedDock = !(layoutMode === "stacked" || (layoutMode === "floating" && isFloatingWideEnough));
  const mainBottomPadding = hasFixedDock ? "pb-56 dt:pb-40" : "pb-8";

  return (
    <div className="min-h-screen bg-paper text-ink">
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:fixed focus:left-2 focus:top-2 focus:z-50 focus:rounded focus:bg-graph focus:px-3 focus:py-2 focus:text-white"
      >
        Saltar al contenido principal
      </a>

      <header className="border-b border-paper-line bg-paper-soft px-3 py-3 sm:px-4">
        <div className="mx-auto flex max-w-[1376px] items-center justify-between gap-2">
          <ProjectBrand />
          <div className="flex shrink-0 items-center gap-1.5 sm:gap-2">
            <button
              type="button"
              onClick={() => setShowHistory((current) => !current)}
              aria-label="Historial"
              aria-expanded={showHistory}
              aria-controls="history-panel"
              className="min-h-11 rounded-full border border-paper-line px-3 text-sm text-ink hover:bg-paper-line/40 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-marker"
            >
              <span className="hidden sm:inline">Historial</span>
              <span className="sm:hidden" aria-hidden="true">▤</span>
            </button>
            <AjustesPopover />
          </div>
        </div>
      </header>

      <nav aria-label="Modos de la calculadora" className="border-b border-paper-line bg-paper-soft">
        <ul className="mx-auto flex max-w-[1376px] flex-nowrap gap-1 overflow-x-auto px-3 py-1.5 sm:justify-center sm:px-4 lg:gap-2">
          {VISIBLE_MODES.map((mode) => {
            const icon = MODE_ICONS[mode];
            return (
              <li key={mode} className="shrink-0">
                <button
                  type="button"
                  onClick={() => setActiveMode(mode)}
                  aria-current={activeMode === mode ? "page" : undefined}
                  className={`flex min-h-11 items-center gap-2 whitespace-nowrap rounded-lg border-b-2 px-3 text-sm font-medium transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-marker ${
                    activeMode === mode
                      ? "border-marker bg-marker-soft text-marker-text"
                      : "border-transparent text-muted hover:bg-paper-line/40 hover:text-ink"
                  }`}
                >
                  {icon && <ModeIcon name={icon} className="h-4 w-4" />}
                  <span>{MODE_LABELS[mode]}</span>
                </button>
              </li>
            );
          })}
        </ul>
      </nav>

      <div className="flex">
        {/* Módulo 0: padding inferior para que el KeyboardDock fijo no
            tape el contenido de ningún modo — cambio de layout global,
            deliberado, ver Cierre del Módulo 0 (mismo criterio que en
            precision-lab-lite/src/App.tsx). Módulo P3: en "stacked" no
            hay dock fijo que compensar (ver mainBottomPadding arriba). */}
        <main
          id="main-content"
          tabIndex={-1}
          className={`mx-auto min-w-0 max-w-[1376px] flex-1 px-3 py-5 sm:px-4 sm:py-6 lg:px-6 dt:px-0 ${mainBottomPadding} focus:outline-none`}
        >
          {lastErrorMessage && (
            <p role="alert" className="mb-4 rounded border border-red-200 bg-red-50 p-3 text-sm text-red-700">
              {lastErrorMessage}
            </p>
          )}

          <section aria-live="polite" aria-label="Resultado" className="min-w-0">
            <ErrorBoundary fallbackLabel="No se pudo mostrar el resultado.">
              <ActiveModeForm mode={activeMode} />
            </ErrorBoundary>
          </section>
        </main>
        <HistoryDrawer isOpen={showHistory} onClose={() => setShowHistory(false)}>
          <ErrorBoundary fallbackLabel="No se pudo mostrar el historial.">
            <History />
          </ErrorBoundary>
        </HistoryDrawer>
      </div>
      <KeyboardDock />
    </div>
  );
}
