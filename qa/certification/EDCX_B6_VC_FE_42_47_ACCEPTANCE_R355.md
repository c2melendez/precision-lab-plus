# EDCX-B6 — aceptación scoped de VC-FE-42 y VC-FE-47 (Plus r355)

Fecha: 2026-10-29 UTC  
Repositorio: `c2melendez/precision-lab-plus`  
Rama canónica: `qa/syntax-audit-in625-a1`

## Decisión

VC-FE-42 y VC-FE-47 quedan **PASS_SCOPED exclusivamente en Precision Lab Plus**. Este cierre no certifica EDCX-B6 completo y no constituye aceptación bilateral.

## SHA y pruebas

SHA técnico exacto: `082fdb7c48add1476554ef90e840fab698b89561`.

Archivo: `backend/tests/test_edcx_b6_formula_real_points.py`.

- VC-FE-42: fórmula de arcsin evaluada en z=1/2; esperado π/6.
- VC-FE-47: fórmula de arctan evaluada en z=1; esperado π/4.
- Ambas pruebas exigen respuesta HTTP 200, éxito, ausencia de error, campos text/LaTeX no vacíos y comparación con oráculo independiente a tolerancia 1e-9. Si existe `result_approx`, también se contrasta.

## Evidencia exacta de Actions

Los cuatro workflows concluyeron SUCCESS sobre el mismo SHA técnico:

| Gate | Run | Resultado |
|---|---:|---|
| CI | [40970642357](https://github.com/c2melendez/precision-lab-plus/actions/runs/40970642357) | SUCCESS |
| Cumulative | [40970642413](https://github.com/c2melendez/precision-lab-plus/actions/runs/40970642413) | SUCCESS |
| H1d | [40970642305](https://github.com/c2melendez/precision-lab-plus/actions/runs/40970642305) | SUCCESS |
| Certification Runner | [40970642558](https://github.com/c2melendez/precision-lab-plus/actions/runs/40970642558) | SUCCESS |

El guard del gate acumulativo informó `skip=false` y `No reusable completed evidence found`. El log registra explícitamente ambas pruebas como PASSED. Resultado del backend: 2,783 passed, 1 skipped, 10 xfailed; cobertura 88.91%.

## Límites y continuidad

- Plus: r355; VC-FE-42 y VC-FE-47 PASS_SCOPED.
- Lite: permanece r334; no se ejecutaron pruebas ni workflows Lite para estas filas. No hay aceptación bilateral.
- Compass P0: WAIT; no se satisficieron sus criterios de salida.
- Las demás filas EDCX-B6 conservan sus estados previos; no se extrapola este resultado.
- Certificación global: OPEN.
- No se relanzaron workflows ni se hicieron cambios de producto.

Siguiente acción canónica: `COMPASS-P0-ACCESS-REVIEW (WAIT)`. Reanudar trabajo matemático más amplio únicamente después de cumplir los criterios de salida de P0.
