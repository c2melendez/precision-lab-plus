# Algebra229 AS-B-07 — aceptación scoped bilateral (Plus)

**Resultado: PASS_SCOPED bilateral.** Esta aceptación cubre exclusivamente AS-B-07; no certifica la matriz completa de 229 filas ni la certificación global.

## Contrato y fuente
- Fila congelada: AS-B-07, N2, `factorizar`, `x^{6}-1` → `\left(x - 1\right) \left(x + 1\right) \left(x^{2} - x + 1\right) \left(x^{2} + x + 1\right)`.
- Fuente: `qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz`; SHA-256 descomprimido `8cd36ff08343f98f92abd83e2b162d565e0cbe5c59dc73f26b1c018f77d663c7`.
- Test: `backend/tests/test_algebra229_as_b07.py`, blob `c5a414af3a3fea308bda66c7e3f100ca25eaa38f`.
- El test coteja las siete celdas, llama a `POST /api/v1/factor`, exige el LaTeX exacto, cuatro factores con grados [1,1,2,2], las formas expandidas `x-1`, `x+1`, `x^2-x+1` y `x^2+x+1`, discriminante negativo en ambos cuadráticos, y valida diez sustituciones enteras con evaluador AST restringido y aritmética Python nativa, independiente de SymPy.

## Evidencia ejecutada sobre el SHA Plus
- SHA: `2e3facb7d48f41902fc16c65090868a6708f2d00`.
- Acumulativo [42145947023](https://github.com/c2melendez/precision-lab-plus/actions/runs/42145947023): **SUCCESS**, guard `skip=false`; ambos focales AS-B-07 PASSED; frontend 1,055 passed / 28 todo.
- H1d [42145946957](https://github.com/c2melendez/precision-lab-plus/actions/runs/42145946957): **SUCCESS**, 38/38.
- CI estándar [42145946946](https://github.com/c2melendez/precision-lab-plus/actions/runs/42145946946): **SUCCESS**, backend 2,800 passed / 1 skipped / 10 xfailed; frontend 1,055 passed.
- Runner [42145946981](https://github.com/c2melendez/precision-lab-plus/actions/runs/42145946981): **SUCCESS**.

## Decisión
AS-B-07 queda **PASS_SCOPED para Plus** y, junto con Lite, **PASS_SCOPED bilateral**. No hubo cambio de producto.
