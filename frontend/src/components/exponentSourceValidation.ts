// Reject a repeated braced superscript before conversion loses its grouping.
function hasRepeatedBracedSuperscript(source: string): boolean {
  for (let i = 0; i < source.length; i++) {
    if (source[i] !== "^") continue;
    let start = i + 1;
    while (/\s/.test(source[start] ?? "") && start < source.length) start++;
    if (source[start] !== "{") continue;
    let depth = 1;
    let end = start + 1;
    while (end < source.length && depth > 0) {
      if (source[end] === "{") depth++;
      else if (source[end] === "}") depth--;
      end++;
    }
    if (depth !== 0) continue; // Existing malformed-group validation owns this case.
    while (end < source.length && /\s/.test(source[end])) end++;
    if (source[end] === "^") return true;
  }
  return false;
}

/** Validate source before the LaTeX-to-ASCII conversion can erase errors. */
export function validateExponentSource(latex: string): void {
  if (hasRepeatedBracedSuperscript(latex)) {
    throw new Error("Doble superíndice sin agrupar: usa (x^{2})^{3} o x^{2^{3}}.");
  }
  if (/^\s*\^/.test(latex)) {
    throw new Error("Exponente sin base.");
  }
  if (/\^\s*\{\s*\}/.test(latex) || /\^\s*$/.test(latex)) {
    throw new Error("Exponente vacío: escriba un exponente antes de calcular.");
  }
}
