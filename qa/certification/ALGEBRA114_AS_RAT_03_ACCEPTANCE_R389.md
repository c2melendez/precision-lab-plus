# Algebra114 AS-RAT-03 — aceptación acotada (r389)

**Estado: PASS_SCOPED — Precision Lab Plus, backend/servicio HTTP únicamente.** No acredita paridad de interfaz con Lite, cierre de Algebra114 ni certificación global.

## Identidad técnica

- Repositorio: c2melendez/precision-lab-plus.
- Rama canónica: qa/syntax-audit-in625-a1.
- SHA técnico probado: `8371417c3b57135dd83ad9af4b502e4bb04a6c92`.
- Fuente original: `qa/certification/algebra114_source.md`, fila AS-RAT-03.
- Blob de fuente: `b30ca7fcec641334ce8128ca25bec542a9d04e79`.
- Test: `backend/tests/test_algebra114_as_rat03.py`.
- Blob del test: `9c234e4be63fcdac14723bf5125c963e3f8508e2`.

## Caso y oráculo independiente

La fila original exige:

`1/(sqrt(2)+sqrt(3)) = sqrt(3)-sqrt(2)`.

La prueba comprueba la fila exacta, ejecuta `simplify_expression` y el endpoint HTTP `POST /api/v1/simplify`, conserva la comparación simbólica contractual separada y calcula el expected numérico con `math.sqrt(2)` y `math.sqrt(3)` de la biblioteca estándar, independientes del CAS. Verifica positividad, la identidad del conjugado y el valor del servicio y HTTP contra el oráculo independiente.

El cambio modifica únicamente el test; no cambia motor, parser, contrato HTTP, dependencias ni workflows.

## Evidencia de ejecución sobre el mismo SHA

- Acumulativo [41994877568](https://github.com/c2melendez/precision-lab-plus/actions/runs/41994877568): **SUCCESS**, backend 2,800 passed, 1 skipped, 10 xfailed; frontend unit/parity y build SUCCESS. El log muestra explícitamente `tests/test_algebra114_as_rat03.py::test_as_rat_03_two_radical_conjugate_service_http_independent_oracle PASSED`.
- CI [41994877761](https://github.com/c2melendez/precision-lab-plus/actions/runs/41994877761): **SUCCESS**, backend y frontend completos.
- H1d [41994877552](https://github.com/c2melendez/precision-lab-plus/actions/runs/41994877552): **SUCCESS**, 38/38 Playwright.
- Certification Runner [41994877571](https://github.com/c2melendez/precision-lab-plus/actions/runs/41994877571): **SUCCESS** en evento push; no certifica workflow_dispatch, dispatch ni persistencia.

## Límite de aceptación

- Aprobación exclusiva para AS-RAT-03 en Plus backend/servicio HTTP.
- No se afirma paridad de presentación UI con Lite.
- La certificación global permanece **OPEN**.
