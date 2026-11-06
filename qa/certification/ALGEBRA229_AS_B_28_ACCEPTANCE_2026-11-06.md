# Algebra229 AS-B-28 — aceptación scoped bilateral (Plus)

**Resultado: PASS_SCOPED bilateral.** La certificación global continúa **OPEN**.

## Contrato y oráculos
- AS-B-28, N3: factorizar el entero 4294967297 → 641*6700417.
- Plus: `backend/tests/test_algebra229_as_b28.py`, 3/3 tests: ocho celdas exactas de la fila congelada; endpoint HTTP POST `/api/v1/factor`; salida ASCII exacta; división de prueba independiente; primalidad de ambos factores, multiplicidades 1, evaluación AST restringida y producto exacto.
- Lite (par bilateral): `tests/algebra229AsB28.audit.test.ts`, 4/4 tests: ocho celdas exactas; salida ASCII; primalidad y multiplicidad independiente; producto y equivalencia simbólica.

## Evidencia Plus — SHA `ab434ccf746ed9fb83b643e5eedc26b69c5f814b`
- Cumulative [42283418797](https://github.com/c2melendez/precision-lab-plus/actions/runs/42283418797) SUCCESS; frontend/backend SUCCESS; focal 3/3; backend 2,807 passed, 1 skipped, 10 xfailed.
- H1d [42283418744](https://github.com/c2melendez/precision-lab-plus/actions/runs/42283418744) SUCCESS; 38/38 Playwright.
- CI [42283418918](https://github.com/c2melendez/precision-lab-plus/actions/runs/42283418918) SUCCESS; 2,807 passed, 1 skipped, 10 xfailed; coverage 88.91%.
- Runner [42283418924](https://github.com/c2melendez/precision-lab-plus/actions/runs/42283418924) SUCCESS; fingerprint push-only.

## Evidencia Lite (par bilateral) — SHA `6aa6b374f50a199886d6f022409f74b457fab2e9`
- Cumulative [42283415265](https://github.com/c2melendez/precision-lab-lite/actions/runs/42283415265) SUCCESS; focal 4/4; 366 archivos, 2,266 passed, 8 expected fail, 34 TODO.
- H1d [42283415226](https://github.com/c2melendez/precision-lab-lite/actions/runs/42283415226) SUCCESS; 22/22 Playwright.
- Scientific UI [42283415403](https://github.com/c2melendez/precision-lab-lite/actions/runs/42283415403) SUCCESS; 456/456 desktop/tablet/mobile.
- CI [42283415015](https://github.com/c2melendez/precision-lab-lite/actions/runs/42283415015) SUCCESS.
- Runner [42283415020](https://github.com/c2melendez/precision-lab-lite/actions/runs/42283415020) SUCCESS; fingerprint push-only.

## Integridad de evidencia y diagnóstico
- Cumulative/H1d/Scientific registraron `skip=false` y `evidence_run_id` vacío; ejecución real en los SHA técnicos exactos, sin REUSE.
- Los logs focales muestran los tres tests Plus y los cuatro tests Lite de B28 en PASS.
- Las corridas preliminares sobre Lite SHA `b5b67cdc8eddaf763c3cfb99082992bb79d5d880` y Plus SHA `8600743de9f52ea3e1bdc65d7fd0d4401de0e03d` fallaron por escapes dobles introducidos en regex de los tests, no por el motor; se corrigieron exclusivamente los tests.
- No hay cambios de motor, API ni producto matemático. Los gaps independientes SG28/H2/DIST y SECURITY-S25 permanecen abiertos; certificación global **OPEN**.

Siguiente: AS-B-29, N2, factorizar 123456789 → 3^2*3607*3803. Test-first bilateral: comparar todas las celdas de la fila congelada; salida ASCII exacta; oráculo independiente por división de prueba que compruebe factores primos, multiplicidades [2,1,1] y producto exacto. Gates: Plus cumulative+H1d; Lite cumulative+H1d+Scientific UI.
