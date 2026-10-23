# EDCX-B6 — auditoría previa de canal y semántica (r268)

Estado: REVIEW; no medir todavía. La auditoría corrige una interpretación incompleta de r267.

## Inventario del campo `canal`

En `qa/certification/edcx_ejecutables.jsonl` hay 638 filas: 589 tienen `canal` vacío y 49 tienen valor. Las 53 filas B6 (`VC-FE-01..53`) están vacías, pero no son las únicas. Los ejemplos poblados (`B → P, T, X`, `P → B, T, X`, etc.) describen transformaciones entre representaciones matemáticas, no rutas HTTP. Por tanto, no es válido concluir que todo campo vacío significa que falta un endpoint, ni completar ese campo con `/api/v1/evaluate`.

Mantener separados estos conceptos:
1. **Canal semántico de matriz**: representación o transformación descrita por el campo `canal`.
2. **Adaptador/canal técnico de prueba**: endpoint, payload y traducción de notación que usa el harness.
3. **Oráculo esperado**: cálculo independiente, con convenciones y tolerancias definidas antes de ejecutar.

El campo de matriz debe conservarse sin cambios hasta que su contrato confirme cómo debe usarse. Esta auditoría no modifica producto ni JSONL.

## Hipótesis técnica de B6

`POST /api/v1/evaluate` es candidato para casos escalares compatibles, no un canal confirmado para las 53 filas. No asignarlo automáticamente ni tratar una salida del producto como oráculo. La ruta exacta debe justificarse fila por fila a partir del contrato y la implementación real.

Antes de crear el harness, documentar por cada `VC-FE-01..53`: expresión de entrada, notación de matriz, adaptación al producto, endpoint/payload, resultado esperado independiente, política exacta/numérica y criterio de aceptación. Como mínimo:
- `VC-FE-11`: exige resultados multivaluados; una sola salida principal no satisface el requisito.
- `VC-FE-12`: compara la no aditividad del logaritmo principal.
- `VC-FE-14`: exige un error de dominio observable y especificado.
- `VC-FE-45`, `VC-FE-49`, `VC-FE-53`: declarar convención de rama/signo.
- La matriz usa `Log`; el producto distingue `log` base 10 y `ln` natural. No reescribir silenciosamente la notación. Definir la semántica y rama principal, y usar oráculo independiente parametrizado con esa misma convención.
- Las filas con `≈` requieren contrastar el valor exacto cuando la aceptación lo exija y derivar tolerancia de la precisión fuente, no del resultado del producto.

## Estado y límites de certificación

- Plus: B6 permanece `REVIEW`; todavía no hay medición ni PASS/FAIL.
- Lite: `NO_EJECUTADO`; no contiene el JSONL ni un motor equivalente de variable compleja. No afirmar paridad.
- EDCX-B5 (`VC-LG-01..25`) sigue `BLOCKED` en Plus por brecha de capacidad y `NO_EJECUTADO` en Lite.
- La certificación global sigue `OPEN`. Mantener los bloqueos SG28/DIST, S25, SY-P-23, SY-X-04-PLUS-HTTP y ALGEBRA229-AS-B-29 en sus estados documentados hasta evidencia de salida.
- Las corridas r264 previamente revisadas fueron `workflow_dispatch` SUCCESS en SHAs anteriores (`86f1ce84...` Plus y `912e3f8a...` Lite); no demuestran B6 ni ejecución sobre HEAD. B4 técnico Plus tiene evidencia citada para cumulative `40014004350` y H1d `40014004348` en `7e501f5...`. No reutilizar esas corridas como evidencia B6.
- En la revisión previa, HEAD registrado era Plus `112e0a3908675bc99fa7295ed84b6d58b6c05d19` y Lite `7838ca80ff6dc899aaee9d1dc654519864dcf40c`; verificar de nuevo HEAD antes de cualquier dispatch, porque los SHA históricos de este documento no son una afirmación de HEAD actual.

## Siguiente acción única

Completar una tabla de contrato B6 por fila (53 entradas) con semántica de notación, adaptación técnica, rama, oráculo independiente, tolerancia y aceptación. Revisar implementación/rutas reales y tests existentes antes de elegir endpoint. Solo cuando la tabla identifique casos ejecutables, construir un harness test-first en Plus y ejecutar gates mínimos contra el SHA técnico exacto. No lanzar CI para este cambio documental; no editar el campo `canal` por inferencia. Lite permanece `NO_EJECUTADO`; global `OPEN`.
