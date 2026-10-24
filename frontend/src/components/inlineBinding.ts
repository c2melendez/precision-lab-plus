/** Recognize the same single-binding syntax preserved by the converter.
 * This only classifies intent; the converter/backend still validate values.
 */
export function parseInlineBinding(source: string): RegExpMatchArray | null {
  const normalized = source.replace(/\\(?:text|mathrm)\s*\{con\}/g, " con ").replace(/\\ /g, " ");
  return normalized.match(/^\s*(.+?)\s+con\s+([A-Za-z])\s*=\s*(.+?)\s*$/s);
}
