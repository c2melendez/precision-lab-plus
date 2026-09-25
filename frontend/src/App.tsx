/**
 * S26.3 — shell global contractual.
 *
 * Navegación principal mediante sidebar izquierdo expandible/compacto.
 * El contenido de los módulos, motores, teclado global e historial se
 * conservan sin cambios funcionales.
 */

import { useEffect, useState } from "react";

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
import { GlobalKeyboardFallback } from "./components/GlobalKeyboardFallback";
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

const VISIBLE_MODES: CalculatorMode[] = ["basic", "graph", "matrix", "statistics", "geometry", "units"];

const MODE_ICONS: Partial<Record<CalculatorMode, ModeIconName>> = {
  basic: "scientific",
  graph: "graph",
  matrix: "matrix",
  statistics: "statistics",
  geometry: "geometry",
  units: "units",
};

const SIDEBAR_STORAGE_KEY = "precision-lab-sidebar-expanded";

function readInitialSidebarExpanded(): boolean {
  if (typeof window === "undefined") return true;
  return localStorage.getItem(SIDEBAR_STORAGE_KEY) !== "false";
}

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
  const [sidebarExpanded, setSidebarExpanded] = useState(readInitialSidebarExpanded);
  const layoutMode = useLayoutModeStore((s) => s.layoutMode);
  const isFloatingWideEnough = useMinWidthMediaQuery(FLOATING_MIN_WIDTH_PX);
  const hasFixedDock = !(layoutMode === "stacked" || (layoutMode === "floating" && isFloatingWideEnough));
  const mainBottomPadding = hasFixedDock ? "pb-56 dt:pb-40" : "pb-8";

  useEffect(() => {
    localStorage.setItem(SIDEBAR_STORAGE_KEY, String(sidebarExpanded));
  }, [sidebarExpanded]);

  return (
    <div className="min-h-screen bg-paper text-ink">
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:fixed focus:left-2 focus:top-2 focus:z-50 focus:rounded focus:bg-graph focus:px-3 focus:py-2 focus:text-white"
      >
        Saltar al contenido principal
      </a>

      <div className="flex min-h-screen">
        <aside
          aria-label="Navegación principal"
          data-sidebar-state={sidebarExpanded ? "expanded" : "compact"}
          className={`sticky top-0 z-10 flex h-screen shrink-0 flex-col border-r border-paper-line bg-paper-soft transition-[width] duration-200 ${sidebarExpanded ? "w-[72px] md:w-60" : "w-[72px]"}`}
        >
          <header className={`flex min-h-[72px] items-center justify-center gap-2 border-b border-paper-line px-3 ${sidebarExpanded ? "flex-col md:flex-row md:justify-start" : ""}`}>
            <div className={`min-w-0 overflow-hidden ${sidebarExpanded ? "w-full md:w-auto md:flex-1" : "w-full"}`}>
              <ProjectBrand />
            </div>
            <button
              type="button"
              onClick={() => setSidebarExpanded((current) => !current)}
              aria-label={sidebarExpanded ? "Contraer navegación" : "Expandir navegación"}
              aria-expanded={sidebarExpanded}
              title={sidebarExpanded ? "Contraer navegación" : "Expandir navegación"}
              className="grid h-11 w-11 shrink-0 place-items-center rounded-lg text-muted hover:bg-paper-line/40 hover:text-ink focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-marker"
            >
              <span aria-hidden="true" className="text-xl leading-none">☰</span>
            </button>
          </header>

          <nav aria-label="Modos de la calculadora" className="min-h-0 flex-1 overflow-y-auto px-2 py-3">
            <ul className="space-y-1">
              {VISIBLE_MODES.map((mode) => {
                const icon = MODE_ICONS[mode];
                const active = activeMode === mode;
                return (
                  <li key={mode}>
                    <button
                      type="button"
                      onClick={() => setActiveMode(mode)}
                      aria-current={active ? "page" : undefined}
                      aria-label={MODE_LABELS[mode]}
                      title={!sidebarExpanded ? MODE_LABELS[mode] : undefined}
                      className={`flex min-h-11 w-full items-center gap-3 rounded-lg px-3 text-sm font-medium transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-marker ${
                        active
                          ? "bg-marker-soft text-marker-text"
                          : "text-muted hover:bg-paper-line/40 hover:text-ink"
                      }`}
                    >
                      {icon && <ModeIcon name={icon} className="h-5 w-5 shrink-0" />}
                      {sidebarExpanded && <span className="hidden truncate md:inline">{MODE_LABELS[mode]}</span>}
                    </button>
                  </li>
                );
              })}
            </ul>
          </nav>

          <div className="space-y-1 border-t border-paper-line px-2 py-3">
            <button
              type="button"
              onClick={() => setShowHistory((current) => !current)}
              aria-label="Historial"
              aria-expanded={showHistory}
              aria-controls="history-panel"
              title={!sidebarExpanded ? "Historial" : undefined}
              className="flex min-h-11 w-full items-center gap-3 rounded-lg px-3 text-muted hover:bg-paper-line/40 hover:text-ink focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-marker"
            >
              <span aria-hidden="true" className="grid h-5 w-5 shrink-0 place-items-center">▤</span>
              {sidebarExpanded && <span className="hidden truncate text-sm md:inline">Historial</span>}
            </button>
            <div className="flex min-h-11 items-center gap-3 rounded-lg px-3 text-muted" title={!sidebarExpanded ? "Configuración" : undefined}>
              <div className="grid h-5 w-5 shrink-0 place-items-center">
                <AjustesPopover />
              </div>
              {sidebarExpanded && <span className="hidden truncate text-sm md:inline">Configuración</span>}
            </div>
          </div>
        </aside>

        <main
          id="main-content"
          tabIndex={-1}
          className={`mx-auto min-h-screen min-w-0 max-w-[1376px] flex-1 overflow-x-hidden px-3 py-5 sm:px-4 sm:py-6 lg:px-6 dt:px-8 ${mainBottomPadding} focus:outline-none`}
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
      <GlobalKeyboardFallback mode={activeMode} />
      <KeyboardDock />
    </div>
  );
}
