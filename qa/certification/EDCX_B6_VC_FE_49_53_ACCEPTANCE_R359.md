# EDCX-B6 — aceptación acotada VC-FE-49 y VC-FE-53 (r359)

**Estado: PASS_SCOPED — Plus únicamente.** No es aceptación bilateral ni cierre de EDCX-B6.

## Identidad de la ejecución

- Repositorio: `c2melendez/precision-lab-plus`.
- Rama: `qa/syntax-audit-in625-a1`.
- SHA técnico exacto: `218d682848a03a000930e2028f057563847381f3`.
- Test: `backend/tests/test_edcx_b6_inverse_complex.py`.

## Gates y evidencia observada

- CI [41136660010](https://github.com/c2melendez/precision-lab-plus/actions/runs/41136660010): SUCCESS; backend y frontend completados satisfactoriamente.
- Cumulative [41136659987](https://github.com/c2melendez/precision-lab-plus/actions/runs/41136659987): SUCCESS; backend **2,800 passed, 1 skipped, 10 xfailed**, cobertura **88.91%**; frontend SUCCESS. El log enumera ambas filas como PASSED.
- H1d [41136660018](https://github.com/c2melendez/precision-lab-plus/actions/runs/41136660018): SUCCESS; **38 E2E passed**.
- Runner [41136660038](https://github.com/c2melendez/precision-lab-plus/actions/runs/41136660038): SUCCESS. Los pasos de dispatch, escritura de resultado y persistencia fueron SKIPPED; esto no acredita despacho real.

## Filas aceptadas

| Fila | Entrada | Oráculo independiente | Resultado |
|---|---|---|---|
| VC-FE-49 | `atan(2*i)` | `cmath.atan(2j)` | PASSED; valor complejo de rama principal dentro de tolerancia |
| VC-FE-53 | `atanh(2)` | `cmath.atanh(complex(2.0, -0.0))` | PASSED; convención de borde inferior fijada, parte imaginaria negativa |

La matriz permite cualquiera de los dos signos para VC-FE-53; esta aceptación registra explícitamente la convención inferior que coincide con el comportamiento observado. El expected se calcula con Python `cmath`; SymPy solo decodifica el texto de salida. Se comparan partes real e imaginaria con tolerancia relativa y absoluta `1e-9`. El campo `result_approx` no se usa como oráculo para valores complejos.

## Revalidación relacionada

El mismo cumulative volvió a ejecutar y pasó VC-FE-37a, VC-FE-37b y VC-FE-38..41, además de las filas inversas anteriores VC-FE-43, 44, 46, 50, 51 y 52. Esto no amplía el alcance de la presente aceptación más allá de las filas nombradas ni sustituye los informes previos.

## Exclusiones y límites

- **VC-FE-45: BLOCKED**, no PASS ni FAIL. La matriz EDCX-B6 pide `asin(2)` complejo con signo de rama ±; el contrato congelado EV-I-12 y la implementación actual exigen `DOMAIN_ERROR` para `asin(2)` como entrada real fuera de dominio. No se debilitó EV-I-12. Hace falta resolver y versionar el contrato o definir un canal complejo explícito.
- Plus únicamente; Lite no ejecutó estas filas. No hay inferencia bilateral.
- No se demuestra soporte general de todos los cortes, singularidades ni identidades de EDCX-B6.
- EDCX-B6 permanece abierto; certificación global permanece **OPEN**.
