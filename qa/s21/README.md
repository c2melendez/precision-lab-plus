# S21 — Compatibilidad

Fuente normativa: Suite exhaustiva v2.0, Fase 16.

## CI obligatorio

La cobertura certificable de S21 combina:

- Chromium: suite Playwright principal ya existente, con desktop, tablet y móvil emulado.
- Firefox: smoke + flujo matemático crítico en desktop 1440×900.
- WebKit: smoke + flujo matemático crítico en iPhone 13 emulado.

Se ejecuta para Precision Lab Plus y para el SHA certificado de Precision Lab Lite.

## Flujo matemático crítico

El caso mínimo cross-browser debe atravesar el producto real:

1. carga del frontend;
2. health backend cuando aplica;
3. escritura en el math-field;
4. cálculo de `2+2`;
5. respuesta matemática correcta;
6. resultado visible;
7. ausencia de errores críticos del navegador.

Además se verifica apertura, navegación por categorías y cierre con Escape del teclado matemático.

## Release con dispositivos reales

La especificación exige, cuando exista device lab externo o runner físico disponible:

- Safari iOS reciente;
- Chrome Android reciente.

Este requisito se documenta como gate de release/manual-físico; el CI emulado no se presenta como sustituto de hardware real.

## Lite / PWA

Instalación, manifest, service worker y offline pertenecen al siguiente módulo S22. S21 solo certifica compatibilidad de navegador/dispositivo emulado.

## Evidencia previa

Lite `main` `9e75fc7447e62e09d6afe7a4b79d6a1b3302e843` ya tiene:
- CI Chromium: success.
- Playwright desktop/tablet/mobile Chromium: success.
- Cross-browser Firefox/WebKit: success.

El workflow S21 vuelve a ejecutar su cross-browser contra ese SHA junto con Plus para tener evidencia conjunta del módulo.
