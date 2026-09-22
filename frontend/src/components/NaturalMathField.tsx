/**
 * src/components/NaturalMathField.tsx — campo de entrada matemática
 * "natural" (fracciones, raíces y exponentes se ven mientras se escriben,
 * como en GeoGebra/Desmos), envolviendo el <math-field> de MathLive.
 *
 * MathLive nunca se muestra al backend: internamente guarda LaTeX, y este
 * componente lo convierte a la sintaxis ASCII que `parsing.py` espera
 * (implicit_multiplication_application + convert_xor, sección 5) antes de
 * llamarlo. Ver `latexToBackendSyntax` para los ajustes puntuales sobre lo
 * que produce `convertLatexToAsciiMath` por defecto.
 *
 * Re-vestido con los tokens Precision Lab (Fase 1/2): el campo vive sobre
 * el panel "paper", así que usa paper-soft/paper-line/ink, con el caret y
 * el resaltado de selección de MathLive en marker (vía sus custom
 * properties --caret-color / --selection-background-color).
 */

import "mathlive";
import { convertLatexToAsciiMath } from "mathlive/ssr";
import { useCallback, useEffect, useId, useRef } from "react";
import type { MathfieldElement, MathfieldElementAttributes } from "mathlive";
import { useKeyboardPanelStore } from "../store/useKeyboardPanelStore";

declare global {
  // eslint-disable-next-line @typescript-eslint/no-namespace
  namespace JSX {
    interface IntrinsicElements {
      "math-field": React.DetailedHTMLProps<
        React.HTMLAttributes<MathfieldElement> & Partial<MathfieldElementAttributes>,
        MathfieldElement
      >;
    }
  }
}

/**
 * `convertLatexToAsciiMath` deja `root(n)(x)` para `\sqrt[n]{x}`, pero el
 * backend no tiene una función `root` (solo `sqrt`, ver
 * `matrix_service`/`parsing.py`) — se reescribe como `(x)**(1/(n))`, que
 * SÍ entiende (`convert_xor`/`**` ambos soportados).
 */
function rewriteNthRoot(ascii: string): string {
  const pattern = /root\s*\(\s*([^()]+?)\s*\)\s*\(\s*([^()]+?)\s*\)/g;
  let result = ascii;
  // Se repite porque una raíz puede anidar otra en el índice o el radicando.
  for (let i = 0; i < 5 && pattern.test(result); i++) {
    pattern.lastIndex = 0;
    result = result.replace(pattern, (_match, n: string, x: string) => `(${x})**(1/(${n}))`);
  }
  return result;
}

/**
 * Fase 10 (auditoría Fase 0 v2): `convertLatexToAsciiMath` no colapsa
 * \mathrm{nombre} en un solo identificador — lo deletrea como letras
 * sueltas separadas por espacio (ej. \mathrm{mean} -> "m e a n"), que es
 * exactamente como LaTeX trata cualquier secuencia de letras en modo
 * matemático sin \mathrm/\operatorname (variables itálicas individuales
 * multiplicándose entre sí) — confirmado que ni \mathrm ni \operatorname
 * evitan esto en esta librería. Antes de este fix, cualquier tecla del
 * teclado que usa \mathrm{...} (mean/median/mode/stdev/var/mad/sort/mod/
 * lcm/nCr/nPr — el menú "Stat" casi completo) llegaba al backend como
 * variables sueltas sin sentido, no como el nombre de función esperado.
 *
 * Se recolapsan aquí, por nombre exacto y con case sensitivity (por eso
 * "nCr"/"nPr" van explícitos, no derivados de un patrón genérico) —
 * deliberadamente NO se usa un regex genérico de "letras sueltas seguidas
 * de paréntesis" porque eso colapsaría también multiplicación implícita
 * legítima entre variables de una letra (ej. "x y(z)").
 */
const KNOWN_MULTI_LETTER_FUNCTION_NAMES = [
  "median",
  "stdev",
  "mean",
  "mode",
  "sort",
  "mad",
  "mod",
  "lcm",
  "nCr",
  "nPr",
  "var",
  // P4 (spec v2 §5, Complejos) — mismo bug, mismo fix: sin esto "re(2+3i)"
  // llegaría al backend como "r e ( 2 + 3 i )" (variables sueltas).
  "re",
  "im",
  "arg",
  "conj",
  "topolar",
  // P6 (spec v2 §7.1): variantes poblacionales — mismo motivo.
  "stdevpop",
  "variancepop",
  "sign",
  "root",
  "log",
  "Log",
  "acsch",
  "asech",
  "acoth",
];

function collapseKnownFunctionNames(ascii: string): string {
  let result = ascii;
  for (const name of KNOWN_MULTI_LETTER_FUNCTION_NAMES) {
    const spelled = name.split("").join("\\s+");
    const pattern = new RegExp(`\\b${spelled}\\s*\\(`, "g");
    result = result.replace(pattern, `${name}(`);
  }
  return result;
}

/**
 * Pendiente #7 (revisión post-Módulo D, pedido por el usuario) —
 * equivalente Full de la notación de grados que Lite ya tiene en
 * normalize.ts. Mismo orden de reglas (DMS compuesto primero, simple
 * después) y misma decisión DEDUCIBLE: ° convierte SIEMPRE a radianes
 * (×π/180), sin consultar angle_unit — el símbolo ° es universal,
 * independiente del modo activo. Opera sobre el ASCII ya convertido por
 * `convertLatexToAsciiMath` (° es un glyph plano, no un macro LaTeX,
 * sobrevive esa conversión sin cambios — mismo criterio que sinh/cosh
 * ya confirmado en este archivo).
 *
 * NIVEL DE EVIDENCIA para esta función específica: 2, no 1 — no hay
 * `mathlive` real instalado en este entorno para confirmar con
 * ejecución qué ASCII exacto produce `convertLatexToAsciiMath` para un
 * "°" suelto. El regex asume que sobrevive como carácter literal, mismo
 * supuesto ya aceptado para sinh/cosh/csch/etc. en este mismo archivo.
 */
function applyDegreeNotation(ascii: string): string {
  let result = ascii;
  result = result.replace(/(-?\d+(?:\.\d+)?)°(\d+(?:\.\d+)?)′(\d+(?:\.\d+)?)″/g, "($1+$2/60+$3/3600)°");
  result = result.replace(/(-?\d+(?:\.\d+)?)°(\d+(?:\.\d+)?)′/g, "($1+$2/60)°");
  result = result.replace(/\(([^()]*)\)°/g, "(($1)*pi/180)");
  result = result.replace(/(-?\d+(?:\.\d+)?)°/g, "(($1)*pi/180)");
  return result;
}

/**
 * Pendiente #8 (revisión de pendientes, intento de verificación pedido
 * por el usuario): activé sinh⁻¹/cosh⁻¹/tanh⁻¹/csch⁻¹/sech⁻¹/coth⁻¹ (spec
 * teclado §5.1, Módulo A del motor) asumiendo que `convertLatexToAsciiMath`
 * resuelve "sinh^{-1}" solo, igual que ya hace para la sección "Inversas"
 * preexistente (sin⁻¹ etc.) — nunca pude confirmarlo con ejecución real:
 * intenté instalar `mathlive` desde el registro real y desde dos CDNs
 * (unpkg, jsdelivr) y los tres están bloqueados por la política de red
 * de este entorno (`host_not_allowed`, verificado con curl).
 *
 * En vez de dejarlo como una suposición sin verificar, esta función
 * ELIMINA la dependencia de esa suposición: convierte "sinhᐩexponente-1"
 * a "asinh" (etc.) de forma explícita, cubriendo las formas de ASCII más
 * probables que `convertLatexToAsciiMath` podría producir para "^{-1}"
 * (con `^` o `**`, con o sin paréntesis alrededor del -1) — así el
 * resultado es determinista sin importar cuál de esas formas use
 * realmente la librería. Sigue siendo nivel de evidencia 2 (no hay
 * ejecución real que lo confirme), pero ya no depende de una conducta
 * no verificada de un tercero.
 */
const HYPERBOLIC_INVERSE_NAMES: Record<string, string> = {
  sinh: "asinh",
  cosh: "acosh",
  tanh: "atanh",
  csch: "acsch",
  sech: "asech",
  coth: "acoth",
};

function rewriteHyperbolicInverses(ascii: string): string {
  let result = ascii;
  for (const [name, inverse] of Object.entries(HYPERBOLIC_INVERSE_NAMES)) {
    const pattern = new RegExp(`\\b${name}\\s*(?:\\^|\\*\\*)\\s*\\(?-1\\)?`, "g");
    result = result.replace(pattern, inverse);
  }
  return result;
}



function rewriteLogSubscriptBase(ascii: string): string {
  let result = ascii;
  // MathLive/Compute Engine puede serializar \\log_{2}(8) como
  // "log _2(8)" o "log _(2)(8)". Normalizamos ambas formas al
  // contrato explícito del backend: log(argumento,base).
  result = result.replace(
    /\blog\s*_\s*\(\s*([^()]+?)\s*\)\s*\(\s*([^()]+?)\s*\)/g,
    "log($2,$1)",
  );
  result = result.replace(
    /\blog\s*_\s*([A-Za-z0-9.+\-*/^]+)\s*\(\s*([^()]+?)\s*\)/g,
    "log($2,$1)",
  );
  return result;
}

function rewritePostfixPercent(ascii: string): string {
  let result = ascii;
  const pattern = /(\([^()]+\)|(?:\d+(?:\.\d+)?)|(?:[A-Za-z][A-Za-z0-9_]*))%/g;
  for (let i = 0; i < 8; i++) {
    const next = result.replace(pattern, "($1)/100");
    if (next === result) break;
    result = next;
  }
  return result;
}

function rewriteCommonInverses(ascii: string): string {
  const names: Record<string, string> = {
    sin: "asin", cos: "acos", tan: "atan", csc: "acsc", sec: "asec", cot: "acot",
  };
  let result = ascii;
  for (const [name, inverse] of Object.entries(names)) {
    result = result.replace(new RegExp(`\\b${name}\\s*(?:\\^|\\*\\*)\\s*\\(?-1\\)?`, "g"), inverse);
  }
  return result;
}

function rewriteFiniteAggregateLatex(latex: string): string | null {
  const m = latex.trim().match(/^\\(sum|prod)_\{([A-Za-z][A-Za-z0-9_]*)=([^{}]+)\}\^\{([^{}]+)\}(.+)$/s);
  if (!m) return null;
  const [, op, variable, lower, upper, body] = m;
  const convert = (part: string) => convertLatexToAsciiMath(part).trim();
  return `${op === "sum" ? "sum" : "product"}(${convert(body)},${variable},${convert(lower)},${convert(upper)})`;
}

function rewriteFiniteAggregateAscii(ascii: string): string | null {
  // MathLive puede serializar una sumatoria/productoria editada como:
  //   "sum _(i=1)^5i" / "prod _(i=1)^5i"
  // e incluso deletrear el operador como "s u m"/"p r o d". Ambas formas
  // aparecen en la conversión real y deben converger al contrato de
  // 4 argumentos del backend.
  const compact = ascii.trim()
    .replace(/\bs\s+u\s+m(?=\s*_)/g, "sum")
    .replace(/\bp\s+r\s+o\s+d(?=\s*_)/g, "prod");
  const m = compact.match(
    /^(sum|prod)\s*_\s*\(\s*([A-Za-z][A-Za-z0-9_]*)\s*=\s*([^()]+?)\s*\)\s*\^\s*(?:\(\s*([^()]+?)\s*\)|([^\s]+))\s*(.+)$/s,
  );
  if (!m) return null;
  const [, op, variable, lower, upperParen, upperBare, body] = m;
  const upper = upperParen ?? upperBare;
  return `${op === "sum" ? "sum" : "product"}(${body.trim()},${variable},${lower.trim()},${upper.trim()})`;
}

export function latexToBackendSyntax(latex: string): string {
  if (latex.trim() === "") return "";
  const aggregate = rewriteFiniteAggregateLatex(latex);
  if (aggregate) return aggregate;
  // MathLive may serialize ± as either \\pm or +-. Preserve its calculator
  // semantics as two branches instead of letting the parser reduce it to -x.
  const pmTrimmed = latex.trim();
  const pmMatch = pmTrimmed.match(/^\\pm\\left\((.*)\\right\)$/s) ?? pmTrimmed.match(/^\\pm\((.*)\)$/s);
  if (pmMatch) return `pm(${latexToBackendSyntax(pmMatch[1])})`;
  // MathLive elimina un signo % literal durante la conversión ASCII.
  // Reescribimos porcentajes postfix simples a una fracción LaTeX antes
  // de convertir, conservando casos como 100+50% -> 100+50/100.
  const latexWithPercent = latex.replace(/(-?\d+(?:\.\d+)?|[A-Za-z])%/g, "\\frac{$1}{100}");
  // MathLive puede descartar macros no estándar como \\csch/\\sech/\\coth
  // durante la conversión ASCII. Reescribimos las formas inversas en LaTeX
  // conocido antes de delegar al conversor, y luego collapseKnownFunctionNames
  // recompone el identificador multi-letra.
  const latexWithReciprocalHyperbolicInverses = latexWithPercent
    .replace(/\\csch\^\{-1\}/g, "\\mathrm{acsch}")
    .replace(/\\sech\^\{-1\}/g, "\\mathrm{asech}")
    .replace(/\\coth\^\{-1\}/g, "\\mathrm{acoth}");
  const ascii = convertLatexToAsciiMath(latexWithReciprocalHyperbolicInverses);
  const asciiAggregate = rewriteFiniteAggregateAscii(ascii);
  if (asciiAggregate) return asciiAggregate;

  const collapsed = collapseKnownFunctionNames(ascii);
  const normalizedAscii = rewriteLogSubscriptBase(rewriteNthRoot(collapsed));
  return rewritePostfixPercent(applyDegreeNotation(
    rewriteCommonInverses(rewriteHyperbolicInverses(normalizedAscii)),
  )).trim();
}

interface NaturalMathFieldProps {
  latex: string;
  onLatexChange: (latex: string) => void;
  ariaLabel: string;
  placeholder?: string;
  fieldRef?: (el: MathfieldElement | null) => void;
  /** Fase E: quita fondo/borde/sombra propios cuando el campo vive
   * anidado dentro de CalculatorScreen.tsx, que ya provee el contenedor
   * "pantalla" único (mismo criterio que NaturalInput.tsx en Lite). El
   * uso standalone original (con su propia píldora) se conserva cuando
   * `bare` no se pasa. */
  bare?: boolean;
}

export function NaturalMathField({
  latex,
  onLatexChange,
  ariaLabel,
  placeholder,
  fieldRef,
  bare = false,
}: NaturalMathFieldProps) {
  const elRef = useRef<MathfieldElement | null>(null);
  const fieldId = useId();

  useEffect(() => {
    const el = elRef.current;
    if (!el) return;

    function handleInput(): void {
      if (el && el.getValue("latex-unstyled") !== latex) {
        onLatexChange(el.getValue("latex-unstyled"));
      }
    }

    el.addEventListener("input", handleInput);
    return () => el.removeEventListener("input", handleInput);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [onLatexChange]);

  // Fase Y (spec_rediseno_visual.md sección 11) — restricción dura: el
  // teclado SIEMPRE inicia colapsado, y uno de los 2 mecanismos
  // obligatorios de apertura es "foco en el campo de entrada". Este
  // componente es el campo de entrada compartido por TODOS los modos
  // (Científica, Derivada, Integral, Ecuación, Sistema, Límite,
  // Gráficas, Unidades) — un solo listener aquí cubre los 4 breakpoints
  // × 6 disposiciones sin tocar cada modo por separado. `getState().open()`
  // en vez de un hook suscrito: esto es un evento imperativo, no algo
  // que deba re-renderizar este componente cuando `isOpen` cambie.
  useEffect(() => {
    const el = elRef.current;
    if (!el) return;
    const field = el;

    function handleFocus(): void {
      // Precision Lab usa exclusivamente su teclado propio. Refuerzo la
      // política "manual" también como propiedad del custom element y
      // oculto cualquier panel nativo que MathLive hubiera conservado.
      field.mathVirtualKeyboardPolicy = "manual";
      window.mathVirtualKeyboard.hide();
      useKeyboardPanelStore.getState().open();
    }

    field.addEventListener("focus", handleFocus);
    return () => field.removeEventListener("focus", handleFocus);
  }, []);

  useEffect(() => {
    const el = elRef.current;
    if (el && el.getValue("latex-unstyled") !== latex) {
      el.setValue(latex);
    }
  }, [latex]);

  // Fix (ver informe del bug de Gráficas a Carlos): el `ref` de abajo NO
  // puede ser una función inline — React reinvoca las callback refs cada
  // vez que su identidad cambia, y una función inline es una identidad
  // nueva en cada render. Cuando el `fieldRef` que pasa el padre también
  // dispara un `setState` (como en Graph2DForm, que guarda un array de
  // campos), eso generaba un bucle infinito de renders ("Maximum update
  // depth exceeded", React error #185). `useCallback` la mantiene
  // estable mientras `fieldRef` (la prop) no cambie de identidad.
  const setRef = useCallback(
    (el: MathfieldElement | null) => {
      elRef.current = el;
      if (el) {
        el.mathVirtualKeyboardPolicy = "manual";
        window.mathVirtualKeyboard.hide();
      }
      fieldRef?.(el);
    },
    [fieldRef],
  );

  return (
    <math-field
      id={fieldId}
      ref={setRef}
      math-virtual-keyboard-policy="manual"
      aria-label={ariaLabel}
      placeholder={placeholder}
      className={
        bare
          ? "w-full bg-transparent px-0 py-1 pr-10 text-right text-2xl text-ink"
          : "w-full rounded-full border border-paper-line bg-paper-soft px-5 py-2.5 text-base text-ink shadow-sm"
      }
      style={
        {
          display: "block",
          width: "100%",
          "--caret-color": "#E8A33D",
          "--selection-background-color": "#FBEFDA",
          "--selection-color": "#8A5A0E",
        } as React.CSSProperties
      }
    />
  );
}
