# Algebra229 AS-B-04 — aceptación scoped bilateral (Plus)

**Resultado: PASS_SCOPED bilateral.** Esta aceptación cubre exclusivamente AS-B-04; no certifica la matriz completa de 229 filas ni la certificación global.

## Contrato y fuente
- Fila congelada: AS-B-04, N1, `factorizar`, `x^{3}+27` → `\left(x + 3\right) \left(x^{2} - 3 x + 9\right)`.
- Fuente: `qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz`; SHA-256 descomprimido `8cd36ff08343f98f92abd83e2b162d565e0cbe5c59dc73f26b1c018f77d663c7`.
- Test: `backend/tests/test_algebra229_as_b04.py`, blob `cb8ba0d07c9a31a13123f3d16e9115d31b8b1e13`.
- El test coteja todas las celdas, llama a `POST /api/v1/factor`, exige un factor lineal y uno cuadrático con discriminante negativo, y valida diez sustituciones enteras mediante evaluador AST restringido y aritmética Python nativa, independiente de SymPy.

## Evidencia ejecutada sobre el SHA Plus
- SHA: `54a7963d47e020b35ea5a3cde75379953d513742`.
- Acumulativo [42137523357](https://github.com/c2melendez/precision-lab-plus/actions/runs/42137523357): **SUCCESS**, guard `skip=false`; ambos focales AS-B-04 PASSED; backend 2,800 passed / 1 skipped / 10 xfailed, cobertura 88.88%; frontend 1,055 passed.
- H1d [42137523360](https://github.com/c2melendez/precision-lab-plus/actions/runs/42137523360): **SUCCESS**, 38/38.
- CI estándar [42137523336](https://github.com/c2melendez/precision-lab-plus/actions/runs/42137523336): **SUCCESS**, backend 2,800 passed; frontend 1,055 passed.
- Runner [42137523341](https://github.com/c2melendez/precision-lab-plus/actions/runs/42137523341): **SUCCESS**.

## Decisión
AS-B-04 queda **PASS_SCOPED para Plus** y, junto con Lite, **PASS_SCOPED bilateral**. No hubo cambio de producto.
