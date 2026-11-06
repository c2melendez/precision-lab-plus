# Algebra229 AS-B-08 — aceptación scoped bilateral (Plus)

**Resultado: PASS_SCOPED bilateral.** Esta aceptación cubre exclusivamente AS-B-08; no certifica la matriz completa de 229 filas ni la certificación global.

## Contrato y fuente
- Fila congelada: AS-B-08, N2, `factorizar`, `x^{4}-5x^{2}+4` → `\left(x - 2\right) \left(x - 1\right) \left(x + 1\right) \left(x + 2\right)`.
- Fuente: `qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz`; SHA-256 descomprimido `8cd36ff08343f98f92abd83e2b162d565e0cbe5c59dc73f26b1c018f77d663c7`.
- Test: `backend/tests/test_algebra229_as_b08.py`, blob `ce7b9c095c4e30f6762441c754b90c60ce48abff`.
- El test coteja las siete celdas, llama a `POST /api/v1/factor`, exige el LaTeX exacto, cuatro factores con grados [1,1,1,1], las formas expandidas `x-2`, `x-1`, `x+1` y `x+2`, y valida diez sustituciones enteras con evaluador AST restringido y aritmética Python nativa, independiente de SymPy.

## Evidencia ejecutada sobre el SHA Plus
- SHA: `073c28998087ad2d24b0688a5089d4af75187f33`.
- Acumulativo [42147155135](https://github.com/c2melendez/precision-lab-plus/actions/runs/42147155135): **SUCCESS**, guard `skip=false`; ambos focales AS-B-08 PASSED; frontend 1,055 passed / 28 todo.
- H1d [42147155163](https://github.com/c2melendez/precision-lab-plus/actions/runs/42147155163): **SUCCESS**, 38/38.
- CI estándar [42147155107](https://github.com/c2melendez/precision-lab-plus/actions/runs/42147155107): **SUCCESS**, backend 2,800 passed / 1 skipped / 10 xfailed; frontend 1,055 passed.
- Runner [42147155112](https://github.com/c2melendez/precision-lab-plus/actions/runs/42147155112): **SUCCESS**.

## Decisión
AS-B-08 queda **PASS_SCOPED para Plus** y, junto con Lite, **PASS_SCOPED bilateral**. No hubo cambio de producto.
