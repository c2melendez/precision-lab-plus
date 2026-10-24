## 2026-10-24 UTC — r291: revalidación automática posterior a documentación

- Tras commits de documentación, PR #29 disparó nuevamente workflows en SHA `91ab2cfaf5a85f4c5a504a078eae361be702b16b`; no fue una campaña focalizada del plan r290.
- S19 run [40086398270](https://github.com/c2melendez/precision-lab-plus/actions/runs/40086398270): workflow SUCCESS; backend mutmut job `120859802944` y artefacto ID `12559771024`. Resumen final: 3,280 mutantes, 971 killed, 2,136 survived, 159 no tests, 14 timeout; score killed 29.60%. Resultado sin mejora frente a run 40069907892; no contar como ejecución de tests dirigidos r290.
- CI run [40086398092](https://github.com/c2melendez/precision-lab-plus/actions/runs/40086398092): SUCCESS (backend/frontend); S25, S17, S20, S21, S23, Playwright E2E, integridad Algebra 229 y gate acumulativo figuran SUCCESS en SHA actual.
- S18 run [40086398104](https://github.com/c2melendez/precision-lab-plus/actions/runs/40086398104): CANCELLED en el paso differential/property; no PASS, mantener bloqueo de infraestructura y no reintentar sin causa de estabilidad.
- No se implementaron los tests del plan r290 ni se cambió código de producto. S19 backend sigue BLOCKED por score/inventario; PR #29 sigue abierto y draft; certificación global OPEN.
- Siguiente paso: revisar/aceptar los casos P0 del plan r290 contra contratos G3/Algebra 229 y añadir pruebas dirigidas antes de la próxima mutación. Para evitar repetición, no volver a disparar el workflow completo con commits solo documentales si puede evitarse; no declarar PASS por workflow SUCCESS.

---

## 2026-10-24 UTC — r290: plan focalizado de pruebas S19 backend

- Se creó `S19_BACKEND_TARGETED_TEST_PLAN_R290.md` (commit `d526cd099a8e5fae3b46a72e812f611e4200ab2a`) con prioridades basadas en el log mutmut por función.
- P0: `_absolute_value_cases_result` (172 survived), `_radical_cases_result` (185 survived), `_rational_domain_result` (143 survived), `_absolute_value_steps` (112 survived), `_absolute_value_equidistance_steps` (105 survived), `validate_g3_structure` (246 survived), `_evaluate_impl` (228 survived); además funciones con no tests como `parse_inequality_tree` (52), `parse_chained_inequalities` (24), `_domain_step` (28) y `_real_radical_value` (12).
- Verificado: los tests seleccionados actuales no nombran explícitamente varias de estas funciones; SG28 slow path queda bloqueado hasta aprobación contractual.
- Plan: revisión de casos y contratos, tests unitarios focalizados, luego una sola corrida mutacional focalizada. No se lanzaron Actions ni se modificó producto.
- S19 backend BLOCKED; SG28 REVIEW_REQUIRED; global OPEN; PR #29 abierto.

---

## 2026-10-24 UTC — r289: discrepancia de alcance S19 backend

- El baseline normativo `qa/s19/BASELINE_MUTATION.md` fija como operativo 1,028 mutantes (590 killed, 371 survived, 58 no tests, 9 timeout; score killed 57.39%). El log final del run actual 40069907892 registra 971 killed, 2,136 survived, 159 no tests y 14 timeout; total 3,280, score killed 29.60% con la misma convención. El archivo `mutmut-results.txt` lista solo estados no-killed; el resumen final del log es necesario para reconstruir el total.
- El inventario creció de 1,028 a 3,280 (+2,252); el score reportado bajó de 57.39% a 29.60% (-27.79 pp). Debe analizarse la expansión del código y de los mutantes por módulo antes de atribuirlo a regresión de tests. Se documentó en `S19_BACKEND_MUTATION_SCOPE_DRIFT_R289.md` (actualización posterior aa38a869be574bf405fdee3169fff00aeee0787d) y se corrigió la interpretación inicial de mutmut results.
- Artefacto baseline recuperado y resumen completo del log comparado. La expansión se concentra en solve_service (+1,071 mutantes; 6→16 funciones), parsing (+717; 19→24 funciones), evaluate (+437; 3→7 funciones) y ast_validator (+27). El score bajó en todos los módulos; la deuda más grande está en solve_service/evaluate. Siguiente paso: revisión de pruebas dirigidas para las funciones nuevas y sobrevivientes de esas superficies, sin ejecutar S19 completo. No repetir S19 completo ni cambiar producto.
- S19 backend sigue BLOCKED; SG28 REVIEW_REQUIRED, S18 CANCELLED por infraestructura, PR #29 abierto, certificación global OPEN. Sin nuevas Actions.

---

## 2026-10-24 UTC — r288: revisión del artefacto S19 backend mutmut

- Revisado artefacto `s19-plus-backend-mutmut` ID `12551670346` del run [40069907892](https://github.com/c2melendez/precision-lab-plus/actions/runs/40069907892), SHA `6e6a59ee556cf6bba60a40010ec707f05a01ca52`.
- Corrección de interpretación: `mutmut-results.txt` lista 2,309 estados no-killed (2,136 survived, 159 no tests, 14 timeout), no el total de la campaña. El resumen final del log confirma 971 killed y 3,280 total; score 29.60%. `mutmut-exit-code.txt` = 0 no equivale a aceptación. El artefacto fuente confirma 14 timeout.
- Nuevo informe `S19_BACKEND_MUTATION_REVIEW_R288.md`: S19 backend acceptance BLOCKED porque no hay kills ni criterio/umbral aprobado. No repetir la corrida hasta versionar el contrato de score/denominador, timeout/no-tests, equivalentes y exclusiones.
- Sin cambios de producto ni Actions nuevas. SG28 REVIEW_REQUIRED, S18 CANCELLED por infraestructura, global OPEN; PR #29 abierto.

---

## 2026-10-24 UTC — r287 addendum: revisión de contrato SG28

- Añadido `SG28_CONTRACT_REVIEW_R287.md` (commit `7c6392336039f8e654acb94dc0f75cc6f0818412`).
- Contraste con `SG28_INTEGRATION_EXIT_CRITERIA.md`: el borrador menciona los seis requisitos, pero no define decisiones implementables para presupuesto total, ACK perdido/renewal, reloj/reinicio, fencing del hijo, tabla HTTP/MathResponse ni topología de aceptación.
- Decisión: no cablear endpoint, no activar flags y no repetir suites por documentación. H2-SG28-DIST-01..08 y SY-X-04-PLUS-HTTP continúan BLOCKED; global OPEN; PR #29 abierto.
- Siguiente acción: revisión explícita del responsable backend/infraestructura sobre la matriz de brechas antes de versionar contrato aprobado.

---

## 2026-10-24 UTC — r287: SG28 lease/fencing contract proposed; S18 classified as infrastructure cancellation

- Reconciled Plus PR-head evidence at `6e6a59ee556cf6bba60a40010ec707f05a01ca52`: CI 40069907974, cumulative 40069907843, Playwright 40069907922 and H1a/H1b/H1c/H1d/S17/S20/S21/S23/S25/Syntax diagnostic SUCCESS.
- S19 40069907892 SUCCESS. Backend Plus, frontend Lite and frontend Plus mutation jobs completed SUCCESS and uploaded reports; score/acceptance still requires reviewing the artifacts against thresholds.
- S18 40069907881 was cancelled when the runner received a shutdown signal during the differential/property step; 40069346239 was cancelled similarly. Classify as infrastructure/cancelled, not product failure and not PASS.
- Added `SG28_LOGICAL_REQUEST_LEASE_CONTRACT_PROPOSAL_v1.md`, explicitly `PROPOSED / REVIEW_REQUIRED`, covering total logical-request budget, lease renewal, authoritative clock, fail-closed behavior, execution fencing, HTTP/MathResponse and distributed topology criteria.
- No production flag activated, no HTTP integration wired, no PR merged. DIST remains BLOCKED pending review and independent-host evidence.

## 2026-10-24 UTC — r286: contrato MathResponse off/on corregido; sg28-prototype PASS, cierre global pendiente

- HEAD técnico `c6df370fd3c5779a56bc29317968b26ea046d4bf`; rama `qa/syntax-audit-in625-a1`; PR #29 continúa abierto y no se mergea.
- El test-first en `492e3ed3`, run [40069155348](https://github.com/c2melendez/precision-lab-plus/actions/runs/40069155348), falló en dos comparaciones y permitió aislar la causa: el modo aislado añadía `ParseSecurityError:` al mensaje `PARSE_ERROR`, y el snapshot de HTTP 422 incluía un `duration_ms` no determinista.
- Corregido en `backend/app/routers/evaluate.py` y `backend/tests/test_in625_sg28_loopback_http.py` en `c6df370fd3c5779a56bc29317968b26ea046d4bf`. Se compara el esquema público completo de MathResponse, igualdad semántica off/on para resultados numéricos/simbólicos y errores de parse/dominio/sustitución, y el cuerpo estable de HTTP 422 (se excluyen solo request_id y duration_ms).
- SG28 prototype [40069343572](https://github.com/c2melendez/precision-lab-plus/actions/runs/40069343572) SUCCESS exacto-en-HEAD: 70 passed, 1 warning. S25 [40069346241](https://github.com/c2melendez/precision-lab-plus/actions/runs/40069346241) SUCCESS exacto-en-HEAD.
- Acumulativo [40069346201](https://github.com/c2melendez/precision-lab-plus/actions/runs/40069346201), CI [40069346209](https://github.com/c2melendez/precision-lab-plus/actions/runs/40069346209) y H1d [40069346229](https://github.com/c2melendez/precision-lab-plus/actions/runs/40069346229) seguían IN_PROGRESS al reconciliar; no se duplican.
- Tras esos gates, siguiente paso documentado: contrato versionado para vigencia de solicitud lógica, presupuesto total, lease/renewal, comportamiento fail-closed, autoridad de reloj, recuperación, fencing aplicado al worker efectivo y mapeo de error HTTP/MathResponse, según `SG28_INTEGRATION_EXIT_CRITERIA.md`. Prepararlo como PROPOSED/REVIEW_REQUIRED, sin afirmar aprobación.
- Global OPEN. H2-SG28-DIST-01..08 y SECURITY-S25 siguen BLOCKED; loopback de un host no constituye evidencia distribuida. No activar en producción ni mergear PR #29.

---

## 2026-10-24 UTC — r284: alineación de harness SG28 en Playwright (sin cierre)

- Evidencia previa exacta en `0325fa77`: Playwright [40047564113](https://github.com/c2melendez/precision-lab-plus/actions/runs/40047564113) FAILURE, 11+1 en `in625-h2-sg28-cancel.spec.ts` por `SG28_CI_EVENT_FILE` ausente y timeouts de «Detener cálculo» con aislamiento off. Clasificación harness.
- S18 [40047563967](https://github.com/c2melendez/precision-lab-plus/actions/runs/40047563967) FAILURE por shutdown del runner, no por diff matemático. [40045973724](https://github.com/c2melendez/precision-lab-plus/actions/runs/40045973724) cancelled. Infraestructura; sin relanzamiento manual.
- S25 [40047564057](https://github.com/c2melendez/precision-lab-plus/actions/runs/40047564057) SUCCESS en ese HEAD. SECURITY-S25 permanece BLOCKED.
- Cambio: `.github/workflows/playwright.yml` en `83b18dab5a176087d9f228725a2140c535d07a2f`. Fase general sin flags SG28; fase SG28 con el env del workflow dedicado y `workers=1`.
- Run automático en curso, no es PASS: [40065789096](https://github.com/c2melendez/precision-lab-plus/actions/runs/40065789096). Decisión WAIT.
- H2-SG28-DIST BLOCKED. Global OPEN. No merge de PR #29.

---

## 2026-10-24 UTC — r285: run SG28 en 83b18dab verificado (harness PASS_SCOPED; DIST sigue BLOCKED)

- Plus Playwright E2E [40065789096] SUCCESS @ `83b18dab`, job 120788643371, intento 1.
- General sin SG28: 627 passed. EN-SG-28 con SG28 aislado: 21 passed (7 x desktop/tablet/movil). `general_exit=0 sg28_exit=0`.
- Fallo previo 40047564113 clasificado como harness; corregido en 83b18dab.
- No cierra H2-SG28-DIST-01..08 ni S25. Lite sin cambios en este commit.
- Hallazgo: `playwright.yml` no dispara push en la rama canonica (pendiente cambio tecnico).
- Siguiente: brecha 4 del contrato SG28 (MathResponse y status HTTP).

---

## 2026-10-23 UTC — r264: registro gates r263 — Plus success

- r264: gates r263 Plus en success: cumulative 40014981162, H1d 40014985059, Native Syntax 40014988262 sobre 177955dc.
- Plus/Lite B4 mantienen la clasificación de r263; no se toca producto.
- Siguiente: EDCX-B5 READY, no iniciado.

---

## 2026-10-23 UTC — r266: EDCX-B5 brecha de capacidad (Plus)

- Filas VC-LG-01..25 (lugares geométricos) con `canal` vacío. Ninguna ruta de Plus devuelve un lugar geométrico (revisión de `/evaluate`, `/solve`, `/complex/*`, `/graph/*`).
- Resultado: 25 BLOCKED por capacidad; sin PASS/FAIL; sin cambio de producto ni de oráculo. Lite NO_EJECUTADO.
- Gates: sin CI (solo documentación). Global OPEN.
- Siguiente: EDCX-B6 (53 filas, VC-FE), REVIEW por canal vacío.


## 2026-10-23 UTC — r263: EDCX B4 (Plus scoped)

- Plus `7e501f5` (test-first): cumulative [40014004350] SUCCESS; H1d [40014004348] SUCCESS. Harness local 33 passed, 4 xfailed.
- B4: 34 filas -> 14 PASS / 14 PASS_SCOPED / 4 FAIL / 2 BLOCKED, medidas con oraculo sympy independiente sobre `/api/v1/solve` y `/api/v1/solve/system`.
- FAIL (xfail estricto, sin cambio de producto): VC-EC-16, 17, 18, 19 (raices faltantes, o vacio con solucion existente).
- BLOCKED: VC-EC-20, 21 (`abs(z)` no soportado).
- Lite: B4 sin ejecutar (`NO_EJECUTADO`).
- Siguiente: EDCX-B5 (25 filas, prefijo VC-LG), READY, no iniciado.

---

## 2026-10-23 UTC — r262: EDCX B3 (Plus scoped)

- Plus `ab220425` (B3): cumulative [39945613218] SUCCESS — 2345 passed, 1 skipped,
  6 xfailed, cobertura 87.92%; H1d [39945613228] SUCCESS. Harness B3 22/22.
- B3: 19 filas -> 7 PASS exactos + 10 PASS_SCOPED / 2 BLOCKED. `evaluate`
  resuelve potencias exactas; `sqrt`/`root` devuelven solo la raíz principal
  (`sqrt(-3+4i)=1+2i`, `8^(1/3)=2`, `1^(1/4)=1`).
- PASS_SCOPED: `PR-07..PR-16`; la enumeración completa se certifica con
  `/api/v1/solve` sobre `z^n=w`, que devuelve todas las raíces exactas. `PR-07`
  devuelve `±sqrt(I)` (equivalente a `±(1+i)/sqrt(2)`); `PR-15/PR-16` emiten
  radicales cartesianos en lugar de la forma exponencial.
- BLOCKED: `PR-17` (sin nodo de sumatoria; `sum`/`Sum` -> `PARSE_ERROR`) y
  `PR-18` (sin operación de producto de raíces).
- Hallazgo: `(-8)^(1/3)=2*(-1)**(1/3)` es la rama principal compleja, no `-2`.
- Acumulado EDCX (A + B1 + B2 + B3): 319 / 638 filas, 188 PASS / 131 BLOCKED.
- Lite: EDCX sin ejecutar (`NO_EJECUTADO`); sin PASS/FAIL bilateral.
- Siguiente: EDCX Parte B, bloque B4 (ecuaciones en C, 34 filas, `VC-EC-01..34`).

---

## 2026-10-23 UTC — r261: EDCX B2 (Plus scoped)

- Plus `7c87b95f` (B2): cumulative [39943293295] SUCCESS — 2323 passed, 1 skipped,
  6 xfailed, cobertura 87.96%; H1d [39943293116] SUCCESS. Harness B2 38/38.
- B2: 41 filas -> 20 PASS exactos + 13 PASS_SCOPED + 8 BLOCKED. Forma binómica
  literal, incluida la multiplicación implícita (`(2+3i)(1-i)=5+i`); las nueve
  entradas `r_{theta}` siguen dando `PARSE_ERROR`.
- PASS_SCOPED: `P-01..P-09` exigen la traducción documentada y emiten forma
  binómica/raíz; `T-05` devuelve `exp(I*(alpha+beta))` (Euler exacto); `X-04`
  devuelve la potencia principal `32*(-1)**(5/6) = -16*sqrt(3)+16i`; `X-08`
  conserva `conjugate(theta)` (exacto con `theta,r` reales); `X-09` devuelve
  `exp(re(a)-im(b))` (exacto con `a,b` reales).
- BLOCKED: `T-04/X-10` devuelven `exp(I*theta)**n` sin combinar; `T-06/T-07/T-08`
  no expanden ángulo múltiple ni linealizan; `T-09` no tiene nodo de sumatoria
  (`sum`/`Sum` -> `PARSE_ERROR`); `X-11/X-12` no reescriben media ángulo ni serie
  geométrica.
- Hallazgo: `cos3theta` se interpreta como símbolo libre, no como `cos(3*theta)`.
- Acumulado EDCX (A + B1 + B2): 300 / 638 filas, 171 PASS / 129 BLOCKED.
- Lite: EDCX sin ejecutar (`NO_EJECUTADO`); sin PASS/FAIL bilateral.
- Siguiente: EDCX Parte B, bloque B3 (potencias y raíces, 19 filas, `VC-PR-01..19`).

---

## 2026-10-23 UTC — r260: EDCX B1 (Plus scoped)

- Plus `a53449db` (B1): cumulative [39940618566] SUCCESS — 2285 passed, 1 skipped,
  6 xfailed, cobertura 87.94%; H1d [39940618559] SUCCESS. Harness B1 61/61.
- B1: 49 filas -> 45 PASS_SCOPED + 4 BLOCKED. No hay notación polar de entrada
  (`2_{pi/3}` -> `PARSE_ERROR`; `2 angle pi/3` -> `2*pi*angle/3`) ni de salida
  (`topolar(3)=3`, `topolar(-2)=-2`, `topolar(1+i)=(-1)**(1/4)*sqrt(2)`).
  La conversión se certifica con `abs`+`arg` y oráculo sympy que reconstruye
  `r*exp(i*theta)=z`, `r*cos(theta)+i*r*sin(theta)=z` y `re+i*im=z`; las 10
  filas P usan la traducción documentada `r_theta -> r*(cos+i*sin)`.
- BLOCKED: `B-17` (`arg(0)=0` sin aviso frente a `topolar(0)=DOMAIN_ERROR`) y
  `T-09/T-10/X-12` (formas semángulo simbólicas sin reducir).
- Hallazgo: `arg(exp(i*pi))` exacto `pi` y aproximado `-3.14159`; `log` base 10
  frente a `ln` natural (`X-10` usa `ln`, como la fuente).
- Acumulado EDCX (A + B1): 259 / 638 filas, 138 PASS / 121 BLOCKED.
- Lite: EDCX sin ejecutar (`NO_EJECUTADO`); sin PASS/FAIL bilateral.
- Siguiente: EDCX Parte B, bloque B2 (operaciones, 41 filas).

---

## 2026-10-23 UTC — r259: EDCX A8 y cierre de la Parte A (Plus)

- Plus `c3d38972` (A8): cumulative [39935820474] SUCCESS — 2224 passed, 1 skipped,
  6 xfailed, cobertura 87.94%; H1d [39935820754] SUCCESS. Harness A8 7/7.
- A8: 6 filas -> 0 PASS / 6 BLOCKED. `CL-01/CL-02` comparten el mismo
  `UNSUPPORTED_OPERATION` (el canal no distingue sin solución de infinitas);
  `CL-03` devuelve una integral implícita sin ramas; `CL-04` evalúa `1/(1-x)` en
  `x=2` como `-1` sin error de intervalo; `CL-05` devuelve solo `-|x|`;
  `CL-06` se rechaza por el límite de una condición inicial, no por
  incompatibilidad de frontera.
- Parte A completa (A1–A8): 210 / 638 filas, 93 PASS / 117 BLOCKED.
- Lite: EDCX sin ejecutar (`NO_EJECUTADO`); sin PASS/FAIL bilateral.
- Siguiente: EDCX Parte B, bloque B1 (conversión de formas, 49 filas).

---

## 2026-10-23 UTC — r258: EDCX A7 (Plus scoped)

- Plus `795a97ef` (A7): cumulative [39934588535] SUCCESS — 2217 passed, 1 skipped,
  6 xfailed, cobertura 87.90%; H1d [39934588487] SUCCESS. Harness A7 19/19.
- A7: 25 filas -> 2 PASS exactos (`ED-Q-23/24`: Si y erf; residuo + condición
  inicial) + 2 PASS_SCOPED (`ED-Q-05/06`: solución exacta, intervalo máximo solo
  derivado con oráculo) + 21 BLOCKED (cualitativas, no unicidad, ortogonales,
  Picard, Euler/Heun/RK4, recurrencias, retardo y Riccati sin canal).
- Acumulado EDCX A1–A7: 204 filas, 93 PASS / 111 BLOCKED.
- Lite: A7 sin ejecutar (`NO_EJECUTADO`); sin PASS/FAIL bilateral.
- Siguiente: EDCX A8 (casos límite, 6 filas).

---

## 2026-10-23 UTC — r257: EDCX A6 (Plus scoped)

- Plus `9a828f3c` (A6): cumulative [39932526897] SUCCESS — 2198 passed, 1 skipped,
  6 xfailed, cobertura 87.90%; H1d [39932526943] SUCCESS. Harness A6 30/30.
- A6: 26 filas -> 1 PASS_SCOPED (`ED-P-25`, laplaciano de `e^x sin y` compuesto
  con dos derivadas parciales reales de orden 2 y suma exacta 0) + 25 BLOCKED
  (EDP, clasificación, características, valores iniciales/frontera, Fourier y
  núcleo del calor; sin motor de EDP). `ED-P-23/24` se bloquean por el rechazo
  determinista de dos condiciones iniciales.
- Acumulado EDCX A1–A6: 179 filas, 89 PASS / 90 BLOCKED.
- Lite: A6 sin ejecutar (`NO_EJECUTADO`); sin PASS/FAIL bilateral.
- Local: 92 pruebas HTTP/seguridad sin servidor vivo fallan (0 fallos EDCX);
  el gate cumulative de CI está verde.
- Siguiente: EDCX A7 (cualitativo/numérico/retardo, 25 filas).

---

## 2026-10-23 UTC — r256: EDCX A5 (Plus scoped)

- Plus `50d9ca03` (A5): cumulative [39929466812] SUCCESS — 2168 passed, 1 skipped,
  6 xfailed, cobertura 87.85%; H1d [39929467052] SUCCESS. Harness A5 11/11.
- A5: 10 filas -> 5 PASS exactos (`ED-F-01..05`: trigonométrica, Airy, Bessel;
  residuo + wronskiano + forma cerrada de la fuente) + 3 PASS_SCOPED
  (`ED-F-06..08`: serie truncada de Legendre y polinomios de Hermite/Chebyshev
  por elección de constantes) + 2 BLOCKED (`ED-F-09..10`: clasificación de
  punto singular regular/irregular sin canal).
- Acumulado EDCX A1–A5: 153 filas, 88 PASS / 65 BLOCKED.
- Lite: A5 sin ejecutar (`NO_EJECUTADO`); sin PASS/FAIL bilateral.
- Siguiente: EDCX A6 (EDP, 26 filas).

---

## 2026-10-23 UTC — r255: EDCX A3+A4 (Plus scoped)

- Plus `6aef2571` (A3): cumulative [39926515965] SUCCESS — 2130 passed, 1 skipped,
  6 xfailed, cobertura 87.92%; H1d [39926515979] SUCCESS. Harness A3 17/17.
- Plus `02e198ac` (A4): cumulative [39927284848] SUCCESS — 2157 passed, 1 skipped,
  6 xfailed, cobertura 87.85%; H1d [39927284862] SUCCESS. Harness A4 27/27.
- A3: 16 filas -> 3 PASS_SCOPED (`ED-M-11..13`, autovalores exactos por
  `/matrix/eigen`) + 13 BLOCKED (sistemas, `expm`, no lineales/Lyapunov).
- A4: 24 filas -> 1 PASS (`ED-T-17` con `t -> x`, residuo + IC) + 23 BLOCKED
  (`laplace`/`ilaplace`, convolución, dos condiciones iniciales, integrales,
  sistema).
- Acumulado EDCX A1–A4: 143 filas, 80 PASS / 63 BLOCKED.
- Defecto confirmado: la segunda condición inicial con `;` documentada en
  `_parse_initial_condition` no está implementada; el valor `0; y'(0)=0` falla con
  `PARSE_ERROR: No se pudo interpretar la condición inicial.` No se corrige en r255.
- Lite: A3/A4 sin ejecutar (`NO_EJECUTADO`); sin PASS/FAIL bilateral.
- Siguiente: EDCX A5 (series / Frobenius, 10 filas).

---

## 2026-10-23 UTC — r254: EDCX A1+A2 PASS_SCOPED (Plus)

- Plus `fdcf2d63` (A2): cumulative [39924322798] SUCCESS — backend 2113 passed,
  1 skipped, 6 xfailed, cobertura 87.92%; H1d [39924322809] SUCCESS.
- Plus `5a76477a` (fix aislamiento ODE): cumulative [39922491068], H1d
  [39922491020], native [39922491000] SUCCESS.
- A1: 53 filas → 47 PASS (sustitución numérica), 6 BLOCKED acotados; 8 filas F4.
- A2: 50 filas → 29 PASS (25 EDO + 3 Wronskianos por determinante + ED-A-05
  renombrado), 21 BLOCKED por alcance medido.
- Regresión de `86241e40` (`mp.pool.Pool` sin importar `multiprocessing.pool`)
  detectada en H1d/security/native y corregida en `5a76477a`; no se declara PASS
  para los runs fallidos.
- Lite: A1/A2 sin ejecutar; gap de alcance del motor (`stepEngine/ode.ts`).
  No se asigna PASS ni FAIL bilateral.
- Siguiente: EDCX A3 (sistemas y exponencial matricial, 16 filas).

---

## 2026-10-23 UTC — r253: MV-J PASS_SCOPED_BILATERAL — catálogo MV completo

- Plus [39914423538] SUCCESS @ `2fcd869`.
- Lite [39914455096] SUCCESS @ `40b000b`.
- 153 filas A–H+J certificadas bilateralmente (scoped donde aplica).
- Siguiente: formalizar cierre dominio MV o retomar Stryker / otros dominios.

---

## 2026-10-23 UTC — r252: MV-H PASS_SCOPED_BILATERAL

- Plus [39913600442] / Lite [39913642080] SUCCESS.


---

## 2026-10-24 UTC — r292: S19 focalizado y conciliación de gates

- HEAD canónico: `561547252456b30124f4f7a1db06347ee0731079` (`fix(qa): match mutmut's qualified mutant names`).
- Se corrigieron filtros de mutmut para usar nombres cualificados reales; el workflow-only change se conserva en alcance focalizado.
- CI [40098526446](https://github.com/c2melendez/precision-lab-plus/actions/runs/40098526446), cumulative [40098526501](https://github.com/c2melendez/precision-lab-plus/actions/runs/40098526501), Playwright [40098526513](https://github.com/c2melendez/precision-lab-plus/actions/runs/40098526513) y S19 focalizado [40098526609](https://github.com/c2melendez/precision-lab-plus/actions/runs/40098526609): SUCCESS en el mismo SHA.
- S19 focalizado: 1,666 mutantes del alcance dirigido; 801 killed, 863 survived, 2 timeout. No sustituye la campaña histórica/global ni cierra el bloqueo de aceptación S19.
- S18 [40098526464](https://github.com/c2melendez/precision-lab-plus/actions/runs/40098526464): no PASS. El log registra shutdown signal del runner durante `python qa/s18/run_differential.py`; el paso se canceló por infraestructura, sin evidencia de fallo funcional.
- PR #29 continúa OPEN/DRAFT. Certificación global OPEN; SECURITY-S25 global BLOCKED, AS-B-29 ON_HOLD y H2-SG28-DIST-01..08 BLOCKED.
- Siguiente acción única: diagnosticar/restablecer infraestructura de S18 y ejecutar ese gate una sola vez. No repetir los gates verdes ni lanzar S19 completo. Después, revisar sobrevivientes de S19 desde el artefacto existente.

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


## 2026-10-24 UTC — r296: S18 cerrado en el SHA técnico y revisión S19 reabierta con evidencia nueva

- HEAD técnico validado: `02d01c3a1f968eab2bf5ecdb438810d55928edce`. S18 Differential Properties run [40105997558](https://github.com/c2melendez/precision-lab-plus/actions/runs/40105997558) SUCCESS en este SHA; el reporte declara `status: PASS`, seed 180018, 149 casos y 60 diferenciales numéricos. El contraejemplo de `exp(-1.3983707058413914)+(-1)*sin(-1.3983707058413914)` ya no agota el timeout de 8 s.
- CI [40105997615](https://github.com/c2melendez/precision-lab-plus/actions/runs/40105997615) SUCCESS; backend: 2,425 passed, 1 skipped, 10 xfailed; frontend también SUCCESS. Gate acumulativo [40105997679](https://github.com/c2melendez/precision-lab-plus/actions/runs/40105997679) SUCCESS; Playwright [40105997559](https://github.com/c2melendez/precision-lab-plus/actions/runs/40105997559) SUCCESS. Corridas corresponden al SHA técnico indicado.
- La corrida automática S19 [40105997583](https://github.com/c2melendez/precision-lab-plus/actions/runs/40105997583) ejecutó alcance FULL: 3,302 mutantes; 1,581 killed, 1,659 survived, 24 sin tests y 16 timeout. Score killed 47.88%, inferior al baseline histórico 57.39%; workflow SUCCESS no implica aceptación. Artefacto existente ID 12564793967, ZIP SHA-256 `20786dce29c0de88b781ae52156f85a4d33c77abd768c1ba5aaa96742cf19983`. S19 sigue BLOCKED; no volver a lanzar campaña completa.
- S25 run [40105997654](https://github.com/c2melendez/precision-lab-plus/actions/runs/40105997654) SUCCESS como ejecución, pero el bloqueo global SECURITY-S25 permanece BLOCKED hasta reconciliar advisories y criterios de salida. Algebra 229 AS-B-29 sigue ON_HOLD; SG28 H2 sigue BLOCKED; PR #29 sigue OPEN/DRAFT; certificación global OPEN.
- Siguiente acción única: revisar los sobrevivientes y categorías sin tests/timeout del artefacto S19 existente, empezando por funciones P0 del plan r290 y priorizando regresiones relevantes; usar el artefacto/log ya generado, sin repetir S19 completo. Después implementar solo tests focalizados que se justifiquen por contratos y evidencia.
