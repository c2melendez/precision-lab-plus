# Algebra114 AS-RAT-07 — aceptación acotada (r391)

**Estado: PASS_SCOPED — Precision Lab Plus, backend/servicio HTTP únicamente.** No acredita paridad de interfaz con Lite, cierre global de Algebra114 ni certificación global.

## Identidad técnica

- Repositorio: c2melendez/precision-lab-plus.
- Rama canónica: qa/syntax-audit-in625-a1.
- SHA técnico probado: `da924df6cdb9a827c2b0ff061db9f1e0e8111167`.
- Fuente original: `qa/certification/algebra114_source.md`, fila AS-RAT-07; blob `b30ca7fcec641334ce8128ca25bec542a9d04e79`.
- Test: `backend/tests/test_algebra114_as_rat07.py`; blob `ac1da7cd460faa1450a7a0f0172c659bcd2009fc`.

## Caso y oráculo independiente

La fila exacta exige `sqrt(2+sqrt(3)) = (sqrt(6)+sqrt(2))/2`.

El test comprueba la fila completa, ejecuta `simplify_expression` y el endpoint `POST /api/v1/simplify`. Mantiene por separado la equivalencia simbólica contractual y usa la biblioteca estándar `math.sqrt` como oráculo numérico independiente de SymPy para la expresión original y la forma denestada. Verifica positividad y que el cuadrado del resultado sea `2+sqrt(3)` para el servicio y la respuesta HTTP.

Se descartó como candidato el SHA `76123db5d0b4671e13875ac49ca602a49f1c4244` porque su literal de fixture tenía escape duplicado. La prueba corregida fue publicada en `da924df6cdb9a827c2b0ff061db9f1e0e8111167`; ninguna corrida del candidato descartado se usó como evidencia.

## Evidencia ejecutada sobre el mismo SHA

- CI [41999414498](https://github.com/c2melendez/precision-lab-plus/actions/runs/41999414498): **SUCCESS**; jobs frontend y backend SUCCESS. Auditoría de dependencias, typecheck, unit/parity, build y backend tests ejecutados. Backend: 2,800 passed, 1 skipped, 10 xfailed.
- Acumulativo [41999414506](https://github.com/c2melendez/precision-lab-plus/actions/runs/41999414506): **SUCCESS**; frontend y backend SUCCESS, fixture integrity y guard de continuidad SUCCESS. Log focal explícito: `test_as_rat_07_nested_radical_denesting_service_http_independent_oracle PASSED`; backend 2,800 passed, 1 skipped, 10 xfailed.
- H1d [41999414450](https://github.com/c2melendez/precision-lab-plus/actions/runs/41999414450): **SUCCESS**, 38/38 Playwright.
- Certification Runner [41999414341](https://github.com/c2melendez/precision-lab-plus/actions/runs/41999414341): **SUCCESS_PUSH_ONLY**. Resolvió la rama canónica, checkout, SHA base y fingerprint; despacho, espera, recibo y persistencia fueron omitidos. No acredita `workflow_dispatch` ni persistencia.

## Límite de aceptación

- Aprobación exclusiva para AS-RAT-07 en Plus backend/servicio HTTP.
- No se afirma paridad de presentación UI con Lite.
- El siguiente caso de Algebra114 Plus es **AS-RAT-08**.
- El bloqueo contractual EDCX-B6 VC-FE-45 frente a EV-I-12 permanece separado y sin cambios.
- La certificación global permanece **OPEN**.
