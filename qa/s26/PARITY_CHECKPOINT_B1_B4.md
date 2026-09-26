# S26.3R — Checkpoint de Paridad Bloques 1–4

Fecha de preparación: 2026-09-26  
Branch: `qa/s26-execution`

## Objetivo
Antes de iniciar el Bloque 5, auditar paridad real Lite ↔ Plus en los Bloques 1–4.

Clasificación:
- **PARIDAD**
- **DIFERENCIA INTENCIONAL**
- **GAP**

## HEAD de código certificado previo al checkpoint
- Lite: `c878da8183cdab6ca791afcacee6841199a5c067`
- Plus: `40fcf3b3aa2d83fa58943fec603198dd0bb291bb`

Los commits documentales posteriores no sustituyen estos HEAD.

## Bloque 1 — Shell / Sidebar / Identidad
Verificar orden contractual; 240/72 px; auto-colapso <1200; restauración de preferencia; PL/PL+; iconos; Historial/Configuración abajo; H1 accesible; convivencia con teclado; cuatro viewports.

## Bloque 2 — Configuración
Verificar ventana independiente; Claro/Oscuro/Sistema; sidebar sensible al tema; Default=fused, Compacto=stacked, Lateral=split; migración legacy a fused; instalación nueva split; X/Escape/foco; responsive.

## Bloque 3 — Historial
Verificar operación natural; módulo de origen; fecha/hora; matrices; resultado natural; Reusar; routing; autofill; integral completa; reutilización dentro del módulo actual.

Diferencia conocida: Geometría/Unidades aún no alimentan Historial con la misma cobertura completa.

## Bloque 4 — Resultados
Verificar encabezado único; caja equivalente; alineación derecha; escala equivalente; selector contextual; Exacto/Decimal/Fracción/Científica cuando apliquen; mixta/impropia; estructurados; DD/DMS exclusivo para grados; RAD normal.

Diferencias intencionales:
- Plus: Pasos, Resumen, warnings, Copiar.
- Lite: fallback numérico local.

## Regla angular
Salida angular en grados → solo:
- DD: `56.55°`
- DMS: `56° 33′ 0.0″`

No mostrar Exacto/Decimal/Fracción/Científica en ese contexto.

## Método
Contrato → Lite → Plus → pruebas → runtime visual → responsive → accesibilidad → clasificación.

## Regla de salida
No iniciar Bloque 5 hasta cerrar la matriz, corregir GAPs y recertificar si hubo cambios.

Siguiente bloque: **Bloque 5 — teclado global: shell, apertura/cierre y responsive.**

## Resultado del checkpoint — 2026-09-26

Estado: **PASS — sin GAPs bloqueantes detectados en B1–B4**.

Clasificación consolidada:
- B1 Shell / Sidebar / Identidad — **PARIDAD**.
- B2 Configuración / Apariencia / Layout — **PARIDAD**.
- B3 Historial — **PARIDAD**, con la diferencia conocida de cobertura incompleta de Geometría/Unidades documentada como limitación vigente, no divergencia entre motores.
- B4 Resultado + formatos — **PARIDAD** en presentación común y política DD/DMS; diferencias de Plus (Pasos, Resumen, warnings, Copiar) y Lite (fallback numérico local) se mantienen como **DIFERENCIAS INTENCIONALES**.

Evidencia de revisión:
- shell 240/72 px, auto-colapso <1200 y H1 accesible equivalente;
- modal de Configuración y modal de Historial con Escape/restauración de foco equivalentes;
- stores de reutilización de Historial equivalentes;
- política `getAvailableResultFormats` idéntica: si hay magnitud angular en grados, expone solo `DD` y `DMS`;
- conversión DD↔DMS e identificación de inversas trigonométricas idénticas en ambos proyectos.

Decisión:
- checkpoint B1–B4 **CERRADO**;
- Bloque 5 **DESBLOQUEADO**;
- no se requirió modificar rutas matemáticas protegidas durante el checkpoint.
