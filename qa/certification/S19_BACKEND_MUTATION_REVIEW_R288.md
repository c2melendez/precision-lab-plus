# S19 — revisión del artefacto mutmut backend (r288)

**Estado:** REVIEWED / ACCEPTANCE_BLOCKED.  
**Run:** https://github.com/c2melendez/precision-lab-plus/actions/runs/40069907892  
**SHA evaluado:** 6e6a59ee556cf6bba60a40010ec707f05a01ca52.  
**Artefacto:** s19-plus-backend-mutmut, ID 12551670346, digest SHA-256 064d33a4f7be9d4e68952dac344f0630153866c2916a97fc7f26786561f73fee.

## Evidencia leída

El ZIP contiene mutmut-exit-code.txt y mutmut-results.txt. El código de salida registrado es 0, pero esto solo indica que el comando terminó sin error de herramienta; no representa un score aprobado.

Resumen de cierre extraído de los logs del job `plus-backend-mutmut` (línea final `3280/3280`), que sí registra todos los estados:

| Estado de mutante | Cantidad |
|---|---:|
| killed | 971 |
| survived | 2,136 |
| no tests | 159 |
| timeout | 14 |
| **Total** | **3,280** |
| **Score killed (mismo denominador histórico)** | **29.60%** |

El artefacto `mutmut-results.txt` lista los estados no-killed, mientras que el log del job conserva el resumen total. El resumen final informa 971 killed, 2,136 survived, 159 no tests y 14 timeout (3,280 en total). El reporte previo de continuidad indicaba 13 timeouts; el artefacto/log fuente confirma **14**.

## Interpretación y límites

- El ZIP no contiene el total/killed, pero el log del job sí: score killed 971/3,280 = 29.60% usando la misma convención de denominador que el baseline. El score está calculado, pero su comparación requiere considerar la expansión del inventario.
- no tests no equivale a mutantes muertos ni debe contarse como éxito.
- timeout no equivale a mutante muerto; debe reportarse por separado y revisarse como ejecución no concluyente.
- Aunque el job de Actions figure SUCCESS y el código de salida diga 0, **S19 backend no queda aceptado automáticamente**: el score es 29.60%, frente a 57.39% en el baseline operativo, y el inventario creció de 1,028 a 3,280 mutantes.
- No se infiere que todos los mutantes listados representen defectos de producto: algunos pueden requerir análisis de equivalencia, observabilidad o alcance de pruebas. El reporte actual no basta para afirmar el número de kills.

## Comparación con el artefacto baseline

Se recuperó el artefacto baseline ID `10740671311` del run `35838270384`. Su archivo `mutmut-results.txt` tiene 438 entradas: 371 survived, 58 no tests y 9 timeout; el documento normativo registra además 590 killed, para un inventario total de 1,028 y score killed 57.39%. La omisión de killed en el listado explica por qué sumar solo sus líneas no reconstruye el total. El log actual sí informa 971 killed y 3,280 total; score 29.60% frente a 57.39% en baseline. La diferencia de 2,252 mutantes adicionales requiere análisis por módulo y cambios de código antes de atribuir la caída a degradación de pruebas.

## Evidencia de resumen de ejecución

Los logs finales muestran `3280/3280 🎉 971 🫥 159 ⏰ 14 🙁 2136`. Distribución por módulos según las líneas finales por mutante:

| Módulo | Killed | Survived | No tests | Timeout | Total |
|---|---:|---:|---:|---:|---:|
| `app.routers.evaluate` | 89 | 347 | 18 | 3 | 457 |
| `app.services.ast_validator` | 28 | 45 | 0 | 0 | 73 |
| `app.services.parsing` | 538 | 653 | 82 | 8 | 1,281 |
| `app.services.solve_service` | 316 | 1,091 | 59 | 3 | 1,469 |
| **Total** | **971** | **2,136** | **159** | **14** | **3,280** |

El baseline usó Python 3.12.14; la ejecución actual, Python 3.12.15. Ambas muestran mutmut 3.8.0 fijado en el workflow y las mismas cinco superficies objetivo a nivel de configuración, aunque los archivos han evolucionado. No se debe comparar el porcentaje como regresión pura sin revisar el crecimiento de inventario y la incorporación de funciones (por ejemplo, rutas SG28 y parseo de desigualdades).

## Decisión

**No repetir todavía la corrida completa.** Primero, establecer un contrato de aceptación versionado para backend que especifique:
1. el denominador oficial del mutation score y el tratamiento de no tests, timeout, mutantes equivalentes y exclusiones;
2. el umbral mínimo aprobado y su justificación;
3. el tratamiento de mutantes que sobreviven por falta de aserciones, con evidencia de cada exclusión;
4. la obligación de publicar recuentos reproducibles y score calculado en el artefacto;
5. una prueba de preflight que falle si el reporte no tiene kills/score cuando el criterio los exige o si faltan superficies críticas.

Después de aprobar el criterio, realizar una única ejecución focalizada en el SHA técnico actualizado, sin relanzar los otros jobs de S19 que no necesiten nueva evidencia. Hasta entonces: **S19 integral = REVIEW_REQUIRED; backend mutation acceptance = BLOCKED**. No cambiar código de producto ni declarar certificación global.

## Relación con otros bloqueos

Este resultado no resuelve SG28 ni S18. SG28 sigue REVIEW_REQUIRED por decisiones de contrato y fencing; S18 sigue cancelado por infraestructura. La certificación global permanece OPEN.
