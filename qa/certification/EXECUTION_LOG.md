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
