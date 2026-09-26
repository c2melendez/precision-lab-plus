# S26.1 — Mapeo de evidencia visual ↔ pruebas funcionales

Proyecto: **Precision Lab Plus**

| Área S26 | Baseline visual | Prueba(s) funcional(es) asociadas |
|---|---|---|
| Shell / navegación | `frontend/e2e/s26-baseline.spec.ts` | `frontend/e2e/smoke.spec.ts` |
| Científica | `frontend/e2e/s26-baseline.spec.ts` | `frontend/e2e/exhaustive-module02-algebra.spec.ts`, `frontend/e2e/exhaustive-module03-calculus.spec.ts`, `frontend/e2e/s16-critical-regressions.spec.ts` |
| Matrices | `frontend/e2e/s26-baseline.spec.ts` | `frontend/e2e/exhaustive-module06-matrices.spec.ts` |
| Gráficas | `frontend/e2e/s26-baseline.spec.ts` | `frontend/e2e/exhaustive-module09-graphing.spec.ts` |
| Estadística | `frontend/e2e/s26-baseline.spec.ts` | `frontend/e2e/exhaustive-module07-statistics.spec.ts` |
| Unidades | `frontend/e2e/s26-baseline.spec.ts` | `frontend/e2e/exhaustive-module08-units.spec.ts` |
| Historial | `frontend/e2e/s26-baseline.spec.ts` | cobertura de flujo dentro de la suite E2E existente + smoke S26 |
| Teclado | `frontend/e2e/s26-baseline.spec.ts` | `frontend/e2e/exhaustive-module10-keyboard.spec.ts`, `frontend/e2e/keyboard.spec.ts` |
| Layouts | `frontend/e2e/s26-baseline.spec.ts` | `frontend/e2e/exhaustive-module11-layout-responsive.spec.ts` |
| Ajustes/persistencia | `frontend/e2e/s26-baseline.spec.ts` | `frontend/e2e/exhaustive-module12-personalization-a11y.spec.ts` |
| Accesibilidad | capturas S26 | `frontend/e2e/accessibility.spec.ts`, `frontend/e2e/s23-accessibility.spec.ts` |
| API/contrato | N/A | `frontend/e2e/api-contract.spec.ts` |

Además, el PR S26 ejecuta gates independientes de mutación, rendimiento, compatibilidad cross-browser, accesibilidad y seguridad cuando corresponde.

## Regla

Una fila de `VISUAL_MATRIX.md` solo podrá pasar a PASS cuando:
1. exista captura/baseline del estado;
2. el test funcional asociado pase sobre el mismo SHA o un SHA posterior sin cambios funcionales;
3. no exista una discrepancia runtime pendiente para esa superficie.
