# Algebra229 AS-B-05 — aceptación scoped bilateral (Plus)

**Resultado: PASS_SCOPED bilateral.** Esta aceptación cubre exclusivamente AS-B-05; no certifica la matriz completa de 229 filas ni la certificación global.

## Contrato y fuente
- Fila congelada: AS-B-05, N2, `factorizar`, `x^{4}-1` → `\left(x - 1\right) \left(x + 1\right) \left(x^{2} + 1\right)`. Nota de fuente: `Sobre ℚ: (x-1)(x+1)(x^{2}+1)`.
- Fuente: `qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz`; SHA-256 descomprimido `8cd36ff08343f98f92abd83e2b162d565e0cbe5c59dc73f26b1c018f77d663c7`.
- Test: `backend/tests/test_algebra229_as_b05.py`, blob `540a519a3cb1ccc3f493bf4c0443719368d7cce1`.
- El test coteja las siete celdas, llama a `POST /api/v1/factor`, exige el LaTeX exacto, un producto de tres factores con grados 1/1/2, el cuadrático exactamente `x^2+1` con discriminante negativo, y valida diez sustituciones enteras mediante evaluador AST restringido y aritmética Python nativa, independiente de SymPy.

## Evidencia ejecutada sobre el SHA Plus
- SHA: `1a93f562579a615e8faed9bac2449ed74c8ef543`.
- Acumulativo [42143597860](https://github.com/c2melendez/precision-lab-plus/actions/runs/42143597860): **SUCCESS**, guard `skip=false`; ambos focales AS-B-05 PASSED; frontend 1,055 passed / 28 todo.
- H1d [42143597715](https://github.com/c2melendez/precision-lab-plus/actions/runs/42143597715): **SUCCESS**, 38/38.
- CI estándar [42143597710](https://github.com/c2melendez/precision-lab-plus/actions/runs/42143597710): **SUCCESS**, backend 2,800 passed / 1 skipped / 10 xfailed; frontend 1,055 passed.
- Runner [42143597834](https://github.com/c2melendez/precision-lab-plus/actions/runs/42143597834): **SUCCESS**.

## Decisión
AS-B-05 queda **PASS_SCOPED para Plus** y, junto con Lite, **PASS_SCOPED bilateral**. No hubo cambio de producto.
