# Hoja de ruta de continuidad y ejecución — Precision Lab Lite / Plus

Versión: 1.0  
Integración: revisión documental r265  
Rama objetivo: resolver siempre desde los punteros canónicos bilaterales; no asumir esta rama por memoria.  
Estado global conocido al integrar: OPEN. La tarea viva siempre es la de `continuity.json`, no la que aparezca como ejemplo en esta hoja.

## 1. Propósito y autoridad

Esta hoja coordina el trabajo autónomo, reduce ejecuciones redundantes y evita cierres sin evidencia. **No reemplaza ni modifica contratos, matrices fuente, oráculos, criterios de aceptación, el protocolo de ejecución ni los gates existentes.**

Orden de autoridad cuando haya discrepancias:
1. GitHub real: HEAD, refs, eventos, workflow runs, jobs y logs verificados.
2. Contrato/matriz fuente, pruebas, configuración del gate y revisión de aceptación vigente.
3. `qa/certification/continuity.json`: índice estructurado, bloqueos y siguiente acción única.
4. `CURRENT_STATE.md`: fotografía humana; debe reconciliarse con GitHub y el índice.
5. `EXECUTION_LOG.md`: historial acumulativo; no es por sí mismo una instrucción vigente.
6. Esta hoja y el prompt: reglas de orquestación subordinadas a los puntos anteriores.
7. Chat, ZIP, memoria o handoff antiguo: solo pistas; nunca autoridad de estado.

Si los documentos no coinciden, no escoger el dato más conveniente ni sobrescribir el historial. Clasificar REVIEW, recuperar evidencia real, corregir el índice/estado y dejar la discrepancia explicada.

## 2. Arranque obligatorio — P1: reconciliación antes de despachar

Realizar este ciclo en **Lite y Plus**, en la rama canónica verificada, antes de cualquier nuevo dispatch o cambio técnico:

1. Leer los README de la rama predeterminada y comprobar que ambos apuntan a la misma rama canónica. Verificar que esa rama existe en los dos repositorios.
2. Leer `continuity.json`, `CONTINUITY.md`, `CURRENT_STATE.md`, `EXECUTION_PROTOCOL.md`, `MANUAL_CAPABILITY_GAPS.md`, `EXECUTION_LOG.md`, el prompt del repositorio y el contrato/matriz del objetivo.
3. Obtener HEAD, commit base y árbol completo de cada repositorio. No confundir `technical_baseline_sha` con HEAD. No aceptar snapshots vencidos o árboles truncados.
4. Consultar corridas relevantes de **push y pull_request**, incluidas las páginas siguientes, intentos repetidos y corridas en curso. Buscar por workflow, rama y SHA exacto. La ausencia de resultados en una API que solo devuelve PR no prueba que no exista un run push.
5. Para cada gate candidato, revisar evento, branch, `head_sha`, estado/conclusión, intento, jobs, pasos y logs. Identificar pasos realmente ejecutados frente a pasos omitidos o evidencia reutilizada. Un workflow SUCCESS con pasos REUSE no demuestra que el test se ejecutó de nuevo.
6. Comparar la evidencia con la huella de insumos y la revisión de aceptación del gate. Verificar también cambios de dependencias/advisories para seguridad.
7. Reconciliar diferencias entre GitHub, `continuity.json`, `CURRENT_STATE.md` y `EXECUTION_LOG.md`. No registrar un PASS por inferencia, resumen parcial, respuesta API vacía o color verde aislado.
8. Antes de publicar un cambio o despachar una corrida, volver a consultar HEAD y Actions. Si cambió HEAD, parar, reconciliar y recalcular. Usar actualización protegida por SHA esperado/compare-and-swap cuando esté disponible; nunca sobrescribir el trabajo de otra sesión.

**Salida P1:** una fotografía bilateral con HEAD real, evidencia vigente por gate, discrepancias resueltas o explicitadas, bloqueos y una única siguiente acción. Si no se puede confirmar un dato, marcar REVIEW; no inventarlo.

## 3. Máquina de decisión por gate

Aplicar un estado a cada gate y justificarlo con SHA, huella, run y revisión de aceptación:

- **RUN** — falta evidencia requerida, cambió algún insumo relevante o cambió el criterio/revisión de aceptación. Despachar solo el gate mínimo que cubre la brecha; después comprobar el run automático del SHA esperado.
- **WAIT** — ya existe una corrida equivalente en curso para el mismo gate, insumos y SHA objetivo. Esperar/inspeccionar esa corrida; no crear otra.
- **REUSE** — existe evidencia ejecutada, revisada y aprobada que cubre exactamente los mismos insumos, canal, oráculo y revisión de aceptación. Registrar el SHA y run de origen. REUSE no significa que la prueba se ejecutó en el HEAD actual.
- **DIAGNOSE** — persiste el mismo fallo con los mismos insumos y precondiciones. Investigar causa raíz, clasificar producto/harness/oráculo/capability/infraestructura y cambiar una precondición relevante antes de repetir. No relanzar para “ver si ahora pasa”.
- **REVIEW** — evidencia incompleta, ambigua, externa/dinámica, con logs ausentes, árbol truncado, canal no cubierto, criterio cambiado o discrepancia de SHA. No declarar PASS ni ejecutar a ciegas; completar la inspección o pedir intervención solo cuando sea inevitable.

Orden de decisión: **REVIEW si la evidencia no es fiable; WAIT si hay run equivalente activo; REUSE si la evidencia vigente satisface el contrato; DIAGNOSE si el fallo es idéntico; RUN si existe una brecha accionable.** Las condiciones externas de seguridad pueden impedir REUSE aunque coincida el SHA.

## 4. P2 — SG28/DIST y S25: bloqueos sin falsos positivos

### SG28 / H2 / DIST-01..08
- Mantener BLOCKED/OPEN hasta que se demuestre el contrato real: nodos/hosts independientes, admisión global, grants, fencing duradero, cancelación efectiva del worker a través de HTTP, aislamiento, recuperación, concurrencia y logs trazables al SHA.
- No tratar varios procesos en un mismo host, runners independientes sin coordinación demostrada, simulaciones ni tests de interfaz como evidencia multinodo.
- Si no se dispone del entorno externo necesario, continuar preparación y pruebas aisladas sin declarar PASS; documentar exactamente qué falta.

### SECURITY-S25
- Gate de seguridad independiente y sin reutilización automática. Consultar advisories y estado de dependencias vigente, además de la ejecución real de los checks exigidos.
- No repetir el mismo fallo si no cambió dependencia, advisory, configuración o precondición. DIAGNOSE y registrar la causa.
- No bajar severidad, suprimir tests, aceptar mutaciones no detectadas ni desactivar un gate para obtener verde.
- Solo cerrar cuando se cumplan todas las condiciones de salida del índice/protocolo y la evidencia corresponda a la revisión vigente.

Estos bloqueos no impiden trabajo matemático independiente, pero no se pueden ocultar ni marcar resueltos por un gate acumulativo verde.

## 5. P3 — pendientes acotados

Retomar cada pendiente desde su contrato y evidencia exacta, no desde el nombre de la tarea:

- **SY-P-23:** inspeccionar la condición de aceptación y el canal requerido; ejecutar solo la evidencia que falte.
- **SY-X-04-PLUS-HTTP:** demostrar el comportamiento por HTTP real de Plus; evidencia de parser/UI u otro endpoint no sustituye este canal.
- **ALGEBRA229-AS-B-29:** verificar la fuente/matriz original, fila, precondiciones y oráculo antes de ejecutar. ON_HOLD no es PASS ni FAIL. Corregir referencias documentales sin repetir pruebas matemáticas si la evidencia técnica sigue válida.
- Clasificar cualquier nuevo rojo como producto, harness, oráculo, capability o infraestructura. Corregir la capa correcta y añadir regresión permanente cuando corresponda.

## 6. P4 — avance matemático independiente, en orden canónico

La tarea exacta siempre se obtiene del `next_action` bilateral de `continuity.json`; esta hoja no fija un número de bloque permanentemente.

Al integrar esta hoja, el estado documental r264 indica **EDCX-B5**: 25 filas, prefijo `VC-LG`, ejecutar en Plus con oráculo SymPy independiente; Lite permanece `NO_EJECUTADO` mientras no exista una implementación equivalente. El bloque B4 ya fue medido en Plus: 14 PASS, 14 PASS_SCOPED, 4 FAIL y 2 BLOCKED; no se vuelve a ejecutar B4 por defecto ni se interpreta como cierre bilateral.

Para cada bloque EDCX:
1. Congelar las filas fuente y su hash; validar que el oráculo independiente representa el contrato correcto.
2. Medir por los canales especificados y clasificar fila por fila: PASS exacto, PASS_SCOPED, FAIL, BLOCKED o NO_EJECUTADO.
3. PASS_SCOPED exige equivalencia válida y una limitación explícita de forma/canal/alcance; no debe ocultar requisitos omitidos.
4. FAIL y BLOCKED se conservan; no se convierten en PASS mediante xfail, cambios de etiqueta o exclusión del denominador.
5. Ejecutar el harness específico y luego solo los gates acumulativos que el protocolo exija para los insumos modificados.
6. Registrar run, SHA, jobs/logs, canal, oráculo, conteos y decisión en ambos repositorios cuando corresponda.
7. No afirmar paridad Lite/Plus si un producto no ejecutó el bloque o carece de capacidad equivalente.

Después de EDCX, seguir el orden de `EXECUTION_PROTOCOL.md`: sintaxis, Álgebra 114, Álgebra 229, trigonometría, log/exp/radicales, matrices/vectores, EDO/complejos, gráficas y reconciliación/paridad final. Los bloqueos de un dominio no autorizan a saltar dependencias del siguiente.

## 7. P5 — preservar cierres válidos

Conservar evidencia previa de sintaxis, álgebra y matrices/vectores si:
- se verificó que el run ejecutó realmente los casos relevantes;
- el SHA de origen, huella, canal y oráculo están registrados;
- la revisión de aceptación coincide con la vigente;
- no hay cambio de código, fixture, contrato, workflow, dependencia u otro insumo que invalide la huella;
- no existe regresión o discrepancia concreta.

Reabrir solo el subbloque afectado cuando una regresión, cambio relevante o revisión de aceptación lo exija. No reabrir la matriz MV completa ni X19 solo para reconstruir contexto entre LLMs. Si el planificador usa una huella global conservadora y una modificación documental está en la allowlist exacta revisada, conservar la evidencia técnica sin despachar Actions innecesarias.

No usar exclusiones generales como `qa/certification/**`. La lista de rutas exclusivamente documentales es explícita, revisada y exacta; fixtures, tests, scripts, workflows, dependencias y contratos siguen siendo insumos.

## 8. Criterios de cierre documental

Después de un avance técnico:
1. Verificar el run automático esperado en el SHA técnico; registrar el evento (push/PR), ID, URL, conclusión, jobs, logs y pasos realmente ejecutados.
2. Actualizar `continuity.json` con una sola siguiente acción y los bloqueos todavía abiertos; incrementar revisión cuando corresponda. No guardar el SHA del propio commit dentro de sí mismo.
3. Actualizar `CURRENT_STATE.md`, `EXECUTION_LOG.md` y gaps en ambos repositorios según el alcance. Diferenciar resultado técnico de cambio solo documental.
4. Releer los archivos y comprobar paridad bilateral y consistencia con GitHub.
5. Si el cambio es exclusivamente documental y la ruta exacta está en `prose_only_paths`, no despachar gates de producto para generar actividad. Si se modifica un contrato, fixture, test, workflow, dependencia o aceptación, tratarlo como insumo técnico y ejecutar los gates correspondientes.
6. Publicar un resumen breve de qué cambió, qué evidencia lo respalda, qué permanece bloqueado y cuál es la siguiente acción única.

## 9. Qué nunca hacer

- No inventar HEAD, run IDs, logs, conteos, fuentes ni resultados.
- No declarar PASS por un workflow verde que reutilizó evidencia o no ejecutó el paso relevante.
- No lanzar una corrida equivalente en curso, repetir un gate verde vigente ni repetir un fallo idéntico por cambiar de LLM.
- No marcar Lite como probado para capacidades que no implementa.
- No cerrar SG28/DIST, S25, SY-P-23, SY-X-04-PLUS-HTTP o Algebra 229 sin cumplir sus condiciones de salida.
- No cambiar contratos, oráculos o matrices fuente solo para hacer pasar tests.
- No crear commits vacíos/artificiales, ni modificar filtros para ocultar pruebas obligatorias.
- No dejar una siguiente acción múltiple o ambigua: seleccionar una tarea primaria y registrar tareas paralelas solo si son independientes y accionables.

## 10. Regla de autonomía

Resolver automáticamente lecturas, comparaciones, diagnósticos, documentación y ejecuciones autorizadas. Solicitar intervención humana únicamente cuando falten permisos/secretos, una aprobación sea obligatoria, el entorno externo indispensable no esté disponible o dos fuentes autoritativas sigan siendo incompatibles después de inspeccionarlas. En esos casos, continuar con trabajo independiente seguro y dejar el bloqueo preciso, no detener toda la certificación.


## Continuidad operativa r292 — 2026-10-24

**HEAD técnico verificado:** `561547252456b30124f4f7a1db06347ee0731079`. La documentación de continuidad se actualiza después en commits separados; no confundir esos commits documentales con el SHA sobre el que corrieron los gates.

- CI [40098526446](https://github.com/c2melendez/precision-lab-plus/actions/runs/40098526446), cumulative [40098526501](https://github.com/c2melendez/precision-lab-plus/actions/runs/40098526501), Playwright [40098526513](https://github.com/c2melendez/precision-lab-plus/actions/runs/40098526513) y S19 focalizado [40098526609](https://github.com/c2melendez/precision-lab-plus/actions/runs/40098526609) concluyeron SUCCESS sobre ese SHA.
- S19 focalizado: 1,666 mutantes, 801 killed, 863 survived, 2 timeout. El workflow está verde, pero la aceptación S19 continúa BLOCKED; no ejecutar la campaña completa ni interpretar estos números como comparables directamente con el baseline histórico.
- S18 [40098526464](https://github.com/c2melendez/precision-lab-plus/actions/runs/40098526464) fue cancelado por shutdown signal del runner durante `qa/s18/run_differential.py`. Es un bloqueo de infraestructura, no un fallo funcional demostrado.
- PR #29 sigue OPEN/DRAFT; certificación global OPEN. SECURITY-S25 global BLOCKED, AS-B-29 ON_HOLD y H2-SG28-DIST-01..08 BLOCKED.

**Siguiente acción única:** diagnosticar/restablecer infraestructura S18 y ejecutar solo S18 una vez; no repetir los gates verdes anteriores. Después actualizar continuidad con evidencia exacta y revisar sobrevivientes S19 usando artefactos ya generados.

## 2026-10-24 UTC — r293: S18 timeout aislado a una expresión reproducible

- Los logs de S18 en SHA `32f8ab617b8222c529de387da8ade9afc0a5eb08` (runs `40099750218` y `40099786410`) muestran la misma última petición iniciada sin respuesta. La señal de shutdown era consecuencia compatible con una operación bloqueada; no prueba por sí sola un problema de infraestructura.
- Se actualizó `qa/s18/run_differential.py` en commit `3dac60a2b4c3467e1ecf719a2c8d02eee36f5889` para aislar cada llamada a Plus en un proceso terminable con límite de 8 s. Run `40103093212` falló en ~41 s y emitió el contraejemplo exacto: `exp(-1.3983707058413914)+(-1)*sin(-1.3983707058413914)` (seed 180018, timeout 8 s). El mismo hash de entrada aparece en los logs anteriores como última petición iniciada sin respuesta.
- Reclasificación: S18 queda `BLOCKED_REPRODUCIBLE_EVALUATION_TIMEOUT`, no `BLOCKED_INFRASTRUCTURE`. La fase interna exacta (parseo, evaluación o presentación) aún no está aislada; no atribuir la causa a un subsistema específico sin instrumentación.
- Siguiente paso: aislar por fase `POST /api/v1/evaluate` con este único contraejemplo, corregir el bloqueo y añadir regresión acotada. No repetir S18 completo hasta disponer de esa corrección; no repetir CI/cumulative/Playwright ni lanzar S19 completo. S19 sigue BLOCKED (801/1666 killed, 863 survived, 2 timeout); seguridad global BLOCKED; Algebra 229 AS-B-29 ON_HOLD; SG28 H2 BLOCKED; PR #29 abierto/draft; certificación global OPEN.

## 2026-10-24 UTC — r294: corrección focalizada del simplify no acotado en S18

- S18 run `40103093212` ya identifica el input reproducible `exp(-1.3983707058413914)+(-1)*sin(-1.3983707058413914)` y falla rápido con timeout por petición de 8 s. El diagnóstico de fase en run `40103478925` quedó inconcluso por un `EOFError` del propio helper diagnóstico; se corrigió el manejo de EOF.
- Reproducción local del parser de SymPy confirma que `rationalize` convierte los decimales de entrada en racionales exactos y que `sympy.simplify()` sobre la expresión resultante puede agotar memoria. La operación costosa corresponde al `sympy.simplify(result.expr)` incondicional en `_render_evaluate_presentation`; no es un fallo genérico del runner.
- Corrección aplicada en `backend/app/routers/evaluate.py`: para expresiones numéricas sin variables libres que contienen `exp`, provienen de una entrada decimal y ya tienen `approx_value`, la presentación usa esa aproximación calculada en vez de intentar una simplificación exacta potencialmente no acotada. Se añadió regresión HTTP en `backend/tests/test_evaluate.py` para el contraejemplo exacto. El harness S18 mantiene el límite por petición y ahora tolera EOF del diagnóstico.
- Estado: `VERIFYING_FIX`. El commit actual debe validar CI y S18; no lanzar S19 completo ni repetir manualmente gates verdes. Si S18 pasa en el SHA actual, registrar PASS para ese gate y continuar con la revisión focalizada de sobrevivientes S19. Global certification OPEN; S19 acceptance BLOCKED; S25 global BLOCKED; Algebra 229 AS-B-29 ON_HOLD; SG28 H2 BLOCKED; PR #29 abierto/draft.

## 2026-10-24 UTC — r295: corrección del patrón decimal en el guard de presentación

- En revisión del commit r294 se detectó que el patrón regex del guard decimal quedó con escapes duplicados por la serialización del cambio (`\\d` literal), por lo que no activaría la protección. Se corrige a `\d+\.\d+` en el código Python. Esta revisión de código se hizo antes de aceptar el resultado de S18; el run de r294 no debe considerarse validación del fix.
- La corrección de presentación y la regresión HTTP permanecen focalizadas en el contraejemplo S18. El siguiente commit debe demostrar que el guard se activa y que CI/S18 terminan; no repetir S19 completo ni aceptar gates solo por estado queued. Certificación global OPEN; S19 BLOCKED; S25 global BLOCKED; AS-B-29 ON_HOLD; SG28 H2 BLOCKED; PR #29 abierto/draft.
