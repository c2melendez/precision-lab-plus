# Algebra114 AS-RAT-06 — aceptación acotada (r388)

**Estado: PASS_SCOPED — Precision Lab Plus, backend/servicio HTTP únicamente.** No acredita paridad de interfaz con Lite, cierre de Algebra114 ni certificación global.

## Identidad técnica

- Repositorio: c2melendez/precision-lab-plus.
- Rama canónica: qa/syntax-audit-in625-a1.
- SHA técnico probado: `a4ab5b03cbde3d53789609823cbfb2314c5aea10`.
- Fuente original: `qa/certification/algebra114_source.md`, fila AS-RAT-06.
- Blob de fuente: `b30ca7fcec641334ce8128ca25bec542a9d04e79`.
- Test: `backend/tests/test_algebra114_as_rat06.py`.
- Blob del test: `855857bacdb636bb2d98622cfeba8fb25e89fc97`.

## Caso y oráculo independiente

Identidad de la matriz:

`(sqrt(x+h)-sqrt(x))/h = 1/(sqrt(x+h)+sqrt(x)), x>0, h>-x, h!=0`

Comprueba fila exacta y restricciones, servicio y HTTP; en siete pares válidos compara contra dos oráculos independientes math.sqrt: el cociente original y la forma conjugada.

La prueba cubre la ejecución del servicio `simplify_expression` y la respuesta del endpoint HTTP `POST /api/v1/simplify`. El resultado esperado numérico se contrasta con funciones de la biblioteca estándar de Python (`math.sqrt`/`math.cbrt`), independientes de SymPy. La comparación simbólica con SymPy se conserva como comprobación contractual separada.

El cambio modifica únicamente tests; no cambia el motor, parser, contrato HTTP, dependencias ni workflows.

## Evidencia de ejecución sobre el mismo SHA

- CI [41993715914](https://github.com/c2melendez/precision-lab-plus/actions/runs/41993715914): **SUCCESS**, backend y frontend completados. El backend reportó 2,800 passed, 1 skipped y 10 xfailed; frontend unit/parity y build pasaron.
- Acumulativo [41993716059](https://github.com/c2melendez/precision-lab-plus/actions/runs/41993716059): **SUCCESS**. El log marca explícitamente las pruebas RAT-01, RAT-02, RAT-05 y RAT-06 como PASSED; backend 2,800 passed, 1 skipped y 10 xfailed; frontend regresión y build SUCCESS.
- H1d [41993715913](https://github.com/c2melendez/precision-lab-plus/actions/runs/41993715913): **SUCCESS**, 38/38 Playwright.
- Certification Runner [41993716068](https://github.com/c2melendez/precision-lab-plus/actions/runs/41993716068): **SUCCESS** en evento push; resolución de rama, checkout y fingerprint. El camino workflow_dispatch/dispatch y persistencia no queda certificado.

## Límite de aceptación

- Aprobación exclusiva para AS-RAT-06 en Plus backend/servicio HTTP.
- No se afirma equivalencia de presentación UI con Lite.
- La certificación global permanece **OPEN**.
