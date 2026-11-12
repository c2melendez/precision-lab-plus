/**
 * Parse a calculator binding, such as \sqrt[3]{x} \text{con} x=27, into
 * the expression and scalar substitution expected by POST /evaluate.
 * This recognizes one top-level binding only; ordinary equations remain
 * routed to /solve.
 */
export interface InlineSubstitution {
  expressionLatex: string;
  variable: string;
  valueLatex: string;
}

const INLINE_SUBSTITUTION = /^(.*?)\\(?:text|mathrm)\{con\}(?:\\\s*)?([A-Za-z][A-Za-z0-9_]*)\s*=\s*(.+)$/s;

export function extractInlineSubstitution(latex: string): InlineSubstitution | null {
  const match = latex.trim().match(INLINE_SUBSTITUTION);
  if (!match) return null;

  const expressionLatex = match[1].replace(/\\\s*$/, "").trim();
  const variable = match[2];
  const valueLatex = match[3].trim();

  if (!expressionLatex || !variable || !valueLatex) return null;
  if (expressionLatex.includes("=") || valueLatex.includes("=")) return null;

  return { expressionLatex, variable, valueLatex };
}
