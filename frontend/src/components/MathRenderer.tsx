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

export function MathRenderer({ latex, fallbackText, className }: MathRendererProps) {
  const rendered = useMemo(() => {
    // KaTeX can render malformed markup-like input as an error expression
    // rather than throwing. Force suspicious HTML-tag payloads through the
    // React text-node fallback; never pass them to the HTML renderer.
    if (/<\/?[a-z][^>]*>/i.test(latex)) {
      return { html: null };
    }

    try {
      // Only KaTeX-generated output reaches dangerouslySetInnerHTML.
      return { html: katex.renderToString(latex, { throwOnError: true, displayMode: false }) };
    } catch {
      return { html: null };
    }
  }, [latex]);

  if (rendered.html === null) {
    return <span className={className}>{fallbackText ?? latex}</span>;
  }

  // Salida de katex.renderToString, ya sanitizada por KaTeX (ver comentario del módulo).
  return <span className={className} dangerouslySetInnerHTML={{ __html: rendered.html }} />;
}
