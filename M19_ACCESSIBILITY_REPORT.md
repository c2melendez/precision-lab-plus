# M19 — Auditoría formal de accesibilidad

Estado: en validación final.

## Alcance
- WCAG 2.x / 2.1 / 2.2 A/AA mediante axe-core 4.13.0.
- Desktop 1440, tablet 1024 y móvil Pixel 7.
- Landmarks, skip-link, navegación por teclado, foco y Escape.
- Modos visibles: Científica, Matrices, Gráficas, Estadística y Unidades.
- Validación explícita del nombre accesible de cada `math-field`.

## Correcciones realizadas
- Destino del skip-link programáticamente enfocable.
- Historial: Escape, foco inicial en móvil/tablet y restauración del foco al disparador.
- Contraste de tokens y controles detectados por axe.
- Contraste de controles de gráficas y teclado.

## MathLive
El componente `math-field` público se valida explícitamente por nombre accesible. Se excluye únicamente el Shadow DOM interno de MathLive del escaneo axe porque su `keyboard-sink` es markup de terceros no controlado por Precision Lab.

La evidencia final de CI/E2E se completará antes de fusionar M19.
