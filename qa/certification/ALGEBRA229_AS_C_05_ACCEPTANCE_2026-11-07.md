# Algebra229 AS-C-05 - aceptación bilateral (Plus)

**Resultado: PASS bilateral.** La certificación global continúa **OPEN**.

## Contrato y oráculos
- AS-C-05, N1, `simplificar`: `\frac{1}{x}+\frac{1}{y}` → `\frac{x + y}{x y}`, con nota "Suma de fracciones con denominador común".
- Plus: `backend/tests/test_algebra229_as_c05.py`, 4/4 tests: ocho celdas exactas de la fila congelada; `POST /api/v1/simplify` devuelve una forma canónica equivalente a `(x+y)/(xy)`; oráculo aritmético independiente con `Fraction` en cinco muestras con `x,y != 0`; `DOMAIN_ERROR` en los puntos excluidos.
- Lite (par bilateral): `tests/algebra229AsC05.audit.test.ts`, 5/5 tests: fila congelada; resultado canónico; equivalencia simbólica; oráculo aritmético independiente; control de dominio en `x=0` e `y=0`.

## Implementación
- Plus no requirió cambios: SymPy ya combinaba la suma sobre denominador común.
- Lite sí requirió una corrección de producto en `src/engine/algebriteClient.ts`: Algebrite `simplify()` deja `1/x+1/y` sin combinar. Se añadió `combinedSingleFraction`, que usa `rationalize()` y acepta el resultado solo cuando es una única fracción con denominador tipo producto. Clasificación: gap de **capability** del motor simbólico, no fallo de harness ni de oráculo.
- No se relajó ningún oráculo matemático.

## Evidencia Plus - SHA `310b7ceaa89c3c309443ae6865263b67bf95373d`
- Cumulative [42346703999](https://github.com/c2melendez/precision-lab-plus/actions/runs/42346703999) SUCCESS; focal AS-C-05 4/4 PASS; backend y frontend SUCCESS.
- CI [42346704029](https://github.com/c2melendez/precision-lab-plus/actions/runs/42346704029) SUCCESS; 2,832 passed, 1 skipped, 10 xfailed; cobertura 88.89%.
- H1d [42346704039](https://github.com/c2melendez/precision-lab-plus/actions/runs/42346704039) SUCCESS; 38/38 Playwright.
- Runner [42346704001](https://github.com/c2melendez/precision-lab-plus/actions/runs/42346704001) SUCCESS.
- Runs por push sin inputs de dispatch: guard `skip=false`, `evidence_run_id` vacío, sin REUSE.

## Evidencia Lite (par bilateral) - SHA `6e83392473bbaebe738ed493d73279f7c595cbfb`
- Cumulative [42347259419](https://github.com/c2melendez/precision-lab-lite/actions/runs/42347259419) SUCCESS; focal AS-C-05 5/5 (469 ms); 372 archivos, 2,296 passed, 8 expected fail, 34 TODO.
- CI [42347259190](https://github.com/c2melendez/precision-lab-lite/actions/runs/42347259190) SUCCESS; focal AS-C-05 5/5 (451 ms); 372 archivos, 2,296 passed.
- H1d [42347259257](https://github.com/c2melendez/precision-lab-lite/actions/runs/42347259257) SUCCESS; 22/22 Playwright.
- Scientific UI [42347259155](https://github.com/c2melendez/precision-lab-lite/actions/runs/42347259155) SUCCESS.
- Runner [42347259168](https://github.com/c2melendez/precision-lab-lite/actions/runs/42347259168) SUCCESS.

## Diagnóstico y clasificación
- Gap de capability en Lite (combinación de fracciones), corregido en producto y cubierto con regresión permanente. En Plus el comportamiento ya era correcto.
- El gate de seguridad (S25) y SG28/H2/DIST siguen siendo frentes independientes abiertos; global **OPEN**.

Siguiente: AS-C-06, N2, `simplificar` - `\frac{\frac{1}{x}-\frac{1}{y}}{x-y}` → `- \frac{1}{x y}`, sin nota de dominio en la fila congelada.
