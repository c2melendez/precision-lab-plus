/**
 * src/components/formatNumber.ts — formato de números (spec, sección 11):
 * notación científica para `result_approx` extremo.
 */

const SCIENTIFIC_THRESHOLD_HIGH = 1e6;
const SCIENTIFIC_THRESHOLD_LOW = 1e-6;

export function formatResultApprox(value: number): string {
  if (value === 0) return "0";
  const magnitude = Math.abs(value);
  if (magnitude >= SCIENTIFIC_THRESHOLD_HIGH || magnitude < SCIENTIFIC_THRESHOLD_LOW) {
    return value.toExponential(6);
  }
  return String(value);
}

/** SY-N-31: render the scientific view as mathematical LaTeX with nine
 * fractional mantissa digits. This does not change exact result fields.
 */
export function formatScientificLatex(value: number): string | null {
  if (!Number.isFinite(value)) return null;
  const [mantissa, exponent] = value.toExponential(9).split("e");
  return mantissa + "\\times10^{" + Number(exponent) + "}";
}
