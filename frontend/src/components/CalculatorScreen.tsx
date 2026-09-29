/**
 * src/components/CalculatorScreen.tsx
 *
 * Fase E (spec UX estilo ClassCalc — mockup confirmado con el usuario,
 * mismo patrón ya aplicado en Precision Lab Lite vía Screen.tsx): fusiona
 * el campo de entrada, el resultado y una mini-cinta de historial
 * reciente en un solo contenedor "pantalla", en vez de que el resultado
 * aparezca condicionalmente debajo del teclado tras enviar el
 * formulario.
 *
 * Diferencia importante con Screen.tsx de Lite: esta versión depende de
 * un backend (POST /evaluate, etc.), así que el resultado es un
 * MathResponse recién llegado de la red (o `null`/`isLoading`), no un
 * cálculo local instantáneo. Por eso el componente recibe `result` +
 * `isLoading` en vez de calcular nada por su cuenta.
 *
 * La mini-cinta usa `useHistoryStore` directamente (ya trae las últimas
 * entradas persistidas) — no duplica esa lógica. `entry.label`/
 * `entry.inputText` son la sintaxis ASCII que el backend espera (ver
 * `latexToBackendSyntax` en NaturalMathField.tsx), NO LaTeX, así que se
 * muestran como texto plano; solo `entry.resultLatex` es LaTeX real y
 * pasa por MathRenderer. History.tsx (el panel completo con "Reusar") no
 * cambia — sigue siendo la vista de historial persistente completo.
 *
 * Fase P (Rediseño visual, Módulo P1 — spec_rediseno_visual.md sección 2):
 * las 6 disposiciones reservan 4 cuadrantes (entrada, resultado, teclado
 * colapsado, gráfica) — instrucción explícita del usuario. El cuadrante
 * de teclado no se renderiza aquí (el dock vive montado en la raíz de la
 * app, independiente de layoutMode); el de gráfica es <GraphPlaceholder />
 * — ver ese archivo para la decisión pendiente de graficación real
 * (Track de Graficación). "focus"/"floating"/"stacked" todavía no tienen
 * render propio (P2/P3/P4 pendientes) — caen al comportamiento de
 * "fused" por ahora.
 */

import type { MathfieldElement } from "mathlive";
import { useEffect } from "react";
import type { ReactNode } from "react";

import type { MathResponse } from "../api/client";
import { useFloatingLayoutStore } from "../store/useFloatingLayoutStore";
import { useHistoryStore, type HistoryEntry } from "../store/useHistoryStore";
import { useKeyboardPanelStore } from "../store/useKeyboardPanelStore";
import type { LayoutMode } from "../store/useLayoutModeStore";
import { FloatingWindow } from "./FloatingWindow";
import { GraphPlaceholder, type ScientificGraphState } from "./GraphPlaceholder";
import type { ScientificGraphContext } from "./scientificGraphContext";
import { KeyboardIcon } from "./KeyboardIcon";
import { MathRenderer } from "./MathRenderer";
import { NaturalMathField } from "./NaturalMathField";
import { ResultPanel } from "./ResultPanel";
import { StepList } from "./StepList";
import { useMinWidthMediaQuery, FLOATING_MIN_WIDTH_PX } from "../hooks/useMinWidthMediaQuery";

const SCIENTIFIC_SESSION_STARTED_AT = Date.now();

interface CalculatorScreenProps {
  latex: string;
  onLatexChange: (latex: string) => void;
  /** B6: callback de evaluación para Enter/Return físico en MathLive. */
  onEnter?: () => void;
  ariaLabel: string;
  placeholder?: string;
  fieldRef?: (el: MathfieldElement | null) => void;
  /** Opcional: algunos backends (derivada, integral, sistemas, matrices)
   * no tienen concepto de unidad angular — omitir ambas props oculta el
   * badge en vez de mostrar un toggle que no afectaría nada real. */
  angleUnit?: "rad" | "deg";
  onToggleAngleUnit?: () => void;
  result: MathResponse | null;
  isLoading: boolean;
  /** Punto 7 del rediseño de teclado: botón "X" para vaciar el campo,
   * visible dentro del display cuando hay contenido. */
  onClearField?: () => void;
  /** Módulo 6 (spec §7) + Fase P (Módulo P0/P1, spec_rediseno_visual.md
   * sección 2/15): "fused" (default) y "separated" ya existían. "split"
   * (Pantalla dividida) implementado en este módulo. "focus"/"floating"/
   * "stacked" están en el tipo pero sin render propio todavía. Paridad
   * con Screen.tsx de Lite. */
  layoutMode?: LayoutMode;
  /** Botón "Graficar" explícito en el cuadrante de gráfica (decisión de
   * producto confirmada por Carlos) — opcional porque no todos los
   * modos que usan CalculatorScreen lo implementan todavía (alcance V1:
   * solo BasicMode.tsx). Sin esta prop, GraphPlaceholder muestra el
   * estado vacío de siempre. */
  onGraphExpression?: () => void;
  graphState?: ScientificGraphState;
  graphContext?: ScientificGraphContext | null;
  onReuseRecent?: (entry: HistoryEntry) => void;
}

export function CalculatorScreen({
  latex,
  onLatexChange,
  onEnter,
  ariaLabel,
  placeholder,
  fieldRef,
  angleUnit,
  onToggleAngleUnit,
  result,
  isLoading,
  onClearField,
  layoutMode = "fused",
  onGraphExpression,
  graphState,
  graphContext,
  onReuseRecent,
}: CalculatorScreenProps) {
  // Botón "Graficar" (cuadrante de gráfica, las 6 disposiciones): solo
  // tiene sentido ofrecerlo cuando hay algo escrito. El backend valida
  // de verdad si es graficable al recibir el click.
  const resolvedGraphState: ScientificGraphState = graphState ?? (latex.trim() ? "available" : "empty");
  const canGraph = Boolean(onGraphExpression) && (
    resolvedGraphState === "available" ||
    (resolvedGraphState === "advanced" && Boolean(graphContext?.graphRequest))
  );
  // B7: la tarjeta "Entradas previas" representa la sesión actual de la
  // app, no el Historial persistente completo.
  const recentEntries = useHistoryStore((state) => state.entries)
    .filter((entry) => entry.timestamp >= SCIENTIFIC_SESSION_STARTED_AT)
    .slice(0, 5);

  const angleBadge = angleUnit && onToggleAngleUnit && (
    <div className="flex justify-end pt-[3px]">
      <button
        type="button"
        onClick={onToggleAngleUnit}
        aria-label={`Unidad angular: ${angleUnit === "rad" ? "radianes" : "grados"}. Cambiar.`}
        className="rounded-md bg-marker-soft px-2 py-1 text-[10px] font-semibold text-marker-text hover:bg-marker-soft/70"
      >
        {angleUnit === "rad" ? "RAD" : "DEG"}
      </button>
    </div>
  );

  const historyRibbon = recentEntries.length > 0 ? (
    <div className="flex min-w-0 flex-col gap-1.5">
      {recentEntries.map((entry, index) => (
        <button
          key={entry.id}
          type="button"
          onClick={() => onReuseRecent?.(entry)}
          disabled={!onReuseRecent}
          aria-label={`Reusar entrada ${index + 1}`}
          title="Reusar en Entrada"
          className={`flex min-w-0 items-center justify-between gap-3 rounded-lg px-2 py-1.5 text-left hover:bg-paper-line/40 disabled:cursor-default ${
            index === 0 ? "opacity-100" : index < 3 ? "opacity-80" : "opacity-65"
          }`}
        >
          <span className="min-w-0 flex-1 overflow-hidden">
            <MathRenderer
              latex={entry.inputText ?? entry.label}
              fallbackText={entry.label}
              className="text-sm text-ink"
            />
          </span>
          {entry.resultLatex ? (
            <MathRenderer
              latex={entry.resultLatex}
              fallbackText={entry.resultText}
              className="max-w-[45%] shrink-0 overflow-hidden text-sm font-medium text-marker-text"
            />
          ) : (
            <span className="max-w-[45%] shrink-0 truncate text-xs text-muted">
              {entry.resultText ?? "—"}
            </span>
          )}
        </button>
      ))}
    </div>
  ) : null;

  const inputField = (
    <div className="relative">
      <NaturalMathField
        latex={latex}
        onLatexChange={onLatexChange}
        onEnter={onEnter}
        ariaLabel={ariaLabel}
        placeholder={placeholder}
        fieldRef={fieldRef}
        bare
      />
      {onClearField && latex.length > 0 && (
        <button
          type="button"
          onClick={onClearField}
          aria-label="Borrar campo"
          title="clear field"
          className="absolute right-10 top-1/2 -translate-y-1/2 rounded p-1 text-muted hover:text-ink"
        >
          ✕
        </button>
      )}
      <button
        type="submit"
        aria-label="Evaluar"
        className="absolute right-1 top-1/2 flex h-8 w-8 -translate-y-1/2 items-center justify-center rounded-full bg-graph text-white hover:bg-graph/90"
      >
        →
      </button>
    </div>
  );

  const inputSurface = (
    <section aria-label="Entrada" className="rounded-xl border border-paper-line bg-paper-soft shadow-sm">
      <div className="flex items-center justify-between border-b border-paper-line px-4 py-2.5">
        <p className="text-xs font-semibold uppercase tracking-[0.14em] text-muted">Entrada</p>
        <span className="text-[11px] text-muted">Expresión matemática</span>
      </div>
      <div className="px-4 py-3">{inputField}</div>
    </section>
  );


  const resultBlock = <ResultPanel result={result} isLoading={isLoading} inputLatex={latex} angleUnit={angleUnit} showSteps={false} />;

  const recentSurface = (
    <section aria-label="Entradas previas" className="min-h-[120px] rounded-xl border border-paper-line bg-paper-soft shadow-sm">
      <div className="flex items-center justify-between border-b border-paper-line px-4 py-2.5">
        <p className="text-xs font-semibold uppercase tracking-[0.14em] text-muted">Entradas previas</p>
        <span className="text-[11px] text-muted">Sesión actual · hasta 5</span>
      </div>
      <div className="px-3 py-2">
        {historyRibbon ?? <p className="px-1 py-3 text-xs text-muted">Tus cálculos recientes de esta sesión aparecerán aquí.</p>}
      </div>
    </section>
  );

  const resultSurface = (
    <div className="min-h-[120px] rounded-xl border border-paper-line bg-paper-soft px-4 py-3 shadow-sm">
      {resultBlock}
    </div>
  );

  const graphSurface = (
    <div className="flex h-full min-h-[240px]">
      <GraphPlaceholder canGraph={canGraph} onGraph={onGraphExpression} state={resolvedGraphState} context={graphContext} />
    </div>
  );

  const isB7Layout =
    layoutMode === "fused" ||
    layoutMode === "split" ||
    layoutMode === "focus" ||
    layoutMode === "separated";

  if (isB7Layout) {
    const gridClass =
      layoutMode === "fused"
        ? "lg:grid-cols-[minmax(0,0.9fr)_minmax(360px,1.1fr)] lg:grid-rows-[auto_auto_minmax(140px,1fr)]"
        : layoutMode === "split"
          ? "lg:grid-cols-[minmax(0,1.35fr)_minmax(220px,0.75fr)_minmax(340px,1fr)] lg:grid-rows-[auto_minmax(180px,1fr)]"
          : layoutMode === "focus"
            ? "lg:grid-cols-[minmax(230px,0.8fr)_minmax(0,1.35fr)_minmax(340px,1fr)] lg:grid-rows-[auto_minmax(180px,1fr)]"
            : "lg:grid-cols-2 lg:grid-rows-[auto_minmax(220px,1fr)]";

    const inputPlacement =
      layoutMode === "fused"
        ? "lg:col-start-1 lg:row-start-1"
        : layoutMode === "split"
          ? "lg:col-start-1 lg:col-span-2 lg:row-start-1"
          : layoutMode === "focus"
            ? "lg:col-start-1 lg:row-start-1"
            : "lg:col-start-1 lg:row-start-1";

    const resultPlacement =
      layoutMode === "fused"
        ? "lg:col-start-1 lg:row-start-2"
        : layoutMode === "split"
          ? "lg:col-start-1 lg:row-start-2"
          : layoutMode === "focus"
            ? "lg:col-start-2 lg:row-start-1 lg:row-span-2"
            : "lg:col-start-2 lg:row-start-1";

    const recentPlacement =
      layoutMode === "fused"
        ? "lg:col-start-1 lg:row-start-3"
        : layoutMode === "split"
          ? "lg:col-start-2 lg:row-start-2"
          : layoutMode === "focus"
            ? "lg:col-start-1 lg:row-start-2"
            : "lg:col-start-1 lg:row-start-2";

    const graphPlacement =
      layoutMode === "fused"
        ? "lg:col-start-2 lg:row-start-1 lg:row-span-3"
        : layoutMode === "split"
          ? "lg:col-start-3 lg:row-start-1 lg:row-span-2"
          : layoutMode === "focus"
            ? "lg:col-start-3 lg:row-start-1 lg:row-span-2"
            : "lg:col-start-2 lg:row-start-2";

    return (
      <div className="flex min-w-0 flex-col gap-3">
        {angleBadge}
        <div className={`grid min-w-0 grid-cols-1 gap-3 ${gridClass}`}>
          <div className={`min-w-0 ${inputPlacement}`}>{inputSurface}</div>
          <div className={`min-w-0 ${resultPlacement}`}>{resultSurface}</div>
          <div className={`min-w-0 ${recentPlacement}`}>{recentSurface}</div>
          <div className={`min-w-0 ${graphPlacement}`}>{graphSurface}</div>
        </div>

        {result?.success && result.has_detailed_steps && result.steps.length > 0 && (
          <section aria-label="Pasos de solución" className="rounded-xl border border-paper-line bg-paper-soft p-4 shadow-sm">
            <div className="mb-3 flex items-center justify-between">
              <h3 className="text-sm font-semibold text-ink">Pasos de solución</h3>
              <span className="text-xs text-muted">{result.steps.length} {result.steps.length === 1 ? "paso" : "pasos"}</span>
            </div>
            <StepList steps={result.steps} />
          </section>
        )}
      </div>
    );
  }


  // "stacked" (Apilado, Módulo P3): una sola columna, teclado como
  // sección colapsada inline (no overlay). Ver Screen.tsx (Lite) para el
  // mismo criterio y por qué no usa <KeyboardPanel>.
  if (layoutMode === "stacked") {
    return (
      <div className="flex flex-col gap-3">
        {angleBadge}
        {historyRibbon && <div className="rounded-xl bg-paper-soft px-4 py-3 shadow-sm">{historyRibbon}</div>}
        {inputSurface}
        {resultBlock && <div className="rounded-xl bg-paper-soft px-4 py-3 shadow-sm">{resultBlock}</div>}
        <GraphPlaceholder canGraph={canGraph} onGraph={onGraphExpression} state={resolvedGraphState} context={graphContext} />
        <StackedKeyboardSection />
      </div>
    );
  }

  // "floating" (Flotante, Módulo P4 — mayor riesgo, confirmada por el
  // usuario). Degrada a Enfoque por debajo de lg (1024px), sin crear
  // estado de ventanas flotantes (P0). Ver Screen.tsx (Lite) para el
  // mismo criterio completo.
  if (layoutMode === "floating") {
    return (
      <FloatingScreenContent
        angleBadge={angleBadge}
        inputField={inputSurface}
        resultBlock={resultBlock}
        canGraph={canGraph}
        onGraphExpression={onGraphExpression}
        graphContext={graphContext}
      />
    );
  }

  // "focus" (Enfoque, Módulo P2): sin historial, resultado destacado,
  // gráfica con más área. Factorizado en <FocusScreenContent> porque
  // Flotante degradado (arriba) reusa exactamente esta composición.
  if (layoutMode === "focus") {
    return (
      <FocusScreenContent
        angleBadge={angleBadge}
        inputField={inputSurface}
        resultBlock={resultBlock}
        canGraph={canGraph}
        onGraphExpression={onGraphExpression}
        graphContext={graphContext}
      />
    );
  }

  if (layoutMode === "separated") {
    return (
      <div className="flex flex-col gap-3">
        {angleBadge}
        {historyRibbon && <div className="rounded-xl bg-paper-soft px-4 py-3 shadow-sm">{historyRibbon}</div>}
        {inputSurface}
        {resultBlock && <div className="rounded-xl bg-paper-soft px-4 py-3 shadow-sm">{resultBlock}</div>}
        <GraphPlaceholder canGraph={canGraph} onGraph={onGraphExpression} state={resolvedGraphState} context={graphContext} />
      </div>
    );
  }

  // "split" (Pantalla dividida, Módulo P1): dos columnas fijas desde dt
  // (≥1440px) — izquierda: historial + entrada; derecha: resultado +
  // gráfica, ambos visibles a la vez. Por debajo de dt colapsa a una sola
  // columna en el mismo orden (equivalente a la degradación a Apilado
  // acordada en P0, implementada solo con clases responsivas, sin
  // depender de que el Módulo P3 ya exista).
  if (layoutMode === "split") {
    return (
      <div className="flex flex-col gap-3">
        {angleBadge}
        <div className="flex flex-col gap-3 dt:grid dt:grid-cols-[1.2fr_1fr] dt:items-start dt:gap-4">
          <div className="flex flex-col gap-3">
            {historyRibbon && <div className="rounded-xl bg-paper-soft px-4 py-3 shadow-sm">{historyRibbon}</div>}
            {inputSurface}
          </div>
          <div className="flex flex-col gap-3">
            {resultBlock && <div className="rounded-xl bg-paper-soft px-4 py-3 shadow-sm">{resultBlock}</div>}
            <GraphPlaceholder canGraph={canGraph} onGraph={onGraphExpression} state={resolvedGraphState} context={graphContext} />
          </div>
        </div>
      </div>
    );
  }

  // "fused" (default) — todas las demás disposiciones ya tienen su
  // propia rama arriba (P1/P2/P3/P4).
  return (
    <div className="flex flex-col gap-3">
      <div className="rounded-xl bg-paper-soft px-4 py-3 shadow-inner shadow-black/10">
        {angleBadge && <div className="mb-1.5">{angleBadge}</div>}

        {historyRibbon && <div className="mb-2 border-b border-paper-line pb-2">{historyRibbon}</div>}

        {inputSurface}

        {resultBlock && <div className="mt-3 border-t border-paper-line pt-3">{resultBlock}</div>}
      </div>
      <GraphPlaceholder canGraph={canGraph} onGraph={onGraphExpression} state={resolvedGraphState} context={graphContext} />
    </div>
  );
}

/**
 * StackedKeyboardSection — Fase P, Módulo P3 ("Apilado"). Idéntico en
 * intención y comportamiento a la versión en Screen.tsx (Lite) — ver ese
 * archivo para el comentario completo de por qué no usa <KeyboardPanel>.
 */
function StackedKeyboardSection() {
  const isOpen = useKeyboardPanelStore((s) => s.isOpen);
  const content = useKeyboardPanelStore((s) => s.content);
  const basicContent = useKeyboardPanelStore((s) => s.basicContent);
  const toggle = useKeyboardPanelStore((s) => s.toggle);

  const canExpand = content !== null || basicContent !== null;

  return (
    <div className="flex flex-col gap-1.5">
      <div className="rounded-xl border border-paper-line bg-paper-soft">
        <button
          type="button"
          onClick={toggle}
          disabled={!canExpand}
          aria-expanded={isOpen}
          aria-label={isOpen ? "Cerrar teclado" : "Abrir teclado"}
          className="flex w-full items-center justify-between px-4 py-2.5 text-sm font-medium text-ink disabled:text-muted/40"
        >
          <span className="flex items-center gap-2">
            <KeyboardIcon className="h-4 w-4 text-marker" />
            Teclado
          </span>
          <span aria-hidden="true">{isOpen ? "▾" : "▴"}</span>
        </button>
        {isOpen && canExpand && (
          <div role="region" aria-label="Teclado matemático" className="border-t border-paper-line px-3 pb-3 pt-2">
            {content ?? basicContent}
          </div>
        )}
      </div>
    </div>
  );
}

interface FocusLikeContentProps {
  angleBadge: ReactNode;
  inputField: ReactNode;
  resultBlock: ReactNode;
  canGraph: boolean;
  onGraphExpression?: () => void;
  graphContext?: ScientificGraphContext | null;
}

/** Módulo P2 ("Enfoque"). Reusado tal cual por Flotante cuando degrada
 * (P0/P4). Ver Screen.tsx (Lite) para el mismo criterio. */
function FocusScreenContent({ angleBadge, inputField, resultBlock, canGraph, onGraphExpression, graphContext }: FocusLikeContentProps) {
  return (
    <div className="flex flex-1 flex-col gap-3">
      {angleBadge}
      {inputField}
      {resultBlock && <div className="rounded-xl bg-paper-soft px-5 py-4 text-center shadow-sm">{resultBlock}</div>}
      <GraphPlaceholder canGraph={canGraph} onGraph={onGraphExpression} context={graphContext} />
    </div>
  );
}

/**
 * Módulo P4 ("Flotante"). Idéntico en intención y comportamiento a
 * Screen.tsx (Lite) — ver ese archivo para el comentario completo sobre
 * el gating por breakpoint y la persistencia/clamp de las ventanas.
 */
function FloatingScreenContent({ angleBadge, inputField, resultBlock, canGraph, onGraphExpression, graphContext }: FocusLikeContentProps) {
  const isWideEnough = useMinWidthMediaQuery(FLOATING_MIN_WIDTH_PX);

  const keyboardWindow = useFloatingLayoutStore((s) => s.keyboardWindow);
  const graphWindow = useFloatingLayoutStore((s) => s.graphWindow);
  const setWindow = useFloatingLayoutStore((s) => s.setWindow);
  const clampAllToViewport = useFloatingLayoutStore((s) => s.clampAllToViewport);
  const resetToDefault = useFloatingLayoutStore((s) => s.resetToDefault);

  const basicContent = useKeyboardPanelStore((s) => s.basicContent);
  const content = useKeyboardPanelStore((s) => s.content);
  const isOpen = useKeyboardPanelStore((s) => s.isOpen);
  const toggle = useKeyboardPanelStore((s) => s.toggle);
  const canExpand = basicContent !== null || content !== null;

  useEffect(() => {
    if (!isWideEnough) return;
    clampAllToViewport(window.innerWidth, window.innerHeight);
    function onResize() {
      clampAllToViewport(window.innerWidth, window.innerHeight);
    }
    window.addEventListener("resize", onResize);
    return () => window.removeEventListener("resize", onResize);
  }, [isWideEnough, clampAllToViewport]);

  if (!isWideEnough) {
    return (
      <FocusScreenContent
        angleBadge={angleBadge}
        inputField={inputField}
        resultBlock={resultBlock}
        canGraph={canGraph}
        onGraphExpression={onGraphExpression}
        graphContext={graphContext}
      />
    );
  }

  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center justify-between">
        {angleBadge}
        <button type="button" onClick={resetToDefault} className="text-[11px] text-muted underline">
          Restablecer posición de ventanas
        </button>
      </div>
      {inputField}
      {resultBlock && <div className="rounded-xl bg-paper-soft px-4 py-3 shadow-sm">{resultBlock}</div>}
      {/* Fase Y (spec_rediseno_visual.md sección 11) — restricción dura:
          el teclado SIEMPRE inicia colapsado, en las 6 disposiciones sin
          excepción, Flotante incluida. Antes de este fix, la
          FloatingWindow de abajo se renderizaba sin condición alguna —
          es decir, el teclado quedaba SIEMPRE abierto en Flotante-ancho,
          violando la restricción. Ahora: colapsado por defecto (botón
          dedicado, mismo ícono/criterio que KeyboardDock.tsx), se abre
          por foco en el campo de entrada (NaturalMathField.tsx) o al
          presionar este botón — mismos 2 mecanismos que las otras 5
          disposiciones, sobre el mismo store `isOpen`. */}
      {isOpen && canExpand ? (
        <FloatingWindow title="Teclado" rect={keyboardWindow} onChange={(rect) => setWindow("keyboard", rect)}>
          {content ?? basicContent}
        </FloatingWindow>
      ) : (
        <button
          type="button"
          onClick={toggle}
          disabled={!canExpand}
          aria-expanded={isOpen}
          aria-label="Abrir teclado"
          className={
            canExpand
              ? "flex items-center justify-center gap-2 self-start rounded-lg bg-marker px-4 py-2 text-sm font-semibold text-chrome hover:bg-marker/90"
              : "flex items-center justify-center gap-2 self-start rounded-lg bg-chrome-soft px-4 py-2 text-sm text-bone/30"
          }
        >
          <KeyboardIcon className="h-4 w-4" />
          Teclado
        </button>
      )}
      <FloatingWindow title="Gráfica" rect={graphWindow} onChange={(rect) => setWindow("graph", rect)}>
        <GraphPlaceholder canGraph={canGraph} onGraph={onGraphExpression} context={graphContext} />
      </FloatingWindow>
    </div>
  );
}
