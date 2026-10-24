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
| killed | 0 |
| survived | 2,136 |
| no tests | 159 |
| timeout | 14 |
| **Total registrado** | **2,309** |

La revisión del archivo muestra cero mutantes killed. El reporte previo de continuidad indicaba 13 timeouts; el artefacto descargado contiene **14**. Para futuras referencias prevalece el artefacto del run, y se corrige la cifra documental.

## Interpretación y límites

- No existe en el artefacto una puntuación de mutación positiva que permita afirmar que el backend satisface un umbral.
- no tests no equivale a mutantes muertos ni debe contarse como éxito.
- timeout no equivale a mutante muerto; debe reportarse por separado y revisarse como ejecución no concluyente.
- Aunque el job de Actions figure SUCCESS y el archivo de salida diga 0, **S19 backend no queda aceptado** con estos datos.
- No se infiere que todos los mutantes sobrevividos representen defectos de producto: algunos pueden requerir análisis de equivalencia, observabilidad o alcance de pruebas. La cifra sí prueba que la ejecución actual no aporta kills registrados.

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
