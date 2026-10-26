# H2 EN-SG-01..32 — Auditoría de evidencia por caso (R315)

**Corte consultado:** 2026-10-26 UTC  
**Rama base consultada:** `qa/syntax-audit-in625-a1`  
**Alcance:** trazabilidad de evidencia existente; no es una declaración de cierre de H2 ni de certificación global.

## Fuentes y método

- Matriz de procedencia: `qa/certification/IN625_H2_MATRIX.md` (blob `54193952beac2080d40bb436ba9ae2ffc1a9ec60`) y fuente primaria recuperada del ZIP corregido de handoff. El archivo completo contiene 625 filas; SHA-256 `58fbc0ed04aef158148981fc28074d470e45ec07a67604f89b3847b55c625528`. El extracto exacto H.2 quedó incorporado en la rama `fix/en-sg-gap-tests-r315-20261026`, PR [#36](https://github.com/c2melendez/precision-lab-plus/pull/36), pendiente de sus checks; los vectores faltantes ya no necesitan inferirse.
- Test backend Plus: `backend/tests/test_in625_h2_security.py` (blob `d1722b92b33e3e189af498510902a7489dba0cd1`).
- E2E de cancelación: `frontend/e2e/in625-h2-sg28-cancel.spec.ts` (blob `38cfc6ccb461e3e839cbd8a4db8684a933c2ac5b`).
- E2E nativo Syntax309: `frontend/e2e/in625-syntax-native.spec.ts` (blob `d2877ea807fae78a6675db28b03d49731f809acc`) y fixtures `qa/certification/syntax309_cases.jsonl` (blob `fd5d8d05ea8b799039cc45e6a4cd88587aab4f8f`).
- Run backend acumulativo del PR de guardrail Plus: [40374409722](https://github.com/c2melendez/precision-lab-plus/actions/runs/40374409722), job `121753424481`, SHA probado `f2a8f9877d8a1b1cde9bf074abbe75b475258913`. Log final observado: **2707 passed, 1 skipped, 10 xfailed, 1 warning**. Este SHA pertenece al branch/PR de reparación; el run prueba el árbol que incorporó los guardrails, no el HEAD canónico antes del merge.
- Run Playwright Plus [40374409444](https://github.com/c2melendez/precision-lab-plus/actions/runs/40374409444), job `121753422799`, SHA `f2a8f9877d8a1b1cde9bf074abbe75b475258913`: **SUCCESS**, 627 pruebas generales y 21 pruebas SG28 (7 escenarios x desktop/tablet/móvil). Es evidencia exacta de este SHA del PR, no del HEAD canónico ni aceptación distribuida.
- Evidencia histórica SG28: [40065789096](https://github.com/c2melendez/precision-lab-plus/actions/runs/40065789096), SHA `83b18dab5a176087d9f228725a2140c535d07a2f`, Playwright 21 passed (7 escenarios x desktop/tablet/móvil). Es anterior al SHA actual de la rama de reparación y prueba alcance single-host; no cierra aceptación distribuida.

**Convención:** `PASS` significa evidencia por SHA/run concordante con el criterio; `PARTIAL` significa una prueba cercana pero insuficiente para el criterio completo; `GAP` significa que no se localizó prueba equivalente con el alcance esperado; `WAIT` significa que la corrida relevante aún no terminó. Los tests etiquetados pasan solo por la conclusión del run y el log citado, no por existir en el árbol.

## Matriz de trazabilidad

| Caso | Estado al corte | Test/archivo y evidencia | Límite o siguiente acción |
|---|---|---|---|
| EN-SG-01 | PARTIAL | `SY-X-15` en `in625-syntax-native.spec.ts` prueba que `\text{<script>alert(1)</script>}` queda inerte/no se convierte en HTML; backend `test_syx15_original_script_text_rejection_and_http_recovery` pasó en el job acumulativo actual. | Confirmar corrida Playwright de este SHA y cotejar el vector original; no equivaler automáticamente una fixture SY-X a la fila H2 original. |
| EN-SG-02 | GAP | No se encontró caso equivalente de imagen con evento `onerror` en los archivos inspeccionados. | Recuperar vector fuente y crear E2E con sonda positiva/negativa que demuestre que el evento no se ejecuta. |
| EN-SG-03 | PARTIAL | Misma evidencia nativa `SY-X-15` cubre texto matemático con HTML y su representación inerte. | Confirmar Playwright actual y cotejar criterio de render literal en la matriz primaria. |
| EN-SG-04 | GAP | No se localizó prueba concreta de hipervínculo LaTeX inseguro que demuestre ausencia de enlace ejecutable. | Recuperar vector canónico y agregar prueba frontend de que no se genera navegación/enlace activo. |
| EN-SG-05 | GAP | No se encontró una prueba dedicada a macros de URL, imagen y HTML conjuntamente. | Recuperar vectores y cubrir rechazo visible por familia de macro, sin abrir recursos. |
| EN-SG-06 | GAP | No se encontró caso dedicado de definición recursiva de macro. | Recuperar vector primario y verificar error claro, sin bloqueo ni resultado tardío. |
| EN-SG-07 | GAP | No se encontró caso dedicado para macros/alias/catcode nuevos. | Recuperar vectores primarios antes de crear fixtures. |
| EN-SG-08 | PARTIAL | `SY-X-16` y `SY-X-17` prueban `\input{/etc/passwd}` sin acceso a archivo y `\write18{ls}` sin lanzamiento de proceso; los tests backend HTTP correspondientes pasaron en el job actual. | El solapamiento cubre las rutas principales de archivo/shell, pero cotejar las formas literales H2 originales y completar browser evidence del SHA actual. |
| EN-SG-09 | PASS | `test_in625_h2_rejects_python_constructs_without_evaluation[EN-SG-09-...]`; job `121753424481`, run `40374409722`, SUCCESS, SHA `f2a8f987...`. | PASS scoped a la entrada explícita y al endpoint probado. |
| EN-SG-10 | PASS | Prueba etiquetada EN-SG-10 de lectura de archivo; mismo job/run/SHA actual, SUCCESS. | Mantener el test de ausencia de evaluación y no divulgar datos del archivo. |
| EN-SG-11 | PASS | Prueba etiquetada de introspección de clases; mismo job/run/SHA actual, SUCCESS. | Sin ampliar payloads fuera de la matriz. |
| EN-SG-12 | PASS | Prueba etiquetada de lambda; mismo job/run/SHA actual, SUCCESS. | Sin cambio. |
| EN-SG-13 | PASS | Casos etiquetados `exec` y `eval`; mismo job/run/SHA actual, SUCCESS. | Ambas variantes explícitas. |
| EN-SG-14 | PASS | Casos etiquetados `import os` y `os.system`; mismo job/run/SHA actual, SUCCESS. | Sin cambio. |
| EN-SG-15 | PASS | Casos etiquetados `x.__class__` y `x.__dict__`; mismo job/run/SHA actual, SUCCESS. | Sin cambio. |
| EN-SG-16 | PASS | Casos etiquetados `Symbol`, `Integer` y `Function`; mismo job/run/SHA actual, SUCCESS. | Sin cambio. |
| EN-SG-17 | PASS | `test_in625_h2_sg17_assignment_does_not_leak_between_evaluations`; mismo job/run/SHA actual, SUCCESS. | Evidencia backend, dos solicitudes. |
| EN-SG-18 | PASS | Casos etiquetados de palabras reservadas y pruebas de reentrada; mismo job/run/SHA actual, SUCCESS. | Evidencia backend; los tests verifican que no se corrompen cálculos posteriores. |
| EN-SG-19 | PASS | Caso etiquetado de 50 paréntesis devuelve 1; mismo job/run/SHA actual, SUCCESS. | No confundirlo con el caso de 1000 paréntesis. |
| EN-SG-20 | PARTIAL | Caso etiquetado de 1000 paréntesis obtiene 422 `VALIDATION_ERROR` porque excede `EvaluateRequest.max_length=500`; mismo job/run/SHA actual, SUCCESS. | Demuestra rechazo temprano seguro, **no** una guarda interna de profundidad. Hace falta reconciliar el criterio de 1000 paréntesis con el límite público de 500 caracteres. |
| EN-SG-21 | GAP | No se halló prueba de suma de 10 000 términos. SY-X-04 cubre 500 sumandos/rechazo de límite, no 10 000 términos. | Contradicción contractual a resolver: `EvaluateRequest.expression` limita a 500 caracteres, mientras el criterio pide 10 000 términos y resultado en menos de 2 s. No relajar el límite ni inventar otra ruta sin consultar la fuente primaria/decisión del contrato. |
| EN-SG-22 | PASS | `test_in625_h2_oversized_expression_rejected_at_request_boundary` prueba 100 000 caracteres rechazados con 422 `VALIDATION_ERROR`; mismo job/run/SHA actual, SUCCESS. | Cumple la alternativa de rechazo controlado de la fila abreviada. |
| EN-SG-23 | PASS | `SY-X-10` en test HTTP nativo envía la potencia `10^(10^10)` y acepta rechazo `COMPLEXITY_LIMIT`; el test `test_syx10_canonical_nested_integer_power_preflight_and_finite_control` pasó en el job acumulativo actual, misma SHA del PR. | Equivalencia de entrada/criterio confirmada; no repetir el test solo para agregar etiqueta EN-SG. |
| EN-SG-24 | PASS | `SY-X-11` y `test_syx11_original_guard_and_finite_nested_power` ejercitan `9^(9^9)` y rechazo `COMPLEXITY_LIMIT`; mismo job/run/SHA actual, SUCCESS. | Equivalencia de entrada/criterio confirmada. |
| EN-SG-25 | GAP | No se encontró un test de `1000000!` que pruebe límite/timeout/cancelación controlada. | No ejecutar la expresión sin aislamiento. Diseñar test de CI usando aislamiento SG28 y presupuesto CPU, con recuperación posterior; no usar el endpoint desplegado. |
| EN-SG-26 | PARTIAL | `backend/tests/test_algebra.py::test_expand_complexity_limit` prueba `(x+1)**60` en `/api/v1/expand` y espera `COMPLEXITY_LIMIT`; ese test pasó en la suite actual. | No prueba el vector `(x+1)^10000`; agregar caso específico solo en entorno de test con límite temporal y verificar que el guard actúa antes de materializar salida masiva. |
| EN-SG-27 | GAP | No se encontró la fixture de potencias anidadas de 2 de la matriz H2. SY-X-09..11 cubren otras potencias, no sustituyen el vector requerido. | Recuperar el vector literal y comprobar rechazo/límite con control pequeño de reentrada. |
| EN-SG-28 | PASS_SCOPED | Run Playwright `40374409444`, job `121753422799`, SHA `f2a8f987...`: 627 tests generales y 21 SG28 pasaron; el log muestra cancelación real de worker, navegación/cierre de pestaña y recuperación en desktop/tablet/mobile. | PASS limitado a un host y al SHA probado; SG28 distribuido sigue `OUT_OF_SCOPE_SINGLE_HOST`, no PASS. Flag de aislamiento continúa desactivada por defecto y no se habilitó en producción. |
| EN-SG-29 | PARTIAL | `test_in625_h2_sg29_twenty_concurrent_evaluations_are_isolated` pasó en run `40374409722`, job `121753424481`, SHA `f2a8f987...`. Verifica 20 cálculos, resultados y request IDs únicos. | La matriz también exige “última entrada” en UI; el test backend declara expresamente que no lo valida. Añadir un E2E de orden/resultado visible si la fila primaria lo confirma. |
| EN-SG-30 | PASS | Pruebas etiquetadas de comillas, apóstrofo, slash, NUL/CRLF/tab/nueva línea; comprueban JSON, request ID y ausencia de traceback/500. Run `40374409722`, job `121753424481`, SHA `f2a8f987...`, SUCCESS. | PASS para el contrato backend de transporte enumerado. |
| EN-SG-31 | PASS | Pruebas etiquetadas 5 MiB 413, request sin Content-Length 413, body stream pequeño válido y recuperación después de oversized. Mismo job/run/SHA actual, SUCCESS. | PASS para los casos HTTP probados. |
| EN-SG-32 | N/A_CONDITIONAL | La fuente primaria confirma que aplica solo si existe límite de frecuencia. La aplicación FastAPI revisada (`backend/app/main.py`) no configura middleware/limitador de frecuencia ni una dependencia de rate-limit a nivel de app. | No inventar un umbral ni un test de limitación. Reabrir solo si la configuración de Render/proxy acredita un rate limit externo; si existe, probar el umbral en un entorno aislado. |

## Hallazgos operativos

1. **No hay razón para relanzar el acumulativo actual:** el run `40374409722` probó exactamente el SHA `f2a8f9877d8a1b1cde9bf074abbe75b475258913`, ejecutó continuidad/CI guards y la suite backend completa terminó SUCCESS. Ese run no cierra GLOBAL ni reemplaza el run Playwright todavía pendiente.
2. **No hacer del test de 1000 paréntesis un PASS de parser-depth:** el límite de 500 caracteres rechaza la entrada antes de alcanzar el parser. Mantener `PARTIAL` hasta una decisión contractual compatible con el límite de tamaño.
3. **No ampliar el límite de expresión para satisfacer EN-SG-21 sin resolución formal:** las 10 000 sumas exceden el campo público de 500 caracteres; el test SY-X-04 de 500 sumandos confirma que este límite es deliberado.
4. **No ejecutar EN-SG-25 ni ráfagas contra producción.** Los vectores literales se recuperaron del archivo fuente completo (SHA-256 consignado arriba) y el extracto H.2 está en PR #36. Las pruebas nuevas de EN-SG-02/04/05/06/07 y EN-SG-25/26/27 están pendientes de la conclusión de CI en ese PR; no se declaran PASS por existir en el árbol.
5. **Conservación de bloqueos:** SECURITY-S25 BLOCKED; ALGEBRA229-AS-B-29 ON_HOLD; EDCX-B5 BLOCKED; SY-X-04-PLUS-HTTP BLOCKED; SG28 distribuido OUT_OF_SCOPE_SINGLE_HOST; global_certification OPEN.

## Siguiente acción única

Recuperar/versionar la fuente primaria `matriz_entrada_sintaxis_calculadora.md` (H.2) o acordar una referencia accesible; después crear tests aislados test-first solo para gaps confirmados: EN-SG-25 (factorial con límites CPU), EN-SG-26 (expansión 10 000), EN-SG-27 (vector original), EN-SG-32 (umbral exacto), EN-SG-02/04/05/06/07 (vectores UI); resolver EN-SG-21 con el propietario del contrato porque el criterio entra en conflicto con el límite de 500 caracteres. No repetir los casos 09–19, 22–24, 30–31 ya cubiertos en el SHA/run citado. Certificación global permanece OPEN.


## Actualización posterior al corte inicial — 2026-10-26 UTC

- El run de Playwright 40374409444 concluyó SUCCESS: 627 pruebas generales y 21 pruebas SG28. EN-SG-28 se marca PASS_SCOPED únicamente para un host y SHA exacto.
- La matriz primaria fue recuperada del ZIP corregido y el extracto se versionó en PR #36. La suite nueva de regresiones está en ejecución/pendiente; sus resultados se registrarán cuando los runs de ese SHA concluyan.
- EN-SG-32 se marca N/A_CONDITIONAL para el código de aplicación observado: no hay limitador de frecuencia configurado en app/main.py. Reabrir solo si la plataforma/proxy tiene una regla externa vigente.


## Actualización R317 — fallo confirmado y corrección en verificación (2026-10-26 UTC)

- El primer acumulativo de PR #36, run [40379627790](https://github.com/c2melendez/precision-lab-plus/actions/runs/40379627790), job `121772036477`, SHA `8bb1049380f285e2cdadb4d7c274759f34ea4f86`, terminó **FAIL**: 2710 passed, 1 failed, 1 skipped, 10 xfailed; cobertura 88.77%. La única falla fue `test_en_sg_26_expand_ten_thousand_power_returns_complexity_limit`, que excedió 20 s. Los casos nuevos EN-SG-21, EN-SG-25 y EN-SG-27 pasaron en ese mismo run.
- Diagnóstico respaldado por el código y el log: `expand_expression()` ejecutaba `sympy.expand(input_expr)` antes de revisar los nodos del resultado. Por eso una expresión `(x+1)**10000` materializaba una expansión demasiado costosa antes de poder devolver `COMPLEXITY_LIMIT`.
- Corrección publicada en el mismo PR como commit `ee7500cbb1152fe856cc5a8e9b5b5bb9be83612f`: `backend/app/services/algebra_service.py` ahora estima de forma conservadora el crecimiento de términos para sumas, productos y potencias enteras y rechaza la expansión excesiva antes de materializarla. Se añadió `backend/tests/test_algebra.py::test_expand_large_binomial_is_rejected_before_materialization`, que comprueba que el preflight impide llamar a `sympy.expand` para el caso de 10 000 términos.
- La prueba original de aceptación EN-SG-26 permanece activa y conserva el oráculo `COMPLEXITY_LIMIT`; no se amplió el timeout. El test existente `(x+1)**60` continúa en el camino tradicional: expande y aplica el límite de nodos al resultado.
- Los checks de la corrección exacta SHA `ee7500cbb1152fe856cc5a8e9b5b5bb9be83612f` ya se iniciaron automáticamente. Acumulativo [40381076250](https://github.com/c2melendez/precision-lab-plus/actions/runs/40381076250) y Playwright [40381076420](https://github.com/c2melendez/precision-lab-plus/actions/runs/40381076420) estaban `in_progress`; S19 [40381076498](https://github.com/c2melendez/precision-lab-plus/actions/runs/40381076498) estaba en cola. No se despacharon manualmente ni se declaran PASS hasta obtener sus conclusiones/logs exactos.
- Flujos automáticos observados en el nuevo SHA: H1a 40381076263, H1b 40381076444, H1c 40381076428, H1d 40381076364, Syntax diagnostic 40381076273, CI 40381076257, S17 40381076251, S18 40381076495, S20 40381076380, S21 40381076325, S23 40381076418, S25 40381076363, Native Syntax 40381076414 y Playwright 40381076420. Son checks propios del PR; no reemplazan la aceptación global ni requieren dispatch adicional.
- API read-only PR [#2](https://github.com/c2melendez/precision-lab-readonly-api/pull/2): el nuevo workflow `Read-only API Tests`, run [40380285802](https://github.com/c2melendez/precision-lab-readonly-api/actions/runs/40380285802), concluyó `failure`, pero GitHub devuelve el job `121774362420` sin pasos, sin `logs_url`, sin artefactos y con 404 al solicitar los logs. **Causa indeterminada**: no se afirma que pytest haya corrido ni que los tests hayan fallado. Requiere recuperar la evidencia del run por una vista autorizada si el conector sigue sin exponerla; no relanzar a ciegas.
- EN-SG-21 sigue bloqueado por incompatibilidad entre 10 000 términos y `EvaluateRequest.max_length=500`. EN-SG-32 sigue `N/A_CONDITIONAL` para el código app-level inspeccionado, sin rate limiter configurado. Certificación global OPEN; SECURITY-S25 BLOCKED; ALGEBRA229-AS-B-29 ON_HOLD; EDCX-B5 BLOCKED; SY-X-04-PLUS-HTTP BLOCKED; SG28 distribuido OUT_OF_SCOPE_SINGLE_HOST.

**Siguiente acción única:** `H2-EN-SG-TESTS-PR36-VERIFY-R317` — consultar jobs/logs de los gates ya activados en SHA `ee7500cbb1152fe856cc5a8e9b5b5bb9be83612f`, confirmar la regresión de preflight y corregir únicamente fallos reproducibles. No volver a despachar ni repetir gates por cambio de sesión.
