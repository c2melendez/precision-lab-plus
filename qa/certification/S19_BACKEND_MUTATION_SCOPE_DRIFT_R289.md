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
2. **Completado en r289:** el log final aporta el resumen completo (971 killed, 2,136 survived, 159 no tests, 14 timeout; total 3,280). Comparar versión de Python, mutmut, configuración efectiva, módulos/archivos seleccionados, IDs/nombres de mutantes y categorías de estado; explicar la expansión de inventario por superficie.
3. Explicar la diferencia entre los 1,028 mutantes del baseline y los 2,309 estados actuales; confirmar si el informe actual es de una campaña comparable y si el conteo se obtiene de estados finales únicos.
4. Solo después proponer una política de score que preserve la definición histórica de killed y mantenga no-tests, timeout y equivalentes/exclusiones separados y auditables. Cualquier cambio de denominador/umbral debe tener justificación explícita y revisión responsable; no se fija aquí un umbral nuevo.
5. Si el artefacto baseline ya no está disponible, documentar esa limitación y preparar una ejecución diagnóstica focalizada, no una repetición completa, una vez estabilizado el plan.

## Actualización r289: interpretación del formato

El conteo de líneas de `mutmut-results.txt` no es el total de mutantes, porque los mutantes killed no aparecen en ese listado. Una lectura inicial que etiquetó 2,309 como total y cero killed fue incorrecta. El log permite reconstruir el total y score actual; el informe `S19_BACKEND_MUTATION_REVIEW_R288.md` contiene la corrección y distribución por módulo. No usar el listado de resultados aislado para calcular score.

## Decisión

**S19 backend continúa BLOCKED.** No cambiar código de producto, no declarar aceptación y no lanzar otra ejecución de S19 hasta resolver la discrepancia de alcance. Mantener SG28 REVIEW_REQUIRED, S18 CANCELLED por infraestructura, PR #29 abierto y certificación global OPEN.
