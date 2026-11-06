# Algebra229 AS-B-03 — aceptación scoped bilateral (Plus)

**Resultado: PASS_SCOPED bilateral.** Esta aceptación cubre exclusivamente AS-B-03; no certifica la matriz completa de 229 filas ni la certificación global.

## Contrato y fuente
- Fila congelada: AS-B-03, N1, `factorizar`, `x^{3}-8` → `\left(x - 2\right) \left(x^{2} + 2 x + 4\right)`.
- Nota contractual: “Diferencia de cubos: factor cuadrático irreducible.”
- Fuente: `qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz`; SHA-256 descomprimido `8cd36ff08343f98f92abd83e2b162d565e0cbe5c59dc73f26b1c018f77d663c7`.
- Test Plus: `backend/tests/test_algebra229_as_b03.py`, blob `cae8d5e4023bffc6dc11f901a1e134bdfaa11b3d`. Coteja la fila y nota, llama a HTTP `POST /api/v1/factor`, exige factores de grado 1 y 2 con discriminante negativo, y usa diez sustituciones enteras con evaluador AST restringido y aritmética Python nativa.

## Diagnóstico y corrección del oráculo
- Primer SHA `300bdede38cf5f58e8f47a59ff20a83dd4389dfe`: el producto devolvió la factorización correcta, pero el oráculo insertaba `-7` sin paréntesis. Python evaluó `-7**2` como `-(7**2)`, dando 531 frente al esperado -351. Fue un falso negativo de precedencia en el harness, no un fallo del motor.
- Corrección: sustitución parentizada `(x_value)`, publicada en SHA `e4122f5fc2f88073feabd89df3f9b0660065dcfb`, test blob `cae8d5e4023bffc6dc11f901a1e134bdfaa11b3d`.

## Evidencia ejecutada sobre el SHA corregido
- Acumulativo [42136796602](https://github.com/c2melendez/precision-lab-plus/actions/runs/42136796602): **SUCCESS**, guard `skip=false`; ambos tests focales PASSED; backend 2,800 passed / 1 skipped / 10 xfailed, cobertura 88.88%; frontend 1,055 passed.
- H1d [42136796500](https://github.com/c2melendez/precision-lab-plus/actions/runs/42136796500): **SUCCESS**, 38/38.
- CI [42136796498](https://github.com/c2melendez/precision-lab-plus/actions/runs/42136796498): **SUCCESS**, backend 2,800 passed / 1 skipped / 10 xfailed; frontend 1,055 passed.
- Runner [42136796513](https://github.com/c2melendez/precision-lab-plus/actions/runs/42136796513): **SUCCESS**.

## Decisión
AS-B-03 queda **PASS_SCOPED para Plus** y, junto con Lite, **PASS_SCOPED bilateral**. No hubo cambio de producto.
