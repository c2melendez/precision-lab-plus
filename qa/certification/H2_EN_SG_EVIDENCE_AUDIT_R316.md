# IN625 H2 — Auditoría de evidencia por caso EN-SG-01..32 (R316)

Fecha de corte: 2026-10-27 UTC  
Rama: `qa/syntax-audit-in625-a1`  
HEAD observado al iniciar: `9c541ca814aaf363f9c2d6ec9ddebaa5a48386ff`  
Fuente de criterios: `qa/certification/IN625_H2_MATRIX.md` (transcripción operativa de Parte H.2; la matriz fuente original sigue siendo referencia primaria).  
Fuente backend revisada: `backend/tests/test_in625_h2_security.py`, blob `d1722b92b33e3e189af498510902a7489dba0cd1`.  
Fuentes frontend revisadas: `frontend/e2e/in625-h2-sg28-cancel.spec.ts`, `frontend/e2e/in625-syntax-native.spec.ts`, `frontend/e2e/scriptInertProbe.ts`, `frontend/e2e/fileAccessProbe.ts`.

## Regla de clasificación

- **PASS**: caso y criterio identificados, ejecución aprobada en un run/job cuyo SHA coincide exactamente con el código auditado y con evidencia recuperable.
- **FAIL**: ejecución verificable que incumple la expectativa.
- **GAP**: falta prueba equivalente suficiente, falta ejecución vinculada a SHA, o la prueba cubre un criterio distinto del declarado.
- **MANUAL**: necesita verificación manual explícita y evidencia adjunta.
- La presencia de una función de test no se considera PASS. No se encontraron en la evidencia disponible de este corte logs de un run H2 que vinculen el conjunto backend completo a un SHA y job concretos. El run Plus `40429424316` es H1d/Playwright y no se usa para acreditar H2. El run Lite `40403964745` es checkout de merge de PR y tampoco acredita esta matriz.

## Tabla de trazabilidad

| Caso | Cobertura observada en código | Estado al corte | Evidencia run/job/SHA y observación |
|---|---|---|---|
| EN-SG-01 | `SY-X-15` en `in625-syntax-native.spec.ts` comprueba texto `<script>alert(1)</script>` inerte y recuperación; el probe también detecta inserción de script. | GAP (evidencia de ejecución) | Equivalencia conductual probable; comprobar adjunto y run exacto antes de adjudicar PASS. No duplicar sin revisar el resultado original. |
| EN-SG-02 | No se identificó una prueba específica de evento de imagen (p. ej. `onerror`) en las rutas revisadas. | GAP | Sin run H2/job/SHA verificado; buscar cobertura conductual adicional antes de implementar. |
| EN-SG-03 | `SY-X-15` verifica que el texto HTML/script se conserva como texto y no se ejecuta; equivalencia exacta con la entrada matemática H2 pendiente. | GAP (equivalencia por confirmar) | Sin run H2/job/SHA verificado. No duplicar hasta comparar entrada y expectativa canónicas. |
| EN-SG-04 | No se identificó un test específico de hipervínculo LaTeX inseguro en los archivos revisados. | GAP | Sin run H2/job/SHA verificado; posible comprobación manual de seguridad de render. |
| EN-SG-05 | No se identificó test específico de macros URL/imagen/HTML para esta fila. | GAP | Sin run H2/job/SHA verificado. |
| EN-SG-06 | No se identificó test específico de definición recursiva de macro para esta fila. | GAP | Sin run H2/job/SHA verificado. |
| EN-SG-07 | No se identificó test específico de macros/alias/catcode para esta fila. | GAP | Sin run H2/job/SHA verificado. |
| EN-SG-08 | `SY-X-16` prueba comando de archivo y `SY-X-17` prueba shell escape; ambos parecen cubrir parte del criterio, pero la equivalencia con toda la fila H2 no está demostrada. | GAP (cobertura parcial/evidencia de ejecución) | Sin run H2/job/SHA verificado. El control positivo del probe no es PASS de producto. |
| EN-SG-09 | Test parametrizado en `test_in625_h2_security.py`: rechaza introspección/ejecución Python. | GAP | Cobertura escrita; ejecución H2 con job/SHA exacto no verificada. |
| EN-SG-10 | Test parametrizado de lectura de archivo Python. | GAP | Cobertura escrita; ejecución H2 con job/SHA exacto no verificada. |
| EN-SG-11 | Test parametrizado de introspección de clases. | GAP | Cobertura escrita; ejecución H2 con job/SHA exacto no verificada. |
| EN-SG-12 | Test parametrizado de lambda Python. | GAP | Cobertura escrita; ejecución H2 con job/SHA exacto no verificada. |
| EN-SG-13 | Casos explícitos `exec` y `eval`. | GAP | Cobertura escrita; ejecución H2 con job/SHA exacto no verificada. |
| EN-SG-14 | Casos `import os` y `os.system`. | GAP | Cobertura escrita; ejecución H2 con job/SHA exacto no verificada. |
| EN-SG-15 | Casos de atributos `__class__` y `__dict__`. | GAP | Cobertura escrita; ejecución H2 con job/SHA exacto no verificada. |
| EN-SG-16 | Variantes `Symbol`, `Integer` y `Function`. | GAP | Cobertura escrita; ejecución H2 con job/SHA exacto no verificada. |
| EN-SG-17 | Test de no filtración de asignación entre evaluaciones. | GAP | Cobertura escrita; ejecución H2 con job/SHA exacto no verificada. |
| EN-SG-18 | Varios tests de palabras reservadas, preservación de llamadas posteriores y cálculo independiente. | GAP | Cobertura escrita; ejecución H2 con job/SHA exacto no verificada. |
| EN-SG-19 | Test de 50 paréntesis espera resultado 1. | GAP | Cobertura escrita; ejecución H2 con job/SHA exacto no verificada. |
| EN-SG-20 | Entrada de 2.001 caracteres se rechaza con HTTP 422/VALIDATION_ERROR por máximo de longitud 500. | GAP | **No acredita** guardia interna de profundidad del parser; acredita rechazo en validación de solicitud. Ejecución H2 con job/SHA exacto no verificada. |
| EN-SG-21 | `qa/s20/backend_perf.py` ya prueba `sum(i,i,1,10000)` y espera resultado `50005000`, con límite duro de 5 s por operación. Es cobertura conductual relacionada, pero no es una suma explícita de 10.000 términos con umbral de 2 s ni resultado 10000. | GAP (criterio no equivalente) | Reutilizar S20 como evidencia auxiliar; no duplicar a ciegas. Decidir si se necesita una prueba específica del criterio literal, aislada y con presupuesto ≤2 s. |
| EN-SG-22 | Test de 100.000 caracteres y rechazo por límite de longitud. | GAP | Cobertura escrita; es rechazo seguro, no evaluación del payload. Ejecución H2 con job/SHA exacto no verificada. |
| EN-SG-23 | `SY-X-10` en `in625-syntax-native.spec.ts` envía `10^{10^{10}}` y espera `COMPLEXITY_LIMIT` más recuperación. Es cobertura conductual equivalente probable. | GAP (falta run H2 exacto) | No crear un duplicado antes de recuperar el run/job/adjunto de SY-X-10 y comparar la fila canónica. |
| EN-SG-24 | `SY-X-11` en `in625-syntax-native.spec.ts` envía `9^{9^{9}}` y espera `COMPLEXITY_LIMIT` más recuperación. Es cobertura conductual equivalente probable. | GAP (falta run H2 exacto) | No crear un duplicado antes de recuperar el run/job/adjunto de SY-X-11 y comparar la fila canónica. |
| EN-SG-25 | No se localizó test dedicado de factorial 1.000.000 con límite/cancelación. | GAP | Test-first en API Plus; no lanzar carga extrema en producción. |
| EN-SG-26 | No se localizó test dedicado de expansión `(x+1)^10000` con límite/cancelación. | GAP | Test-first en API Plus; no lanzar carga extrema en producción. |
| EN-SG-27 | Se localizaron controles de potencias astronómicas `10^{10^{10}}` y `9^{9^{9}}`, pero no una prueba específica de la familia de potencias anidadas de 2. | GAP | Verificar primero cobertura equivalente en otros tests backend; no asumir que los controles 10/9 cubren el caso 2. |
| EN-SG-28 | `in625-h2-sg28-cancel.spec.ts` tiene varios tests de cancelación y recuperación; algunos usan ruta interceptada y otros backend real. | GAP | No se vinculó aquí un run/job/SHA exacto que pruebe cada variante. La ruta mock no acredita por sí sola el worker real. No activar `SG28_EVALUATE_ISOLATION` en producción. |
| EN-SG-29 | Backend tiene test de 20 cálculos concurrentes y request IDs únicos; el propio docstring aclara que no prueba “last input wins” del frontend. | GAP | Cobertura parcial; falta evidencia de ejecución y evidencia UI para el criterio de última entrada. |
| EN-SG-30 | Tests de caracteres JSON especiales; comprueban respuesta estructurada, correlación de request ID y ausencia de traceback. | GAP | Cobertura escrita; ejecución H2 con job/SHA exacto no verificada. |
| EN-SG-31 | Tests de cuerpo JSON de 5 MiB con y sin Content-Length, cuerpo pequeño de control y recuperación tras rechazo; esperan 413. | GAP | Cobertura escrita; ejecución H2 con job/SHA exacto no verificada. Ejecutar solo en CI/local aislado. |
| EN-SG-32 | No se localizó test explícito de ráfaga con rate limit condicional. | GAP | Test-first en API Plus solo si se confirma que no existe cobertura conductual equivalente; definir primero cómo se activa y observa el rate limit sin asumirlo siempre activo. |

## Conclusiones del corte

1. **No hay PASS H2 adjudicables con la evidencia recuperada en este corte**: esto no significa que todas las pruebas fallen; significa que no se ha adjuntado/verificado el enlace exacto caso → test → run/job → SHA.
2. Hay pruebas escritas identificables para EN-SG-09..20, 22, 28..31. EN-SG-20 y EN-SG-22 son rechazos por límite de longitud; no deben describirse como prueba de profundidad interna ni de rendimiento.
3. Gaps de implementación a priorizar según la acción canónica: EN-SG-21, EN-SG-23..27 y EN-SG-32 en API Plus; EN-SG-01..08 en frontend solo tras confirmar que no existe cobertura conductual equivalente sin etiqueta.
4. Antes de escribir pruebas nuevas, buscar tests conductuales equivalentes y conservar el ID canónico al añadir trazabilidad. No inventar PASS ni ejecutar cargas extremas en producción.
5. El estado global permanece **OPEN**. Se mantienen sin cambio los bloqueos declarados en `continuity.json`: SECURITY-S25 BLOCKED, ALGEBRA229-AS-B-29 ON_HOLD, EDCX-B5 BLOCKED, SY-X-04-PLUS-HTTP BLOCKED, SG28-DIST OUT_OF_SCOPE_SINGLE_HOST, PR #29 OPEN/DRAFT.
6. Este archivo es una auditoría documental y no cambia `continuity.json` ni su `next_action`. No se ha lanzado ninguna corrida nueva.
