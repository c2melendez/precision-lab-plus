# S26 — Log de ejecución

## Sesión

Fecha: 2026-09-23  
Proyecto: **Precision Lab Plus**  
Branch: `qa/s26-execution`  
Baseline funcional protegido previo a S26: `5de721e32c13a60f77671cd2bd98a8cc05cf0140`  
SHA de preparación S26 integrado en main: `d9db58881be0704520c634032c45e5318dc35307`

## Estado del módulo

- [x] Preparación documental S26 integrada en `main`.
- [x] Política de integridad matemática definida.
- [x] Hoja de ruta y handoff definidos.
- [x] Inventario de superficies reales creado en `INVENTORY.md`.
- [x] Matriz visual ampliada a superficies, estados, layouts y personalización reales.
- [x] Suite `frontend/e2e/s26-baseline.spec.ts` añadida para baseline reproducible.
- [x] S26.0 — Baseline y congelamiento: **CERRADO**.
- [x] S26.1 — Inventario y matriz: **CERRADO**.
- [ ] S26.2 — Diseño objetivo.
- [ ] S26.3 — Implementación por bloques.
- [ ] S26.4 — Regresión visual automatizada.
- [ ] S26.5 — Recertificación matemática.
- [ ] S26.6 — Cierre.

## Decisiones vigentes

1. S26 no se limita a la pantalla científica.
2. El alcance visual primario se basa en superficies actualmente visibles, no en componentes muertos/ocultos.
3. Los modos internos deliberadamente ocultos conservan smoke funcional para detectar regresiones por componentes compartidos.
4. Se cubrirán Desktop 1440×900, Laptop 1280×800, Tablet 768×1024 y Mobile 390×844.
5. Existen seis layouts transversales: `fused`, `separated`, `split`, `focus`, `stacked`, `floating`.
6. Tema, densidad, movimiento y paleta gráfica se cubren mediante estrategia combinatoria controlada; no se multiplica cada pantalla por todas las combinaciones.
7. La capa matemática queda congelada salvo defecto reproducible y documentado.
8. Una captura visual nunca sustituye una prueba funcional.
9. Antes del cierre se ejecutará recertificación matemática completa.

## S26.0 — Baseline y congelamiento

### Completado
- Branch de ejecución creada desde el `main` posterior a la preparación S26.
- Baseline funcional previo a S26 registrado y protegido.
- Rutas matemáticas protegidas definidas en `MATHEMATICAL_INTEGRITY_POLICY.md`.
- PR S26 de ejecución abierto como draft para impedir cierre prematuro.
- Suite de baseline añadida: cinco superficies visibles × cuatro viewports.
- Captura adicional de historial, ajustes y teclado.
- Cobertura de seis layouts en Desktop/Mobile.
- Captura explícita de `floating` a 1023 px y 1024 px.

### Validación final
- CI: PASS.
- Playwright E2E: PASS.
- S19 Mutation Baseline: PASS.
- S20 Performance Robustness: PASS.
- S21 Cross-browser Compatibility: PASS.
- S23 Accessibility Gate: PASS.
- S25 Security Gate: PASS.
- Evidencia visual adjunta al reporte Playwright mediante `testInfo.attach`.

## S26.1 — Inventario y matriz

### Completado
- Inventario de navegación visible real.
- Inventario de modos internos/no visibles.
- Inventario de historial, ajustes y teclado.
- Identificación de seis layouts globales.
- Definición de cuatro viewports oficiales.
- Estrategia combinatoria para temas/densidad/movimiento/paletas.
- Matriz ampliada con estados funcionales y cobertura transversal.

### Cierre S26.1
- Baseline runtime confirmado en PASS.
- Matriz enlazada a pruebas funcionales mediante `TEST_MAPPING.md`.
- No se detectaron regresiones funcionales ni cambios en rutas matemáticas protegidas.
- Siguiente fase: S26.2 Diseño objetivo.

## Rutas protegidas tocadas

Ninguna.

## Cambios funcionales

Ninguno. S26 sigue limitado a QA/documentación; no se ha modificado producto ni motor matemático.

## Instrucción de continuidad

S26.0 y S26.1 están cerrados. Continuar con S26.2 — Diseño objetivo, sin modificar rutas matemáticas protegidas.

## S26.3 — Implementación por bloques

### Bloque 1 — Shell, identidad, navegación y teclado global — CERRADO
- Navegación final: Científica → Matrices → Gráficas → Estadística → Geometría → Unidades.
- Identidad persistente PL / PL+ integrada.
- Geometría incorporada como sexto módulo visible.
- Teclado existente reutilizado como entrada global; no se duplicó la botonería.
- Científica conserva prioridad sobre su teclado propietario.
- Accesibilidad y semántica de marca preservadas.
- Regresiones detectadas y corregidas: contraste del monograma Lite, h1 de branding Plus y selectores ambiguos de Matrices.
- Gates posteriores al bloque: PASS completos en ambos repos.

### Bloque 2 — Científica / Entrada / Resultado / Pasos / Formatos — EN CURSO
Objetivos:
- conservar dec / frac / scn / exacto-radical;
- añadir presentación mixta cuando el racional impropio lo permita;
- añadir presentación DMS cuando el valor sea angular y tenga simbología válida;
- no introducir ceros finales innecesarios;
- preservar resultados exactos y aproximados;
- armonizar Entrada / Resultado / Pasos con el contrato visual;
- no tocar motor matemático salvo defecto reproducible.

### Excepción documentada — trigonometría inversa en DEG/GRAD
Motivo: ampliación funcional explícitamente aprobada durante S26.3.

Cambio matemático:
- RAD conserva salidas de las seis trigonométricas inversas convencionales en radianes.
- DEG/GRAD devuelve en grados sexagesimales las salidas de seno/coseno/tangente inversos y secante/cosecante/cotangente inversos.
- Las salidas angulares en grados pueden alternarse a DMS.
- Las trigonométricas directas conservan su semántica de entrada por modo angular.

Rutas protegidas modificadas:
- `backend/app/services/evaluate_service.py`

Pruebas añadidas:
- `backend/tests/test_exhaustive_module01_trigonometry.py`
- `frontend/src/__tests__/ResultPanel.test.tsx`

Criterio de aceptación:
- las seis trigonométricas inversas convencionales en DEG/GRAD devuelven grados.
- composición directa(inversa) conserva resultado correcto.
- RAD no cambia.
- UI etiqueta grados con `°` y ofrece DMS solo cuando el resultado es angular.

### Plantillas visuales DEG/GRAD
- En DEG/GRAD, el teclado inserta `°` dentro del argumento de sin/cos/tan/sec/csc/cot.
- En RAD, conserva la plantilla sin `°`.
- El placeholder permanece antes del símbolo de grado.
- Las inversas no reciben `°` en el argumento; su salida se expresa en la unidad angular activa.
- Las pruebas cubren teclado, escritura manual sin `°`, símbolo explícito `°` y ausencia de doble conversión.

### Subbloque angular — CERRADO
Estado: PASS completo en Lite y Plus.

Alcance certificado:
- RAD/DEG/GRAD coherente para trigonometría directa.
- Plantillas visuales con `°` dentro del argumento en DEG/GRAD.
- RAD conserva plantillas sin `°`.
- Las seis trigonométricas directas están cubiertas: sin/cos/tan/sec/csc/cot.
- Las seis inversas convencionales devuelven la unidad angular activa.
- DEG/GRAD etiqueta salida con grados y habilita DMS.
- RAD conserva radianes.
- Símbolo `°` explícito entendido por ambos motores sin doble conversión.
- Casos decimales de inversas cubiertos, incluyendo `asin(0.5)` y `arcsin(0.5)`.
- Composiciones como `sin(asin(0.5))` preservan semántica correcta.
- CI, Playwright, diferencial, mutación, fuzzing, rendimiento, cross-browser, accesibilidad y seguridad: PASS.


### Subbloque Resultado + Formatos — CERRADO
Estado: PASS completo en Lite y Plus.

Certificado:
- jerarquía visual de Resultado alineada;
- selector de formatos convertido a chips sin cambiar nombres ni acciones;
- DMS contextual preservado;
- fracción mixta/impropia preservada;
- aviso de fallback numérico Lite preservado como contrato funcional;
- región accesible Resultado Plus sin duplicación;
- CI, Playwright y gates aplicables: PASS.


### Subbloque Entrada + Pasos — CERRADO
Estado: PASS completo en Lite y Plus.

Certificado:
- superficie visual de Entrada alineada entre ambos proyectos;
- jerarquía Entrada → Resultado → Formatos → Pasos consistente;
- timeline de Pasos numerado y visualmente homologado;
- contratos accesibles preservados;
- layouts split/focus/floating/stacked/separated/fused sin regresiones funcionales;
- corrección adicional en Plus para EDO y'=2x y serializaciones MathLive equivalentes (y′, y^{\\prime}, y^′);
- Playwright E2E, CI, mutación, diferencial, fuzzing, rendimiento, cross-browser, accesibilidad y seguridad: PASS.


### Subbloque Gráficas — shell + selector + rail/visor base — CERRADO
Estado: PASS completo en Lite y Plus.

Certificado:
- shell visual de Gráficas ampliado y alineado al workspace S26;
- selector de tipo 2D/Polar/Paramétrica/3D armonizado;
- Lite: rail de expresiones separado de la superficie de vista/análisis;
- semántica accesible del selector preservada sin romper contratos E2E;
- Plus: corrección de JSX en AnalysisPanel verificada;
- CI, Playwright, accesibilidad, cross-browser, seguridad y gates aplicables: PASS.


### Subbloque Gráficas 2D Plus — CERRADO
Estado: PASS completo.

Certificado:
- rail izquierdo para expresiones, teclado y controles;
- visor/análisis separado en columna derecha en desktop;
- degradación a una columna en tablet/móvil;
- endpoints, payloads, ResultArea, GraphViewer y análisis preservados;
- CI, Playwright, S17, S18, S19, S20, S21, S23 y S25: PASS.


### Subbloque Gráficas Polar + Paramétrica + 3D Plus — CERRADO
Estado: PASS completo.

Certificado:
- formularios Polar, Paramétrica y 3D reorganizados en rail de controles + visor/resultado;
- una columna en tablet/móvil;
- IDs, labels, botones, endpoints y payloads preservados;
- sin cambios en backend ni lógica matemática;
- CI, Playwright, S17, S18, S19, S20, S21, S23 y S25: PASS.


### Decisión de proceso — Preview S26 incorporado
Se añade formalmente **S26.3.5 — Preview S26** entre implementación (S26.3) y regresión visual automatizada (S26.4).

Motivo:
- permitir revisión visual humana del rediseño antes de congelar baselines;
- mantener producción estable durante la implementación;
- separar claramente producción, preview y rama de trabajo.

Regla acordada:
- el preview puede habilitarse cuando Gráficas + Matrices estén rediseñadas y verdes;
- el preview no sustituye pruebas ni baselines;
- cualquier ajuste derivado del preview debe aplicarse antes de S26.4.


### Subbloque Gráficas — visor + análisis Plus — CERRADO
Estado: PASS completo.

Certificado:
- AnalysisPanel reorganizado como sección visual coherente con S26;
- tarjetas por expresión y jerarquía de métricas mejoradas;
- datos, endpoints y cálculo sin cambios;
- integración visual compatible con 2D, Polar, Paramétrica y 3D;
- CI, Playwright, S17, S18, S19, S20, S21, S23 y S25: PASS.


### Bloque Gráficas — CERRADO
Estado: PASS completo en Lite y Plus.

Cobertura certificada:
- shell visual y selector 2D / Polar / Paramétrica / 3D;
- rail de expresiones/controles y visor separado;
- Gráficas 2D Plus reorganizadas y certificadas;
- Polar, Paramétrica y 3D Plus armonizadas y certificadas;
- visor y análisis Plus armonizados;
- análisis Lite armonizado con el mismo lenguaje visual;
- responsive preservado para desktop, tablet y móvil;
- endpoints, payloads, cálculo y motores sin cambios funcionales;
- gates aplicables completos en verde.

Siguiente bloque: Matrices.

### Subbloque Matrices — shell visual base — CERRADO
Estado: PASS completo en Lite y Plus.

Certificado:
- shell principal reorganizado al patrón S26;
- entrada y resultado separados visualmente;
- responsive desktop/tablet/móvil preservado;
- overflow móvil de Lite corregido;
- operaciones, payloads, worker/API y lógica matemática sin cambios;
- gates aplicables completos en verde.


### Subbloque Matrices — cuadrículas y contención responsive — CERRADO
Cambios:
- cuadrículas agrupadas en tarjetas visuales;
- dimensiones visibles de forma compacta;
- scroll horizontal contenido dentro de la tarjeta cuando una matriz grande no cabe;
- mejora de etiquetas accesibles de celdas en Lite;
- sin cambios en operaciones, API/worker ni motor matemático.

Estado:
- Lite: PASS completo.
- Plus: PASS completo, incluido S19 Mutation Baseline.

### Bloque Matrices — CERRADO
Estado: PASS completo en Lite y Plus.

Cobertura cerrada:
- shell S26;
- entrada/resultado separados;
- cuadrículas y dimensiones refinadas;
- contención responsive de matrices grandes;
- banco A–F y expresión matricial preservados en Lite;
- operaciones existentes preservadas en Plus;
- sin cambios en motores matemáticos;
- todos los gates aplicables en verde.

Hito alcanzado: Gráficas + Matrices cerradas y verdes.
Siguiente paso de proceso: S26.3.5 — Preview S26.

### S26.3.5 — Preview S26 — REVISIÓN HUMANA: FAIL VISUAL

Fecha: 2026-09-24.

La revisión humana del preview Plus detectó discrepancias entre la implementación visible y los contratos `DESIGN_TARGET.md` / `KEYBOARD_CONTRACT.md`.

Hallazgos confirmados:
- teclado global duplicado al abrirse: se renderizaban `basicContent` y `content` simultáneamente;
- Gráficas mantenía un `NaturalMathKeyboard` inline, creando un segundo teclado específico del módulo y contradiciendo el contrato de teclado global único;
- Científica aún no presenta de forma satisfactoria la jerarquía Entrada → Resultado → Pasos → Gráfica acordada;
- Estadística y Unidades siguen pendientes de rediseño S26 y aparecen visualmente como generación anterior;
- Geometría es una base parcial, no un módulo visual terminado;
- la armonización transversal de los seis layouts aún no puede considerarse cerrada.

Decisión:
- NO avanzar a S26.4;
- reabrir aceptación visual de Científica/Teclado y Gráficas;
- mantener Matrices funcionalmente verde, pero su aceptación visual final queda condicionada a la corrección del dock/teclado global;
- completar Estadística, Unidades, Historial/Ajustes y responsive antes de una nueva aprobación humana del Preview;
- los cierres anteriores conservan valor como certificación funcional, pero NO constituyen aprobación visual final.

Correcciones iniciadas:
- render exclusivo de `content ?? basicContent` para impedir duplicación de teclado;
- layouts stacked/floating ajustados al mismo criterio;
- Gráficas 2D/3D/Paramétrica/Polar migradas del teclado inline al teclado global único.

### Cierre de sesión / Handoff — 2026-09-24

Estado de proceso: **PAUSA CONTROLADA PARA RECONFIRMACIÓN VISUAL S26.2R**.

La sesión se cierra deliberadamente para continuar en otra conversación sin perder trazabilidad.

#### Regla de reanudación
La próxima sesión **NO debe empezar modificando código**.

Primero debe:
1. leer `MOCKUP_REGENERATION_BRIEF.md`;
2. regenerar mockups definitivos consolidados;
3. mostrar teclado colapsado y desplegado;
4. reconciliar todos los módulos y breakpoints;
5. presentar al usuario;
6. esperar aprobación explícita.

Solo tras la aprobación se retoma S26.3.

#### Estado de código de referencia
Último SHA de producto relevante antes del cierre documental:
`75d816b8e74acfe1b91661e02843966719e7fcc0`

Preview:
https://precision-lab-plus-s26.onrender.com

#### Estado técnico
- Revisión humana Preview: FAIL visual.
- Teclado duplicado corregido en arquitectura compartida.
- Layouts stacked/floating ajustados a `content ?? basicContent`.
- Gráficas migradas del teclado inline al teclado global único.
- Teclado Desktop limitado a ~45vh.
- Regresión TypeScript por cuatro `setActiveMode` sin uso corregida.
- Último estado consultado: CI, Playwright, S17, S18, S20, S21, S23 y S25 PASS; S19 Mutation Baseline seguía in_progress.
- Preview Render separado de producción; API Preview: https://precision-lab-plus-s26-api.onrender.com.

#### Decisión sobre el teclado
El teclado visible actualmente en Preview **NO constituye el diseño visual final aprobado**.

Debe conservarse su funcionalidad/paridad, pero su composición visual deberá adaptarse al próximo mockup definitivo. El contrato final del teclado se congelará únicamente después de la revisión del usuario.

#### Documentos de continuidad obligatorios
- `qa/s26/HANDOFF_PROMPT.md`
- `qa/s26/MOCKUP_REGENERATION_BRIEF.md`
- `qa/s26/VISUAL_REFERENCE_CHECKLIST.md`
- `qa/s26/ROADMAP.md`
- `qa/s26/KEYBOARD_CONTRACT.md`
- `qa/s26/DESIGN_TARGET.md`
- `qa/s26/RESULT_FORMATS.md`
- `qa/s26/GRAPH_3D_CONTRACT.md`
- `qa/s26/GEOMETRY_CONTRACT.md`
- `qa/s26/BRAND_IDENTITY.md`
- `qa/s26/MATHEMATICAL_INTEGRITY_POLICY.md`
- `qa/s26/TEST_MAPPING.md`

#### No cerrar
- S26.3: no cerrado visualmente.
- S26.3.5 Preview: revisión humana FAIL visual.
- S26.4: NO iniciar.
- S26.5: pendiente.
- S26.6: pendiente.



## S26.3R — Bloque 1 — Shell + Sidebar + Identidad visual — PASS DEFINITIVO

Fecha de cierre: 2026-09-25.

Contrato aplicado:
- navegación lateral azul contractual;
- orden visible: Científica → Gráficas → Matrices → Estadística → Geometría → Unidades;
- identidad PL / PL+ persistente;
- nombre completo visible en estado expandido;
- icono de producto visible también en estado compacto;
- paridad de iconos entre Lite y Plus, con Geometría = cubo;
- Historial y Configuración anclados en la zona inferior;
- dock/panel de teclado reconciliados para no invadir el sidebar;
- auto-colapso responsive por debajo de 1200 px;
- preferencia manual restaurada cuando vuelve a existir ancho suficiente;
- H1 de producto preservado de forma accesible en estado compacto.

HEAD certificado:
- Lite: `fa0ede18dfa67ef8e384f4b2f2170b074722520f`;
- Plus: `09deab33673a035a0327234ee29c6a95a2df5b21`.

Gates:
- Lite: CI, Playwright E2E, S22 PWA Offline, S23 Accessibility, S25 Security y Cross-browser smoke: PASS.
- Plus: CI, Playwright E2E, S17, S18, S19, S20, S21, S23 y S25: PASS.

Decisión:
- Bloque 1 queda congelado salvo defecto reproducible.
- Siguiente bloque contractual: Configuración + Apariencia + selector de layouts.


## S26.3R — Estado certificado Bloques 2–4 — 2026-09-26

### Bloque 2 — Configuración — PASS DEFINITIVO
Ventana independiente; Claro/Oscuro/Sistema; sidebar sensible al tema; Default=fused, Compacto=stacked, Lateral=split; legacy → fused; instalación nueva split; foco/cierre/responsive preservados.

HEAD histórico:
- Lite: `3ceff37f912cb66c3cb46a8e21de46843cdb387f`
- Plus: `ee6136235af29cc52336c16c2c44aadfbd574722`

### Bloque 3 — Historial — PASS DEFINITIVO
Operaciones naturales; módulo de origen; matrices; fecha/hora; resultado natural; Reusar; routing/autofill; integral completa al reutilizar; E2E/gates completos.

HEAD histórico:
- Lite: `167df02c734543e093eca726ca9e06488acfb58f`
- Plus: `d1ca0ac6226f8d68c0c85a510f70d1e0fdf5873f`

### Bloque 4 — Resultado + formatos — PASS DEFINITIVO
Selector común; etiquetas naturales; formatos contextuales; mixta/impropia; estructurados Plus; encabezado único; alineación/escala armonizadas; región semántica preservada; DD/DMS exclusivo para grados.

HEAD certificado:
- Lite: `c878da8183cdab6ca791afcacee6841199a5c067`
- Plus: `40fcf3b3aa2d83fa58943fec603198dd0bb291bb`

Gates Lite: CI, Playwright, S22, S23, S25, Cross-browser — PASS.
Gates Plus: CI, Playwright, S17, S18, S19, S20, S21, S23, S25 — PASS.

### Próximo paso obligatorio
Ejecutar `PARITY_CHECKPOINT_B1_B4.md`. No iniciar Bloque 5 antes de cerrar la auditoría.


## 2026-09-26 — Checkpoint B1–B4 cerrado / inicio B5

- Se ejecutó reconciliación estática Lite ↔ Plus contra `PARITY_CHECKPOINT_B1_B4.md`.
- Resultado: **PASS sin GAPs bloqueantes** en B1–B4.
- B1/B2/B3/B4 mantienen paridad contractual; las diferencias documentadas de capacidades Plus/Lite permanecen intencionales.
- Regla angular verificada por código compartido equivalente: salida en grados expone solo DD/DMS; RAD conserva formatos numéricos normales.
- No se modificaron rutas matemáticas protegidas durante el checkpoint.
- Bloque 5 quedó **DESBLOQUEADO / EN CURSO**.
- Alcance B5: shell global del teclado, apertura/cierre y responsive. La paridad de las seis categorías se reserva para B6.
- Se añadió `frontend/e2e/s26-b5-keyboard-shell.spec.ts` como gate específico de B5: cerrado inicial, apertura, cierre por botón, cierre por Escape, contención en viewport y límite de altura por breakpoint.


## 2026-09-26 — Regresión B3/B4 Plus detectada por revisión humana

- Preview demostró una divergencia real no detectada por revisión estática.
- Caso: `sin⁻¹(1)` en DEG.
- Resultado principal: `90°` correcto.
- Historial previo: `asin(1)` + representación simbólica interna; Reusar degradaba la expresión.
- Se reabren B3/B4 y se pausa B5.
- Correcciones: `HistoryEntry.resultApprox`, `submitAndRecord(..., historyInputText?)`, preservación del LaTeX visible, normalización natural de inversas y gate E2E de reuso.
- Cierre condicionado a CI + Playwright + Preview.


## 2026-09-26 — Reintento Plus tras fallo de integral histórica

- CI y todos los gates no-E2E quedaron verdes.
- El nuevo caso `sin⁻¹(1)` DEG → Historial natural + `90°` → Reusar natural pasó en Desktop/Tablet/Mobile.
- El gate B5 del shell del teclado también pasó en Desktop/Tablet/Mobile.
- Playwright falló únicamente en el test histórico de integral completa: recibió `∫x**2/4` en vez de reconstruir `\\int ... dx`.
- Causa: la nueva prioridad de `inputText` aceptó una etiqueta histórica parcial de operación estructurada.
- Corrección: solo reutilizar literalmente `inputText` en operaciones estructuradas cuando ya contiene LaTeX completo; si no, reconstruir desde `requestPayload`.
- Nuevo commit de corrección: `677c70717a83c4861b74649968089e052fa5e52d`.


## 2026-09-26 — B3/B4 recertificados, B5 reanudado

- HEAD recertificado: `c82779a8b411e7b0a695e3e873e94bf24516e145`.
- CI, Playwright, S17, S18, S19, S20, S21, S23 y S25: PASS.
- Regresión de `sin⁻¹(1)` en DEG cerrada.
- Reuso de integral completa nuevamente PASS.
- B3/B4 cerrados; B5 reanudado.


## 2026-09-26 — B5 shell/responsive Plus armonizado

- Auditoría Lite↔Plus encontró offset Desktop fijo en Plus frente a anclaje real del dock en Lite.
- `KeyboardDock` Plus ahora mide el borde superior real del dock con ResizeObserver + resize y entrega offset al panel.
- `KeyboardPanel` usa `--keyboard-panel-bottom` dinámico en Desktop.
- Playwright B5 ahora exige 12 px entre panel y dock.
- M11 Plus ahora verifica que Compacto abre teclado inline y no dentro de contenedor fixed.
- B5 Plus también verifica apertura/cierre global en los seis módulos.
- B6 (contenido/paridad de categorías) no fue modificado.


## 2026-09-26 — B5 rerun 1: hallazgos CI/Compacto

- CI frontend falló porque `ResizeObserver` no existe en JSDOM; Stryker reprodujo el mismo fallo en dry-run.
- Playwright B5 shell/global pasó en Desktop/Tablet/Mobile.
- Playwright M11 Compacto falló porque Plus no exponía el teclado inline con `role=region`/`aria-label=Teclado matemático`, aunque el contenido sí se renderizaba inline.
- Correcciones aplicadas: fallback opcional de `ResizeObserver`; semántica accesible de Compacto alineada con Lite.
- B5 permanece EN CURSO hasta rerun verde.


## 2026-09-26 — Cierre B5

- HEAD certificado: `17bb72b5e12cd6fb0d1961459dae80631ca3766b`.
- Todos los gates relevantes quedaron verdes, incluido S19 Mutation Baseline.
- Se cerraron los GAPs de offset Desktop, semántica accesible de Compacto y fallback de `ResizeObserver`.
- El teclado global fue validado en Científica, Gráficas, Matrices, Estadística, Geometría y Unidades.
- B5: **PASS DEFINITIVO**.
- Próximo bloque: B6 — inventario/paridad de Básico, Símbolos, Álgebra, Trigonométricas, Cálculo y Complejos.


## 2026-09-26 — Inicio B6 con autoridad visual aprobada

- Decisión explícita: usar `Mockups definitivos de Precision Lab.png` junto con `VISUAL_CONTRACT_FINAL_S26_2R.md` como autoridad visual.
- `KEYBOARD_CONTRACT.md` queda como autoridad funcional/semántica.
- Se elimina como requisito previo regenerar el mockup: la captura aprobada ya existe.
- Próximo trabajo: reconciliación categoría por categoría y tecla por tecla Lite↔Plus.


## 2026-09-26 — B6 Básico implementado

- Se reconciliaron Lite y Plus contra captura + contrato.
- Se congelaron 31 teclas y sus cuatro filas mediante tests.
- Plus recibió tooltips descriptivos faltantes.
- Enter quedó como glyph visual común; `=` conserva inserción sin ejecución.
- Lite dejó la gramática dark legacy del panel Básico y usa tokens `paper/marker/graph` equivalentes a Plus.
- Se creó `B6_BASIC_RECONCILIATION.md`.
- No avanzar a Símbolos hasta revisar gates y Preview de este subbloque.


## 2026-09-27 — B6 teclado unificado: cierre de sesión

### Resultado
- Reconciliada arquitectura visual con captura aprobada: familias superiores, subcategorías separadas, panel contextual y núcleo debajo.
- Eliminada interpretación previa izquierda/centro/derecha.
- Eliminada tira global f(x)=0 / Sistema / Simplificar en B6; acciones restringidas a Álgebra → Ecuaciones.
- Selector de sistemas 2–5 restaurado dentro de Ecuaciones.
- SmartDock Recientes / Var./const. retirado de dock, Apilado y Flotante.
- Ajustadas suites heredadas a navegación familia → subcategoría → tecla.
- Corregido contraste de subcategoría activa en Plus.
- B6 Basic histórico marcado como supersedido.

### HEAD certificado
`a61f57f5a234723a199ca3afaa273ab826c6d7ec`

### Gates
- CI — PASS
- Playwright E2E — PASS
- S17 API fuzzing — PASS
- S18 Differential Properties — PASS
- S19 Mutation Baseline — PASS
- S20 Performance Robustness — PASS
- S21 Cross-browser Compatibility — PASS
- S23 Accessibility — PASS
- S25 Security — PASS

### Estado
**B6 PASS AUTOMATIZADO.** Falta únicamente revisión visual humana final de las últimas correcciones antes de declarar PASS DEFINITIVO y abrir B7.


## Cierre técnico B6 — 2026-09-27

HEAD certificado: `a61f57f5a234723a199ca3afaa273ab826c6d7ec`.

Cambios consolidados:
- jerarquía final: familias arriba → subcategorías → teclas contextuales → núcleo básico debajo;
- Básico dejó de ser pestaña; núcleo canónico de 23 teclas;
- una sola subcategoría visible a la vez;
- Enter virtual y físico comparten flujo;
- `=` solo inserta;
- `EXP` retirada y `^` conservado;
- MCM/MCD de aridad variable;
- `sgn` y `mod` conservadas;
- límites x→a, x→∞, x→a⁻ y x→a⁺;
- hiperbólicas inversas conservadas;
- Símbolos ampliados con variables/parámetros y `τ`;
- selector de sistema 2–5 dentro de Álgebra → Ecuaciones;
- tira global f(x)=0 / Sistema / Simplificar retirada de B6;
- SmartDock Recientes / Var./const. retirado de la UI;
- suites unitarias/E2E heredadas reconciliadas con familia → subcategoría → tecla;
- accesibilidad/contraste recertificados.

Gates:
CI, Playwright E2E, S17 API fuzzing, S18 Differential Properties, S19 Mutation Baseline, S20 Performance Robustness, S21 Cross-browser Compatibility, S23 Accessibility y S25 Security: PASS.

Estado:
**B6 PASS AUTOMÁTICO / pendiente confirmación visual humana final**.

La próxima sesión debe iniciar con revisión visual, no con nueva implementación.


## 2026-09-27 — B6 PASS DEFINITIVO / apertura B7

- Revisión humana final del teclado aprobada.
- Paridad visual Lite/Plus cerrada: familias, subcategorías, Básico, contextuales, densidad, tamaños, ODE, Complejos y responsive.
- Contraste de subcategoría activa corregido y recertificado.
- HEAD certificado B6: `e74865bb8ea52513f57e9d115cda1bd1e915ab36`.
- Gates: CI, Playwright E2E, S17 API fuzzing, S18 Differential Properties, S19 Mutation Baseline, S20 Performance Robustness, S21 Cross-browser Compatibility, S23 Accessibility y S25 Security: PASS.
- B6: **PASS DEFINITIVO**.
- B7 — Científica: **EN CURSO**.
- Política B7: no tocar motor matemático salvo defecto reproducible.

## 2026-09-28 — B7 Plus: regiones y acciones de copia

- En el HEAD `11fc106`, `App.tsx` nombraba `Resultado` a la envoltura de todo el modo activo y `ResultPanel` nombraba igual a su propia región. Esto explica la duplicación detectada por S23 y Playwright; no dependía de un merge ref distinto.
- La envoltura de `App` ahora es un `div` neutro. `ResultPanel` conserva su región `Resultado` y su anuncio de cambios.
- Los botones mantienen texto compacto `Copiar` / `LaTeX` y exponen nombres accesibles `Copiar resultado` / `Copiar como LaTeX`. Se actualizaron las aserciones unitarias que dependían del nombre anterior.
- Verificación local: `npm run build` PASS; `ResultPanel.test.tsx` 25/25 PASS. Pendiente certificar S23, S21 y Playwright completos en Actions; B7 sigue EN CURSO.
- Primer commit remoto `d4a8666`: S21 PASS. S23 falló en una aserción heredada que exigía un descendiente `aria-live`; tras eliminar la región externa redundante, la propia región Resultado lleva `aria-live="polite"`. Se ajusta la prueba para comprobar el atributo del elemento semántico real. Playwright completo seguía en ejecución al momento de este ajuste.
- Commit `b1d3aa1`: CI, S17–S21, S23 y S25 PASS. Playwright E2E: 229 PASS, 4 SKIP, 10 FAIL agrupados en cuatro pruebas. S23 se corrigió; Argand esperaba el botón antiguo `Graficar` aunque B7 usa `Abrir en Gráficas`; B5 esperaba un margen de 12 px ya retirado; la prueba de gráfica/teclado comparaba la posición inicial de una superficie apilada fuera del viewport con el panel fijo. Se reconciliaron esas aserciones conservando la validación funcional Argand y la posibilidad de desplazar la gráfica completamente fuera de la zona del teclado. `log₂(8)` queda bajo investigación: tras insertar la plantilla no se encuentra la tecla 8 en el diálogo; no se desactiva ni se debilita esta prueba.
- Commit `ceafc22`: todos los gates salvo Playwright PASS; E2E 233 PASS, 4 SKIP, 6 FAIL. Argand y shell B5 pasan. La reserva inferior con teclado abierto era insuficiente para desplazar la tarjeta Gráfica por encima del panel fijo (diferencias 4.5 px desktop, 64 px tablet, 329 px móvil); se aumenta la reserva responsiva solamente al abrir el teclado. Para `log₂(8)` se añaden aserciones intermedias que distinguen cierre del diálogo, pérdida del núcleo numérico o ausencia de la tecla, manteniendo la evaluación de extremo a extremo.
- Commit `0b8f38e`: E2E 236 PASS, 4 SKIP, 3 FAIL; Gráfica/teclado ya pasa en los tres viewports. Los tres fallos restantes son el mismo caso S16 `log₂(8)`: el diálogo desaparece inmediatamente después de pulsar la plantilla. Se instrumenta temporalmente la prueba para distinguir una tecla Escape sintética de MathLive de un desmontaje por error React. S21 Plus falló dos veces durante `pip install` por ausencia temporal de `click>=7.0` en el índice; Lite pasa, por lo que se trata como bloqueo de infraestructura, no regresión funcional.
- Commit `8e8af4b`: S21 volvió a PASS; E2E sigue 236 PASS, 3 FAIL. Diagnóstico: no se emitió Escape y se activó `ErrorBoundary` al insertar `log₂`. Reproducción local aislada: `detectCalculusIntent("\\log_{2}\\left(\\right)")` lanzaba `TypeError` dentro de `.json` de Compute Engine durante `detectIntegral`, incluso cuando la expresión no era una integral. Corrección: detectar la forma `\\int`/`\\lim` antes de invocar Compute Engine y capturar también errores al leer MathJSON. Se añadió regresión unitaria para plantillas logarítmicas incompletas; 32/32 pruebas de `calculusIntent` PASS y TypeScript PASS. Se retira la instrumentación temporal de S16, conservando la comprobación de diálogo, núcleo numérico y resultado 3.

## 2026-09-28 — B7 Plus: P0 certificado y comienzo P1

- Commit `bad0554f7f02f94ea899e2360caeff734a240ee0`: CI, Playwright E2E, S17, S18, S19, S20, S21, S23 y S25 PASS. P0 Plus certificado; B7 permanece EN CURSO.
- P1, primer caso función directa: objeto tipado con operación, expresión original en sintaxis del motor, LaTeX de entrada separado, resultado canónico del motor cuando existe, variables, metadatos, restricciones, representación recomendada y request de Gráficas. La vista previa consume el objeto semántico; el puente conserva contexto y resultado del gráfico. Gráficas rellena expresión, variable y unidad angular a partir del objeto, sin analizar el texto visual de Resultado. El backend recibe la variable real en lugar de `x` fijo.
- Verificación local: TypeScript, ESLint y 34 pruebas unitarias focalizadas PASS. E2E local no pudo iniciar Chromium porque este entorno carece del binario de Playwright; prueba de transferencia añadida a Actions. No extrapolar este caso a derivadas, integrales, límites, sistemas, inecuaciones, complejos o EDO; siguen pendientes en P2–P4.
- Commit `4c8ad6073f5dcfa5aa5830713babe85a87f4ba39`: los nueve workflows PASS (CI, Playwright E2E, S17–S21, S23 y S25). El caso de variable `y` y transferencia del resultado canónico pasó de extremo a extremo.
- Siguiente tramo de función directa: la vista previa consulta `/graph/2d` después de una evaluación exitosa, sin registrar una nueva entrada en historial, y dibuja SVG compacto a partir de las trazas del motor. Respeta `null` como corte de curva y muestra un estado claro si el motor no devuelve puntos reales. El análisis completo sigue en Gráficas y no se reinterpreta el texto de Resultado. Pruebas unitarias de geometría y E2E de render añadidas; pendiente certificación del nuevo commit.
- Commit `d5fa7e520c29817a9bd8100ee6c95969c0647c99`: CI, Playwright E2E, S17, S18, S20, S21, S23 y S25 PASS; S19 aún ejecutándose al comenzar el subbloque de derivadas. E2E comprobó el SVG real tras `y²+1`.
- Derivada ordinaria (orden 1–5): se conserva el operando original y el resultado canónico del endpoint `/derivative`, con variable, orden y unidad angular. Si ambas expresiones son univariables respecto de esa variable y existe LaTeX de resultado, `/graph/2d` produce dos trazas; la derivada se dibuja con mayor peso y el puente abre las dos expresiones en Gráficas. Si hay otro parámetro libre, se mantiene estado avanzado sin prometer un gráfico cartesiano inválido. TypeScript, lint y pruebas focalizadas PASS; E2E de las dos curvas añadido. Pendiente certificar nuevo commit; integrales y límites siguen fuera de este tramo.
- Commit `566be585a7bdb3d3d4f6d784f9b8cd62caa61d15`: nueve workflows PASS, incluido E2E de función original + derivada y S19.
- Integral indefinida: el backend añade campos opcionales `antiderivative_expression` y `antiderivative_latex` sin constante; el resultado existente conserva `+ C` y el motor matemático no cambia. La preview y Gráficas usan esos campos estructurados para integrando + antiderivada representativa con C=0, nunca recortan `+ C` del texto o LaTeX mostrado. El modo angular de gráfica para cálculo usa radianes porque `/derivative` y `/integral` calculan en radianes, aunque la UI estuviera configurada en grados. Si faltan campos o hay parámetros adicionales, la tarjeta mantiene estado avanzado. Pruebas de contrato, frontend y E2E añadidas; integral definida/área firmada sigue pendiente.
- Commit `6fac44e49b85eacf154dbaded339cc737f728a8e`: los nueve workflows PASS, incluida la integral indefinida de extremo a extremo y S19.

## 2026-09-29 — B7 Plus: integral definida con región firmada

- El contexto canónico conserva integrando, límites en su orden original, orientación, variable y valor exacto del endpoint `/integral`. La gráfica se centra en el intervalo con margen y usa radianes para la semántica de cálculo.
- La preview traza el integrando y colorea cada tramo entre la curva y el eje según su aporte firmado. Recorta los tramos a los límites, separa los cruces por cero y respeta la inversión de límites. El valor mostrado procede del backend, no de la suma numérica de polígonos.
- El puente a Gráficas conserva límites, valor firmado y rango de vista; las pruebas cubren el caso invertido `2 → 0` de `x²`, cuyo resultado exacto es `-8/3`.
- TypeScript y 12 pruebas unitarias focalizadas PASS. Pendiente certificar E2E y los nueve workflows en Actions; B7 permanece EN CURSO.
- Segundo tramo: Gráficas dibuja los mismos segmentos firmados con relleno Plotly detrás de la curva, guías de límites y eje vertical que incluye cero. La geometría compartida evita unir áreas a través de discontinuidades. TypeScript, pruebas de geometría y lint focalizado PASS; certificación remota pendiente.
- Commit `1efc63fa325f9445dff1b7ed8d35e320d03dd247`: CI, Playwright E2E, S17, S18, S20, S21, S23 y S25 PASS; S19 aún en ejecución. El caso E2E `∫₂⁰x²dx = -8/3` pasó.
- Commit `ab291ad8744da98eb2d3423e5f49e1df99fbe25c`: ampliación Plotly; CI, S17, S18, S20, S21, S23 y S25 PASS, Playwright y S19 en ejecución. Se estabilizan las dependencias del visor por los límites numéricos para evitar redibujados durante rerenders del padre.

## 2026-09-29 — B7 Plus: integral definida certificada y límites en desarrollo

- HEAD `0ab1446b22d6b90458dcaca7093f5e972baa4012`: CI, Playwright E2E, S17 API fuzzing, S18 Differential Properties, S19 Mutation Baseline, S20 Performance Robustness, S21 Cross-browser Compatibility, S23 Accessibility y S25 Security PASS. La integral definida, la región firmada y el puente a Gráficas quedan certificados técnicamente. B7 completo sigue EN CURSO; falta revisión visual humana y operaciones posteriores.
- Límite: snapshot canónico de expresión, punto, dirección, variable y resultado de `/limit`. La vista previa usa `/graph/2d` en un rango cercano al punto finito o lejano para ±∞; traza la aproximación bilateral o solo el lado solicitado y marca DNE cuando el backend lo devuelve. Gráficas conserva punto, dirección, rango y resultado sin analizar el LaTeX de Resultado.
- TypeScript, lint focalizado y 18 pruebas unitarias focalizadas PASS. Dos casos E2E añadidos para bilateral DNE y lateral derecho; pendientes Actions y verificación visual. No declarar cierre de límites ni B7 todavía.
- Commit `ea8ec0bbef4992588e82bb102fac5f0e79b6143a`: primer tramo de límites publicado. CI, S18, S20, S23 y S25 PASS; Playwright, S17, S19 y S21 en ejecución al iniciar el siguiente tramo.
- La vista ampliada de Gráficas resalta tramos izquierdo/derecho según el contexto y marca el punto finito. Se comparte la selección de muestras con la vista previa, sin deducir el valor del límite a partir de los puntos. TypeScript, lint focalizado y prueba de geometría PASS; pendiente publicar y certificar.
- Commit `405433eafd5ac0fb341f3a3d6529bbb52e6743fb`: resaltado contextual publicado; Actions en ejecución. Comprobación directa del backend: `lim_{x→0} 1/x` devuelve `DNE`, lateral derecho `oo`, y `/graph/2d` devuelve 200 muestras sin un punto exacto en cero. Por ello la curva de fondo debe cortarse explícitamente entre muestras que cruzan el punto, además de separar los resaltados. Corrección local en SVG y Plotly con prueba de regresión, TypeScript y lint PASS; pendiente publicación/certificación.
- HEAD `c376503d464784e010a9b03c3fda2614eb3f5667`: nueve workflows PASS, incluidos Playwright y S19. Límites bilateral finito, lateral derecho y separación de la asíntota certificados técnicamente. No equivale al cierre B7: faltan otras operaciones y revisión visual humana.
- Se agrega comprobación E2E de `x→+∞` con rango lejano y resalte hacia la derecha; `x→−∞` queda cubierto por geometría unitaria. Se ajusta el texto a «Comportamiento hacia ±∞», sin llamar bilateral a la aproximación en el infinito. TypeScript, lint y 18 pruebas unitarias focalizadas PASS; pendiente Actions.
- Commit `722ba594e1b749978686ea7944a48bb8da5c5ce0`: nueve workflows PASS, incluido Playwright de `x→+∞` y S19. Tramo de límites implementado certificado técnicamente; B7 sigue EN CURSO.

## 2026-09-29 — B7 Plus: transformación algebraica, dominio conservador

- `/simplify` y `/factor` agregan `graph_polynomial_comparison` al contrato de respuesta: verdadero solo si entrada y salida son polinomios de una única variable. El motor de cálculo no cambia. La prueba `x²−4` confirma el caso seguro; `x/x → 1` no se certifica porque el original excluye cero.
- Científica conserva operación, expresión original, forma transformada y resultado canónico. En el caso seguro grafica una sola curva, porque ambas formas comparten el mismo dominio real y superponer dos curvas idénticas no aporta información. El puente a Gráficas conserva ambas formas en el contexto. Para un caso sin certificación de dominio, la vista indica que hay que comprobar restricciones y no ofrece una comparación gráfica engañosa.
- 11 pruebas de álgebra backend, 12 pruebas de contexto frontend, TypeScript y lint focalizado PASS. E2E de factorización y de `x/x` añadidos; pendiente Actions y revisión visual. B7 permanece EN CURSO.
- Commit `680c465295c50ea9fa586576a276fd5088406be1`: nueve workflows PASS, incluyendo ambos E2E de álgebra y S19. Tramo polinómico conservador certificado técnicamente; expresiones con restricciones de dominio aún requieren representación avanzada.

## 2026-09-29 — B7 Plus: soluciones EDO

- `/ode` expone campos opcionales estructurados para el lado derecho de una solución particular y para tres miembros representativos de una familia con exactamente una constante arbitraria. El resultado canónico `Eq(y(x), ...)` permanece intacto; no se extrae el lado derecho del texto mostrado.
- Científica grafica solo la solución particular, o tres miembros `C₁=−1, 0, 1` de una familia de un parámetro, marcados explícitamente como representantes. Una familia de dos constantes conserva estado avanzado sin inventar un corte 2D ni elegir parámetros silenciosamente. Gráficas recibe expresiones, resultado y origen EDO.
- 6 pruebas EDO backend, 15 pruebas de contexto frontend, TypeScript y lint focalizado PASS. E2E particular y familia añadidos; pendiente Actions, visual final y demás operaciones de B7.
- Commit `87360a2eec89523c8c8d8f576eac691e788c5f40`: nueve workflows PASS, incluidos Playwright E2E y S19. Tramo EDO certificado técnicamente; revisión visual y demás operaciones pendientes.

## 2026-09-29 — B7 Plus: sistemas lineales, primer tramo

- `/solve/system` expone curvas explícitas certificadas solo para dos ecuaciones lineales reales en `x,y` con coeficiente no nulo de `y`; conserva `result_data` canónico. Entrega puntos comunes reales desde `linsolve`, no desde muestreo gráfico. Paralelas muestran ambas curvas sin punto; coincidentes muestran una curva e infinitas soluciones. Rectas verticales, no lineales y sistemas de tres variables no reciben un certificado cartesiano engañoso.
- Científica muestra las curvas y puntos certificados; Gráficas recibe ambas ecuaciones, soluciones y marcas de intersección. Dos pruebas de backend y 17 pruebas de contexto frontend PASS; TypeScript y lint focalizado PASS. E2E de cruce y paralelas añadidos, pendiente Actions: el navegador Playwright no está instalado en este entorno local.
- Quedan pendientes la representación implícita de rectas verticales/no lineales, las inecuaciones, complejos y la revisión visual humana. B7 EN CURSO.
- Commit `1949d6bf31e273bf1f4999118a847c545232f105`: nueve workflows PASS, incluidos los E2E de cruce y rectas paralelas. Primer tramo de sistemas certificados.
- Extensión en desarrollo: cuando hay una recta vertical real, `/solve/system` devuelve `graph_data` con trazas lineales geométricas y marcador de intersección exacta; cubre vertical con horizontal/oblicua, dos paralelas y coincidentes. Científica y Gráficas reutilizan el sistema original mediante `/solve/system`, sin enviarlo al motor `y=f(x)`. Dos pruebas backend, 17 de contexto frontend, TypeScript y lint focalizado PASS; E2E vertical añadido. Permanecen las curvas no lineales implícitas y revisión visual.
- Commit `83167ee6ad6b82a966f0b006ceb21ed3487e2dc6`: nueve workflows PASS, incluido el E2E de recta vertical. Sistemas lineales 2×2 certificados técnicamente.
- Sistemas polinómicos no lineales de dos variables: si todas las componentes admiten de una a dos ramas reales explícitas `y=f(x)` de grado ≤4 (grado en y ≤2), se grafican todas con índices de componente y colores compartidos. Las intersecciones reales finitas proceden de `sympy.solve`; las coincidentes se deduplican solo si sus polinomios difieren por una constante no nula. Círculo + recta muestra dos cruces; círculos disjuntos, ninguno. Mezclas implícitas como círculo + recta vertical permanecen avanzadas. Tres pruebas backend, 18 pruebas de contexto, TypeScript y lint focalizado PASS; E2E añadido, pendiente Actions y revisión visual.
- Commit `97a3efb243654aca684f7ec10dd8b29d9b63e7a4`: nueve workflows PASS, incluido el E2E círculo + recta. Tramo explícito no lineal certificado técnicamente; representación implícita general sigue pendiente.

## 2026-09-29 — B7 Plus: recta real para inecuación de una variable

- `/inequality` conserva conjunto exacto y LaTeX, y añade variable e intervalos estructurados con extremos numéricos, etiquetas exactas e inclusión. Union de intervalos, conjunto vacío, toda la recta y puntos aislados se representan sin reparsear Resultado. Conjuntos que no admiten intervalos reales finitos representables quedan en estado avanzado sin inventar gráfica.
- Científica usa recta real con segmento, extremos huecos/rellenos y flechas al infinito. Abrir en Gráficas conserva entrada, variable, intervalos y conjunto exacto, con una vista ampliada de la misma recta. Dos pruebas backend, 21 pruebas frontend de contexto/recta, TypeScript y lint focalizado PASS. E2E de estricta, inclusiva y vacía añadido; pendiente Actions y revisión visual.
- Sistemas de inecuaciones bidimensionales y complejos permanecen pendientes. B7 EN CURSO.
- Commit `b69c8500395f294abdf0125b5cff35d2a292a482`: nueve workflows PASS, incluidos E2E de `x>0`, `x≥0`, vacío y puente a Gráficas. Recta real univariada certificada técnicamente.

## 2026-09-29 — B7 Plus: región de sistemas de inecuaciones lineales 2D

- El backend expone tipo de región, restricciones con operador original, vértices, polígono de la intersección recortado para la vista y rango. Si una intersección solo contenía frontera excluida (`x>0`, `x<0`), se clasifica como vacía. Una solución de dimensión menor que dos queda sin relleno previo y requiere vista especializada.
- Científica y Gráficas comparten la misma región semántica. La zona factible se rellena una vez; cada frontera inclusiva es continua y cada estricta discontinua. Región vacía sin relleno; no acotada se recorta al marco de la vista y se indica como tal. Se conservan entrada, variables, restricciones, tipo y vértices.
- 15 pruebas backend focalizadas/auditoría, 22 frontend, TypeScript y lint focalizado PASS; E2E de región mixta y sistema estricto imposible añadido. Pendiente Actions, revisión visual y complejos. B7 EN CURSO.
- Commit `c8193347639bf17823269fa8ab285c67b30f5118`: nueve workflows PASS, incluidos Playwright E2E y S19. Región factible lineal 2D certificada técnicamente.

## 2026-09-29 — B7 Plus: plano de Argand

- `/evaluate` expone coordenadas Re/Im solo para un número complejo concreto, finito y acotado; `/solve` expone todas las raíces numéricas de una ecuación cuando aparece alguna compleja, incluidos los puntos reales del mismo conjunto. Las expresiones con variable libre no se reducen a un punto.
- Científica presenta una vista previa de Argand y Gráficas recibe el contexto original y los puntos estructurados. Dos pruebas backend, 22 pruebas frontend focalizadas, TypeScript y lint focalizado PASS. E2E de punto aislado y raíces complejas añadidos; pendiente Actions y revisión visual.
- Permanecen pendientes las curvas Re/Im de función compleja de variable real y una representación apropiada de función genuina de variable compleja. B7 EN CURSO.
- Commit `8f3a9aeb6d955edc56658ba3ca8be0fee94e5e06`: CI backend FAIL en tres entradas trigonométricas reales por una evaluación de `is_real` de SymPy al buscar un complejo. Se limita el detector a expresiones con `I` y se cubre la regresión. Suite local: 423 PASS; tres S25 fallan solo por variable de entorno CORS ausente en esta ejecución. Se publica la corrección para certificar en Actions.
- Commit `95c9f4acd706e20e7a8a545b12039097cc8afba6`: nueve workflows PASS, incluidos CI, Playwright E2E y S19. Punto aislado y raíces numéricas complejas en Argand certificados técnicamente. B7 permanece EN CURSO.
- Función compleja de variable real: `/evaluate` expone expresiones y LaTeX separados de Re e Im para una variable convencional real `x` o `t`, con presupuesto de complejidad; `f(z)` conserva estado avanzado. Científica traza ambas curvas con colores y etiquetas explícitos; Gráficas recibe las componentes y la expresión original. El ejemplo `exp(I*x)` produce `cos(x)` y `sin(x)` y `/graph/2d` devuelve dos trazas. TypeScript, 22 pruebas frontend focalizadas y dos backend PASS. E2E de la cadena completa añadido; pendiente Actions y revisión visual.
- Commit `1f9d66806b8f20b2423f56bde9cce48e81f49dab`: nueve workflows PASS, incluidos CI, Playwright E2E y S19. Curvas Re/Im certificadas técnicamente.
- Función genuina `f(z)`: el backend calcula hasta cuatro pares de muestras finitas `z → f(z)` (0, 1, i, 1+i), omite puntos indefinidos y conserva la expresión canónica. Científica y Gráficas muestran dos planos de Argand vinculados por color y advierten que la muestra no cubre todo el dominio ni comparte escala. No se fuerza una curva real 2D. `z²` incluye `f(i)=−1`; `1/z` omite `z=0`. Suite local 427 backend, 24 frontend focalizadas, TypeScript y lint PASS. E2E agregado; pendientes Actions y revisión visual humana. B7 EN CURSO.
- Commit `984c80dbd50adb84a308dd4ea0eed19246bdeb9f`: nueve workflows PASS, incluidos Playwright E2E y S19. Mapeo por muestras de `f(z)` certificado técnicamente.
- Sistemas mixtos con recta vertical y curva polinómica de hasta dos ramas explícitas: se muestrean las ramas reales, se traza `x=a` vertical y se marcan únicamente intersecciones reales finitas calculadas simbólicamente. `x=0` con círculo produce dos cruces; `x=1`, tangencia; `x=2`, ninguna intersección real aunque Resultado conserva dos soluciones complejas. Se corrige el texto de la vista para no afirmar ausencia total de soluciones. Pruebas y Actions pendientes; B7 EN CURSO.
- Commit `83da592c60e88b1613f67d93fa3ce9d21293115a`: ocho workflows PASS. Playwright FAIL solo en la expectativa anterior de rectas paralelas que buscaba «no tiene solución» tras cambiar el texto común; el E2E nuevo del círculo con vertical pasó. Corrección: el texto ahora depende del resultado estructurado; paralelas sin solución conservan el mensaje previo y sistemas con raíces complejas indican ausencia de cruce real sin descartarlas. Se agrega E2E del caso complejo sin marcador real. Pendiente recertificación.
- Inecuación lineal 2D directa: `/inequality` delega el caso con variables `{x,y}` al solver de semiplanos ya usado por `/inequality/system`, devuelve región y frontera estructuradas. Científica y Gráficas consumen el mismo contexto sin reparsear el resultado. `x+y>0` traza semiplano abierto; `x+y≥0` conserva frontera incluida; `x>0` sigue en recta real. La prueba histórica que exigía rechazar `x+y<5` se actualiza al nuevo contrato, mientras tres variables aún producen error explícito. Suite local 428 backend, 28 frontend focalizadas, TypeScript y lint PASS. E2E añadido; pendiente Actions y revisión visual. B7 EN CURSO.
- Commit `40362c71454d630eca7b2d529c9f7c9eb7a13c67`: nueve workflows PASS. La distinción entre sistema sin soluciones y sistema con soluciones complejas sin cruces reales pasó Playwright E2E.
- Commit `de916833dd4386e4457fee0cb55974b547133be5`: nueve workflows PASS, incluidos Playwright E2E y S19. Semiplano lineal de dos variables en `/inequality` certificado técnicamente. B7 permanece EN CURSO por revisión visual humana y los casos de región de dimensión menor o frontera no lineal aún no cubiertos.

## 2026-09-29 — B7 Plus: intersecciones factibles de dimensión menor

- El solver conserva la dimensión y geometría de la solución recortada: línea/rayo/segmento con dos extremos, o punto con una coordenada. Una intersección puntual excluida por una desigualdad estricta se clasifica vacía; el recorte numérico no debe hacerla parecer factible.
- Científica y Gráficas trazan solo el tramo común, sin relleno de área, y marcan extremos incluidos o huecos. Los extremos del marco indican continuación de una solución no acotada. Pruebas de rayo abierto, segmento semiabierto, punto y punto excluido añadidas.
- Suite local: 428 backend, 30 frontend focalizadas, TypeScript y lint PASS. E2E del rayo y puente a Gráficas añadido; pendiente Actions y revisión visual. B7 EN CURSO.
- Commit `2ce022994c490eed4d6ae10378b352697183f40e`: ocho workflows PASS; Playwright E2E FAIL en la nueva aserción `toBeVisible` sobre una línea SVG vertical que sí existe y tiene coordenadas/trazo correctos, pero cuyo bounding box tiene ancho cero. Se verifica el contenedor visible y el atributo del trazo en su lugar; pendiente recertificar. El cálculo y las demás 317 pruebas de navegador pasaron.
- Commit `dcd59b57f25301717a960d9a21ed531015fb779c`: CI, Playwright E2E (incluido el nuevo rayo en desktop, tablet y mobile), S17, S18, S19, S20, S23 y S25 PASS. S21 falló durante `npm install` por 404 transitorio de `std-env@4.3.0.tgz` antes de probar Plus; se repitió únicamente el job y Plus/Lite terminaron PASS. Nueve puertas certificadas técnicamente para las soluciones de dimensión menor. B7 permanece EN CURSO por la revisión visual y fronteras curvas adicionales.

## 2026-09-29 — B7 Plus: círculo como primera frontera curva

- `/inequality` reconoce únicamente desigualdades de círculo real no degenerado, incluso trasladado y con factor cuadrático negativo. Expone centro/radio exactos y numéricos, interior/exterior y borde incluido/excluido; elipses y otras cónicas no reciben certificado circular.
- Científica y Gráficas muestran el disco o su exterior con hueco, y frontera continua o discontinua según la relación. El puente conserva la expresión original y la estructura geométrica. Suite local: 429 backend, 33 frontend focalizadas, TypeScript y lint PASS. E2E del disco abierto añadido; pendientes Actions y revisión visual humana. B7 EN CURSO.
- Commit `f4369a54dfc72838e61d67a1d83cb985b3844a9b`: ocho workflows PASS; Playwright FAIL en el E2E circular porque el orquestador de Científica clasificaba la nueva visualización como avanzada y el puente a Gráficas omitía el contexto. Se incluyen `circle-region` en el estado disponible y en el traspaso de contexto de ambos módulos; pendiente recertificar.
