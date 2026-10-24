# EDCX-B6 — matriz de trazabilidad test → fila (r273)

**Estado global: REVIEW. No es certificado de aceptación.** Este documento relaciona el harness `backend/tests/test_edcx_b6_contract.py` con las 53 filas de `edcx_ejecutables.jsonl`, a partir del borrador de contrato y del log CI de la corrida [40026869114](https://github.com/c2melendez/precision-lab-plus/actions/runs/40026869114).

## Evidencia CI verificada

- SHA técnico probado: `bd25d58fac8e8333bd9e0aa90a1b9a54efa6aa69`.
- Corrida 40026869114: `SUCCESS`; backend y frontend `SUCCESS`.
- Backend: `2383 passed, 1 skipped, 10 xfailed`; cobertura total `87.97%`.
- Los cinco checks de `test_edcx_b6_contract.py` aparecen como `PASSED`.
- Corrida H1d 40026869004: `SUCCESS` en el mismo SHA.
- Estos resultados prueban el estado de esa revisión del código, no la aceptación de todas las filas B6.

## Criterio de interpretación

- `PARCIAL_TRANSPORTE` no significa aceptación matemática de la fila.
- `PARCIAL_ERROR` solo cubre el código de error comprobado, no necesariamente todo el mensaje o contrato documental.
- `NO_COBERTURA_DIRECTA` significa que el harness actual no tiene una aserción que vincule esa fila fuente a un oráculo independiente.
- `BLOQUEO_CONTRATO` indica que el contrato requerido no se satisface con una salida escalar principal.
- Los checks de `log(100)`, `ln(e)` y `Log(100)` verifican semántica de notación del producto; no corresponden a una aceptación directa de una fila B6 del inventario.
- Por lo tanto, **0 de 53 filas tiene aceptación matemática completa demostrada por este harness**. Dos filas tienen cobertura parcial (VC-FE-05 y VC-FE-14), y VC-FE-11 requiere un contrato multivaluado aparte.

## Matriz de trazabilidad

| Fila | Estado con el harness actual | Alcance / hueco |
|---|---|---|
| VC-FE-01 | NO_COBERTURA_DIRECTA | Sin prueba específica que compare el resultado de esta fila con un oráculo independiente. |
| VC-FE-02 | NO_COBERTURA_DIRECTA | Sin prueba específica que compare el resultado de esta fila con un oráculo independiente. |
| VC-FE-03 | NO_COBERTURA_DIRECTA | Sin prueba específica que compare el resultado de esta fila con un oráculo independiente. |
| VC-FE-04 | NO_COBERTURA_DIRECTA | Sin prueba específica que compare el resultado de esta fila con un oráculo independiente. |
| VC-FE-05 | PARCIAL_TRANSPORTE | Log(-1) solo verifica success, result_approx=null y texto/LaTeX no vacíos; no compara contra iπ ni valida rama. |
| VC-FE-06 | NO_COBERTURA_DIRECTA | Sin prueba específica que compare el resultado de esta fila con un oráculo independiente. |
| VC-FE-07 | NO_COBERTURA_DIRECTA | Sin prueba específica que compare el resultado de esta fila con un oráculo independiente. |
| VC-FE-08 | NO_COBERTURA_DIRECTA | Sin prueba específica que compare el resultado de esta fila con un oráculo independiente. |
| VC-FE-09 | NO_COBERTURA_DIRECTA | Sin prueba específica que compare el resultado de esta fila con un oráculo independiente. |
| VC-FE-10 | NO_COBERTURA_DIRECTA | Sin prueba específica que compare el resultado de esta fila con un oráculo independiente. |
| VC-FE-11 | BLOQUEO_CONTRATO | La API escalar de log principal no satisface el conjunto multivaluado 2πik; requiere contrato de conjunto separado. |
| VC-FE-12 | NO_COBERTURA_DIRECTA | Sin prueba específica que compare el resultado de esta fila con un oráculo independiente. |
| VC-FE-13 | NO_COBERTURA_DIRECTA | Sin prueba específica que compare el resultado de esta fila con un oráculo independiente. |
| VC-FE-14 | PARCIAL_ERROR | Log(0) verifica success=false y DOMAIN_ERROR; falta validar mensaje/detalle si el contrato fuente lo exige. |
| VC-FE-15 | NO_COBERTURA_DIRECTA | Sin prueba específica que compare el resultado de esta fila con un oráculo independiente. |
| VC-FE-16 | NO_COBERTURA_DIRECTA | Sin prueba específica que compare el resultado de esta fila con un oráculo independiente. |
| VC-FE-17 | NO_COBERTURA_DIRECTA | Sin prueba específica que compare el resultado de esta fila con un oráculo independiente. |
| VC-FE-18 | NO_COBERTURA_DIRECTA | Sin prueba específica que compare el resultado de esta fila con un oráculo independiente. |
| VC-FE-19 | NO_COBERTURA_DIRECTA | Sin prueba específica que compare el resultado de esta fila con un oráculo independiente. |
| VC-FE-20 | NO_COBERTURA_DIRECTA | Sin prueba específica que compare el resultado de esta fila con un oráculo independiente. |
| VC-FE-21 | NO_COBERTURA_DIRECTA | Sin prueba específica que compare el resultado de esta fila con un oráculo independiente. |
| VC-FE-22 | NO_COBERTURA_DIRECTA | Sin prueba específica que compare el resultado de esta fila con un oráculo independiente. |
| VC-FE-23 | NO_COBERTURA_DIRECTA | Sin prueba específica que compare el resultado de esta fila con un oráculo independiente. |
| VC-FE-24 | NO_COBERTURA_DIRECTA | Sin prueba específica que compare el resultado de esta fila con un oráculo independiente. |
| VC-FE-25 | NO_COBERTURA_DIRECTA | Sin prueba específica que compare el resultado de esta fila con un oráculo independiente. |
| VC-FE-26 | NO_COBERTURA_DIRECTA | Sin prueba específica que compare el resultado de esta fila con un oráculo independiente. |
| VC-FE-27 | NO_COBERTURA_DIRECTA | Sin prueba específica que compare el resultado de esta fila con un oráculo independiente. |
| VC-FE-28 | NO_COBERTURA_DIRECTA | Sin prueba específica que compare el resultado de esta fila con un oráculo independiente. |
| VC-FE-29 | NO_COBERTURA_DIRECTA | Sin prueba específica que compare el resultado de esta fila con un oráculo independiente. |
| VC-FE-30 | NO_COBERTURA_DIRECTA | Sin prueba específica que compare el resultado de esta fila con un oráculo independiente. |
| VC-FE-31 | NO_COBERTURA_DIRECTA | Sin prueba específica que compare el resultado de esta fila con un oráculo independiente. |
| VC-FE-32 | NO_COBERTURA_DIRECTA | Sin prueba específica que compare el resultado de esta fila con un oráculo independiente. |
| VC-FE-33 | NO_COBERTURA_DIRECTA | Sin prueba específica que compare el resultado de esta fila con un oráculo independiente. |
| VC-FE-34 | NO_COBERTURA_DIRECTA | Sin prueba específica que compare el resultado de esta fila con un oráculo independiente. |
| VC-FE-35 | NO_COBERTURA_DIRECTA | Sin prueba específica que compare el resultado de esta fila con un oráculo independiente. |
| VC-FE-36 | NO_COBERTURA_DIRECTA | Sin prueba específica que compare el resultado de esta fila con un oráculo independiente. |
| VC-FE-37 | NO_COBERTURA_DIRECTA | Sin prueba específica que compare el resultado de esta fila con un oráculo independiente. |
| VC-FE-38 | NO_COBERTURA_DIRECTA | Sin prueba específica que compare el resultado de esta fila con un oráculo independiente. |
| VC-FE-39 | NO_COBERTURA_DIRECTA | Sin prueba específica que compare el resultado de esta fila con un oráculo independiente. |
| VC-FE-40 | NO_COBERTURA_DIRECTA | Sin prueba específica que compare el resultado de esta fila con un oráculo independiente. |
| VC-FE-41 | NO_COBERTURA_DIRECTA | Sin prueba específica que compare el resultado de esta fila con un oráculo independiente. |
| VC-FE-42 | NO_COBERTURA_DIRECTA | Sin prueba específica que compare el resultado de esta fila con un oráculo independiente. |
| VC-FE-43 | NO_COBERTURA_DIRECTA | Sin prueba específica que compare el resultado de esta fila con un oráculo independiente. |
| VC-FE-44 | NO_COBERTURA_DIRECTA | Sin prueba específica que compare el resultado de esta fila con un oráculo independiente. |
| VC-FE-45 | NO_COBERTURA_DIRECTA | Sin prueba específica que compare el resultado de esta fila con un oráculo independiente. |
| VC-FE-46 | NO_COBERTURA_DIRECTA | Sin prueba específica que compare el resultado de esta fila con un oráculo independiente. |
| VC-FE-47 | NO_COBERTURA_DIRECTA | Sin prueba específica que compare el resultado de esta fila con un oráculo independiente. |
| VC-FE-48 | NO_COBERTURA_DIRECTA | Sin prueba específica que compare el resultado de esta fila con un oráculo independiente. |
| VC-FE-49 | NO_COBERTURA_DIRECTA | Sin prueba específica que compare el resultado de esta fila con un oráculo independiente. |
| VC-FE-50 | NO_COBERTURA_DIRECTA | Sin prueba específica que compare el resultado de esta fila con un oráculo independiente. |
| VC-FE-51 | NO_COBERTURA_DIRECTA | Sin prueba específica que compare el resultado de esta fila con un oráculo independiente. |
| VC-FE-52 | NO_COBERTURA_DIRECTA | Sin prueba específica que compare el resultado de esta fila con un oráculo independiente. |
| VC-FE-53 | NO_COBERTURA_DIRECTA | Sin prueba específica que compare el resultado de esta fila con un oráculo independiente. |

## Próxima acción

Construir pruebas por grupos, empezando por los casos escalares complejos que pueden expresarse en `POST /api/v1/evaluate`, con adaptador de entrada explícito, comparación contra oráculo independiente y tolerancia documentada. Separar los casos de identidad simbólica, ramas/cortes y singularidades. Definir por separado la capacidad multivaluada para VC-FE-11 y la parte multivaluada de VC-FE-15. No ejecutar otro workflow hasta preparar un conjunto dirigido con aceptación concreta y revisar si una corrida existente ya cubre el SHA exacto.

## Estados que no cambian

- EDCX-B6: `REVIEW`.
- EDCX-B5: `BLOCKED` en Plus.
- Lite: `NO_EJECUTADO`; no inferir paridad.
- H2-SG28-DIST-01..08 y SECURITY-S25: `BLOCKED`.
- SY-P-23: `OPEN`.
- SY-X-04-PLUS-HTTP: `BLOCKED`.
- ALGEBRA229-AS-B-29: `ON_HOLD`.
- Certificación global: `OPEN`.
