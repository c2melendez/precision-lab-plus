# Algebra229 AS-C-09 - aceptación bilateral (Plus)

**Resultado: PASS bilateral.** La certificación global continúa **OPEN**.

## Contrato y oráculos
- AS-C-09, N2, `simplificar`: `\frac{a}{b}+\frac{b}{a}` → `\frac{a^{2} + b^{2}}{a b}`, sin nota de dominio en la fila congelada.
- Plus: `backend/tests/test_algebra229_as_c09.py`, 4/4 tests: ocho celdas exactas de la fila congelada; el endpoint devuelve una única fracción canónica `(a**2 + b**2)/(a*b)` y la diferencia exacta con la expectativa es `0`; oráculo aritmético independiente con `Fraction` en cinco muestras con `a,b != 0`; `DOMAIN_ERROR` en `a=0`, `b=0` y `a=b=0`.
- Lite (par bilateral): `tests/algebra229AsC09.audit.test.ts`, 4/4 tests: fila congelada; fracción única combinada; equivalencia exacta; oráculo numérico independiente; control de dominio.

## Test-first y corrección
- El commit de pruebas `bc4473ff8121c829eac37ad66130fb4b39e1b4d1` reprodujo el gap real: `test_as_c09_simplify_endpoint_returns_one_combined_fraction` **FAILED** porque Plus devolvía `a/b + b/a` sin combinar (Cumulative [42451545272](https://github.com/c2melendez/precision-lab-plus/actions/runs/42451545272), 1 failed). No se relajó la expectativa congelada.
- Corrección acotada en `backend/app/services/algebra_service.py`: `_is_sum_of_fractions` exige que **todos** los términos de la suma tengan denominador y `_is_single_fraction_with_product_denominator` acepta el resultado de `cancel()` solo si es una fracción única con denominador producto. Se aplica dentro de `_cancel_common_factors`; el resto de formas conserva la regla anterior de complejidad. Clasificación: gap de **capability** del motor simbólico.
- Lite no requirió cambios: la ruta `rationalize()` ya introducida en C-05 combina la suma.
- Limitación de harness registrada: `POST /api/v1/evaluate` de Plus no admite sustitución multivariable del tipo `con a=1, b=2` (`PARSE_ERROR`); los oráculos numéricos se evalúan sustituyendo los valores directamente en la expresión. No afecta a la fila `simplificar` ni a la exactitud del resultado.

## Evidencia Plus - SHA `75f3bd5a3ff8455893ca469d15b38c572ab4c27a`
- Cumulative [42451561391](https://github.com/c2melendez/precision-lab-plus/actions/runs/42451561391) SUCCESS; focal AS-C-09 4/4 PASS.
- CI [42451561464](https://github.com/c2melendez/precision-lab-plus/actions/runs/42451561464) SUCCESS; 2,848 passed, 1 skipped, 10 xfailed; cobertura 88.90% (incluye la suite completa con el cambio).
- H1d [42451561379](https://github.com/c2melendez/precision-lab-plus/actions/runs/42451561379) SUCCESS; 38/38 Playwright.
- Native Syntax and Recovery [42451561395](https://github.com/c2melendez/precision-lab-plus/actions/runs/42451561395) SUCCESS.
- Runner [42451561385](https://github.com/c2melendez/precision-lab-plus/actions/runs/42451561385) SUCCESS.
- Runs por push sin inputs de dispatch: guard `skip=false`, `evidence_run_id` vacío, sin REUSE.

## Evidencia Lite (par bilateral) - SHA `388048d0d5811c2f52d1fc877c5fa70bc9b687a1`
- Cumulative [42451545801](https://github.com/c2melendez/precision-lab-lite/actions/runs/42451545801) SUCCESS; focal AS-C-09 4/4 (622 ms); 376 archivos, 2,313 passed, 8 expected fail, 34 TODO.
- CI [42451545670](https://github.com/c2melendez/precision-lab-lite/actions/runs/42451545670) SUCCESS; focal AS-C-09 4/4 (479 ms); 376 archivos, 2,313 passed.
- H1d [42451545781](https://github.com/c2melendez/precision-lab-lite/actions/runs/42451545781) SUCCESS; 22/22 Playwright.
- Scientific UI [42451545826](https://github.com/c2melendez/precision-lab-lite/actions/runs/42451545826) SUCCESS; 456/456.
- Runner [42451545669](https://github.com/c2melendez/precision-lab-lite/actions/runs/42451545669) SUCCESS.

## Diagnóstico y clasificación
- Gap de capability en Plus (suma de fracciones sin combinar), corregido en producto y cubierto con regresión permanente. El resto de C-02..C-08 no cambia; la suite Ubuntu completa pasa con el cambio.
- El gate de seguridad (S25) y SG28/H2/DIST siguen siendo frentes independientes abiertos; global **OPEN**.

Siguiente: AS-C-10, N2, `simplificar` - `\frac{1-\frac{1}{x^{2}}}{1-\frac{1}{x}}` → `\frac{x + 1}{x}`, sin nota de dominio en la fila congelada.
