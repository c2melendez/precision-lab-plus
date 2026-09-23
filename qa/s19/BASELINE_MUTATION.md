# S19 — Baseline de mutation testing

Fecha de baseline: 2026-09-23

## Alcance

Este documento fija el primer baseline normativo de mutation testing de Precision Lab Plus y del snapshot certificado de Precision Lab Lite usado por la suite oficial.

Herramientas fijadas:
- StrykerJS 10.0.0 + Vitest runner 10.0.0.
- mutmut 3.8.0.
- Lite certificado: `6cbec7645b73ad18875d4472182c704eb35228b0`.
- Plus: PR #19, rama `qa/s19-mutation-baseline`.

La política de S19 no exige un porcentaje inicial arbitrariamente alto. A partir de este baseline, el score no debe degradarse sin una revisión y justificación explícita.

## Resultado cuantitativo certificado

| Superficie | Total mutantes | Killed | Survived | No tests / No coverage | Timeout | Score |
|---|---:|---:|---:|---:|---:|---:|
| Plus frontend / Stryker | 1,468 | 225 | 977 | 266 | 0 | 15.33% |
| Lite frontend / Stryker | 2,161 | 223 | 1,548 | 390 | 0 | 10.32% |
| Plus backend / mutmut estable | 1,028 | 590 | 371 | 58 | 9 | 57.39% killed; 58.27% si los timeouts se cuentan como controlados |

Los pisos automatizados de Stryker quedan fijados en:
- Plus frontend: `break = 15.3`.
- Lite frontend: `break = 10.3`.

### Evidencia histórica de campaña amplia

Antes de estabilizar el harness se ejecutó una campaña backend más amplia de 6,810 mutantes sobre más superficies. Esa corrida produjo:
- 6,349 killed.
- 453 survived.
- 8 timeout.
- ~93.23% killed; ~93.35% contando timeout como controlado.

Ese resultado se conserva como evidencia histórica, pero **no es el baseline operativo actual**. La campaña amplia mostró inestabilidad del harness en la fase de clean/stats con rutas trigonométricas como `sec(pi/2)` y `csc(pi/2)`, incluso cuando CI normal permanecía verde. Por ello el gate final backend se acotó a superficies y pruebas dirigidas estables.

## Alcance backend estable

Mutmut queda limitado a:
- `app/services/parsing.py`
- `app/services/ast_validator.py`
- `app/services/solve_service.py`
- `app/routers/evaluate.py`
- `app/schemas/responses.py`

Y usa como selección de pruebas:
- `tests/test_parsing.py`
- `tests/test_evaluate.py`
- `tests/test_solve.py`
- `tests/test_exhaustive_module13_security.py`

Las rutas trigonométricas E2E continúan certificadas por CI, Playwright, S17 y S18; no se consideran parte del gate mutacional backend estable mientras el runner instrumentado de mutmut reproduzca el flake documentado.

## Lectura del baseline

### Plus frontend

La principal deuda está en:
- `NaturalMathField.tsx`: normalización y transformación de sintaxis matemática.
- `calculusIntent.ts`: reconocimiento de intents matemáticos.
- `KeyboardBasicPanel.tsx`: inventario, acciones y metadatos del teclado.
- persistencia de historial/recent keys.
- conversiones de unidades.

Reglas críticas revisadas:
- `log(100)`, `ln(e)` y logaritmo con base ya tienen regresiones funcionales S16/S18, pero sobreviven mutaciones internas de regex/normalización. Se consideran deuda de granularidad de unit tests, no regresión funcional conocida.
- decimal, grados, valor absoluto, porcentaje y enteros grandes permanecen cubiertos por las regresiones certificadas de S16; S19 revela que la cobertura mutacional de las rutas internas aún puede mejorar.
- persistencia presenta mutantes sobrevivientes en versionado de schema, escritura a localStorage y actualización de listas. Se remite además a S27 para validación de migración/persistencia end-to-end.

### Lite frontend

La deuda principal está en:
- `engine/parsing/normalize.ts`.
- `engine/parsing/index.ts`.
- `engine/algebriteClient.ts`.
- helpers de aridad, multiplicación implícita, desigualdades y sistemas.
- `historyDb.ts` y `useRecentKeysStore.ts`.

Reglas críticas revisadas:
- `log` y `log10`: existen mutantes sobrevivientes en `rewriteLogBase` / `rewriteCommonLog`; las regresiones funcionales certifican resultados conocidos, pero se requieren unit tests más quirúrgicos para matar cambios estructurales equivalentes o cercanos.
- validación decimal: sobrevive la eliminación de `validateDecimalPoints(...)`; debe conservarse como deuda prioritaria de test unitario.
- límites de derivada, errores de parser, raíces y normalización de `sqrt` muestran supervivientes; no se observó una regresión funcional nueva en la suite previa.
- persistencia IndexedDB/localStorage tiene sobrevivientes; S27 deberá certificar recuperación/migración y los tests unitarios podrán endurecerse después del baseline.

### Plus backend

La campaña estable detectó 371 sobrevivientes y 58 mutantes sin pruebas. Los focos principales siguen siendo:
- validación y complejidad en `ast_validator`.
- normalización y parsing en `parsing`.
- `_expand_sqrt_tokens`.
- separación de ecuaciones y validación decimal.
- helpers de solución lineal/cuadrática en `solve_service`.
- manejo de respuestas/error del router `evaluate`.

Reglas críticas:
- decimales: `validate_decimal_and_reject_scientific` mantiene mutantes sobrevivientes; el comportamiento funcional está cubierto, pero se prioriza endurecer tests unitarios.
- errores de dominio/división por cero y respuestas controladas están cubiertos por S16/S17/S18; S25 volverá a validar CORS/error handling a nivel HTTP.
- los 9 timeouts del baseline estable se concentran en mutaciones de `_expand_sqrt_tokens`; se registran como no terminación controlada, no como regresiones funcionales.
- no se modifica el límite global de Python para enteros; el fix S17 de presentación segura se mantiene como decisión normativa.
- el flake de `sec(pi/2)`/`csc(pi/2)` observado en el runner instrumentado no se resolvió cambiando producto, porque CI normal demostraba que la semántica certificada era correcta. Se trató como limitación del harness y se mantuvo fuera del gate mutacional estable.

## Clasificación de sobrevivientes

S19 distingue tres grupos:

1. **Críticos funcionales**: mutaciones que podrían alterar semántica matemática, validación o persistencia. Se conservan como backlog QA explícito y no pueden ignorarse en cambios futuros sobre esas superficies.
2. **Metadatos/UI**: etiquetas, descripciones y strings de presentación. Deben cubrirse cuando afecten accesibilidad/paridad; S23/S26 complementan esta área.
3. **Equivalentes o de bajo valor**: mutaciones que no cambian comportamiento observable o que afectan solo formulaciones internas. Deben justificarse antes de excluirse de futuras campañas.

## Gates y política posterior

- El primer baseline no se invalida por tener score bajo.
- Toda reducción de los pisos Stryker requiere justificación explícita.
- El baseline backend operativo es la campaña estable de 1,028 mutantes.
- Los mutantes críticos conocidos de logaritmos, decimales, división por cero/dominio, límites de enteros, manejo de errores/CORS y persistencia no deben descartarse silenciosamente.
- Cambios futuros sobre parser/normalización deben acompañarse de pruebas dirigidas capaces de matar los mutantes relevantes cuando sea razonable.
- S25 será autoridad adicional para CORS/error handling.
- S27 será autoridad adicional para persistencia/migración.
- Los reportes JSON/HTML y mutmut de esta ejecución son evidencia de baseline y deben conservarse como artefactos de CI.

## Evidencia

Workflow final certificado: `S19 Mutation Baseline`, run `35838270384`.

Jobs:
- Plus backend mutmut: `107106893639` — success.
- Lite frontend Stryker: `107106893880` — success.
- Plus frontend Stryker: `107106893932` — success.

Artefactos:
- Plus backend: artifact `10740671311`, `s19-plus-backend-mutmut`.
- Plus frontend: artifact `10741420388`, `s19-plus-frontend-stryker`.
- Lite frontend: artifact `10740479210`, `s19-lite-frontend-stryker`.

Gates del mismo head `7568020f22534bbe41df722e82e7f18fa3a7e37a`:
- CI — success.
- Playwright E2E — success.
- S17 API fuzzing — success.
- S18 Differential Properties — success.
- S19 Mutation Baseline — success.

## Criterio de cierre

S19 puede cerrarse cuando:
1. este baseline quede versionado en el PR;
2. los pisos de no-regresión estén activos;
3. CI/Playwright/S17/S18/S19 estén verdes en el head final;
4. el PR sea fusionado;
5. los gates post-merge de main confirmen verde.

La deuda de sobrevivientes queda registrada y no bloquea por sí sola el primer baseline, salvo que se descubra un mutante crítico que evidencie una regresión funcional reproducible.
