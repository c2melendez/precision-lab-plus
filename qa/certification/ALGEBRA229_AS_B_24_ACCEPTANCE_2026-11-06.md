# Algebra229 AS-B-24 — aceptación scoped bilateral (Plus)

**Resultado: PASS_SCOPED bilateral.** La certificación global permanece **OPEN**.

## Contrato
- AS-B-24, N3, operación `factorizar`.
- Entrada de matriz: `x^{2}-2\ \text{sobre }\mathbb{R}`.
- Salida de matriz: `\left(x - \sqrt{2}\right) \left(x + \sqrt{2}\right)`.
- Nota congelada: `Con raíces permitidas: (x-\sqrt{2})(x+\sqrt{2}).`
- Salida ASCII del endpoint: `(x-sqrt(2))*(x+sqrt(2))`.
- AS-B-23 sigue distinguiendo el dominio ℚ: `x^2-2` permanece irreducible allí.

## Pruebas
- Plus `backend/tests/test_algebra229_as_b24.py`: tres pruebas; siete celdas semánticas exactas, endpoint HTTP `POST /api/v1/factor`, salida ASCII exacta, equivalencia SymPy y evaluador AST independiente con diez muestras enteras `[0,1,-1,2,-2,3,-3,4,5,10]`.
- Lite (par bilateral) `tests/algebra229AsB24.audit.test.ts`: cuatro pruebas; fila congelada, salida ASCII, equivalencia simbólica y oráculo numérico independiente en las mismas diez muestras.

## Evidencia Plus — SHA `5d8d78f8e35d02830bfbce63c107fe5990904cd1`
- Cumulative [42221909462](https://github.com/c2melendez/precision-lab-plus/actions/runs/42221909462) SUCCESS; frontend/backend SUCCESS; focal 3/3; backend 2,803 passed, 1 skipped, 10 xfailed.
- H1d [42221909235](https://github.com/c2melendez/precision-lab-plus/actions/runs/42221909235) SUCCESS; 38/38 Playwright.
- CI [42221909164](https://github.com/c2melendez/precision-lab-plus/actions/runs/42221909164) SUCCESS; frontend/backend SUCCESS; backend 2,803 passed, 1 skipped, 10 xfailed.
- Runner [42221910347](https://github.com/c2melendez/precision-lab-plus/actions/runs/42221910347) SUCCESS; push-only fingerprint.

## Evidencia Lite — SHA `2342cbd5ac2de6e9a7b1fbf42ddb9df4ee1f9c8d`
- Cumulative [42222060038](https://github.com/c2melendez/precision-lab-lite/actions/runs/42222060038) SUCCESS; focal 4/4; 366/366 archivos.
- CI [42222060154](https://github.com/c2melendez/precision-lab-lite/actions/runs/42222060154) SUCCESS; focal 4/4, 366/366 archivos.
- Scientific UI [42222060025](https://github.com/c2melendez/precision-lab-lite/actions/runs/42222060025) SUCCESS; 456/456 desktop/tablet/mobile.
- H1d [42222060032](https://github.com/c2melendez/precision-lab-lite/actions/runs/42222060032) SUCCESS; 22/22 Playwright.
- Runner [42222059941](https://github.com/c2melendez/precision-lab-lite/actions/runs/42222059941) SUCCESS; push-only fingerprint.

## Alcance
- Los logs focales demuestran ejecución real en los SHA listados, sin REUSE.
- Los únicos archivos técnicos modificados fueron las pruebas de certificación. No hubo cambio de motor, parser, frontend o backend de producto.
- Los intentos intermedios corrigieron las aserciones del harness para reflejar exactamente los delimitadores y escapes del fixture, no fallos matemáticos del producto.
- SG28/H2/DIST, SECURITY-S25 y otros capability gaps no relacionados continúan abiertos.

**Siguiente acción:** AS-B-25, `factor(x^2+1) sobre ℂ` → `(x-i)*(x+i)`, solo con dominio complejo explícito; sin sufijo no introducir `i`. Global **OPEN**.
