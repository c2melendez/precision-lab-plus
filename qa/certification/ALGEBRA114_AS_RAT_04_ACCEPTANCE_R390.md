# Algebra114 AS-RAT-04 — aceptación acotada (r390)

**Estado: PASS_SCOPED — Precision Lab Plus, backend/servicio HTTP únicamente.** No acredita paridad de interfaz con Lite, cierre global de Algebra114 ni certificación global.

## Identidad técnica

- Repositorio: c2melendez/precision-lab-plus.
- Rama canónica: qa/syntax-audit-in625-a1.
- SHA técnico probado: `1ff1230e63d6788f1fec2b769b779f70f308eba5`.
- Fuente original: `qa/certification/algebra114_source.md`, fila AS-RAT-04.
- Blob de fuente: `b30ca7fcec641334ce8128ca25bec542a9d04e79`.
- Test: `backend/tests/test_algebra114_as_rat04.py`.
- Blob del test: `6cfb85dda9ff884ebd270a03bcdbb6e247627c9a`.

## Caso y oráculo independiente

La fila original exige:

`1/cuberoot(2) = cuberoot(4)/2`.

El test valida la fila de la matriz, ejecuta `simplify_expression` y `POST /api/v1/simplify`, y conserva la equivalencia simbólica como comprobación contractual separada. El valor numérico esperado se calcula con `math.cbrt(4.0)/2.0` de la biblioteca estándar de Python, independiente de SymPy. Comprueba positividad, compara los resultados del servicio y HTTP con ese valor y verifica que el cubo sea `1/2` con tolerancia `1e-12`.

El cambio técnico afecta únicamente a la prueba focal; no modifica motor, parser, contrato HTTP, dependencias ni workflows.

## Evidencia de ejecución sobre el mismo SHA

- Acumulativo [41995788254](https://github.com/c2melendez/precision-lab-plus/actions/runs/41995788254): **SUCCESS**. El log muestra explícitamente `tests/test_algebra114_as_rat04.py::test_as_rat_04_cube_root_denominator_service_http_independent_oracle PASSED`; backend: 2,800 passed, 1 skipped, 10 xfailed. Los pasos de typecheck, regresión/paridad y build del frontend también terminaron correctamente.
- CI [41995788422](https://github.com/c2melendez/precision-lab-plus/actions/runs/41995788422): **SUCCESS**, jobs frontend y backend completos, incluida auditoría de dependencias, typecheck, unit/parity, build y backend tests.
- H1d [41995788274](https://github.com/c2melendez/precision-lab-plus/actions/runs/41995788274): **SUCCESS**, 38/38 pruebas Playwright.
- Certification Runner [41995788237](https://github.com/c2melendez/precision-lab-plus/actions/runs/41995788237): **SUCCESS** en evento push. La ejecución verificó resolución canónica, checkout, fingerprint y resumen push-only; despacho, espera de gate, recibo y persistencia fueron omitidos. No se acredita `workflow_dispatch` ni persistencia.

## Límite de aceptación

- Aprobación exclusiva para AS-RAT-04 en Plus backend/servicio HTTP.
- No se afirma paridad de presentación UI con Lite.
- El siguiente caso matemático de Plus es AS-RAT-07; RAT-05 y RAT-06 ya están aceptadas en el backend.
- El bloqueo contractual EDCX-B6 VC-FE-45 frente a EV-I-12 permanece separado y sin cambios.
- La certificación global permanece **OPEN**.
