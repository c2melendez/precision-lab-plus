# Algebra229 AS-A-06 — aceptación bilateral (r393)

**Estado: PASS_SCOPED bilateral — Lite y Plus, sección Algebra229 A, fila AS-A-06 únicamente.** No acredita la matriz completa ni la certificación global.

## Contrato congelado

Fuente normativa: `qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz`; SHA-256 `8cd36ff08343f98f92abd83e2b162d565e0cbe5c59dc73f26b1c018f77d663c7`.

Fila AS-A-06: `(x+y+z)^2 → x^2+2xy+2xz+y^2+2yz+z^2`.

## Plus

- SHA técnico: `0b2f02e6507f50ea4072691c96d5270dfdb0827c`.
- Test: `backend/tests/test_algebra229_as_a06.py`, blob `2ec9c63c8f7eb4a522c65b173573369fbed34ada`.
- Exige la fila congelada completa; ejecuta `expand_expression` y HTTP `POST /api/v1/expand`; verifica equivalencia simbólica y ocho ternas firmadas con oráculo aritmético Python independiente.
- CI [42002301382](https://github.com/c2melendez/precision-lab-plus/actions/runs/42002301382): **SUCCESS**; frontend audit/typecheck/unit/parity/build y backend test step SUCCESS.
- Acumulativo [42002301613](https://github.com/c2melendez/precision-lab-plus/actions/runs/42002301613): **SUCCESS**; fixture integrity, guard, frontend y backend regression steps SUCCESS.
- H1d [42002301152](https://github.com/c2melendez/precision-lab-plus/actions/runs/42002301152): **SUCCESS**, 38/38.
- Runner [42002301346](https://github.com/c2melendez/precision-lab-plus/actions/runs/42002301346): **SUCCESS_PUSH_ONLY**; dispatch/QA receipt/persist omitted.
- pytest discovers `tests` via `backend/pyproject.toml`; CI runs `pytest -q`, cumulative `pytest -vv`, no file-selection filter. Individual job-log download returned 404; full test steps completed successfully.

## Lite

- SHA técnico: `790c49034f88ef0b20ad76c0e49c41fbb3cbd763`; test `tests/algebra229AsA06.audit.test.ts`, blob `6ffb510661f5c88c1c5f553a188f3d8566d05e1b`.
- Acumulativo [42001452228](https://github.com/c2melendez/precision-lab-lite/actions/runs/42001452228) **SUCCESS**, 2 focal tests, 366 files / 2,259 passed.
- H1d [42001452201](https://github.com/c2melendez/precision-lab-lite/actions/runs/42001452201) **SUCCESS**, 22/22; Scientific UI [42001452411](https://github.com/c2melendez/precision-lab-lite/actions/runs/42001452411) **SUCCESS**, job desktop/tablet/mobile, 456 passed.
- CI [42001452519](https://github.com/c2melendez/precision-lab-lite/actions/runs/42001452519) **FAILURE** por 4 moderadas en el hard gate de auditoría; typecheck/unit/build fueron omitidos en CI estándar. Sin bajar umbral.

## Cierre acotado

- La fila AS-A-06 queda **PASS_SCOPED bilateral** con test-first y evidencia por motor.
- La matriz Algebra229 no está cerrada; el resultado no se extrapola a otras filas.
- Siguiente fila bilateral: **AS-A-07**, expansión de `(2x-3)^4`.
- EDCX-B6 VC-FE-45 frente a EV-I-12, H2/SG28/DIST y seguridad de dependencias Lite permanecen separados y no se debilitan.
- Certificación global **OPEN**.
