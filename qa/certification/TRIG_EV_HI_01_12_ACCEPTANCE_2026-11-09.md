# Aceptación: Trigonometría EV-HI-01..12 (inversas hiperbólicas)

- Estado: **PASS_SCOPED** (corregido desde PASS bilateral; alcance abajo).
- Fuente congelada: `qa/certification/legacy_sources/ejercicios_trigonometria.md.gz`, blob `3a41b0c2e0d79f2eef48e4684dc1324689d0a0fb` (sin cambios en los cuatro commits de la operación). Filas EV-HI-01..12 en la matriz.
- Commit técnico test-first: `4ec0be2bcd32d432c947fc11aebc458598c3079f` (Cumulative 42552094129 y CI 42552094202 FAILURE).
- Commit técnico final: `a8ddc0ad9838c6cffb3d932950d72bdafa7d0a48`.
- Corridas en el SHA final: Cumulative 42555334429 SUCCESS; CI 42555334439 SUCCESS; H1d 42555334469 SUCCESS; Runner 42555334546 SUCCESS. Detalle: focal EV-HI 4/4 PASSED en Cumulative (tests/test_trigonometry_ev_hi01_hi12.py); backend 2,916 passed, 1 skipped, 10 xfailed.
- Otras corridas del SHA: Plus Native Syntax and Recovery 42555334521 SUCCESS; SG28 prototype 42555334631 SUCCESS; Runner 42555334546 SUCCESS.
- Cambios de producto: backend/app/services/evaluate_service.py (guard DOMAIN_ERROR para acosh con argumento real en (0,1)); EDCX-B6 conserva sus ramas complejas.
- Ajuste de literales (solo Lite): en `4ec0be2bcd32d432c947fc11aebc458598c3079f` los casos EV-HI-07..09 esperaban decimales aproximados. En `a8ddc0ad9838c6cffb3d932950d72bdafa7d0a48` se alinearon con la forma exacta de la matriz congelada (`\ln\left(1+\sqrt{2}\right)`, `\ln\left(2+\sqrt{3}\right)`, `\frac{1}{2}\ln 3`). Los valores numéricos esperados no cambiaron.
- Resultado: EV-HI-01..03 exactos en 0; EV-HI-04..09 numéricos dentro de 1e-6; EV-HI-10 `sinh(arsinh(3))` = 3 exacto; EV-HI-11 `artanh(1)` y EV-HI-12 `arcosh(1/2)` con `DOMAIN_ERROR` y mensaje claro.
- Sin relajación de oráculos. Global OPEN; S25, SG28, H2 y DIST siguen abiertos.

## Alcance y límites (PASS_SCOPED)

- Verificado: las 12 filas EV-HI con las entradas ASCII de los tests de cada motor, con los oráculos numéricos y exactos ya registrados.
- No certificado todavía: los literales LaTeX de entrada de EV-HI en cada motor. Plus prueba entradas ASCII; Lite usa literales LaTeX solo como forma esperada de salida.
- No certificado todavía: la forma exacta de cada resultado frente a la matriz. Lite compara valores numéricos dentro de 1e-6 en EV-HI-04..09, no la forma simbólica exacta.
- Plus prueba `acsch`, `asech` y `acoth`; los alias `arcsch`, `arsech` y `arcoth` de la matriz no tienen test propio en Plus.
- Para volver a PASS: certificar en ambos motores las entradas LaTeX y las formas exactas de EV-HI-01..12, con evidencia CI en el SHA final.

- Verificación Plus: el alcance se limita a las entradas ASCII probadas en `test_trigonometry_ev_hi01_hi12.py`.
