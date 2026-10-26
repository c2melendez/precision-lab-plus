# S19 backend — plan de pruebas dirigidas (r290)

**Estado:** PROPOSED / REVIEW_REQUIRED.  
**Fuente:** logs del job `plus-backend-mutmut` del run [40069907892](https://github.com/c2melendez/precision-lab-plus/actions/runs/40069907892), SHA `6e6a59ee556cf6bba60a40010ec707f05a01ca52`.  
**Propósito:** reducir mutantes sobrevivientes/no cubiertos con pruebas pequeñas y semánticamente justificadas antes de una nueva ejecución mutacional focalizada. Este plan no aprueba un umbral nuevo ni autoriza cambios de producto.

## Evidencia que prioriza el plan

| Función | Killed | Survived | No tests | Timeout | Prioridad |
|---|---:|---:|---:|---:|---|
| `solve_service._absolute_value_cases_result` | 0 | 172 | 0 | 0 | P0 |
| `solve_service._radical_cases_result` | 2 | 185 | 0 | 0 | P0 |
| `solve_service._rational_domain_result` | 0 | 143 | 0 | 0 | P0 |
| `solve_service._absolute_value_steps` | 0 | 112 | 0 | 0 | P0 |
| `solve_service._absolute_value_equidistance_steps` | 0 | 105 | 0 | 0 | P0 |
| `parsing.validate_g3_structure` | 106 | 246 | 0 | 0 | P0 |
| `routers.evaluate._evaluate_impl` | 44 | 228 | 0 | 3 | P0 |
| `solve_service.solve_equation` | 132 | 161 | 0 | 0 | P1 |
| `routers.evaluate._render_evaluate_presentation` | 31 | 113 | 0 | 0 | P1 |
| `parsing.parse_inequality_tree` | 0 | 0 | 52 | 0 | P0 — no tests |
| `parsing.parse_chained_inequalities` | 0 | 0 | 24 | 0 | P0 — no tests |
| `solve_service._domain_step` | 0 | 0 | 28 | 0 | P0 — no tests |
| `solve_service._real_radical_value` | 0 | 0 | 12 | 0 | P0 — no tests |
| `routers.evaluate._sg28_ci_slow_evaluate` | 0 | 0 | 8 | 0 | BLOCKED — depende del contrato SG28 |

## Brechas verificadas en la selección de pruebas S19

El workflow ejecuta `tests/test_parsing.py`, `tests/test_evaluate.py`, `tests/test_solve.py` y `tests/test_exhaustive_module13_security.py`. En la versión inspeccionada, los tests de `test_solve.py` no contienen casos explícitos de valor absoluto, radicales, dominio, denominadores o ecuaciones racionales. `test_evaluate.py` no menciona SG28 ni las nuevas funciones internas de evaluación. `test_parsing.py` no menciona `parse_chained_inequalities`, `parse_inequality_tree` ni `validate_g3_structure`. El estado `no tests` de mutmut confirma que la selección actual no llega a esas funciones para los mutantes listados.

## Matriz propuesta de casos

### P0 — `tests/test_solve.py`

1. Valor absoluto: `|x| = a` con (a>0) (dos soluciones), (a=0) (una solución) y (a<0) (sin solución real).
2. Valor absoluto/equidistancia: verificar casos con soluciones simétricas, unicidad cuando proceda y sustitución de cada candidata en la ecuación original.
3. Radicales reales: raíz principal con solución válida, candidato extráneo que debe rechazarse al sustituir en la ecuación original, y radicando sin solución real.
4. Ecuaciones racionales: denominador con raíz excluida, solución algebraica que coincide con un cero del denominador y debe rechazarse, y exclusiones derivadas del denominador de origen.
5. Dominio: comprobar que los pasos explicativos reflejen las exclusiones reales y no omitan restricciones.

### P0 — `tests/test_parsing.py`

1. `parse_chained_inequalities`: cadena válida creciente/decreciente, desigualdades estrictas/no estrictas y rechazos de cadenas incompletas o con operadores incompatibles.
2. `parse_inequality_tree`: comparación simple y compuesta, operandos inválidos, límites de complejidad y rechazo de sintaxis mal formada.
3. `validate_g3_structure`: parametrizar las clases de estructura raw de G3 cubiertas por el contrato, incluidos delimitadores incompletos, tokens desconocidos y casos válidos de referencia. Los tests deben derivarse del contrato G3 versionado, no de los IDs de mutante solamente.
4. Añadir regresiones de parser para `permutation_alias_args`, `symbolic_pair_binomial_variable` y `symbolic_identity_sum_bound`: casos válidos, argumentos fuera de rango y rechazos de entradas inválidas.

**Corrección de trazabilidad (r292):** estas tres funciones son helpers del parser/calculadora y no corresponden a filas de la matriz normativa Algebra 229. La matriz congelada se comprueba mediante `qa/certification/check_algebra229_source.py`; las filas AS-B-26..28 documentan factorización de enteros (la AS-B-28 prueba `factor(4294967297)`), mientras que AS-B-29 permanece `ON_HOLD`. Estas regresiones cuentan solo como cobertura de parser; no cierran ni sustituyen ALGEBRA229-AS-B-29. La afirmación anterior de que debían derivarse del contrato Algebra 229 era incorrecta.

### P0/P1 — `tests/test_evaluate.py`

1. Cubrir resultados y errores observables de `_evaluate_impl`: éxito, error de parseo/validación, error de dominio, timeout/error controlado y serialización de respuesta, con asserts de código/campos públicos.
2. Cubrir `_render_evaluate_presentation`: resultado con presentación completa, presentación opcional ausente y límites de salida, sin acoplarse a detalles privados innecesarios.
3. `_sg28_ci_slow_evaluate`: no escribir una prueba de aceptación distribuida ni afirmar K=1 hasta que el contrato SG28 esté aprobado. Después, cubrir fail-closed, límite de tiempo y mapeo de errores conforme a la matriz contractual aprobada.

## Secuencia de ejecución sin duplicación

1. Revisar/aceptar este plan y contrastar cada caso con los contratos de G3, Algebra 229 y SG28.
2. Añadir únicamente los tests dirigidos aprobados; no modificar el código de producto para matar mutantes sin una regresión funcional demostrada.
3. Ejecutar primero las pruebas unitarias focalizadas, no S19 completo.
4. Ejecutar una sola campaña mutacional focalizada sobre las funciones cubiertas, conservando el log de resumen y el inventario de mutantes por función.
5. Recalcular score con el denominador histórico y reportar por separado killed, survived, no tests y timeout. Documentar cualquier cambio de alcance antes de comparar con el baseline.

## Bloqueos y límites

- S19 backend acceptance sigue BLOCKED hasta revisar el score 29.60%, la expansión de inventario y el plan de cobertura.
- SG28 sigue REVIEW_REQUIRED; las pruebas de integración distribuida que dependan de su contrato no deben adelantarse.
- No se lanzaron Actions ni se modificó código de producto en la elaboración de este plan.
- Certificación global permanece OPEN; PR #29 permanece abierto.


## Actualización de ejecución r292 (2026-10-24)

- El filtro mutmut fue corregido en `561547252456b30124f4f7a1db06347ee0731079` y la campaña focalizada sí terminó: [S19 run 40098526609](https://github.com/c2melendez/precision-lab-plus/actions/runs/40098526609), 1,666 mutantes, 801 killed, 863 survived, 2 timeout.
- El resultado confirma ejecución del alcance focalizado, pero no aceptación: sobrevivientes siguen siendo significativos y el denominador no es comparable directamente con el baseline histórico de 1,028. S19 permanece BLOCKED; no lanzar la campaña completa.
- CI 40098526446, cumulative 40098526501 y Playwright 40098526513 SUCCESS en el mismo SHA.
- S18 40098526464 fue cancelado por shutdown del runner durante `qa/s18/run_differential.py`; tratar como infraestructura. Próxima acción es diagnosticar/restablecer S18 y repetir solo ese gate una vez.
