# Algebra229 AS-B-06 — aceptación scoped bilateral (Plus)

**Resultado: PASS_SCOPED bilateral.** Esta aceptación cubre exclusivamente AS-B-06; no certifica la matriz completa de 229 filas ni la certificación global.

## Contrato y fuente
- Fila congelada: AS-B-06, N3, `factorizar`, `x^{4}+4` → `\left(x^{2} - 2 x + 2\right) \left(x^{2} + 2 x + 2\right)`. Nota: identidad de Sophie Germain.
- Fuente: `qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz`; SHA-256 descomprimido `8cd36ff08343f98f92abd83e2b162d565e0cbe5c59dc73f26b1c018f77d663c7`.
- Test: `backend/tests/test_algebra229_as_b06.py`, blob `f71b0b3c6838ce6cf1334077213c44048f55b73b`.
- El test coteja las siete celdas, llama a `POST /api/v1/factor`, exige el LaTeX exacto, dos factores cuadráticos con grados [2,2], las formas expandidas `x^2-2x+2` y `x^2+2x+2`, discriminante negativo en ambos, y diez sustituciones enteras con evaluador AST restringido y aritmética Python nativa, independiente de SymPy.

## Evidencia ejecutada sobre el SHA Plus
- SHA: `ac6785822c2bb0b3fdff45fef12536d00b009c9e`.
- Acumulativo [42144769877](https://github.com/c2melendez/precision-lab-plus/actions/runs/42144769877): **SUCCESS**, guard `skip=false`; ambos focales AS-B-06 PASSED; frontend 1,055 passed / 28 todo.
- H1d [42144769822](https://github.com/c2melendez/precision-lab-plus/actions/runs/42144769822): **SUCCESS**, 38/38.
- CI estándar [42144769863](https://github.com/c2melendez/precision-lab-plus/actions/runs/42144769863): **SUCCESS**, backend 2,800 passed / 1 skipped / 10 xfailed; frontend 1,055 passed.
- Runner [42144769876](https://github.com/c2melendez/precision-lab-plus/actions/runs/42144769876): **SUCCESS**.

## Decisión
AS-B-06 queda **PASS_SCOPED para Plus** y, junto con Lite, **PASS_SCOPED bilateral**. No hubo cambio de producto.
