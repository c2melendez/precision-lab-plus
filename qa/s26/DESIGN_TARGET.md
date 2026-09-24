# S26.2 — Diseño objetivo

Proyecto: **Precision Lab Plus**  
Branch: `qa/s26-execution`  
Estado: **CONTRATO VISUAL**

## 1. Principio rector

S26.2 reorganiza la interfaz sin cambiar el contrato matemático ni la API.

Plus debe compartir el mismo lenguaje visual y responsive de Lite, conservando sus ventajas propias:
- backend SymPy;
- resultados exactos/aproximados;
- pasos detallados;
- warnings y errores de API;
- tipos de resultado estructurados.

## 2. Shell global

### Header
Desktop/Laptop:
- workspace alineado a un máximo útil de ~1376 px;
- marca a la izquierda;
- Historial + Ajustes a la derecha;
- altura compacta.

Tablet/Mobile:
- controles táctiles >=44 px;
- evitar wrap irregular.

### Navegación
Orden:
1. Científica
2. Matrices
3. Gráficas
4. Estadística
5. Unidades

Desktop/Laptop: fila única.  
Tablet/Mobile: scroll horizontal preferido sobre wrap múltiple.

## 3. Workspace

Desktop 1440:
- ancho útil máximo ~1376 px;
- eliminar la sensación de formulario estrecho centrado cuando hay espacio;
- layouts de dos columnas cuando la función lo justifica.

Laptop 1280:
- dos columnas selectivas;
- gaps más compactos.

Tablet/Mobile:
- una columna;
- scroll interno para contenido ancho;
- sin overflow horizontal global.

## 4. Científica

La jerarquía primaria debe ser:
`Entrada → Resultado → Pasos → Gráfica`.

Desktop:
- campo activo amplio;
- resultado con mayor peso visual que controles de formato;
- selector exacto/dec/frac/scn como control secundario;
- botones copiar debajo del resultado;
- warnings visibles pero no dominantes;
- pasos detallados en timeline debajo del resultado;
- GraphPlaceholder como panel separado.

Mobile:
- preservar el resultado cerca de la expresión;
- formatos/copy pueden envolver de forma controlada;
- pasos debajo, sin columnas.

Errores de API:
- alerta dentro del flujo, cerca de la operación que falló;
- no desplazar todo el layout con una barra global innecesariamente grande.

## 5. Pasos Plus

Plus tiene prioridad especial en S26:
- StepList debe sentirse parte del resultado, no una segunda aplicación;
- título y descripción legibles;
- before → after alineado;
- pasos largos permiten wrap/scroll interno de matemáticas;
- regla técnica no se vuelve a exponer.

## 6. Matrices

Desktop:
- izquierda ~60%: operación, dimensiones, matrices, acción;
- derecha ~40%: resultado estructurado + pasos;
- resultados matriciales usan scroll interno si exceden ancho.

Tablet/Mobile:
- matrices primero;
- acción;
- resultado;
- pasos.

## 7. Gráficas

Desktop:
- rail de expresiones 260–300 px;
- canvas flexible;
- controles agrupados;
- análisis debajo o lateral secundario.

Tablet/Mobile:
- expresiones → canvas → análisis.

2D/paramétrica/polar/3D comparten shell visual. Los controles específicos aparecen solo cuando aplican.

## 8. Estadística

Unificar visualmente:
- Descriptiva
- Combinatoria
- Distribuciones
- Correlación

Desktop:
- shell común más ancho que el actual `max-w-3xl` cuando sea útil;
- forms complejos con dos columnas internas;
- ResultPanel como bloque de salida consistente.

Mobile:
- priorizar una columna;
- grids de botones 2 columnas cuando 3 comprometan targets táctiles.

## 9. Unidades

Mismo patrón que Lite:
Categoría → De/A → Valor → Resultado.

Desktop:
- card compacta, pero no artificialmente angosta.

Mobile:
- controles apilados;
- resultado destacado.

## 10. Historial

Desktop:
- drawer lateral 280–320 px;
- no sacrificar demasiado ancho del workspace.

Tablet/Mobile:
- overlay/drawer ancho;
- backdrop;
- Escape y restauración de foco existentes preservados.

## 11. Ajustes

Secciones:
- Tema
- Disposición
- Densidad
- Movimiento
- Paleta gráfica

Debe caber dentro del viewport mediante scroll interno.

## 12. Teclado virtual

- inicia colapsado siempre;
- no teclado fijo permanente;
- Desktop: panel inferior alineado al workspace, máximo ~45% viewport;
- Mobile: bottom sheet/panel con scroll;
- recientes asociados visualmente;
- pestañas completas;
- tooltips consistentes.

## 13. Seis layouts

### fused
Entrada + resultado integrados visualmente; gráfica separada.

### separated
Tarjetas independientes.

### split
Desktop 1440: entrada/historial izquierda, resultado/gráfica derecha.
Por debajo: una columna.

### focus
Sin historial de sesión embebido; resultado destacado; dock compacto.

### stacked
Flujo vertical; teclado inline colapsable.

### floating
>=1024: teclado y gráfica en ventanas flotantes persistidas.
<1024: degrada a Focus.

Todas deben compartir tokens y jerarquía.

## 14. Sistema visual

Plus y Lite deben converger en:
- radios;
- paddings;
- títulos de card;
- estados hover/focus;
- uso de marker/graph/alpha;
- alturas y separación del teclado;
- breakpoint behavior.

No es obligatorio que el tema default sea idéntico, pero una misma selección temática debe producir una identidad hermana reconocible.

## 15. Estados Plus

Cubrir:
- vacío;
- loading;
- éxito exacto;
- aproximado;
- fracción;
- matriz;
- soluciones de ecuación;
- procedimiento resumido;
- procedimiento detallado;
- warning;
- error API;
- contenido largo.

## 16. Accesibilidad

- contraste AA;
- focus-visible;
- aria-live existente;
- targets >=44 px en móvil;
- reduced-motion;
- semántica de tablas/matrices preservada.

## 17. Restricciones técnicas

No tocar sin defecto reproducible:
- `backend/app/services/**`
- `backend/app/routers/evaluate.py`
- `backend/app/services/parsing.py`
- `backend/app/services/ast_validator.py`
- `frontend/src/api/**`
- `frontend/src/types/api.ts`

S26.3 debe concentrarse en frontend visual/componentes/tokens.

## 18. Orden S26.3

1. Shell + navegación + workspace.
2. Científica + CalculatorScreen + ResultPanel + StepList + GraphPlaceholder.
3. Matrices.
4. Gráficas.
5. Estadística.
6. Unidades.
7. Historial + Ajustes.
8. Teclado + responsive.
9. Armonización final de seis layouts.

Cada bloque requiere test funcional + evidencia visual.

## 19. Criterio de aceptación S26.2

S26.2 queda aprobado cuando:
- todas las superficies visibles tienen composición objetivo;
- los cuatro viewports están definidos;
- los seis layouts tienen regla explícita;
- estados propios de Plus están contemplados;
- no quedan decisiones visuales críticas que bloqueen S26.3.
