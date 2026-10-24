# S19 backend — discrepancia de alcance del baseline (r289)

**Estado:** INVESTIGATION_REQUIRED / ACCEPTANCE_BLOCKED.  
**Referencia de ejecución:** [run 40069907892](https://github.com/c2melendez/precision-lab-plus/actions/runs/40069907892), SHA evaluado `6e6a59ee556cf6bba60a40010ec707f05a01ca52`.  
**Artefacto backend:** `s19-plus-backend-mutmut`, ID `12551670346`, digest SHA-256 `064d33a4f7be9d4e68952dac344f0630153866c2916a97fc7f26786561f73fee`.

## Hallazgo que precede a fijar un umbral

El baseline normativo `qa/s19/BASELINE_MUTATION.md` identifica como baseline operativo backend estable **1,028 mutantes**: 590 killed, 371 survived, 58 no tests y 9 timeout; score reportado 57.39% killed (58.27% bajo una métrica alternativa que cuenta timeout como controlados). Ese documento advierte expresamente que la campaña amplia histórica de 6,810 mutantes no es el baseline operativo.

El artefacto de 2026-10-24 registra **2,309 entradas en `mutmut-results.txt`**: 2,136 survived, 159 no tests y 14 timeout. El listado no incluye killed; el log del job aporta el resumen final completo: 971 killed, 2,136 survived, 159 no tests, 14 timeout, total 3,280 y score killed 29.60% bajo la convención histórica. El baseline recuperado tiene 438 entradas listadas más 590 killed, total 1,028 y score 57.39%. Por tanto, el inventario actual aumentó en 2,252 mutantes y el score bajó 27.79 puntos porcentuales; debe analizarse el crecimiento y los cambios de código antes de atribuirlo a una regresión de tests.

## Configuración observada en la rama canónica

- `.github/workflows/s19-mutation.yml` fija `mutmut==3.8.0`.
- `backend/pyproject.toml` fija `source_paths = ["app/"]`, cinco módulos en `only_mutate` y cuatro archivos de prueba en la selección.
- El workflow repite las superficies y pruebas en la línea de comando, pero no publica en el artefacto un manifiesto de configuración efectiva, lista normalizada de mutantes por módulo, versión completa de Python/dependencias ni comparación con el inventario baseline.
- El job SUCCESS y el código de salida 0 solo acreditan que la herramienta terminó; no acreditan score ni equivalencia de alcance.

## Siguiente paso seguro

Antes de aprobar o imponer un nuevo umbral:

1. Recuperar el artefacto baseline histórico `10740671311` del run `35838270384` y cotejar sus ficheros/reportes con el artefacto actual.
2. **Completado en r289:** el log final aporta el resumen completo (971 killed, 2,136 survived, 159 no tests, 14 timeout; total 3,280). La expansión se concentra en solve_service (+1,071 mutantes), parsing (+717), evaluate (+437) y ast_validator (+27); comparar mutantes sobrevivientes con las funciones añadidas y pruebas existentes.
3. Explicar la diferencia entre los 1,028 mutantes del baseline y los 2,309 estados actuales; confirmar si el informe actual es de una campaña comparable y si el conteo se obtiene de estados finales únicos.
4. Solo después proponer una política de score que preserve la definición histórica de killed y mantenga no-tests, timeout y equivalentes/exclusiones separados y auditables. Cualquier cambio de denominador/umbral debe tener justificación explícita y revisión responsable; no se fija aquí un umbral nuevo.
5. Priorizar una revisión de pruebas dirigidas para las funciones añadidas de solve_service y evaluate, además de parsing; ejecutar solo una campaña focalizada cuando se haya definido el alcance y estén listas las pruebas, no repetir la campaña completa sin necesidad.

## Actualización r289: comparación de inventario y cambios de código

Se compararon las superficies mutadas entre SHA baseline `7568020f22534bbe41df722e82e7f18fa3a7e37a` y SHA actual `6e6a59ee556cf6bba60a40010ec707f05a01ca52`. La comparación del historial reporta ramas divergentes, por lo que se usan los datos por archivo solo como contexto y no como una comparación global lineal de commits.

| Módulo | Líneas baseline → actual | Funciones baseline → actual | Mutantes baseline | Mutantes actuales | Score killed baseline → actual |
|---|---:|---:|---:|---:|---:|
| `services.solve_service` | 239 → 788 | 6 → 16 | 398 | 1,469 | 65.08% → 21.51% |
| `services.parsing` | 715 → 982 | 19 → 24 | 564 | 1,281 | 51.24% → 42.00% |
| `routers.evaluate` | 100 → 249 | 3 → 7 | 20 | 457 | 70.00% → 19.47% |
| `services.ast_validator` | 130 → 147 | 3 → 3 | 46 | 73 | 60.87% → 38.36% |
| **Total** | — | — | **1,028** | **3,280** | **57.39% → 29.60%** |

El aumento no es un simple cambio de contador: `solve_service.py` creció 239→788 líneas e incorporó 10 funciones, incluidas ramas de valor absoluto, radicales y dominio; `parsing.py` creció 715→982 e incorporó cinco funciones de validación/parseo; `evaluate.py` creció 100→249 e incorporó cuatro funciones, incluida la ruta SG28 `_sg28_ci_slow_evaluate`. Esto explica parte del inventario nuevo, pero **no elimina la deuda de cobertura**: el score bajó en todos los módulos y las superficies nuevas requieren pruebas dirigidas.

## Actualización r289: interpretación del formato

El conteo de líneas de `mutmut-results.txt` no es el total de mutantes, porque los mutantes killed no aparecen en ese listado. Una lectura inicial que etiquetó 2,309 como total y cero killed fue incorrecta. El log permite reconstruir el total y score actual; el informe `S19_BACKEND_MUTATION_REVIEW_R288.md` contiene la corrección y distribución por módulo. No usar el listado de resultados aislado para calcular score.

## Decisión

**S19 backend continúa BLOCKED.** No cambiar código de producto, no declarar aceptación y no lanzar otra ejecución de S19 hasta resolver la discrepancia de alcance. Mantener SG28 REVIEW_REQUIRED, S18 CANCELLED por infraestructura, PR #29 abierto y certificación global OPEN.
