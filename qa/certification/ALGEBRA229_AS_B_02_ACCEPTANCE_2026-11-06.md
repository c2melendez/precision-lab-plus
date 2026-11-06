# Algebra229 AS-B-02 — aceptación scoped bilateral (Plus)

**Resultado: PASS_SCOPED bilateral.** Esta aceptación cubre exclusivamente AS-B-02; no certifica la matriz completa de 229 filas ni la certificación global.

## Contrato y fuente
- Fila congelada: AS-B-02, N1, `factorizar`, `x^{2}-9` → `\left(x - 3\right) \left(x + 3\right)`.
- Fuente: `qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz`; SHA-256 descomprimido `8cd36ff08343f98f92abd83e2b162d565e0cbe5c59dc73f26b1c018f77d663c7`.
- Test: `backend/tests/test_algebra229_as_b02.py`, blob `e6a56a899f4a62f32b483debe3959fca99c29594`.
- El test coteja la fila exacta, llama a `POST /api/v1/factor`, exige dos factores lineales y verifica diez sustituciones enteras con evaluador AST restringido y aritmética Python nativa, independiente de SymPy.

## Evidencia ejecutada sobre el SHA Plus
- SHA: `e8bbb528bdf1d70ee8acd947c8e58144ad07d3a6`.
- Acumulativo [42135022942](https://github.com/c2melendez/precision-lab-plus/actions/runs/42135022942): **SUCCESS**, guard `skip=false`; ambos focales AS-B-02 PASSED; backend 2,800 passed / 1 skipped / 10 xfailed, cobertura 88.93%; frontend 1,055 passed.
- H1d [42135022812](https://github.com/c2melendez/precision-lab-plus/actions/runs/42135022812): **SUCCESS**, 38/38.
- CI estándar [42135022746](https://github.com/c2melendez/precision-lab-plus/actions/runs/42135022746): **SUCCESS**, backend 2,800 passed; frontend 1,055 passed.
- Runner [42135022814](https://github.com/c2melendez/precision-lab-plus/actions/runs/42135022814): **SUCCESS**.

## Decisión
AS-B-02 queda **PASS_SCOPED para Plus** y, junto con Lite, **PASS_SCOPED bilateral**. No hubo cambio de producto.
