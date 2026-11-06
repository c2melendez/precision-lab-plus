# Algebra229 AS-B-09 — aceptación scoped bilateral (Plus)

**Resultado: PASS_SCOPED bilateral.** Esta aceptación cubre exclusivamente AS-B-09; no certifica la matriz completa de 229 filas ni la certificación global.

## Contrato y fuente
- Fila congelada: AS-B-09, N2, `factorizar`, `6x^{2}+5x-4` → `\left(2 x - 1\right) \left(3 x + 4\right)`.
- Fuente: `qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz`; SHA-256 descomprimido `8cd36ff08343f98f92abd83e2b162d565e0cbe5c59dc73f26b1c018f77d663c7`.
- Test: `backend/tests/test_algebra229_as_b09.py`, blob `2858d1440635087d8698f8db798672e6b2ed0b49`.
- El test coteja las siete celdas de contrato, exige `POST /api/v1/factor` con success=true, `result_latex` exacto, dos factores lineales (degrees [1,1]) y valida diez sustituciones enteras con oráculo AST/aritmética entera nativa independiente de SymPy.

## Evidencia ejecutada sobre el SHA Plus
- SHA: `ffd0ab3149679046c7a19092d8081aebc7f93323`.
- Acumulativo [42148198258](https://github.com/c2melendez/precision-lab-plus/actions/runs/42148198258): **SUCCESS** (backend + frontend).
- H1d [42148198289](https://github.com/c2melendez/precision-lab-plus/actions/runs/42148198289): **SUCCESS**, 38/38.
- CI [42148198266](https://github.com/c2melendez/precision-lab-plus/actions/runs/42148198266): **SUCCESS** (backend + frontend).
- Runner [42148198228](https://github.com/c2melendez/precision-lab-plus/actions/runs/42148198228): **SUCCESS**.

## Decisión
AS-B-09 queda **PASS_SCOPED para Plus** y, junto con Lite, **PASS_SCOPED bilateral**. No hubo cambio de producto.
