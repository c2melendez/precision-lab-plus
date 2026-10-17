# Algebra 114 — preparación

Estado: PREPARATORY; no hay acreditación de los 114 requisitos ni cierre Syntax309.

El protocolo ordena Syntax309, Algebra114 y Algebra229. Se observaron en Plus: `backend/app/routers/algebra.py`, `backend/app/services/algebra_service.py`, `backend/tests/test_algebra.py`, `backend/tests/test_exhaustive_module02_algebra.py`, `frontend/e2e/exhaustive-module02-algebra.spec.ts`. No se localizó matriz de 114 casos por nombre de ruta en los árboles revisados. Esto no demuestra su inexistencia.

Siguiente paso: localizar y validar el contrato fuente de Algebra114 con 114 IDs y oráculos, después mapear implementación/cobertura de Lite y Plus por canal y seleccionar primer caso comprobable. No generar PASS a partir de nombres de archivos. SY-P-23, X04 y X14 Plus permanecen abiertos/bloqueados y certificación global OPEN. No ejecutar CI por documentación.

## Inventario verificado — 2026-10-17

Se inspeccionaron árboles completos de la rama canónica: Lite (567 entradas) y Plus (648 entradas). No apareció un archivo de matriz `Algebra114`, `Algebra229` ni una lista de 114 IDs en las rutas de certificación. **Resultado: SOURCE_NOT_LOCATED**, no ausencia demostrada fuera de los repositorios.

| Capacidad observada | Lite | Plus | Alcance verificable |
|---|---|---|---|
| Evaluación algebraica numérica | `tests/exhaustive-module02-algebra.test.ts` | `backend/tests/test_exhaustive_module02_algebra.py` | Testigos de log/exp/radical; sin IDs de Algebra114 |
| Ecuaciones, expansión e inecuaciones | `src/engine/stepEngine/algebra.ts` y pruebas del módulo 2 | `backend/app/services/algebra_service.py` y pruebas del módulo 2 | Implementaciones presentes, cobertura de requisitos aún ND |
| Interfaz/teclado Álgebra | `e2e/exhaustive-module02-algebra.spec.ts` | `frontend/e2e/exhaustive-module02-algebra.spec.ts` | Verifica botones y entrada, no 114 recorridos E2E |
| API/Worker | Lite: motor local, parser y Worker por canal | Plus: router `backend/app/routers/algebra.py` | No se atribuye equivalencia canal por nombre de archivo |

**No calcular porcentaje de requisitos cubiertos.** Antes de construir una matriz de 114 filas se necesita el documento normativo o fixture original, su versión, ID, expresión y oráculo para cada fila. No fabricar esa matriz a partir de funciones o casos de prueba existentes.

Acción independiente útil: inventariar la procedencia de la suite original (issue/adjunto/commit/archivo externo) y vincular únicamente casos con identificadores canónicos. Mantener SY-P-23 BLOCKED_ON_CONTRACT y Global OPEN. No enviar CI por este cambio documental.

## 2026-10-17 — SOURCE LOCATED and validated

**Source:** `qa/certification/algebra114_source.md`, preserved verbatim from user Library document `Matriz de estrés — Álgebra simbólica.md` (two additional Library copies were byte-for-byte identical in extracted text). **114 original table rows, 114 distinct `AS-*` IDs, four columns ID/Nivel/Ejercicio/Resultado esperado; no additional/generated oracle.**

Official counts by section: SIM 10; EXP 10; FAC 12; PF 8; RAT 10; DIV 8; PAR 10; AVS 10; RAD 10; DOM 6; MUL 6; CONV 8; LIM 6 (total 114). Historical `SOURCE_NOT_LOCATED` status above is superseded: original source is now versioned in both repos. **Source validated; tests still NOT MAPPED/NOT CERTIFIED**. Domain restrictions, real/complex conventions, symbolic equivalents and declared assumptions are part of the original oracles and must not be dropped.

Next: create a deterministic read-only fixture validator for exact original IDs/sections/row count and then a case-channel inventory; begin with `AS-SIM-01` only after explicit parser/engine/UI expected semantics identified. Do not infer 114 PASS from existing Module 2 tests. Keep Syntax309 X04/X14 Plus and SY-P23 blockers, H2/DIST, security S25, mutation S19 and global OPEN. Do not dispatch CI solely for source documentation.
