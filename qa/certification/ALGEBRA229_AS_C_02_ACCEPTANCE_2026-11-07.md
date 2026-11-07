# Algebra229 AS-C-02 - aceptación bilateral

**Resultado: PASS bilateral.** Certificación global continúa **OPEN**.

## Contrato
- AS-C-02, N2, `simplificar`: `\frac{x^{3}-1}{x^{2}-1}` → `\frac{x^{2} + x + 1}{x + 1}`, sin nota de dominio en la fila congelada.

## Historial de este bloque
- Test-first inicial: Lite con 4/5 pasando; Plus con 3/4 (el endpoint devolvía la entrada sin cancelar).
- Corrección: Plus aplica `cancel` sobre el resultado de `simplify` cuando no aumenta la complejidad; Lite acepta `simplify(expand(...))` solo si da `0` o no tiene denominador.
- Oráculo de Plus: normalización de notación `**` → `^`; expectativa matemática intacta.

## Evidencia Plus — SHA `610cfc2e37ac898412a483c0eb0437b9949e4fc1`
- Cumulative 42335766429 SUCCESS; focal AS-C-02 4/4; backend 2,820 passed.
- CI 42335766470, H1d 42335766401 (38/38), Runner 42335766423: SUCCESS.
