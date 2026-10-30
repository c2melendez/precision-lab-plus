# EDCX-B6 — aceptación acotada VC-FE-23..31 (r357)

**Estado:** PASS_SCOPED — Plus únicamente. **No es aceptación bilateral ni cierre de EDCX-B6.**

## Alcance evaluado

Nueve filas de escalares trigonométricos complejos: VC-FE-23..31 (`sin(i)`, `cos(i)`, `tan(i)`, `cot(i)`, `sin(1+i)`, `cos(1+i)`, `sin(pi/2+i)`, `cos(pi+i)` y `sin(2i)`).

El test `backend/tests/test_edcx_b6_trig_complex.py` (blob SHA `030742e9b09b9d84159279f54f5fb752a1795c80`) usa `cmath`/`math` como oráculo independiente de rama principal. Comprueba HTTP 200, `success=true`, ausencia de error, `result_text` y `result_latex`, decodifica el resultado con SymPy y compara las partes real e imaginaria con tolerancia relativa/absoluta `1e-9`. Para valores reales acepta forma simbólica exacta cuando `result_approx` es nulo; para resultados complejos exige `result_approx` nulo, conforme al contrato real-only del campo.

## Evidencia exacta

- Commit de harness: `382563b15a0250eb1fa48082b6e51ebc6438f590` (`test(edcx-b6): accept exact symbolic real results for VC-FE-29/30 (harness)`).
- SHA técnico final validado: `082fdb7c48add1476554ef90e840fab698b89561`.
- CI [40970642357](https://github.com/c2melendez/precision-lab-plus/actions/runs/40970642357): SUCCESS en el SHA técnico final.
- Cumulative [40970642413](https://github.com/c2melendez/precision-lab-plus/actions/runs/40970642413): SUCCESS en el SHA técnico final; `skip=false`. El log del job backend registra explícitamente VC-FE-23, 24, 25, 26, 27, 28, 29, 30 y 31 como PASSED. Resultado global backend: 2,783 passed, 1 skipped, 10 xfailed; cobertura 88.91%.
- H1d [40970642305](https://github.com/c2melendez/precision-lab-plus/actions/runs/40970642305): SUCCESS en el mismo SHA.
- Certification Runner [40970642558](https://github.com/c2melendez/precision-lab-plus/actions/runs/40970642558): SUCCESS en el mismo SHA.

## Límites de la aceptación

- Solo cubre VC-FE-23..31 en Plus. Lite no ejecutó este lote; no hay aceptación bilateral.
- No certifica identidades simbólicas VC-FE-32..36, hiperbólicas VC-FE-37..41, inversas VC-FE-43..53 ni el resto de la matriz de 53 filas.
- No prueba el comportamiento sobre todos los cortes de rama, valores multivaluados o singularidades; los nueve puntos se comparan con los valores principales esperados.
- No cierra EDCX-B6 ni la certificación global, que permanece OPEN.

## Decisión de continuidad

VC-FE-23..31 pasa de VERIFYING a PASS_SCOPED. No repetir el test ni los cuatro workflows citados salvo discrepancia nueva o cambio justificado de precondición. El siguiente frente matemático en Plus es revisar el contrato y el canal de VC-FE-32..36 (identidades simbólicas), sin saltar esas filas para ir directamente a hiperbólicas/inversas. Compass P0 no es prerrequisito del motor matemático y permanece en su backlog independiente.
