# Algebra114 AS-RAT-08 — aceptación acotada (r392)

**Estado: PASS_SCOPED — Precision Lab Plus, backend/servicio HTTP únicamente.** No acredita paridad de interfaz con Lite ni certificación global.

## Identidad técnica

- Repositorio: c2melendez/precision-lab-plus.
- Rama canónica: qa/syntax-audit-in625-a1.
- SHA técnico probado: `8f38520aea1a98099f2fc95909a0af94459476cf`.
- Fuente: `qa/certification/algebra114_source.md`, fila AS-RAT-08; blob `b30ca7fcec641334ce8128ca25bec542a9d04e79`.
- Test: `backend/tests/test_algebra114_as_rat08.py`; blob `136f9b0319bf7bd1363ee18f5fbe75d2c3a11ca4`.

## Contrato y oráculo independiente

La fila requiere `sqrt(5+2*sqrt(6)) = sqrt(3)+sqrt(2)`. El test compara la fila congelada completa, ejecuta `simplify_expression` y `POST /api/v1/simplify`, y conserva la equivalencia simbólica. Como oráculo numérico separado usa Python `math.sqrt` para calcular la raíz original y la forma denestada; verifica positividad, compara servicio y HTTP con ambos valores y comprueba la identidad del cuadrado `5+2*sqrt(6)`. El valor esperado numérico no depende de SymPy.

## Evidencia sobre el mismo SHA

- CI [42001054496](https://github.com/c2melendez/precision-lab-plus/actions/runs/42001054496): **SUCCESS**. Frontend: auditoría de dependencias, typecheck, regresión/paridad y build SUCCESS; backend SUCCESS (2,800 passed, 1 skipped, 10 xfailed).
- Acumulativo [42001054497](https://github.com/c2melendez/precision-lab-plus/actions/runs/42001054497): **SUCCESS**; frontend y backend SUCCESS. El log del backend confirma `test_as_rat_08_nested_radical_original_service_http_independent_oracle PASSED`; total backend 2,800 passed, 1 skipped, 10 xfailed.
- H1d [42001054407](https://github.com/c2melendez/precision-lab-plus/actions/runs/42001054407): **SUCCESS** (38/38 Playwright).
- Certification Runner [42001054193](https://github.com/c2melendez/precision-lab-plus/actions/runs/42001054193): **SUCCESS_PUSH_ONLY**. No acredita workflow_dispatch, dispatch del gate, recibo QA o persistencia: esos pasos no se ejecutaron.

## Límite de aceptación

- Aprobación exclusiva para AS-RAT-08 en Plus backend/servicio HTTP.
- No se afirma paridad UI con Lite.
- Siguiente trabajo matemático: Algebra229 AS-A-06, según el ciclo test-first bilateral.
- El bloqueo contractual EDCX-B6 VC-FE-45 frente a EV-I-12 permanece separado y sin cambios.
- Certificación global **OPEN**.
