# Algebra114 AS-PF-03 — aceptación acotada (Precision Lab Plus, r380)

**Estado: PASS_SCOPED — Precision Lab Plus únicamente.** Cubre el servicio backend y el endpoint HTTP; no implica paridad UI con Lite ni certificación global.

- SHA técnico: `a8dc4ee0f987caa3768c3184da6cd2890f91b653`.
- Fuente: `qa/certification/algebra114_source.md`, blob `b30ca7fcec641334ce8128ca25bec542a9d04e79`.
- Test: `backend/tests/test_algebra114_as_pf03.py`, blob `b3ddb122174ee893fc183a60a11e27e7f840e982`.
- Identidad: `(x+1)/(x*(x^2+1)) = 1/x + (1-x)/(x^2+1)`.
- Verificaciones: resultado simbólico de servicio, respuesta HTTP de `POST /api/v1/partial-fractions`, y 8 integer substitutions with Python Fraction; verifies service and HTTP payload. Los valores expected usan Python `fractions.Fraction`, no otra evaluación SymPy.

## Gates sobre el mismo SHA

- Acumulativo [41988031275](https://github.com/c2melendez/precision-lab-plus/actions/runs/41988031275) **SUCCESS**; backend: 2800 passed, 1 skipped, 10 xfailed. PF-01..PF-08 aparecen explícitamente como PASSED.
- CI [41988031170](https://github.com/c2melendez/precision-lab-plus/actions/runs/41988031170) **SUCCESS**; backend 2800 passed y frontend SUCCESS.
- H1d [41988031154](https://github.com/c2melendez/precision-lab-plus/actions/runs/41988031154) **SUCCESS**, 38 passed.
- Runner [41988031114](https://github.com/c2melendez/precision-lab-plus/actions/runs/41988031114) **SUCCESS**, push-only.

No se modifica motor ni contrato. VC-FE-45 sigue BLOCKED frente a EV-I-12. Global certification OPEN.
