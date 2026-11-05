# Algebra229 AS-A-10 — aceptación bilateral (r397)

**Estado: PASS_SCOPED bilateral — Lite y Plus, sección Algebra229 A, fila AS-A-10 únicamente.** No certifica toda la sección ni la matriz completa.

## Contrato congelado

Fuente normativa: `qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz`; SHA-256 del contenido descomprimido `8cd36ff08343f98f92abd83e2b162d565e0cbe5c59dc73f26b1c018f77d663c7` (blob `d216dc77cb1356ef29cb8c803cbff809450e0456`).

Fila exacta: `| AS-A-10 | N2 | \`expandir\` | \`\\left(x^{2}+x+1\\right)^{3}\` | \`x^{6} + 3 x^{5} + 6 x^{4} + 7 x^{3} + 6 x^{2} + 3 x + 1\` |  |`.

## Plus

- SHA técnico: `e4e864881ebaa53e725efbf72f1b9a33aa2f4b7f`; test `backend/tests/test_algebra229_as_a10.py`, blob `9016f0af123164166f4629c3158693822746179f`.
- Fila congelada exacta, servicio `expand_expression` y HTTP `POST /api/v1/expand`; equivalencia simbólica y ocho muestras `x=[-4,-3,-2,-1,0,1,2,3]` contra `(x*x+x+1)**3` en Python nativo, independiente de SymPy.
- CI [42022365744](https://github.com/c2melendez/precision-lab-plus/actions/runs/42022365744): **SUCCESS**; backend 2,800 passed / 1 skipped / 10 xfailed; frontend 150 archivos / 1,055 passed.
- Acumulativo [42022365789](https://github.com/c2melendez/precision-lab-plus/actions/runs/42022365789): **SUCCESS**; ambos tests focales PASSED.
- H1d [42022365878](https://github.com/c2melendez/precision-lab-plus/actions/runs/42022365878): **SUCCESS**, 38/38.
- Runner [42022365762](https://github.com/c2melendez/precision-lab-plus/actions/runs/42022365762): **SUCCESS_PUSH_ONLY**.

## Lite

- SHA técnico: `41d345902105bc93e51d331bd0d239bad946dd6b`; test `tests/algebra229AsA10.audit.test.ts`, blob `e7ade6cc7fa02e24ce3a79a4d4772034a9c40b59`.
- Acumulativo [42022352712](https://github.com/c2melendez/precision-lab-lite/actions/runs/42022352712): **SUCCESS**, 2 tests focales, 366 archivos / 2,259 passed; typecheck y build 7.31 s.
- H1d [42022352301](https://github.com/c2melendez/precision-lab-lite/actions/runs/42022352301): **SUCCESS**, 22/22; Scientific UI [42022352493](https://github.com/c2melendez/precision-lab-lite/actions/runs/42022352493): **SUCCESS**, 456/456.
- CI estándar [42022352305](https://github.com/c2melendez/precision-lab-lite/actions/runs/42022352305): **FAILURE** por cuatro moderadas en QA dependency audit; umbral intacto.
- Runner [42022352496](https://github.com/c2melendez/precision-lab-lite/actions/runs/42022352496): **SUCCESS_PUSH_ONLY**.

## Cierre acotado

- AS-A-10 queda **PASS_SCOPED bilateral**.
- La matriz Algebra229 completa no está cerrada.
- Siguiente fila bilateral: **AS-A-11**, `(a+b+c)^3`.
- PR draft #62 con todos los checks en SUCCESS pero pendiente de revisión/fusión humana; bloqueo de dependencias Lite sin resolver.
- EDCX-B6 VC-FE-45/EV-I-12 y H2/SG28/DIST permanecen separados.
- Certificación global **OPEN**.
