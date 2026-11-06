# Algebra229 AS-B-10 — aceptación scoped bilateral (Plus)

**Resultado: PASS_SCOPED bilateral.** Esta aceptación cubre exclusivamente AS-B-10; no certifica la matriz completa de 229 filas ni la certificación global.

## Contrato y fuente
- Fila congelada: AS-B-10, N2, `factorizar`, `x^{3}+3x^{2}+3x+1` → `\left(x + 1\right)^{3}`.
- Fuente: `qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz`.
- Test: `backend/tests/test_algebra229_as_b10.py`, blob `a2929d544b5fd0fe52e60ad8ab152ee64ec920f0`.
- El test coteja las siete celdas de contrato, exige `POST /api/v1/factor` con success=true, `result_latex` exacto, estructura Pow(exp=3) y valida diez sustituciones enteras con oráculo AST/aritmética entera nativa independiente de SymPy.

## Evidencia ejecutada sobre el SHA Plus
- SHA: `978cf1a6cc2930f2b58af1a845be12ecd7d1a4cf`.
- Acumulativo [42151649390](https://github.com/c2melendez/precision-lab-plus/actions/runs/42151649390): **SUCCESS**.
- H1d [42151649251](https://github.com/c2melendez/precision-lab-plus/actions/runs/42151649251): **SUCCESS**, 38/38.
- CI [42151649250](https://github.com/c2melendez/precision-lab-plus/actions/runs/42151649250): **SUCCESS**.
- Runner [42151649347](https://github.com/c2melendez/precision-lab-plus/actions/runs/42151649347): **FAILURE** en fingerprint (continuity simplificado previo); no bloquea aceptación matemática.

## Decisión
AS-B-10 queda **PASS_SCOPED para Plus** y, junto con Lite, **PASS_SCOPED bilateral**. No hubo cambio de producto.
