# Algebra229 AS-A-08 — aceptación bilateral (r395)

**Estado: PASS_SCOPED bilateral — Lite y Plus, sección Algebra229 A, fila AS-A-08 únicamente.** No certifica toda la sección ni la matriz completa.

## Contrato congelado

Fuente normativa: `qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz`; SHA-256 `8cd36ff08343f98f92abd83e2b162d565e0cbe5c59dc73f26b1c018f77d663c7`.

Fila exacta: `(x-1)^5 → x^5-5x^4+10x^3-10x^2+5x-1`.

## Plus

- SHA técnico: `6a42292878494500c8d902cada0dadaa39e8d2ee`; test `backend/tests/test_algebra229_as_a08.py`, blob `5d95493a65876a9456515164995147c6ef6d3e59`.
- Fila congelada exacta, `expand_expression` y HTTP `POST /api/v1/expand`; equivalencia simbólica y aritmética entera Python independiente en siete puntos firmados.
- CI [42006654279](https://github.com/c2melendez/precision-lab-plus/actions/runs/42006654279): **SUCCESS**, frontend y backend; backend 2,800 passed, 1 skipped, 10 xfailed.
- Acumulativo [42006654698](https://github.com/c2melendez/precision-lab-plus/actions/runs/42006654698): **SUCCESS**; ambos tests focales PASSED; backend 2,800 passed, 1 skipped, 10 xfailed.
- H1d [42006653939](https://github.com/c2melendez/precision-lab-plus/actions/runs/42006653939): **SUCCESS**, 38/38.
- Runner [42006654470](https://github.com/c2melendez/precision-lab-plus/actions/runs/42006654470): **SUCCESS_PUSH_ONLY**; dispatch y persistencia no probados.

## Lite

- SHA técnico: `e1f5c9cc67ffe2cd9bdfc3dcdcb07b8de291d21f`; test `tests/algebra229AsA08.audit.test.ts`, blob `3863c4a54007bb3200ced4a157a4c8a4f4617390`.
- Acumulativo [42006623286](https://github.com/c2melendez/precision-lab-lite/actions/runs/42006623286): **SUCCESS**, 2 tests focales, 366 archivos, 2,259 passed.
- H1d [42006623192](https://github.com/c2melendez/precision-lab-lite/actions/runs/42006623192): **SUCCESS**, 22/22; Scientific UI [42006623224](https://github.com/c2melendez/precision-lab-lite/actions/runs/42006623224): **SUCCESS**, 456 pasadas desktop/tablet/mobile.
- CI estándar [42006623461](https://github.com/c2melendez/precision-lab-lite/actions/runs/42006623461): **FAILURE** por cuatro vulnerabilidades moderadas en QA dependency audit; typecheck/unit/build omitidos, umbral intacto.
- Runner [42006623362](https://github.com/c2melendez/precision-lab-lite/actions/runs/42006623362): **SUCCESS_PUSH_ONLY**.

## Cierre acotado

- AS-A-08 queda **PASS_SCOPED bilateral** con oráculos independientes y los gates de aceptación contractuales.
- La matriz Algebra229 completa no está cerrada.
- Siguiente fila bilateral: **AS-A-09**, producto de cuatro factores lineales.
- El bloqueo de dependencias Lite sigue abierto en la rama canónica; PR draft #62 no fusionado.
- EDCX-B6 VC-FE-45/EV-I-12 y H2/SG28/DIST permanecen separados.
- Certificación global **OPEN**.
