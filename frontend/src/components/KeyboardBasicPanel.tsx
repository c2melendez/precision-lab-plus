import { useState, type MouseEvent as ReactMouseEvent } from "react";
import type { MathfieldElement } from "mathlive";
import { useLongPress } from "../hooks/useLongPress";
import { KeyGlyph } from "./KeyGlyph";
import { key, type KeyDef } from "./NaturalMathKeyboard";
import { triggerKeyFeedback } from "../utils/keyFeedback";

/**
 * Panel básico V5. Paridad funcional con Precision Lab Lite: concentra
 * escritura/control (ANS, DEL, DMS, prima, relacionales y Enter), mientras
 * variables y constantes viven exclusivamente en la categoría Símbolos.
 * `=` solo inserta igualdad; `⏎` es la única tecla que ejecuta el cálculo.
 */

export const BASIC_V5_ROWS: KeyDef[][] = [
  [
    key("7", "7", "7", false, undefined, "inserta el número siete"),
    key("8", "8", "8", false, undefined, "inserta el número ocho"),
    key("9", "9", "9", false, undefined, "inserta el número nueve"),
    key("(", "(", "paréntesis izquierdo", false, undefined, "abre un grupo o establece prioridad de operación"),
    key(")", ")", "paréntesis derecho", false, undefined, "cierra el grupo iniciado con un paréntesis"),
    key("⌫", "", "borrar", false, undefined, "borra el último carácter escrito"),
    key("DEL", "", "borrar todo el campo", false, undefined, "borra todo lo escrito en el campo actual"),
    key("ANS", "", "insertar el último resultado", false, undefined, "inserta el resultado del último cálculo"),
  ],
  [
    key("4", "4", "4"), key("5", "5", "5"), key("6", "6", "6"),
    key("×", "\\cdot", "multiplicar"), key("÷", "\\frac{#0}{#1}", "dividir"),
    key("%", "\\%", "porcentaje", false, undefined, "convierte el valor anterior en porcentaje dividiéndolo entre 100"), key("<", "<", "menor que"), key(">", ">", "mayor que"),
  ],
  [
    key("1", "1", "1"), key("2", "2", "2"), key("3", "3", "3"),
    key("+", "+", "sumar"), key("−", "-", "restar"), key(".", ".", "punto decimal"),
    key("=", "=", "igual", false, undefined, "inserta un signo de igualdad sin ejecutar el cálculo"),
    key("′", "'", "prima", false, undefined, "agrega una prima para escribir ecuaciones diferenciales"),
  ],
  [
    key("0", "0", "0"),
    key("°", "°", "grados", false, undefined, "inserta el símbolo de grados"),
    key("DMS", "#0°#1′#2″", "grados minutos segundos", false, undefined, "inserta la plantilla editable grados, minutos y segundos"),
    key("±()", "\\pm\\left(#0\\right)", "más/menos", false, undefined, "inserta las alternativas positiva y negativa"),
    key("≤", "\\le", "menor o igual que", false, undefined, "compara si el valor izquierdo es menor o igual que el derecho"),
    key("≥", "\\ge", "mayor o igual que", false, undefined, "compara si el valor izquierdo es mayor o igual que el derecho"),
    key("↵ Enter", "", "calcular", false, undefined, "ejecuta o resuelve la expresión actual"),
  ],
];

interface KeyboardBasicPanelProps {
  field: MathfieldElement | null;
  onSubmit?: () => void;
  lastAnswerLatex: string | null;
}

function BasicKey({
  k,
  onPress,
  onShowTooltip,
  className,
}: {
  k: KeyDef;
  onPress: (k: KeyDef, useSecondary?: boolean) => void;
  onShowTooltip: (k: KeyDef) => void;
  className: string;
}) {
  const hasSecondary = Boolean(k.secondaryAction);
  const hasTooltipOnly = !hasSecondary && Boolean(k.description);
  const longPress = useLongPress({
    onLongPress: () => {
      if (k.secondaryAction) onPress(k, true);
      else if (k.description) onShowTooltip(k);
    },
    onPress: () => onPress(k, false),
    disabled: !hasSecondary && !hasTooltipOnly,
  });

  if (!hasSecondary && !hasTooltipOnly) {
    return (
      <button
        type="button"
        onClick={() => onPress(k, false)}
        aria-label={k.ariaLabel}
                        aria-disabled={k.unavailable ? "true" : undefined}
        title={k.description}
        className={className}
      >
        <KeyGlyph glyph={k.glyph} />
      </button>
    );
  }

  return (
    <button type="button" {...longPress} aria-label={k.ariaLabel}
                        aria-disabled={k.unavailable ? "true" : undefined} title={k.description} className={className}>
      <KeyGlyph glyph={k.glyph} />
    </button>
  );
}

export function KeyboardBasicPanel({ field, onSubmit, lastAnswerLatex }: KeyboardBasicPanelProps) {
  const [notice, setNotice] = useState<string | null>(null);

  function press(k: KeyDef, useSecondary?: boolean) {
    if (useSecondary && k.secondaryAction) {
      if (k.unavailable) {
        setNotice(`${k.ariaLabel}: todavía no disponible.`);
        window.setTimeout(() => setNotice(null), 2500);
        return;
      }
      if (k.secondaryAction.type === "glyph") {
        field?.focus();
        field?.insert(secondaryGlyphLatex(k.secondaryAction.value));
      } else {
        field?.focus();
        field?.insert(k.secondaryAction.latex);
      }
      return;
    }
    if (k.unavailable) {
      setNotice(`${k.ariaLabel}: todavía no disponible.`);
      window.setTimeout(() => setNotice(null), 2500);
      return;
    }
    if (k.glyph === "⌫") {
      field?.focus();
      field?.executeCommand("deleteBackward");
      return;
    }
    if (k.glyph === "DEL") {
      field?.focus();
      field?.setValue("");
      return;
    }
    if (k.ariaLabel === "calcular") return onSubmit?.();
    if (k.glyph === "ANS") {
      if (!lastAnswerLatex) {
        setNotice("Sin resultado previo todavía.");
        window.setTimeout(() => setNotice(null), 2500);
        return;
      }
      field?.focus();
      field?.insert(lastAnswerLatex);
      return;
    }
    field?.focus();
    if (k.insertLatex) field?.insert(k.insertLatex);
  }

  function showTooltip(k: KeyDef) {
    if (!k.description) return;
    setNotice(k.description);
    window.setTimeout(() => setNotice(null), 3000);
  }

  function keyClass(k: KeyDef): string {
    const glyphStr = String(k.glyph);
    const base = "min-h-[38px] rounded-lg border shadow-sm transition-colors";
    if (k.unavailable) return `${base} border-dashed border-paper-line bg-paper text-muted/60 a11y-key-sm`;
    if (k.ariaLabel === "calcular") return `col-span-2 ${base} border-graph bg-graph text-white a11y-key-sm font-semibold hover:bg-graph/90`;
    if (glyphStr === "=") return `${base} border-marker/50 bg-paper-soft text-marker a11y-key-sm font-semibold hover:bg-marker-soft/30`;
    if (["×", "−", "+", "÷"].includes(glyphStr)) return `${base} border-marker/25 bg-marker-soft text-marker-text a11y-key-base font-semibold hover:bg-marker-soft/70`;
    if (["<", ">", "≤", "≥"].includes(glyphStr)) return `${base} border-marker/45 bg-paper-soft text-marker a11y-key-sm font-semibold hover:bg-marker-soft/20`;
    if (/^[0-9.%]$/.test(glyphStr)) return `${base} border-paper-line bg-paper-soft text-ink a11y-key-sm font-medium hover:border-marker/40 hover:bg-paper`;
    return `${base} border-paper-line bg-paper-soft text-ink a11y-key-tiny hover:border-marker/40 hover:bg-paper`;
  }

  function handleKeyboardClickCapture(e: ReactMouseEvent<HTMLDivElement>) {
    if ((e.target as HTMLElement).closest("button")) triggerKeyFeedback();
  }

  return (
    <div className="relative flex flex-col gap-1.5" onClickCapture={handleKeyboardClickCapture}>
      {notice && (
        <div className="absolute bottom-full left-0 right-0 z-20 mb-2 rounded-lg bg-chrome px-3 py-2 text-center text-xs text-bone shadow-xl">
          {notice}
        </div>
      )}

      {BASIC_V5_ROWS.map((row, i) => (
        <div key={i} className="grid grid-cols-8 gap-1">
          {row.map((k, j) => (
            <BasicKey key={j} k={k} onPress={press} onShowTooltip={showTooltip} className={keyClass(k)} />
          ))}
        </div>
      ))}
    </div>
  );
}

function secondaryGlyphLatex(glyph: import("./KeyGlyph").Glyph): string {
  if (typeof glyph !== "string") return "";
  if (glyph === "≤") return "\\le";
  if (glyph === "≥") return "\\ge";
  return glyph;
}
