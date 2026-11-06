# Algebra229 AS-B-01 — aceptación scoped bilateral (Plus)

**Resultado: PASS_SCOPED bilateral.** Esta aceptación cubre exclusivamente la fila AS-B-01. No certifica la matriz completa de 229 filas ni la certificación global.

## Contrato y fuente
- Fila congelada: AS-B-01, N1, `factorizar`, `x^{2}-5x+6` → `\left(x - 3\right) \left(x - 2\right)`.
- Fuente: `qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz`; SHA-256 del contenido descomprimido `8cd36ff08343f98f92abd83e2b162d565e0cbe5c59dc73f26b1c018f77d663c7`.
- Test: `backend/tests/test_algebra229_as_b01.py`, blob `12aa538e77b63137ef92e47ede8f68506f6dbc71`.
- El test coteja la fila fuente exacta, ejercita `POST /api/v1/factor`, exige dos factores lineales y coteja diez sustituciones enteras con un evaluador de AST restringido y aritmética Python nativa, independiente de SymPy.

## Evidencia ejecutada sobre el SHA Plus
- SHA: `eb3a45c4b0ae68ff3d8da440b434c27098cf69c1`.
- Acumulativo [42133788691](https://github.com/c2melendez/precision-lab-plus/actions/runs/42133788691): **SUCCESS**, guard `skip=false`; ambos focales AS-B-01 PASSED; backend 2,800 passed / 1 skipped / 10 xfailed, cobertura 88.91%; frontend 1,055 passed / 28 todo.
- H1d [42133788792](https://github.com/c2melendez/precision-lab-plus/actions/runs/42133788792): **SUCCESS**, 38/38.
- CI estándar [42133788642](https://github.com/c2melendez/precision-lab-plus/actions/runs/42133788642): **SUCCESS**; backend 2,800 passed, frontend 1,055 passed.
- Runner [42133788643](https://github.com/c2melendez/precision-lab-plus/actions/runs/42133788643): **SUCCESS**.

## Decisión
AS-B-01 queda **PASS_SCOPED para Plus** y, junto con la evidencia equivalente de Lite, **PASS_SCOPED bilateral**. No hubo cambio de producto.
