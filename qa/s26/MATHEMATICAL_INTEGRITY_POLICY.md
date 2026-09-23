# S26 — Política de integridad matemática

## Baseline protegido

SHA previo a S26: `5de721e32c13a60f77671cd2bd98a8cc05cf0140`

## Rutas protegidas

- `backend/app/services/**`
- `backend/app/routers/evaluate.py`
- `backend/app/services/parsing.py`
- `backend/app/services/ast_validator.py`
- `frontend/src/api/**`
- `frontend/src/types/api.ts`

## Regla de cambio

Durante S26 estas rutas se consideran congeladas.

Un cambio dentro de una ruta protegida solo puede hacerse si:
1. existe un defecto reproducible;
2. se documenta por qué un cambio visual no basta;
3. se agrega o actualiza un regression test;
4. se ejecutan nuevamente los gates matemáticos correspondientes;
5. el log S26 registra archivo, causa, test y resultado.

## Gate de integridad post-rediseño

Antes del cierre:
- tests unitarios completos;
- Playwright E2E;
- regresiones conocidas;
- teclado↔motor;
- recorridos funcionales por científica, gráfica, matrices, estadística y conversión;
- comparación con baseline previo cuando aplique.

## Principio de separación

Los cambios visuales deben concentrarse en componentes, estilos, layout y presentación. No se mezclará una refactorización matemática con una refactorización visual en el mismo bloque salvo defecto explícito.

## Resultado esperado

No se promete imposibilidad absoluta de regresión. La garantía operativa de S26 será:
- aislamiento de capas;
- detección de cambios sensibles;
- cobertura funcional;
- recertificación completa antes del merge final.
