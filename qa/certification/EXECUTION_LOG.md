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
