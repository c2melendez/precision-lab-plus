# EDCX-B6 — aceptación acotada VC-FE-32..41 e inversas seleccionadas (r358)

**Estado:** PASS_SCOPED — Plus únicamente. **No es aceptación bilateral ni cierre de EDCX-B6.**

## SHA y evidencia de CI

- SHA técnico exacto: `adbf5c3826480a015456c8f64257f866f23ca3c4`.
- CI [41134338836](https://github.com/c2melendez/precision-lab-plus/actions/runs/41134338836): SUCCESS (backend y frontend).
- Cumulative [41134338772](https://github.com/c2melendez/precision-lab-plus/actions/runs/41134338772): SUCCESS; backend **2,798 passed, 1 skipped, 10 xfailed**, cobertura **88.91%**. Los logs enumeran explícitamente los casos de este documento como PASSED.
- H1d [41134338840](https://github.com/c2melendez/precision-lab-plus/actions/runs/41134338840): SUCCESS.
- Certification Runner [41134338750](https://github.com/c2melendez/precision-lab-plus/actions/runs/41134338750): SUCCESS. No sustituye la evidencia matemática anterior.

## VC-FE-32..36 — identidades complejas con sustituciones finitas

Test: `backend/tests/test_edcx_b6_symbolic_identities.py`, blob SHA `9ba9eea1186ed76ddaf32b0ff6d0c80c0daea721`.

- VC-FE-32 y 33: tres pares reales explícitos para cada identidad de módulo.
- VC-FE-34 y 35: tres valores complejos explícitos para cada identidad exponencial-trigonométrica.
- VC-FE-36: tres valores complejos para `sin(z)^2 + cos(z)^2 = 1`.
- Oráculo independiente: Python `math`/`cmath`; tolerancia relativa/absoluta `1e-9`. SymPy solo decodifica el texto emitido por el producto, no calcula el esperado.
- Las 15 instancias fueron PASSED en cumulative. Para VC-FE-36, `result_approx=null` se acepta según el contrato real-only opcional del campo; el valor complejo se valida decodificando `result_text`.

**Límite:** PASS_SCOPED por sustituciones finitas declaradas. No demuestra identidad simbólica universal ni manejo general de supuestos simbólicos.

## VC-FE-37..41 — escalares hiperbólicos complejos

Test: `backend/tests/test_edcx_b6_hyperbolic_complex.py`, blob SHA `40f45a2f50c897cac705354273abed6ec586d820`.

Seis instancias PASSED: VC-FE-37a `sinh(i*pi)`, VC-FE-37b `cosh(i*pi)`, y VC-FE-38..41. El oráculo usa Python `cmath`/`math`, rama principal y tolerancia relativa/absoluta `1e-9`. Se admite `result_approx=null` para resultados simbólicos reales cuando el texto decodificado coincide.

**Límite:** escalares puntuales de rama principal; no certifica toda identidad hiperbólica ni todos los cortes.

## Subconjunto de funciones trigonométricas inversas e hiperbólicas inversas

Test: `backend/tests/test_edcx_b6_inverse_complex.py`, blob SHA `8355a4909532275a99e593f09b640d8df557a917`.

PASSED: VC-FE-43, 44, 46, 48, 50, 51 y 52. Incluye el error controlado `DOMAIN_ERROR` para la singularidad VC-FE-48 (`atan(i)`). Oráculo independiente Python `cmath`/`math`, rama principal, tolerancia relativa/absoluta `1e-9`.

**Excluidas por convención de rama pendiente:** VC-FE-45, VC-FE-49 y VC-FE-53. No se asigna PASS/FAIL a esas filas.

## Decisión y continuidad

- VC-FE-32..41: PASS_SCOPED en Plus.
- VC-FE-43,44,46,48,50,51,52: PASS_SCOPED en Plus.
- VC-FE-45,49,53: REVIEW; primero documentar la convención de rama/corte en el contrato y contrastarla con la semántica real del evaluador.
- VC-FE-01..53 no está cerrada; EDCX-B6 no está cerrada.
- Lite no ejecutó EDCX-B6; no hay paridad ni aceptación bilateral.
- Certificación global: OPEN.
