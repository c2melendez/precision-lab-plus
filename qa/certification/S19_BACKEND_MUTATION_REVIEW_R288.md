# S19 — revisión del artefacto mutmut backend (r288)

**Estado:** REVIEWED / ACCEPTANCE_BLOCKED.  
**Run:** https://github.com/c2melendez/precision-lab-plus/actions/runs/40069907892  
**SHA evaluado:** 6e6a59ee556cf6bba60a40010ec707f05a01ca52.  
**Artefacto:** s19-plus-backend-mutmut, ID 12551670346, digest SHA-256 064d33a4f7be9d4e68952dac344f0630153866c2916a97fc7f26786561f73fee.

## Evidencia leída

El ZIP contiene mutmut-exit-code.txt y mutmut-results.txt. El código de salida registrado es 0, pero esto solo indica que el comando terminó sin error de herramienta; no representa un score aprobado.

Recuento directo de las líneas de estado del informe:

| Estado de mutante | Cantidad |
|---|---:|
| survived | 2,136 |
| no tests | 159 |
| timeout | 14 |
| **Entradas listadas** | **2,309** |

**Limitación de interpretación:** el listado `mutmut results` representa estados no-killed/no resueltos y no incluye necesariamente los mutantes `killed`. Por tanto, las 2,309 líneas no son el total de mutantes de la campaña ni prueban cero killed; el artefacto por sí solo no permite calcular el score actual. El reporte previo de continuidad indicaba 13 timeouts; el artefacto descargado contiene **14**.

## Interpretación y límites

- El artefacto no publica un resumen completo con el total de mutantes y el recuento `killed`; no permite calcular el score actual ni afirmar que satisface un umbral.
- no tests no equivale a mutantes muertos ni debe contarse como éxito.
- timeout no equivale a mutante muerto; debe reportarse por separado y revisarse como ejecución no concluyente.
- Aunque el job de Actions figure SUCCESS y el código de salida diga 0, **S19 backend no queda aceptado** con estos datos.
- No se infiere que todos los mutantes listados representen defectos de producto: algunos pueden requerir análisis de equivalencia, observabilidad o alcance de pruebas. El reporte actual no basta para afirmar el número de kills.

## Comparación con el artefacto baseline

Se recuperó el artefacto baseline ID `10740671311` del run `35838270384`. Su archivo `mutmut-results.txt` tiene 438 entradas: 371 survived, 58 no tests y 9 timeout; el documento normativo registra además 590 killed, para un inventario total de 1,028 y score killed 57.39%. La omisión de killed en el listado explica por qué sumar solo sus líneas no reconstruye el total. El artefacto actual tiene 2,309 entradas listadas (2,136 survived, 159 no tests, 14 timeout), pero carece de recuento completo de killed/total comparable. Debe investigarse la diferencia de estados no-killed antes de evaluar tendencia.

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
