# Algebra229 AS-C-06 - aceptación bilateral (Plus)

**Resultado: PASS bilateral.** La certificación global continúa **OPEN**.

## Contrato y oráculos
- AS-C-06, N2, `simplificar`: `\frac{\frac{1}{x}-\frac{1}{y}}{x-y}` → `- \frac{1}{x y}`, sin nota de dominio en la fila congelada.
- Plus: `backend/tests/test_algebra229_as_c06.py`, 4/4 tests: ocho celdas exactas de la fila congelada; `POST /api/v1/simplify` devuelve una forma canónica equivalente a `-1/(x*y)`; oráculo aritmético independiente con `Fraction` en cinco muestras con `x,y != 0` y `x != y`; los puntos excluidos (`x=0`, `y=0`, `x=y`) no se declaran equivalentes (`DOMAIN_ERROR`).
- Lite (par bilateral): `tests/algebra229AsC06.audit.test.ts`, 5/5 tests: fila congelada; resultado canónico; equivalencia simbólica; oráculo aritmético independiente; control de los tres puntos excluidos.

## Implementación
- Plus no requirió cambios: SymPy reduce la expresión a la forma canónica.
- Lite requirió una corrección de producto en `src/engine/algebriteClient.ts`: `simplify()` dejaba la fracción anidada sin reducir. Cuando el resultado conserva más de un signo de división, se aplica `factoredCancellation`: `rationalize()`, factorización de numerador y denominador, y `simplify()` conjunto; el candidato se acepta solo si es una única fracción con denominador tipo producto. Clasificación: gap de **capability** del motor simbólico, no fallo de harness ni de oráculo.
- Se verificó que la corrección no altera C-02, C-03, C-04 ni C-05; suite completa Lite 373/373 archivos en verde. No se relajó ningún oráculo matemático.

## Evidencia Plus - SHA `9ddc8205ec97a13bed7857a1487024a2650e1e78`
- Cumulative [42403960553](https://github.com/c2melendez/precision-lab-plus/actions/runs/42403960553) SUCCESS; focal AS-C-06 4/4 PASS; backend y frontend SUCCESS.
- CI [42403960642](https://github.com/c2melendez/precision-lab-plus/actions/runs/42403960642) SUCCESS; 2,836 passed, 1 skipped, 10 xfailed; cobertura 88.89%.
- H1d [42403960552](https://github.com/c2melendez/precision-lab-plus/actions/runs/42403960552) SUCCESS; 38/38 Playwright.
- Runner [42403960657](https://github.com/c2melendez/precision-lab-plus/actions/runs/42403960657) SUCCESS.
- Runs por push sin inputs de dispatch: guard `skip=false`, `evidence_run_id` vacío, sin REUSE.

## Evidencia Lite (par bilateral) - SHA `12cab2e2e536d313635256f280ce0951a73afebd`
- Cumulative [42449459397](https://github.com/c2melendez/precision-lab-lite/actions/runs/42449459397) SUCCESS; focal AS-C-06 5/5 (1,399 ms); 373 archivos, 2,301 passed, 8 expected fail, 34 TODO.
- CI [42449459368](https://github.com/c2melendez/precision-lab-lite/actions/runs/42449459368) SUCCESS; focal AS-C-06 5/5 (998 ms); 373 archivos, 2,301 passed.
- H1d [42449459386](https://github.com/c2melendez/precision-lab-lite/actions/runs/42449459386) SUCCESS; 22/22 Playwright.
- Scientific UI [42449459435](https://github.com/c2melendez/precision-lab-lite/actions/runs/42449459435) SUCCESS; 456/456.
- Runner [42449459424](https://github.com/c2melendez/precision-lab-lite/actions/runs/42449459424) SUCCESS.

## Diagnóstico y clasificación
- El primer intento Lite (SHA `6a36f3af2`) falló solo en la expectativa exacta: devolvía `(1/x-1/y)/(x-y)`. Fue un gap real de capability del motor, corregido en producto y cubierto con regresión permanente; no se relajó la expectativa congelada.
- El gate de seguridad (S25) y SG28/H2/DIST siguen siendo frentes independientes abiertos; global **OPEN**.

Siguiente: AS-C-07, N2, `simplificar` - `\frac{1}{x-1}-\frac{1}{x+1}` → `\frac{2}{\left(x - 1\right) \left(x + 1\right)}`, sin nota de dominio en la fila congelada.
