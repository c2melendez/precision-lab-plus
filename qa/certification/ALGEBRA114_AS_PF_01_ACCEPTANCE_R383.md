# Algebra114 AS-PF-01 — aceptación acotada (Precision Lab Plus, r383)

**Estado: PASS_SCOPED — Precision Lab Plus únicamente.** Cubre el servicio backend y el endpoint HTTP de fracciones parciales; no implica paridad UI con Lite ni certificación global.

## Identidad técnica

- Repositorio: c2melendez/precision-lab-plus.
- Rama: qa/syntax-audit-in625-a1.
- SHA técnico: `e7f88498eb4520a968cd45a216a20ff43688a509`.
- Fixture: `qa/certification/algebra114_source.md`, blob `b30ca7fcec641334ce8128ca25bec542a9d04e79`.
- Test: `backend/tests/test_algebra114_as_pf01.py`.
- Blob del test: `06b14beebcaec379036971feec704e336c21479c`.

## Identidad matemática y oráculo independiente

`(3x+5)/((x+1)(x+2)) = 2/(x+1)+1/(x+2)`

El test verifica el resultado simbólico del servicio `simplify/partial-fractions` según la fila, la respuesta del endpoint `POST /api/v1/partial-fractions`, y además eight integer substitutions, checked with Python fractions.Fraction against both the two simple-pole decomposition and original rational expression. Los expected numéricos usan `fractions.Fraction`, no otra evaluación SymPy.

No se modifica el motor, el parser, la API, las dependencias ni los workflows.

## Gates sobre el mismo SHA

- Acumulativo [41989977600](https://github.com/c2melendez/precision-lab-plus/actions/runs/41989977600) **SUCCESS**; PF-01..PF-08 explícitamente PASSED; backend 2800 passed, 1 skipped, 10 xfailed.
- CI [41989977569](https://github.com/c2melendez/precision-lab-plus/actions/runs/41989977569) **SUCCESS**; backend 2800 passed y frontend SUCCESS.
- H1d [41989977542](https://github.com/c2melendez/precision-lab-plus/actions/runs/41989977542) **SUCCESS**, 38 passed.
- Runner [41989977594](https://github.com/c2melendez/precision-lab-plus/actions/runs/41989977594) **SUCCESS**, push-only.

## Límites

- PASS_SCOPED solo para AS-PF-01 en backend/service+HTTP de Plus.
- No declarar paridad UI global con Lite.
- VC-FE-45 permanece BLOCKED por EV-I-12.
- Global certification permanece **OPEN**.
