# Actualización de certificación - 2026-11-10 UTC (r490; EC-I-01 PASS_SCOPED bilateral)

## Trigonometría TRIG-EC-I-01 - PASS_SCOPED bilateral

- Fila congelada del gzip legacy (blob 3a41b0c2e0d79f2eef48e4684dc1324689d0a0fb): \(\arcsin x=\frac{\pi}{6}\) → \(x=\frac{1}{2}\). Tres columnas; sin nota separada.
- Lite SHA técnico final `5eb357d1d5e944777b2a0b392de8aab3e2de70d7`. Corrección de producto: `solveInverseSineEquation` en `src/engine/stepEngine/trigonometricEquation.ts`, enrutado desde `algebra.ts`; restringe c a [-π/2, π/2], verifica x=sin(c) en la ecuación original y acepta la forma invertida. Tests `tests/trigonometryEcI01.audit.test.ts` y `tests/trigonometryInverseSineRegression.audit.test.ts`. CI 42796690318 SUCCESS; Cumulative 42796690519 SUCCESS; H1d 42796690060 SUCCESS; Scientific UI 42796690585 SUCCESS; Runner 42796690081 SUCCESS push-only.
- Plus SHA técnico `b51612f19bab96e11c51f24644e991301a07d673`, solo prueba `backend/tests/test_trigonometry_ec_i01.py`; sin cambio de producto. Cumulative 42793636117 SUCCESS; CI 42793636114 SUCCESS; H1d 42793636399 SUCCESS; Runner 42793636120 SUCCESS push-only.
- Acta bilateral: qa/certification/TRIG_EC_I_01_ACCEPTANCE_2026-11-10.md en ambos repositorios.
- continuity.json no se modificó en esta pasada; su esquema sigue pendiente de revisión.

## Estado y siguiente acción

- Último caso aceptado: TRIG-EC-I-01 — PASS_SCOPED bilateral.
- Siguiente: TRIG-EC-I-02, sección 2.B Inversas: \(\arccos x=\frac{\pi}{3}\) → \(x=\frac{1}{2}\). Recuperar la fila exacta del gzip y escribir primero las pruebas focales en ambos repositorios.
- Certificación global: OPEN. EV-D-01 en Plus /api/v1/evaluate sigue BLOCKED; EV-HI conserva PASS_SCOPED; S25, SG28, H2 y DIST siguen abiertos.
- No repetir gates verdes de EC-D-01..10 ni de EC-I-01; no ejecutar dispatch manual.

---

# Actualización de certificación - 2026-11-10 UTC (r489; EC-D-10 PASS_SCOPED bilateral)

## Trigonometría TRIG-EC-D-10 - PASS_SCOPED bilateral

- Fila congelada del gzip legacy (blob 3a41b0c2e0d79f2eef48e4684dc1324689d0a0fb): \(\sin x=2\) → sin solución real. Tres columnas; sin nota separada.
- Lite SHA técnico `d32c724afca7159280758ed12eaf1d87baa75549`. Test `tests/trigonometryEcD10.audit.test.ts`: 2/2 PASS en Cumulative 42767488183 (log verificado). CI 42767488254 SUCCESS; H1d 42767488334 SUCCESS; Scientific UI 42767488416 SUCCESS; Runner 42767488196 SUCCESS push-only.
- Plus SHA técnico `fea4d7c6c94ce15b28954f64bfb0423b90e17982`. Tests `backend/tests/test_trigonometry_ec_d10.py`: ambos PASSED en Cumulative backend 42768654446 (log verificado). CI 42768654580 SUCCESS; H1d 42768654442 SUCCESS; Native Syntax 42768654659 SUCCESS; dependency 42768654564 SUCCESS; Runner 42768654622 SUCCESS push-only.
- Intento previo Plus `704fce9` (CI 42767510829 y Cumulative 42767510903 FAILURE) no es evidencia; corregido en `fea4d7c`, que acota el guard de dominio real a la variable `x`.
- Acta bilateral: qa/certification/TRIG_EC_D_10_ACCEPTANCE_2026-11-10.md en ambos repositorios.

## Estado y siguiente acción

- Último caso aceptado: TRIG-EC-D-10 — PASS_SCOPED bilateral. Sección 2.A Directas (EC-D-01..10) completa.
- Siguiente: TRIG-EC-I-01, sección 2.B Inversas de la batería: \(\arcsin x=\frac{\pi}{6}\) → \(x=\frac{1}{2}\). Recuperar y fijar la fila exacta del gzip (blob 3a41b0c2…) antes de escribir pruebas; no inferir el contrato por el identificador.
- Certificación global: OPEN. EV-D-01 en Plus /api/v1/evaluate sigue BLOCKED; EV-HI conserva PASS_SCOPED; S25, SG28, H2 y DIST siguen abiertos.
- No repetir gates verdes de EC-D-01..10 ni ejecutar dispatch manual.

---

# Actualización de certificación - 2026-11-10 UTC (r488; EC-D-09 PASS_SCOPED bilateral)

## Trigonometría TRIG-EC-D-09 - PASS_SCOPED bilateral

- Fila congelada del gzip legacy (blob 3a41b0c2e0d79f2eef48e4684dc1324689d0a0fb): \(\cot x=1,\quad x\in[0,2\pi)\) → \(\{\pi/4,\ 5\pi/4\}\). La fila original tiene tres columnas (ID, ejercicio y resultado esperado); no existe una nota separada.
- Oráculo: exactamente dos raíces distintas, ambas en el intervalo semiabierto y verificadas por sustitución en la ecuación cotangente original.
- Lite SHA técnico `b5cbbd727a9493c3606378a007f44350e550b3f2`. Test focal tests/trigonometryEcD09.audit.test.ts: 2/2 PASS en CI y Cumulative. CI 42765580144 SUCCESS (402 archivos, 2,414 passed, 8 expected fail, 34 TODO); Cumulative 42765579797 SUCCESS (focal 2/2; mismos totales; skip=false, evidence_run_id vacío); H1d 42765579607 SUCCESS (22/22); Scientific UI 42765579621 SUCCESS (456/456 desktop/tablet/mobile; skip=false, evidence_run_id vacío); Runner 42765579737 SUCCESS push-only.
- Plus SHA técnico `0b18ddf9f7ca0a94e905867ea83d62d88e07b656`. Test focal backend/tests/test_trigonometry_ec_d09.py: ambos tests PASSED explícitamente en Cumulative 42765602623. Backend 2,939 passed, 1 skipped, 11 xfailed; guard skip=false y evidence_run_id vacío. CI 42765601827 SUCCESS (backend y frontend 150 archivos, 1,055 passed, 28 TODO); H1d 42765602038 SUCCESS (38/38); Native Syntax 42765602152 SUCCESS (26 desktop y 52 tablet/mobile); Runner 42765601905 SUCCESS push-only.
- Lite normaliza cot(x) a cos(x)/sin(x); el helper acotado reconoce sólo esa forma, reutiliza la rama arctan(1), enumera ambas ramas en [0,2π) y verifica cada raíz en la ecuación original. Plus resuelve tan(x)=1 sobre [0,2π), exige exactamente dos raíces y las verifica en cot(x)=1. No son resolvedores generales de cotangentes.
- Acta bilateral: qa/certification/TRIG_EC_D_09_ACCEPTANCE_2026-11-10.md en ambos repositorios.

## Estado y siguiente acción

- Último caso aceptado: TRIG-EC-D-09 - PASS_SCOPED bilateral.
- Siguiente: TRIG-EC-D-10; recuperar primero la fila fuente exacta del gzip (`\sin x=2` → sin solución real) y fijar el oráculo de ausencia de soluciones reales antes de escribir pruebas.
- Certificación global: OPEN. EV-D-01 en Plus /api/v1/evaluate sigue BLOCKED; EV-HI conserva PASS_SCOPED; S25, SG28, H2 y DIST siguen abiertos.
- No repetir gates verdes de EC-D-01..09 ni ejecutar dispatch manual.

---

# Actualización de certificación — 2026-11-10 UTC (r487; EC-D-08 PASS_SCOPED bilateral)

## Trigonometría TRIG-EC-D-08 — PASS_SCOPED bilateral

- Fila congelada del gzip legacy (blob 3a41b0c2e0d79f2eef48e4684dc1324689d0a0fb): \(\sec x=-2,\quad x\in[0,2\pi)\) → \(\{2\pi/3,4\pi/3\}\). La fila original tiene tres columnas (ID, ejercicio y resultado esperado); no existe una nota separada.
- Oráculo: exactamente dos raíces distintas, ambas en el intervalo semiabierto y verificadas por sustitución en la ecuación secante original.
- Lite SHA técnico `b8c3ffcf7815c373c7f46849dc547d1cf1864de8`. Test focal tests/trigonometryEcD08.audit.test.ts: 2/2 PASS en CI y Cumulative. CI 42754588522 SUCCESS; Cumulative 42754588411 SUCCESS (401 archivos, 2,412 passed, 8 expected fail, 34 TODO; skip=false, evidence_run_id vacío); H1d 42754588566 SUCCESS (22/22); Scientific UI 42754588396 SUCCESS (456/456 desktop/tablet/mobile); Runner 42754588787 SUCCESS push-only.
- Plus SHA técnico `fb430768589eabfb930b03790d135b879ddf9109`. Test focal backend/tests/test_trigonometry_ec_d08.py: ambos tests PASSED explícitamente en Cumulative 42755121582. Backend 2,937 passed, 1 skipped, 11 xfailed; guard skip=false y evidence_run_id vacío. CI 42755121784 SUCCESS (backend y frontend); H1d 42755121628 SUCCESS (38/38); Native Syntax 42755121609 SUCCESS (26 desktop y 52 tablet/mobile); Runner 42755121603 SUCCESS push-only.
- Lite utiliza un helper acotado para la forma parser-normalizada 1/cos(x)=-2; Plus resuelve la entrada sec(x)=-2 mediante un helper que resuelve cos(x)=-1/2 directamente en [0,2π). Ambos verifican las raíces en la ecuación recíproca original. No son resolvedores generales de secante.
- Acta bilateral: qa/certification/TRIG_EC_D_08_ACCEPTANCE_2026-11-10.md en ambos repositorios.

- Seguimiento independiente al corte r487: el workflow de dependencias/seguridad Plus 42755121617 continúa IN_PROGRESS únicamente en mutation/plus-backend-mutmut; no forma parte del oráculo matemático de EC-D-08 y no cambia su PASS_SCOPED.

## Estado y siguiente acción

- Último caso aceptado: TRIG-EC-D-08 — PASS_SCOPED bilateral.
- Siguiente: TRIG-EC-D-09; recuperar primero la fila fuente exacta del gzip y fijar ecuación, intervalo y conjunto esperado antes de escribir pruebas.
- Certificación global: OPEN. EV-D-01 en Plus /api/v1/evaluate sigue BLOCKED; EV-HI conserva PASS_SCOPED; S25, SG28, H2 y DIST siguen abiertos.
- No repetir gates verdes de EC-D-01..08 ni ejecutar dispatch manual.

---

# Actualización de certificación — 2026-11-10 UTC (r486; EC-D-07 PASS_SCOPED bilateral)

## Trigonometría TRIG-EC-D-07 — PASS_SCOPED bilateral

- Fila congelada de qa/certification/legacy_sources/ejercicios_trigonometria.md.gz, blob 3a41b0c2e0d79f2eef48e4684dc1324689d0a0fb: \(\csc x=2,\ x\in[0,2\pi)\) → \(\{\pi/6,5\pi/6\}\). La fila original tiene tres columnas (ID, ejercicio, resultado esperado); no existe nota separada.
- Oráculo focal: exactamente dos raíces distintas, ambas en el intervalo semiabierto y ambas verificadas por sustitución en la ecuación recíproca original.
- Lite SHA técnico 3ad626602b3639310921ba6fd27952293732be39. Test tests/trigonometryEcD07.audit.test.ts: 2/2 PASS en CI y Cumulative. CI 42748347965 SUCCESS; Cumulative 42748348152 SUCCESS (400 archivos, 2,410 passed, 8 expected fail, 34 TODO; skip=false, sin evidencia reutilizada); H1d 42748347964 SUCCESS (22/22); Scientific UI 42748348035 SUCCESS (456/456 desktop/tablet/mobile); Runner 42748348237 SUCCESS push-only.
- Plus SHA de prueba 864c4cf68bb88e331b6df3b64a0ddb2354b047af, sin cambios de producto. Test backend/tests/test_trigonometry_ec_d07.py: 2/2 PASS explícitos en Cumulative 42748028770 SUCCESS (backend 2,935 passed, 1 skipped, 11 xfailed; frontend SUCCESS; skip=false, sin reutilización); CI 42748028579 SUCCESS (backend 2,935 passed; frontend 150 archivos, 1,055 passed, 28 TODO); H1d 42748028455 SUCCESS (38/38); Runner 42748028867 SUCCESS push-only.
- Lite requiere helper acotado porque el parser normaliza csc(x) a 1/sin(x); el helper reconoce únicamente la forma normalizada 1/sin(x)=2, reutiliza el caso de seno y verifica la ecuación recíproca. Plus resuelve el caso sin cambios del motor.
- No se certifica ingesta LaTeX literal en Plus /api/v1/evaluate ni se afirma resolución general de funciones recíprocas.

## Estado y siguiente acción

- Último caso aceptado: TRIG-EC-D-07 — PASS_SCOPED bilateral.
- Siguiente: TRIG-EC-D-08; recuperar primero la fila fuente exacta y fijar su contrato antes de escribir pruebas.
- Certificación global: OPEN. EV-D-01 /api/v1/evaluate continúa BLOCKED; EV-HI permanece PASS_SCOPED; S25, SG28, H2 y DIST siguen abiertos.
- No repetir los gates ya verdes de EC-D-01..07 ni ejecutar dispatch manual.

---

# Actualización de certificación — 2026-11-10 UTC (r485; EC-D-07 IN_PROGRESS)

## Trigonometría TRIG-EC-D-07 — test focal en validación backend

- Fila congelada recuperada directamente del gzip, blob `3a41b0c2e0d79f2eef48e4684dc1324689d0a0fb`: `\csc x=2,quad x\in[0,2\pi)` → `x=\frac{\pi}{6},\ \frac{5\pi}{6}`. La fila original tiene tres columnas (ID, ejercicio, resultado esperado); no hay nota separada.
- Test focal `backend/tests/test_trigonometry_ec_d07.py`: anclaje de fuente, POST `/api/v1/solve`, dos raíces exactas, intervalo y sustitución recíproca.
- SHA de prueba Plus `864c4cf68bb88e331b6df3b64a0ddb2354b047af`. No hay todavía cambio de producto Plus; se espera a comprobar si SymPy resuelve el caso sin modificación del motor.
- Plus H1d [42748028455](https://github.com/c2melendez/precision-lab-plus/actions/runs/42748028455) SUCCESS; Runner [42748028867](https://github.com/c2melendez/precision-lab-plus/actions/runs/42748028867) SUCCESS.
- Plus CI [42748028579](https://github.com/c2melendez/precision-lab-plus/actions/runs/42748028579) y Cumulative [42748028770](https://github.com/c2melendez/precision-lab-plus/actions/runs/42748028770) tenían frontend SUCCESS y backend IN_PROGRESS al corte. Logs backend aún no disponibles; no declarar PASS/FAIL focal hasta que terminen.

## Estado bilateral

- Lite SHA técnico final `3ad626602b3639310921ba6fd27952293732be39`: CI [42748347965](https://github.com/c2melendez/precision-lab-lite/actions/runs/42748347965) SUCCESS (EC-D-07 2/2; 400 archivos, 2,410 passed, 8 expected fail, 34 TODO); Cumulative [42748348152](https://github.com/c2melendez/precision-lab-lite/actions/runs/42748348152) SUCCESS (focal 2/2, skip=false/no REUSE, mismos conteos); H1d [42748347964](https://github.com/c2melendez/precision-lab-lite/actions/runs/42748347964) SUCCESS. Scientific UI [42748348035](https://github.com/c2melendez/precision-lab-lite/actions/runs/42748348035) seguía IN_PROGRESS.
- Lite requirió helper acotado porque el parser convierte `csc(x)` en `1/sin(x)` y el solver genérico no encontraba soluciones. El helper reconoce solo `1/sin(x)=2`, reutiliza el solver directo de `sin(x)=1/2` y verifica en la ecuación recíproca original.
- No emitir PASS_SCOPED bilateral ni acta hasta verificar Plus CI/Cumulative y completar el E2E complementario Lite.

**Siguiente:** revisar los logs backend Plus para los dos tests EC-D-07 explícitos y el conteo total; comprobar Scientific UI Lite. Si Plus pasa por la ruta general, no añadir código de producto innecesario. No repetir Lite CI/Cumulative/H1d ni Plus H1d/Runner.

---

# Actualización de certificación — 2026-11-10 UTC (r484; EC-D-06 PASS_SCOPED)

## Trigonometría TRIG-EC-D-06 — PASS_SCOPED bilateral

- Fila congelada: `sin(2x)=cos(x)`, `x∈[0,2π)` → `{π/6, π/2, 5π/6, 3π/2}`; gzip blob `3a41b0c2e0d79f2eef48e4684dc1324689d0a0fb`. La fuente contiene tres columnas, sin nota independiente.
- Lite SHA `2af7cefc410d1b7cb2c15483f3affd3473b54a89`: test `tests/trigonometryEcD06.audit.test.ts` 2/2; Cumulative 42746381569 SUCCESS (399 archivos, 2,408 passed, 8 expected fail, 34 TODO, skip=false, sin REUSE); CI 42746381637 SUCCESS (typecheck/audit/tests/build, mismos conteos); H1d 42746381850 SUCCESS (22/22, skip=false); Scientific UI 42746381589 SUCCESS (456/456 desktop/tablet/mobile, skip=false); Runner 42746381595 SUCCESS push-only.
- Plus SHA `2a7ff0f2b243597ef6476e665b4a102dcfffdd85`: test `backend/tests/test_trigonometry_ec_d06.py` 2/2 PASS explícito en Cumulative 42746666257; backend 2,933 passed, 1 skipped, 11 xfailed, skip=false. CI 42746666105 SUCCESS (mismos conteos backend y frontend SUCCESS); H1d 42746666095 SUCCESS 38/38 (skip=false); Native Syntax 42746666542 SUCCESS 52/52 (skip=false); Runner 42746666546 SUCCESS push-only.
- Lite factoriza este caso concreto mediante identidad de ángulo doble; Plus normaliza las raíces al intervalo usando solveset sobre los factores. Cada candidato se sustituye en la ecuación original.
- Acta bilateral: `qa/certification/TRIG_EC_D_06_ACCEPTANCE_2026-11-10.md`.

## Alcance y límites

- PASS_SCOPED cubre solo la ecuación congelada y el conjunto exacto de cuatro raíces en `[0,2π)`; no generaliza a ecuaciones trigonométricas mixtas arbitrarias ni a familias sobre toda `R`.
- Las entradas de cálculo son ASCII/forma normalizada. No se certifica aquí ingesta literal LaTeX en Plus `/api/v1/evaluate`.
- Plus `Certification dependency and security gates` 42746666307 seguía ejecutando `plus-backend-mutmut`, independiente de la aceptación matemática EC-D-06.
- Certificación global **OPEN**. EV-D-01 Plus `/api/v1/evaluate` BLOCKED; EV-HI PASS_SCOPED; S25, SG28, H2 y DIST abiertos.

**Siguiente:** TRIG-EC-D-07, cuya fila congelada ya fue recuperada: `csc(x)=2,\ x∈[0,2π)` → `{π/6,5π/6}`. Fijar el contrato literal y continuar test-first bilateral. No repetir EC-D-01..06.

---

# Actualización de certificación — 2026-11-10 UTC (r483; EC-D-06 IN_PROGRESS)

## Trigonometría TRIG-EC-D-06 — IN_PROGRESS; Plus en validación backend final

- Fila congelada recuperada del gzip, blob `3a41b0c2e0d79f2eef48e4684dc1324689d0a0fb`: `sin(2x)=cos(x)`, intervalo `[0,2π)`; resultado exacto `{π/6, π/2, 5π/6, 3π/2}`.
- Test focal `backend/tests/test_trigonometry_ec_d06.py`: verifica fila exacta, POST `/api/v1/solve`, cuatro raíces exactas, sustitución en la ecuación original y pertenencia al intervalo.
- Primer intento Plus SHA `7b038743f96afc782997e059f5b4215985e231e3`: CI backend falló porque la salida incluyó `-π/2` en lugar de `3π/2`; ese valor es equivalente trigonométricamente pero no es la representación dentro del intervalo congelado. El backend anterior tuvo 2,932 passed, 1 skipped, 11 xfailed.
- Corrección de producto acotada en `backend/app/services/solve_service.py`: helper `_double_angle_sine_equals_cosine_interval_result` reconoce solo esta ecuación, factoriza por identidad de ángulo doble y calcula cada factor con `solveset` sobre `[0,2π)`. SHA técnico final `2a7ff0f2b243597ef6476e665b4a102dcfffdd85`.
- Plus H1d [42746666095](https://github.com/c2melendez/precision-lab-plus/actions/runs/42746666095) SUCCESS (38/38; guard skip=false, evidence_run_id vacío); Native Syntax [42746666542](https://github.com/c2melendez/precision-lab-plus/actions/runs/42746666542) SUCCESS (52/52; guard skip=false, sin reutilización); Runner [42746666546](https://github.com/c2melendez/precision-lab-plus/actions/runs/42746666546) SUCCESS, push-only.
- Plus CI [42746666105](https://github.com/c2melendez/precision-lab-plus/actions/runs/42746666105) y Cumulative [42746666257](https://github.com/c2melendez/precision-lab-plus/actions/runs/42746666257) tenían frontend SUCCESS, backend IN_PROGRESS al corte. No hay todavía prueba focal Plus final aprobada.
- Gate de seguridad/mutación [42746666307](https://github.com/c2melendez/precision-lab-plus/actions/runs/42746666307) seguía en `plus-backend-mutmut`; se registra aparte del alcance matemático.

## Estado bilateral

Lite ya tiene EC-D-06 focal 2/2 y CI/Cumulative/H1d SUCCESS sobre SHA `2af7cefc...`; Scientific UI Lite [42746381589](https://github.com/c2melendez/precision-lab-lite/actions/runs/42746381589) seguía IN_PROGRESS al corte. **EC-D-06 no se acepta bilateralmente** hasta que Plus CI/Cumulative muestren los dos tests focales PASSED y cierre de éxito. Baseline aceptado EC-D-05 PASS_SCOPED; global OPEN.

**Siguiente:** inspeccionar backend CI/Cumulative de Plus en SHA `2a7ff0f2...`, confirmar los dos tests EC-D-06 explícitos y sus conteos; luego verificar Scientific UI Lite. No repetir Lite Cumulative/CI/H1d ni Plus H1d/Native. No dispatch manual.

---

# Actualización de certificación — 2026-11-10 UTC (r482; EC-D-05 PASS_SCOPED)

## Trigonometría TRIG-EC-D-05 — PASS_SCOPED bilateral

- Contrato congelado desde `qa/certification/legacy_sources/ejercicios_trigonometria.md.gz`, blob `3a41b0c2e0d79f2eef48e4684dc1324689d0a0fb`: `\sin x+\cos x=1,\quad x\in[0,2\pi)` → `\{0,\frac{\pi}{2}\}`.
- Oráculo: exactamente dos raíces reales distintas, ambas en el intervalo semiabierto y verificadas por sustitución en la ecuación original.
- Lite SHA técnico `28964186aa61be64924d49e83e929ea724fc7383`. Test `tests/trigonometryEcD05.audit.test.ts`: anclaje de fuente + resolución focal, 2/2. CI [42732509176](https://github.com/c2melendez/precision-lab-lite/actions/runs/42732509176) SUCCESS (398 archivos, 2,406 passed, 8 XFAIL esperados, 34 TODO); Cumulative [42732509088](https://github.com/c2melendez/precision-lab-lite/actions/runs/42732509088) SUCCESS (focal 2/2; guard skip=false, evidence_run_id vacío); H1d [42732509506](https://github.com/c2melendez/precision-lab-lite/actions/runs/42732509506) SUCCESS (22/22; skip=false); Scientific UI [42732509163](https://github.com/c2melendez/precision-lab-lite/actions/runs/42732509163) SUCCESS (456/456; skip=false); Runner [42732509098](https://github.com/c2melendez/precision-lab-lite/actions/runs/42732509098) SUCCESS, push-only.
- Plus SHA técnico `971774693b5e3bd35cebe188be2fa8d9d96a55dd`. Test `backend/tests/test_trigonometry_ec_d05.py`: los dos tests PASSED explícitamente en Cumulative [42731929122](https://github.com/c2melendez/precision-lab-plus/actions/runs/42731929122); backend 2,931 passed, 1 skipped, 11 xfailed; guard skip=false, evidence_run_id vacío. CI [42731929126](https://github.com/c2melendez/precision-lab-plus/actions/runs/42731929126) SUCCESS (backend/frontend); H1d [42731929115](https://github.com/c2melendez/precision-lab-plus/actions/runs/42731929115) SUCCESS (38/38; skip=false); Runner [42731929156](https://github.com/c2melendez/precision-lab-plus/actions/runs/42731929156) SUCCESS, push-only.
- Implementación Lite estrictamente acotada: sustitución `t=tan(x/2)`; el numerador resultante es `2t(1-t)`, con candidatos `t=0,1`, que se convierten en `x=0,pi/2`. Los candidatos se normalizan al intervalo y se verifican en la ecuación original. Plus no necesitó cambio de producto; SymPy resolvió por la ruta general.

## Alcance y límites

- PASS_SCOPED cubre solamente el conjunto exacto `{0, π/2}` en `[0,2π)` para `sin(x)+cos(x)=1`; no generaliza a combinaciones arbitrarias de funciones trigonométricas ni a una familia periódica sobre toda `R`.
- Las entradas de cálculo son ASCII/forma normalizada y la fila fuente se ancla como fixture. No se certifica ingesta literal LaTeX en Plus `/api/v1/evaluate` ni una interfaz dedicada a este ejercicio.
- EV-D-01 Plus `/api/v1/evaluate` permanece BLOCKED; EV-HI conserva PASS_SCOPED; S25, SG28, H2 y DIST siguen abiertos.
- La certificación global permanece **OPEN**.

**Siguiente:** TRIG-EC-D-06. Recuperar primero la fila literal de EC-D-06 desde el gzip congelado; fijar ejercicio, intervalo y resultado esperado antes de escribir pruebas. No inferir el contrato por el identificador ni repetir EC-D-01..05.

---

# Actualización de certificación — 2026-11-10 UTC (r481; EC-D-04 PASS_SCOPED)

## Trigonometría EC-D-04 — PASS_SCOPED bilateral

- Contrato congelado: \(2\sin^{2}x-\sin x-1=0,\ x\in[0,2\pi)\) → \(\{\frac{\pi}{2},\frac{7\pi}{6},\frac{11\pi}{6}\}\). Fuente qa/certification/legacy_sources/ejercicios_trigonometria.md.gz, blob 3a41b0c2e0d79f2eef48e4684dc1324689d0a0fb.
- Plus SHA 633ec35dc8de728c657cd00907328a2ff6f5c2eb; test backend/tests/test_trigonometry_ec_d04.py. Los tests de anclaje y POST /api/v1/solve PASSED explícitamente en Cumulative 42730138929.
- Cumulative 42730138929 SUCCESS: backend 2,929 passed, 1 skipped, 11 xfailed; guard skip=false, evidence_run_id vacío. Frontend 150 archivos, 1,055 passed, 28 TODO; typecheck y build SUCCESS.
- CI 42730138619 SUCCESS: backend 2,929 passed, 1 skipped, 11 xfailed; frontend 150 archivos, 1,055 passed; typecheck, auditoría y build SUCCESS.
- H1d 42730138616 SUCCESS: 38/38, guard skip=false y sin reutilización.
- Native Syntax and Recovery 42730138595 SUCCESS: 52/52 desktop/tablet/mobile; guard skip=false y evidence_run_id vacío.
- Runner 42730138951 SUCCESS, push-only, sin dispatch manual.
- Implementación acotada: _quadratic_sine_interval_result sustituye u=sin(x), resuelve el cuadrático numérico, genera ambas ramas, normaliza a [0,2π) y verifica cada resultado en la ecuación original.
- Acta bilateral: qa/certification/TRIG_EC_D_04_ACCEPTANCE_2026-11-10.md.

## Alcance y límites

- Se certifica exactamente el conjunto de tres raíces reales dentro de [0,2π), no una familia general sobre toda la recta real.
- La entrada de cálculo al endpoint es ASCII. La fila original se ancla como fixture, pero no se certifica ingesta literal LaTeX ni el endpoint /api/v1/evaluate.
- Plus Certification dependency/security gates 42730139009 sigue IN_PROGRESS en plus-backend-mutmut; es independiente de la aceptación matemática de EC-D-04.
- La certificación global sigue **OPEN**. EV-D-01 /api/v1/evaluate continúa BLOCKED; EV-HI PASS_SCOPED; S25, SG28, H2 y DIST siguen abiertos.

**Siguiente:** TRIG-EC-D-05. Recuperar su fila original exacta del gzip congelado, fijar entrada/intervalo/salida y diseñar prueba focal bilateral antes de ampliar motores.

---

# Actualización de certificación — 2026-11-10 UTC (r480; EC-D-04 IN_PROGRESS)

## Trigonometría EC-D-04 — pruebas focales bilaterales PASS; gates finales pendientes

- Contrato congelado desde `qa/certification/legacy_sources/ejercicios_trigonometria.md.gz`, blob `3a41b0c2e0d79f2eef48e4684dc1324689d0a0fb`: \(2\sin^{2}x-\sin x-1=0,\ x\in[0,2\pi)\) → \(\{\frac{\pi}{2},\frac{7\pi}{6},\frac{11\pi}{6}\}\).
- Plus SHA técnico verificado `633ec35dc8de728c657cd00907328a2ff6f5c2eb`; test `backend/tests/test_trigonometry_ec_d04.py`. Los tests de anclaje y endpoint `POST /api/v1/solve` pasan explícitamente en Cumulative. La entrada del endpoint es ASCII; se valida la fuente literal como fixture independiente.
- Plus [Cumulative 42730138929](https://github.com/c2melendez/precision-lab-plus/actions/runs/42730138929) SUCCESS: `test_ec_d04_source_row_and_exact_oracle_are_frozen` y `test_ec_d04_http_solve_returns_exact_three_roots_in_half_open_interval` PASSED; backend 2,929 passed, 1 skipped, 11 xfailed. Guard `skip=false`, `evidence_run_id=""`.
- Plus frontend Cumulative SUCCESS: 150 archivos, 1,055 passed, 28 TODO; typecheck y production build SUCCESS. [H1d 42730138616](https://github.com/c2melendez/precision-lab-plus/actions/runs/42730138616) SUCCESS, 38/38, guard skip=false y sin reutilización. [Native Syntax and Recovery 42730138595](https://github.com/c2melendez/precision-lab-plus/actions/runs/42730138595) SUCCESS, 52/52 desktop/tablet/mobile. [Runner 42730138951](https://github.com/c2melendez/precision-lab-plus/actions/runs/42730138951) SUCCESS push-only.
- Plus [CI 42730138619](https://github.com/c2melendez/precision-lab-plus/actions/runs/42730138619) IN_PROGRESS al corte: frontend SUCCESS; backend tests todavía ejecutándose.
- Implementación: `_quadratic_sine_interval_result` en `backend/app/services/solve_service.py` sustituye \(u=\sin x\), resuelve el polinomio cuadrático y normaliza ambas ramas a \([0,2\pi)\); verifica cada raíz en la ecuación original. El cambio es acotado a cuadráticos numéricos en \(\sin x\), sin funciones trigonométricas mezcladas ni argumentos transformados.
- Alcance: la ecuación de cálculo se envía en ASCII. La matriz original se ancla, pero este caso no certifica ingesta literal LaTeX ni el endpoint `/api/v1/evaluate`.
- Estado: **IN_PROGRESS**; no crear acta ni avanzar a EC-D-05 hasta que Plus CI 42730138619 concluya SUCCESS. Baseline EC-D-03 PASS_SCOPED; certificación global **OPEN**. El workflow Plus security/mutation 42730139009 es independiente y no es un gate de aceptación matemática de EC-D-04.

**Siguiente:** verificar Plus CI 42730138619. Si SUCCESS, documentar PASS_SCOPED bilateral y avanzar a EC-D-05; si falla, diagnosticar backend CI sin repetir Cumulative/H1d/Native que ya están verdes.

---

# Actualización de certificación — 2026-11-09 UTC (r479; EC-D-03 PASS_SCOPED)

## Trigonometría EC-D-03 — PASS_SCOPED bilateral

- Contrato congelado: \(\tan x=\sqrt{3}\) → \(x=\frac{\pi}{3}+k\pi,\ k\in\mathbb{Z}\). La matriz exige la familia infinita completa.
- Plus SHA verificado d02a3076b57d9bb2cd02d7c89e1bce3e176a9055; test backend/tests/test_trigonometry_ec_d03.py. POST /api/v1/solve devuelve una ImageSet sobre Integers.
- Plus Cumulative 42712350673 SUCCESS (tests EC-D-03 2/2 explícitos; 2,927 passed, 1 skipped, 11 xfailed; guard skip=false, evidence_run_id vacío); CI 42712350706 SUCCESS; H1d 42712350501 SUCCESS (38/38, skip=false); Native Syntax and Recovery 42712350400 SUCCESS (52/52); Runner 42712350393 SUCCESS push-only.
- La implementación Plus usa solveset y verifica simbólicamente el residuo de la familia al sustituir su expresión en la ecuación.
- Aceptación: qa/certification/TRIG_EC_D_03_ACCEPTANCE_2026-11-09.md.
- Alcance: familia completa \(x=\pi/3+k\pi,\ k\in\mathbb Z\) en radianes. La prueba HTTP usa ecuación ASCII; no certifica ingesta literal LaTeX ni UI específica del caso.
- Plus Certification dependency and security gates 42712350624 sigue IN_PROGRESS en mutation/plus-backend-mutmut; tarea independiente.
- Global **OPEN**; EV-D-01 /api/v1/evaluate permanece BLOCKED; EV-HI PASS_SCOPED; S25, SG28, H2 y DIST abiertos.

**Siguiente:** TRIG-EC-D-04. Fila congelada: \(2\sin^{2}x-\sin x-1=0,\ x\in[0,2\pi)\) → \(x=\frac{\pi}{2},\ \frac{7\pi}{6},\ \frac{11\pi}{6}\). Fijar primero la prueba focal y demostrar el conjunto exacto de tres raíces en el intervalo; no inferir el contrato por el nombre del caso.

---

# Actualización de certificación — 2026-11-09 UTC (r478; EC-D-02 PASS_SCOPED)

## Trigonometría EC-D-02 — PASS_SCOPED bilateral

- Contrato congelado: `2\cos x-1=0,\quad x\in[0,2\pi)` → `x=\frac{\pi}{3},\ \frac{5\pi}{3}`. Tres columnas en la fuente; no hay nota separada.
- Plus SHA técnico `6a150e29bba160fd4f2cff92748dee0baccb35a2`; test `backend/tests/test_trigonometry_ec_d02.py`, ambos tests PASSED explícitamente en Cumulative.
- [Plus Cumulative 42669733996](https://github.com/c2melendez/precision-lab-plus/actions/runs/42669733996) SUCCESS: focal 2/2; backend 2,925 passed, 1 skipped, 11 xfailed; guard `skip=false`, `evidence_run_id=""`.
- [Plus CI 42669734319](https://github.com/c2melendez/precision-lab-plus/actions/runs/42669734319) SUCCESS (backend/frontend); [H1d 42669734287](https://github.com/c2melendez/precision-lab-plus/actions/runs/42669734287) SUCCESS, guard `skip=false`; [Runner 42669734406](https://github.com/c2melendez/precision-lab-plus/actions/runs/42669734406) SUCCESS push-only.
- La entrada de Plus fue ASCII en `POST /api/v1/solve`; no se certifica ingesta literal LaTeX ni `/api/v1/evaluate`.
- Aceptación: `qa/certification/TRIG_EC_D_02_ACCEPTANCE_2026-11-09.md`.
- Global **OPEN**; EV-D-01 /evaluate permanece BLOCKED; EV-HI PASS_SCOPED; S25, SG28, H2 y DIST abiertos.

**Siguiente:** TRIG-EC-D-03; contrato de fuente `tan x=\sqrt{3}` → `x=\frac{\pi}{3}+k\pi,\ k\in\mathbb{Z}`. Se requiere una familia infinita, no dos soluciones de un período. Investigar representación paramétrica en ambos motores antes de ampliar los resolvers.

---

# Actualización de certificación — 2026-11-09 UTC (r477; EC-D-02 IN_PROGRESS)

## Trigonometría TRIG-EC-D-02 — IN_PROGRESS; espera de evidencia Lite

- Contrato recuperado directamente de `qa/certification/legacy_sources/ejercicios_trigonometria.md.gz`: `2\cos x-1=0,\quad x\in[0,2\pi)` → `x=\frac{\pi}{3},\ \frac{5\pi}{3}`. La fila original tiene tres columnas (ID, ejercicio, resultado esperado); no existe una columna de nota separada y no se inventa.
- Test Plus creado: `backend/tests/test_trigonometry_ec_d02.py`; ancla la fila completa y verifica por `POST /api/v1/solve` las dos raíces exactas, intervalo y sustitución. La entrada HTTP usada es ASCII (`2*cos(x)-1=0`); esto no certifica ingesta literal LaTeX ni `/api/v1/evaluate`.
- Plus SHA técnico probado `6a150e29bba160fd4f2cff92748dee0baccb35a2`: [Cumulative 42669733996](https://github.com/c2melendez/precision-lab-plus/actions/runs/42669733996) SUCCESS; el log ejecutó los dos tests EC-D-02 y ambos PASSED. Backend: 2,925 passed, 1 skipped, 11 xfailed. [CI 42669734319](https://github.com/c2melendez/precision-lab-plus/actions/runs/42669734319) SUCCESS (jobs backend y frontend); [H1d 42669734287](https://github.com/c2melendez/precision-lab-plus/actions/runs/42669734287) SUCCESS; [Runner 42669734406](https://github.com/c2melendez/precision-lab-plus/actions/runs/42669734406) SUCCESS.
- Plus está PASS para el alcance probado, pero el caso bilateral permanece **IN_PROGRESS** hasta que Lite tenga evidencia real. No se emite PASS_SCOPED bilateral ni acta de aceptación. Baseline global permanece EC-D-01 PASS_SCOPED; certificación global **OPEN**.

**Siguiente:** no repetir los gates verdes Plus mientras no cambie el árbol. Resolver la ejecución pre-job de GitHub Actions Lite, validar el test focal Lite y después completar la aceptación bilateral con el alcance de interfaces claramente delimitado. Mantener separado EV-D-01 `/api/v1/evaluate` y EV-HI PASS_SCOPED.

---

# Actualización de certificación — 2026-11-09 UTC (r476)

## Trigonometría EC-D-01 — PASS_SCOPED bilateral (soluciones exactas en [0, 2π))

- Fila congelada: `sin(x)=1/2`, intervalo `[0,2π)`; raíces exactas esperadas `π/6` y `5π/6`. La prueba ancla el caso a la fila original de `ejercicios_trigonometria.md.gz`.
- Alcance: ambas raíces exactas, pertenencia al intervalo y sustitución se verifican por los dos motores. Plus ejercita `/api/v1/solve` con `sin(x)-1/2=0`; no se afirma certificación de la ingesta literal idéntica en todos los endpoints.
- Plus SHA técnico `21a29a342034ed7b0427b62ca2fbbc67395cbca8`; test `backend/tests/test_trigonometry_ec_d01.py` (anclaje del contrato + endpoint HTTP, 2/2 PASS).
- Plus CI [42662156729](https://github.com/c2melendez/precision-lab-plus/actions/runs/42662156729) SUCCESS: backend 2,923 passed, 1 skipped, 11 xfailed; frontend 150 test files, 1,055 passed, 28 TODO.
- Plus Cumulative [42662156740](https://github.com/c2melendez/precision-lab-plus/actions/runs/42662156740) SUCCESS: el log ejecutó explícitamente `test_ec_d01_source_row_and_exact_oracle_are_frozen` y `test_ec_d01_http_solve_returns_both_exact_roots_in_interval`; ambas PASSED. Backend 2,923 passed, 1 skipped, 11 xfailed; frontend 1,055 passed.
- Plus H1d [42662156790](https://github.com/c2melendez/precision-lab-plus/actions/runs/42662156790) SUCCESS (38 pruebas); Runner [42662156997](https://github.com/c2melendez/precision-lab-plus/actions/runs/42662156997) SUCCESS.
- Resultado **PASS_SCOPED** bilateral con Lite. No cambia el bloqueo separado EV-D-01 LaTeX en Plus `/api/v1/evaluate`; no se amplió el parser ni se certificó ese endpoint. EV-HI-01..12 sigue PASS_SCOPED. S25, SG28/H2 y DIST siguen abiertos; global **OPEN**.

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
