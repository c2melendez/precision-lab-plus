/**
 * src/components/MathRenderer.tsx — vista previa KaTeX (spec, sección 11).
 *
 * KaTeX SOLO vía su API segura (`katex.renderToString`) — el texto del
 * usuario NUNCA llega a `dangerouslySetInnerHTML` sin pasar antes por
 * KaTeX, que sanitiza su propia salida HTML internamente. Si KaTeX no
 * puede parsear el texto (no es LaTeX válido — esperado para ASCII crudo o
 * errores de conversión), fallback a texto plano, nunca a HTML sin
 * sanitizar.
 */

import katex from "katex";
import { useMemo } from "react";

interface MathRendererProps {
  latex: string;
  fallbackText?: string;
  className?: string;
}

// EN-SG-06/07: bound macro expansion so a self-referencing definition cannot
// loop. KaTeX's own default is 1000; it is pinned here so a library change
// cannot silently raise it.
export const MAX_KATEX_EXPANSIONS = 1000;

export function MathRenderer({ latex, fallbackText, className }: MathRendererProps) {
  const rendered = useMemo(() => {
    // KaTeX can render malformed markup-like input as an error expression
    // rather than throwing. Force suspicious HTML-tag payloads through the
    // React text-node fallback; never pass them to the HTML renderer.
    if (/<\/?[a-z][^>]*>/i.test(latex)) {
      return { html: null as string | null, reason: "markup" as const };
    }

    try {
      // Only KaTeX-generated output reaches dangerouslySetInnerHTML.
      // maxExpand is explicit so the recursion/expansion bound is a product
      // guarantee (EN-SG-06/07) and not an implicit library default.
      return {
        html: katex.renderToString(latex, {
          throwOnError: true,
          displayMode: false,
          maxExpand: MAX_KATEX_EXPANSIONS,
        }),
        reason: null as "markup" | "syntax" | null,
      };
    } catch {
      return { html: null as string | null, reason: "syntax" as const };
    }
  }, [latex]);

  if (rendered.html === null) {
    return (
      <span className={className} data-render-fallback={rendered.reason}>
        {fallbackText ?? latex}
      </span>
    );
  }

  // Salida de katex.renderToString, ya sanitizada por KaTeX (ver comentario del módulo).
  return <span className={className} dangerouslySetInnerHTML={{ __html: rendered.html }} />;
}
