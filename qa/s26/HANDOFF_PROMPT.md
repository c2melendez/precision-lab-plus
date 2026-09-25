# S26 — Prompt de continuidad para la próxima sesión

Proyecto: **Precision Lab Plus**  
Branch de trabajo: `qa/s26-execution`  
Baseline matemático protegido: `5de721e32c13a60f77671cd2bd98a8cc05cf0140`  
Último head de código relevante al cierre: `75d816b8e74acfe1b91661e02843966719e7fcc0`  
Preview: https://precision-lab-plus-s26.onrender.com

## PRIMERA INSTRUCCIÓN OBLIGATORIA

**NO EMPIECES MODIFICANDO CÓDIGO.**

Antes de cualquier nueva implementación debes:

1. leer `qa/s26/MOCKUP_REGENERATION_BRIEF.md`;
2. leer `qa/s26/VISUAL_REFERENCE_CHECKLIST.md`;
3. leer `qa/s26/DESIGN_TARGET.md`;
4. leer `qa/s26/KEYBOARD_CONTRACT.md`;
5. leer `qa/s26/RESULT_FORMATS.md`;
6. leer `qa/s26/GRAPH_3D_CONTRACT.md`;
7. leer `qa/s26/GEOMETRY_CONTRACT.md`;
8. leer `qa/s26/BRAND_IDENTITY.md`;
9. leer `qa/s26/ROADMAP.md`;
10. leer el final de `qa/s26/EXECUTION_LOG.md`.

Después, tu **primera tarea de producto** es regenerar los **mockups definitivos del contrato visual S26** de forma consolidada.

Debes presentar al usuario:
- tablero maestro;
- mockup definitivo de Científica;
- Matrices;
- Gráficas 2D/Polar/Paramétrica/3D;
- Estadística;
- Geometría;
- Unidades;
- Historial;
- Ajustes;
- mockups del teclado global **colapsado y desplegado**;
- categorías Básico, Símbolos, Álgebra, Trigonométricas, Cálculo y Complejos;
- Desktop 1440×900 como referencia principal;
- estrategia laptop/tablet/mobile;
- seis layouts: fused, separated, split, focus, stacked, floating.

### Regla de parada
Después de mostrar los mockups, **detente y espera aprobación explícita del usuario**.

No continúes implementando S26.3 hasta que el usuario confirme que los mockups definitivos representan el contrato final.

## REGLA CRÍTICA DEL TECLADO

El teclado que todavía puede verse actualmente en los previews deriva del diseño/implementación anterior.

**NO se considera visualmente aprobado.**

La referencia visual que debe implementarse después de la aprobación es el teclado reconstruido a partir de los mockups definitivos S26.2/S26.

No interpretes “conservar botonería y funcionalidad” como “conservar la distribución visual del teclado legado”.

Debe conservarse:
- funcionalidad;
- teclas aprobadas;
- tooltips;
- seis categorías;
- paridad teclado↔motor.

Debe reemplazarse si contradice el contrato:
- distribución visual antigua;
- duplicaciones;
- teclados inline por módulo;
- jerarquía/espaciado legado.

El teclado final:
- es único y global;
- inicia colapsado;
- se abre desde los seis módulos;
- `=` inserta, Enter ejecuta;
- usa `°` y `′` correctos;
- pestañas siempre visibles;
- máximo aprox. 45% del viewport Desktop;
- responsive móvil;
- cuatro límites separados en Cálculo;
- funciones de Álgebra acordadas solo cuando exista soporte real.

## ESTADO TÉCNICO AL CIERRE

Último código visual: limpieza del refactor de teclado global de Gráficas.
Gates: CI PASS, Playwright PASS, S17 PASS, S18 PASS, S20 PASS, S21 PASS, S23 PASS, S25 PASS; S19 Mutation Baseline seguía in_progress al cierre de esta sesión.
La corrida anterior falló por cuatro setActiveMode no usados tras retirar teclados inline de Gráficas; quedó corregido en 75d816b8e74acfe1b91661e02843966719e7fcc0.

## ESTADO DEL PREVIEW

La revisión humana del Preview fue **FAIL VISUAL** en ambos proyectos.

Conclusión:
- los PASS anteriores conservan valor funcional;
- NO constituyen aprobación visual final;
- NO avanzar a S26.4;
- primero reconfirmar mockups definitivos;
- después reconciliar implementación con ellos;
- luego repetir revisión humana del Preview.

## BLOQUES YA TRABAJADOS

Funcionalmente se han trabajado:
- shell/navegación;
- identidad básica;
- Resultado/formatos;
- trigonometría angular + DMS;
- Entrada/Pasos;
- Gráficas;
- Matrices;
- Preview separado;
- Estadística Lite;
- Unidades Lite en curso;
- teclado global Plus en reconciliación.

Pero visualmente varios bloques quedan **reabiertos** por la revisión humana.

## REGLAS DE INTEGRIDAD

- no reducir S26 a Científica;
- no simplificar eliminando funciones;
- no tocar rutas matemáticas protegidas salvo defecto reproducible;
- toda modificación visual con impacto funcional debe tener prueba;
- una captura no sustituye una prueba;
- un gate verde no sustituye aprobación visual;
- mockups son autoridad visual, no matemática;
- no copiar números incorrectos de mockups históricos;
- preservar diferencias legítimas Lite vs Plus;
- actualizar logs, roadmap y contratos después de cada decisión importante.

## FLUJO DESPUÉS DE APROBAR MOCKUPS

1. congelar contrato visual definitivo;
2. reconciliar teclado global;
3. Científica;
4. Matrices;
5. Gráficas;
6. Estadística;
7. Geometría por etapas;
8. Unidades;
9. Historial/Ajustes;
10. responsive + seis layouts;
11. nueva revisión humana Preview;
12. S26.4 regresión visual;
13. S26.5 recertificación matemática/funcional;
14. S26.6 cierre.

Si la conversación anterior no está disponible, **estos documentos son la fuente de continuidad y prevalecen sobre suposiciones**.
