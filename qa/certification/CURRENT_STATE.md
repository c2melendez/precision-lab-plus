# Actualización de certificación — 2026-11-09 UTC (r477; EC-D-02 IN_PROGRESS)

## Trigonometría TRIG-EC-D-02 — IN_PROGRESS; espera de evidencia Lite

- Contrato recuperado directamente de `qa/certification/legacy_sources/ejercicios_trigonometria.md.gz`: `2\cos x-1=0,quad xin[0,2pi)` → `x=\frac{pi}{3}, rac{5pi}{3}`. La fila original tiene tres columnas (ID, ejercicio, resultado esperado); no existe una columna de nota separada y no se inventa.
- Test Plus creado: `backend/tests/test_trigonometry_ec_d02.py`; ancla la fila completa y verifica por `POST /api/v1/solve` las dos raíces exactas, intervalo y sustitución. La entrada HTTP usada es ASCII (`2*cos(x)-1=0`); esto no certifica ingesta literal LaTeX ni `/api/v1/evaluate`.
- Plus SHA técnico probado `6a150e29bba160fd4f2cff92748dee0baccb35a2`: [Cumulative 42669733996](https://github.com/c2melendez/precision-lab-plus/actions/runs/42669733996) SUCCESS; el log ejecutó los dos tests EC-D-02 y ambos PASSED. Backend: 2,925 passed, 1 skipped, 11 xfailed. [CI 42669734319](https://github.com/c2melendez/precision-lab-plus/actions/runs/42669734319) SUCCESS (jobs backend y frontend); [H1d 42669734287](https://github.com/c2melendez/precision-lab-plus/actions/runs/42669734287) SUCCESS; [Runner 42669734406](https://github.com/c2melendez/precision-lab-plus/actions/runs/42669734406) SUCCESS.
- Plus está PASS para el alcance probado, pero el caso bilateral permanece **IN_PROGRESS** hasta que Lite tenga evidencia real. No se emite PASS_SCOPED bilateral ni acta de aceptación. Baseline global permanece EC-D-01 PASS_SCOPED; certificación global **OPEN**.

**Siguiente:** no repetir los gates verdes Plus mientras no cambie el árbol. Resolver la ejecución pre-job de GitHub Actions Lite, validar el test focal Lite y después completar la aceptación bilateral con el alcance de interfaces claramente delimitado. Mantener separado EV-D-01 `/api/v1/evaluate` y EV-HI PASS_SCOPED.

---

# Actualización de certificación — 2026-11-09 UTC (r476)

## Trigonometría EC-D-01 — PASS_SCOPED bilateral (soluciones exactas en [0, 2π))

- Fila congelada: \`sin(x)=1/2\`, intervalo \`[0,2π)\`; raíces exactas esperadas \`π/6\` y \`5π/6\`. La prueba ancla el caso a la fila original de \`ejercicios_trigonometria.md.gz\`.
- Alcance: ambas raíces exactas, pertenencia al intervalo y sustitución se verifican por los dos motores. Plus ejercita \`/api/v1/solve\` con \`sin(x)-1/2=0\`; no se afirma certificación de la ingesta literal idéntica en todos los endpoints.
- Plus SHA técnico \`21a29a342034ed7b0427b62ca2fbbc67395cbca8\`; test \`backend/tests/test_trigonometry_ec_d01.py\` (anclaje del contrato + endpoint HTTP, 2/2 PASS).
- Plus CI [42662156729](https://github.com/c2melendez/precision-lab-plus/actions/runs/42662156729) SUCCESS: backend 2,923 passed, 1 skipped, 11 xfailed; frontend 150 test files, 1,055 passed, 28 TODO.
- Plus Cumulative [42662156740](https://github.com/c2melendez/precision-lab-plus/actions/runs/42662156740) SUCCESS: el log ejecutó explícitamente \`test_ec_d01_source_row_and_exact_oracle_are_frozen\` y \`test_ec_d01_http_solve_returns_both_exact_roots_in_interval\`; ambas PASSED. Backend 2,923 passed, 1 skipped, 11 xfailed; frontend 1,055 passed.
- Plus H1d [42662156790](https://github.com/c2melendez/precision-lab-plus/actions/runs/42662156790) SUCCESS (38 pruebas); Runner [42662156997](https://github.com/c2melendez/precision-lab-plus/actions/runs/42662156997) SUCCESS.
- Resultado **PASS_SCOPED** bilateral con Lite. No cambia el bloqueo separado EV-D-01 LaTeX en Plus \`/api/v1/evaluate\`; no se amplió el parser ni se certificó ese endpoint. EV-HI-01..12 sigue PASS_SCOPED. S25, SG28/H2 y DIST siguen abiertos; global **OPEN**.

**Siguiente:** EC-D-02. Recuperar su fila exacta desde el gzip congelado y fijar el contrato antes de escribir pruebas.

---

# Actualización de certificación - 2026-11-09 UTC (r475)

## Trigonometría EV-D-01 - BLOCKED en Plus

- Entrada: `\sin\left(\frac{\pi}{6}\right)` → `1/2` (matriz `ejercicios_trigonometria.md.gz`).
- Plus `/api/v1/evaluate` rechaza esa entrada LaTeX (`\left` no reconocido; `\frac{\pi}{6}` y `\pi` no interpretados). La variante ASCII `sin(pi/6)` sí pasa.
- Decisión: la ingesta LaTeX queda fuera del alcance de certificación por ahora. El parser certificado no incluye soporte LaTeX nuevo.
- Test `tests/test_trigonometry_ev_d01_matrix_latex.py`: `xfail(strict=True)` con razón BLOCKED.
- Lite: su test EV-D-01 (literal LaTeX → `1/2`) sigue en verde; el bloqueo es solo de Plus.
- Referencia: la ingesta acotada existe en `331a379` (CI verde) y puede retomarse como trabajo separado.

## Trigonometría EV-HI-01..12 - PASS_SCOPED (corregido desde PASS bilateral)

- Motivo: la auditoría de alcance no sostiene un PASS bilateral completo. Las entradas se probaron en ASCII y no se certificaron los literales LaTeX ni las formas exactas de la matriz.
- Limitación de entrada encontrada en EV-D-01: Plus `/evaluate` no acepta literales LaTeX con `\left`, `\frac` o `\pi`; por eso EV-HI tampoco certifica entrada LaTeX en Plus.
- Evidencia que se mantiene: Plus `a8ddc0ad9838c6cffb3d932950d72bdafa7d0a48` (Cumulative 42555334429 y CI 42555334439 SUCCESS; focal 4/4).
- Detalle: `TRIG_EV_HI_01_12_ACCEPTANCE_2026-11-09.md`.
- No es cierre global: S25, SG28, H2 y DIST siguen abiertos.

**Siguiente:** decidir si la ingesta LaTeX de `/evaluate` entra en un ciclo de certificación propio. Hasta entonces EV-D-01 queda BLOCKED en Plus.

---

# Actualización de certificación — 2026-11-09 UTC (r472)

## Algebra229 AS-C-23 — PASS bilateral · Sección C 23/23 (cerrada)

- Contrato congelado: N2, `valor`, `p(2)` con `p(x)=x^{3}-3x+1` → `3`; nota «Evaluar un polinomio en un punto.». Fila de la matriz legacy comprimida (blob d216dc77cb1356ef29cb8c803cbff809450e0456; 229 filas).
- Lite SHA técnico 1d404ea1343ed21507d01969b5977fe76389a4d5: Cumulative 42550854839 SUCCESS (AS-C-23 4/4, 390 test files, 2,374 passed); CI 42550854770 SUCCESS (audit 0, typecheck, unit/parity, build); H1d 42550854778 SUCCESS (22/22); Scientific UI 42550854777 SUCCESS (456/456).
- Plus SHA técnico 4efac10f268319f95d8757f424f5a44d44e77772: Cumulative 42550854786 SUCCESS (AS-C-23 4/4; backend 2,912 passed, 1 skipped, 10 xfailed; frontend 1,055 passed); CI 42550854863 SUCCESS (backend 2,912 passed; frontend 150 test files passed); H1d 42550854740 SUCCESS (38/38).
- Los guards de Cumulative/H1d/Scientific registraron skip=false y evidence_run_id vacío en ambos proyectos donde aplica; evidencia realmente ejecutada, sin REUSE. Runner fue push summary con dispatch manual omitido.
- Implementación: sin cambios de motor. `p(2)=3` exacto en ambos al primer intento test-first; verificación adicional por forma canónica y oráculos de sustitución directa/Horner.
- Aceptación: ALGEBRA229_AS_C_23_ACCEPTANCE_2026-11-08.md. Sección C: 23/23 PASS bilateral. Matriz Algebra229 completa (A, B, C).
- No es cierre global: S25/seguridad, SG28, H2 y DIST siguen abiertos. S25 permanece BLOCKED por `braces` sin parche publicado; npm audit de Plus sigue en 12/13 hallazgos.

**Siguiente:** abrir el dominio trigonometría. Recuperar y validar `qa/certification/legacy_sources/ejercicios_trigonometria.md.gz` (IDs EV-*), inventariar la evidencia EV-M/EV-T existente y su alcance, identificar el primer caso no certificado y ejecutarlo test-first bilateral. No reutilizar PASS_SCOPED fuera de su alcance declarado.

---

# Actualización de certificación — 2026-11-09 UTC (r471)

## Algebra229 AS-C-22 — PASS bilateral (cerrado)

- Contrato congelado: N2, `valor`, resto de `x^{100}-1` entre `x-1` → `0`; nota «Teorema del resto: `p(1)=0`.». Fila de la matriz legacy comprimida (blob d216dc77cb1356ef29cb8c803cbff809450e0456; 229 filas).
- Lite SHA técnico ab7a067d0cb16d59ab912444ccf0923ab10b2a7d: Cumulative 42549824064 SUCCESS (AS-C-22 4/4, 389 test files, 2,370 passed); CI 42549824060 SUCCESS (audit 0, typecheck, unit/parity, build); H1d 42549824101 SUCCESS (22/22); Scientific UI 42549824059 SUCCESS (456/456).
- Plus SHA técnico 77c64aca73130382c46da427d11a1e25d2aa17c6: Cumulative 42549824419 SUCCESS (AS-C-22 4/4; backend 2,908 passed, 1 skipped, 10 xfailed; frontend 1,055 passed); CI 42549824404 SUCCESS (backend 2,908 passed; frontend 150 test files passed); H1d 42549824409 SUCCESS (38/38).
- Los guards de Cumulative/H1d/Scientific registraron skip=false y evidence_run_id vacío en ambos proyectos donde aplica; evidencia realmente ejecutada, sin REUSE. Runner fue push summary con dispatch manual omitido.
- Implementación: sin cambios de motor. Se verificó `p(1)=0` y el cociente exacto en `x=2` (`2^100-1`). Ningún producto expone resto de división polinómica (`rem` da PARSE_ERROR en Plus); la aceptación usa el teorema del resto de la fila y la identidad geométrica exacta, sin fabricar capability.
- Aceptación: ALGEBRA229_AS_C_22_ACCEPTANCE_2026-11-08.md. Sección C: 22/23 PASS bilateral.
- No es cierre global: S25/seguridad, SG28, H2 y DIST siguen abiertos. S25 permanece BLOCKED por `braces` sin parche publicado; npm audit de Plus sigue en 12/13 hallazgos.

**Siguiente:** AS-C-23, N2, valor — `p(2)` con `p(x)=x^{3}-3x+1` → `3`. Continuar test-first bilateral, sin modificar producto hasta observar el resultado.

---

# Actualización de certificación — 2026-11-08 UTC (r470)

## Algebra229 AS-C-21 — PASS bilateral (cerrado)

- Contrato congelado: N1, `valor`, `\operatorname{lcm}(48,180)` → `720`; nota vacía. Fila extraída de la matriz legacy comprimida (blob d216dc77cb1356ef29cb8c803cbff809450e0456; 229 filas).
- Lite SHA técnico e3987a2536ae7d3a78f104b572b3e445eeccd89f: Cumulative 42515359869 SUCCESS (AS-C-21 3/3, 388 test files); CI 42515359905 SUCCESS (audit 0, typecheck, unit/parity, build); H1d 42515359842 SUCCESS (22/22); Scientific UI 42515359846 SUCCESS (456/456).
- Plus SHA técnico 2724b464f63778cfebf71329748714dccf407cd0: Cumulative 42515399590 SUCCESS (AS-C-21 4/4; backend 2,904 passed, 1 skipped, 10 xfailed; frontend 1,055 passed); CI 42515399583 SUCCESS (backend 2,904 passed, 1 skipped, 10 xfailed; frontend 150 test files passed); H1d 42515399592 SUCCESS (38/38).
- Los guards de Cumulative/H1d/Scientific registraron skip=false y evidence_run_id vacío en ambos proyectos donde aplica; evidencia realmente ejecutada, sin REUSE. Runner fue push summary con dispatch manual omitido.
- Implementación: no fue necesario modificar ningún motor; `lcm(48,180)` devolvió 720 en ambos al primer intento test-first, sin commits de corrección de harness.
- Aceptación: ALGEBRA229_AS_C_21_ACCEPTANCE_2026-11-08.md. Sección C: 21/23 PASS bilateral.
- No es cierre global: S25/seguridad, SG28, H2 y DIST siguen abiertos. npm audit de Plus sigue reportando 12 vulnerabilidades (2 low, 10 moderate) y 13 (2 low, 11 moderate), pendiente de revisión S25.

**Siguiente:** AS-C-22, N2, valor — resto de `x^{100}-1` entre `x-1` → `0` (teorema del resto: `p(1)=0`). Continuar test-first bilateral, sin modificar producto hasta observar el resultado.

---

# Actualización de certificación — 2026-11-08 UTC (r469)

## Algebra229 AS-C-20 — PASS bilateral (cerrado)

- Contrato congelado: N1, valor, gcd(48,180) → 12; nota de la fila vacía. Fila extraída de la matriz legacy comprimida (blob d216dc77cb1356ef29cb8c803cbff809450e0456; 229 filas).
- Lite SHA técnico e43c028d0ef8b96b7d2d743c41a6053941c34624: Cumulative 42514437202 SUCCESS (AS-C-20 3/3, 387 test files); CI 42514437070 SUCCESS (audit 0, typecheck, unit/parity, build); H1d 42514437057 SUCCESS (22/22); Scientific UI 42514437060 SUCCESS (456/456).
- Plus SHA técnico 5ff8bd3e61c2c052091f4adb993033f19959c27c: Cumulative 42514461767 SUCCESS (AS-C-20 4/4; backend 2,900 passed, 1 skipped, 10 xfailed); CI 42514461597 SUCCESS (backend 2,900 passed, 1 skipped, 10 xfailed; frontend 150 test files passed); H1d 42514461658 SUCCESS (38/38).
- Los guards de Cumulative/H1d/Scientific registraron skip=false y evidence_run_id vacío en ambos proyectos donde aplica; evidencia realmente ejecutada, sin REUSE. Runner fue push summary con dispatch manual omitido.
- Implementación: no fue necesario modificar ningún motor; la prueba del GCD entero dio 12 en ambos. Los commits iniciales de test tuvieron un error de escape del separador de filas; se corrigió el harness y solo los SHA finales anteriores sustentan la aceptación.
- Aceptación: ALGEBRA229_AS_C_20_ACCEPTANCE_2026-11-08.md. Sección C: 20/23 PASS bilateral.
- No es cierre global: S25/seguridad, SG28, H2 y DIST siguen abiertos. npm audit de Plus sigue reportando 12 vulnerabilidades (2 low, 10 moderate) y 13 (2 low, 11 moderate) en los pasos correspondientes, pendiente de revisión S25.

**Siguiente:** AS-C-21, N1, valor — lcm(48,180) → 720. Continuar test-first bilateral, sin modificar producto hasta observar el resultado.

---

# Actualización de certificación — 2026-11-08 UTC (r468)

## Algebra229 AS-C-19 — PASS bilateral (cerrado)

- Contrato N2: valor, gcd(12*x^2*y, 18*x*y^2) → 6*x*y.
- Lite SHA técnico ee251a95f7cd5012623a183edda9507274a4e5b4: Cumulative 42512905625, CI 42512905597, H1d 42512905598, Scientific UI 42512905608 — todos SUCCESS. Cumulative ejecutó AS-C-19 3/3.
- Plus SHA técnico 78103b975569799afade2c6c540cc45930bbcdc0: Cumulative 42510750283, CI 42510750258, H1d 42510750377 — todos SUCCESS. Cumulative ejecutó AS-C-19 5/5.
- AS-C-18 también queda cerrado bilateralmente: Lite 4/4 y Plus 5/5, en los mismos acumulativos. Restauración y regla exacta LCM de Lite quedan documentadas en ALGEBRA229_AS_C_18_ACCEPTANCE_2026-11-08.md.
- Aceptación bilateral: ALGEBRA229_AS_C_19_ACCEPTANCE_2026-11-08.md. Sección C: 19/23 PASS bilateral.
- Los guards del acumulativo Lite y Plus registran skip=false y evidence_run_id vacío; los tests focales se ejecutaron realmente, no por REUSE. H1d y Scientific UI de Lite también se ejecutaron realmente y terminaron SUCCESS.
- No se declara PASS global: S25/seguridad, SG28, H2 y DIST siguen abiertos. Los informes npm audit de Plus (12 vulnerabilidades en CI y 13 en H1d) permanecen bajo revisión S25.

**Siguiente:** recuperar/verificar desde la fuente comprimida congelada la fila AS-C-20 y su contrato íntegro antes de escribir pruebas test-first. El contenido exacto no está disponible en texto plano en el árbol actual; no inferir input ni expected.

---

# Actualización de certificación — 2026-11-08 UTC (r467)

## Algebra229 AS-C-19 — PASS Plus / Lite BLOCKED

- Contrato N2: `valor` `\gcd\left(12x^{2}y,\ 18xy^{2}\right)` → `6 x y`.
- **Plus** SHA `78103b975569799afade2c6c540cc45930bbcdc0`: Cumulative 42510750283, CI 42510750258, H1d 42510750377, Runner 42510750319 — todos SUCCESS.
- **Lite BLOCKER:** `src/engine/algebriteClient.ts` corrupto (marcador de emergencia desde commits de restore fallidos). CI Lite en rojo. Test-first AS-C-19 publicado (`bf7b361`) pero no verificable.
- **AS-C-18:** Plus PASS; Lite pendiente de restore + regla acotada `lcm` (Algebrite hang).
- Restauración requerida: ver `qa/certification/RESTORE_ALGEBRITE_CLIENT.md` en Lite; copia válida en `artifacts/algebriteClient_RESTORE.ts` del ejecutor (incluye AS-C-18).
- Baseline bilateral AS-C-18/AS-C-19: **pendiente**. Sección C efectiva bilateral: **17/23** (última cerrada AS-C-17).
- Global **OPEN**; S25, SG28, H2 y DIST siguen abiertos.
- **Siguiente:** restaurar motor Lite → verificar AS-C-18/19 bilateral → AS-C-20.

---

# Actualización de certificación — 2026-11-08 UTC (r466)

## Algebra229 AS-C-17 — PASS bilateral (cerrado)

- Sección C en 17/23. **Siguiente (en ese momento):** AS-C-18.

---

# Historial previo

Ver commits documentales para AS-C-01..AS-C-16, sección B y frentes S25/SG28/H2/DIST. Estado operativo vigente: bloque r467.
