/**
 * src/components/StepList.tsx — procedimiento paso a paso.
 * Mismo lenguaje visual que Precision Lab Lite (ficha tipo "margen de
 * cuaderno"), aprovechando aquí el modelo de datos completo (title, rule,
 * latex_before/after) que expone el backend SymPy. Ver auditoría Fase 0.
 *
 * Fase BB, Módulo BB0 (spec_rediseno_visual.md sección 14) — decisión
 * DEDUCIBLE registrada: `step.rule` (identificador técnico en inglés/
 * PascalCase, ej. "PowerRule", "ChainRule") dejó de renderizarse como
 * insignia junto al título. Se optó por la opción (b) del spec —dejar de
 * mostrarlo— y no (a) traducirlo ni (c) fusionarlo en `description`,
 * porque `title`/`description` ya están en español natural y cubren el
 * mismo propósito sin necesitar mantener un diccionario de traducción
 * para cada identificador que puedan emitir los distintos motores
 * (derivada, integral, límite, sistemas, EDO). El campo `rule` se
 * mantiene en el contrato de datos (`Step.rule`, sin cambios de tipo) por
 * si algún consumidor futuro lo necesita — solo se retiró su
 * visualización aquí, único punto donde se renderizaba (auditoría
 * confirmada: `grep` de `step.rule`/`.rule` en todo `src/` antes de este
 * cambio no encontró otro sitio).
 */

import type { components } from "../types/api";
import { MathRenderer } from "./MathRenderer";

type Step = components["schemas"]["Step"];

interface StepListProps {
  steps: Step[];
  activeIndex?: number;
}

export function StepList({ steps, activeIndex }: StepListProps) {
  if (steps.length === 0) return null;

  return (
    <ol className="relative flex flex-col gap-4 pl-7" aria-label="Procedimiento paso a paso">
      <div className="absolute bottom-2 left-[11px] top-2 w-px bg-paper-line" aria-hidden="true" />

      {steps.map((step, i) => {
        const isActive = activeIndex === i;
        return (
          <li key={step.index} className="relative fade-in">
            <span
              className={
                isActive
                  ? "absolute -left-7 top-0 grid h-6 w-6 place-items-center rounded-full bg-marker text-[10px] font-bold text-chrome ring-4 ring-marker-soft"
                  : "absolute -left-7 top-0 grid h-6 w-6 place-items-center rounded-full border border-paper-line bg-paper text-[10px] font-semibold text-muted"
              }
              aria-hidden="true"
            >
              {i + 1}
            </span>
            <div className={isActive ? "rounded-xl border border-marker/30 bg-marker-soft p-3" : "rounded-xl border border-paper-line bg-paper/60 p-3"}>
              <div className="flex items-center justify-between">
                <span className={isActive ? "text-sm font-medium text-marker-text" : "text-sm font-medium text-muted"}>
                  {step.title}
                </span>
              </div>
              <p className="mt-1 text-sm text-muted">{step.description}</p>
              <div className="mt-2 flex flex-wrap items-center gap-2 text-sm">
                <MathRenderer latex={step.latex_before} className="text-muted" />
                <span className="text-muted">→</span>
                <MathRenderer latex={step.latex_after} className="text-ink" />
              </div>
            </div>
          </li>
        );
      })}
    </ol>
  );
}
