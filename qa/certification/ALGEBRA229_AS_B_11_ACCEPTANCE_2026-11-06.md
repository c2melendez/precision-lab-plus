# Algebra229 AS-B-11 — aceptación scoped bilateral (Plus)

**Resultado: PASS_SCOPED bilateral.** Esta aceptación cubre exclusivamente AS-B-11; no certifica la matriz completa de 229 filas ni la certificación global.

## Contrato y fuente
- Fila congelada: AS-B-11, N2, `factorizar`, `ax+ay+bx+by` → `\left(a + b\right) \left(x + y\right)`.
- Fuente: `qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz`.
- Test: `backend/tests/test_algebra229_as_b11.py`, blob `abee8dd22b5e813dc836dac781cbf4555d5abba6`.
- El test coteja las siete celdas de contrato, exige `POST /api/v1/factor` con success=true, `result_latex` exacto, estructura Mul de dos binomios y valida diez sustituciones multi-variable con oráculo AST/aritmética entera nativa independiente de SymPy.

## Evidencia ejecutada sobre el SHA Plus
- SHA: `8fbac45e34c99ed08588930f92d0ee37876af78b`.
- Acumulativo [42153137640](https://github.com/c2melendez/precision-lab-plus/actions/runs/42153137640): **SUCCESS**.
- H1d [42153137790](https://github.com/c2melendez/precision-lab-plus/actions/runs/42153137790): **SUCCESS**.
- CI [42153137651](https://github.com/c2melendez/precision-lab-plus/actions/runs/42153137651): **SUCCESS**.
- Runner [42153137717](https://github.com/c2melendez/precision-lab-plus/actions/runs/42153137717): **SUCCESS**.

## Decisión
AS-B-11 queda **PASS_SCOPED para Plus** y, junto con Lite, **PASS_SCOPED bilateral**. No hubo cambio de producto.
