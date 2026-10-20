## 2026-10-20 UTC — AS-B-13 PASS_SCOPED bilateral (continuity r179)

**ALGEBRA229-AS-B-13** — factorizar `2x^{3}-x^{2}-13x-6` → `\left(x - 3\right) \left(x + 2\right) \left(2 x + 1\right)` (fila fuente N3 en la matriz congelada Section B).

| Repo | Technical SHA | Gates (SUCCESS sobre el SHA exacto, evento push) |
|------|---------------|--------------------------------------------------|
| Plus | `7ea34354edb2b1d783858ec0460ef53055ff917a` | cumulative [39453858654](https://github.com/c2melendez/precision-lab-plus/actions/runs/39453858654), h1d [39453858516](https://github.com/c2melendez/precision-lab-plus/actions/runs/39453858516) |

Test-first sin cambios de producto: el motor ya devolvía una factorización equivalente al original en ambos repos, con tres factores lineales. Evidencia: `tests/algebra229AsB13.audit.test.ts` (fila fuente, diferencia exacta cero y forma `(x-3)*(x+2)*(2*x+1)`) y `backend/tests/test_algebra229_as_b13.py` (`/api/v1/factor` por HTTP, producto de tres factores). Global OPEN.

**Siguiente único:** `ALGEBRA229-AS-B-14-TEST-FIRST` — `x^{4}+x^{2}+1` → `\left(x^{2} - x + 1\right) \left(x^{2} + x + 1\right)` (fila N3; diferencia de cuadrados en ℚ).

---

## 2026-10-20 UTC — AS-B-12 PASS_SCOPED bilateral (continuity r178)

**ALGEBRA229-AS-B-12** — factorizar `x^{5}-x` → `x \left(x - 1\right) \left(x + 1\right) \left(x^{2} + 1\right)` (fila fuente N2 en la matriz congelada Section B).

| Repo | Technical SHA | Gates (SUCCESS sobre el SHA exacto, evento push) |
|------|---------------|--------------------------------------------------|
| Plus | `ccbcdb5e2f2d3e2bc6e22247ca440b8e9c8450e3` | cumulative [39452217842](https://github.com/c2melendez/precision-lab-plus/actions/runs/39452217842), h1d [39452217825](https://github.com/c2melendez/precision-lab-plus/actions/runs/39452217825) |

Test-first sin cambios de producto: el motor ya devolvía una factorización equivalente al original en ambos repos. Evidencia: `tests/algebra229AsB12.audit.test.ts` (fila fuente, diferencia exacta cero y forma `x*(x-1)*(x+1)*(x^2+1)`) y `backend/tests/test_algebra229_as_b12.py` (`/api/v1/factor` por HTTP, producto de cuatro factores). Global OPEN.

**Siguiente único:** `ALGEBRA229-AS-B-13-TEST-FIRST` — `2x^{3}-x^{2}-13x-6` → `\left(x - 3\right) \left(x + 2\right) \left(2 x + 1\right)` (fila N3).

---

## 2026-10-20 UTC — AS-B-11 PASS_SCOPED bilateral (continuity r177)

**ALGEBRA229-AS-B-11** — factorizar `ax+ay+bx+by` → `\left(a + b\right) \left(x + y\right)` (fila fuente N2 en la matriz congelada Section B; agrupación de términos).

| Repo | Technical SHA | Gates (SUCCESS sobre el SHA exacto, evento push) |
|------|---------------|--------------------------------------------------|
| Plus | `cdc2bf73e143384834c0a726862ec70872e6c498` | cumulative [39450890699](https://github.com/c2melendez/precision-lab-plus/actions/runs/39450890699), h1d [39450890712](https://github.com/c2melendez/precision-lab-plus/actions/runs/39450890712) |

Test-first sin cambios de producto: el motor ya devolvía una factorización equivalente al original en ambos repos, con la forma de producto de dos binomios. Evidencia: `tests/algebra229AsB11.audit.test.ts` (fila fuente, diferencia exacta cero y forma `(a+b)*(x+y)`) y `backend/tests/test_algebra229_as_b11.py` (`/api/v1/factor` por HTTP, producto de dos factores). Entrada probada con `*` explícito para evitar ambigüedad de multiplicación implícita. Global OPEN.

**Siguiente único:** `ALGEBRA229-AS-B-12-TEST-FIRST` — `x^{5}-x` → `x \left(x - 1\right) \left(x + 1\right) \left(x^{2} + 1\right)` (fila N2).

---

## 2026-10-20 UTC — AS-B-10 PASS_SCOPED bilateral (continuity r176)

**ALGEBRA229-AS-B-10** — factorizar `x^{3}+3x^{2}+3x+1` → `\left(x + 1\right)^{3}` (fila fuente N2 en la matriz congelada Section B).

| Repo | Technical SHA | Gates (SUCCESS sobre el SHA exacto, evento push) |
|------|---------------|--------------------------------------------------|
| Plus | `f6edeca8f11f7bfc9a1aab367faa0f0f90deb88d` | cumulative [39449552737](https://github.com/c2melendez/precision-lab-plus/actions/runs/39449552737), h1d [39449552940](https://github.com/c2melendez/precision-lab-plus/actions/runs/39449552940) |

Test-first sin cambios de producto: el motor ya devolvía una factorización equivalente al original en ambos repos. Evidencia: `tests/algebra229AsB10.audit.test.ts` (fila fuente, diferencia exacta cero y forma de potencia) y `backend/tests/test_algebra229_as_b10.py` (`/api/v1/factor` por HTTP, potencia cúbica). Global OPEN.

**Siguiente único:** `ALGEBRA229-AS-B-11-TEST-FIRST` — `ax+ay+bx+by` → `\left(a + b\right) \left(x + y\right)` (fila N2, agrupación de términos).

---

## 2026-10-20 UTC — AS-B-09 PASS_SCOPED bilateral (continuity r175)

**ALGEBRA229-AS-B-09** — factorizar `6x^{2}+5x-4` → `\left(2 x - 1\right) \left(3 x + 4\right)` (fila fuente N2 en la matriz congelada Section B).

| Repo | Technical SHA | Gates (SUCCESS sobre el SHA exacto, evento push) |
|------|---------------|--------------------------------------------------|
| Plus | `df59c1efdedf7d6c38e5de2ba54ad1c86dd5864e` | cumulative [39448192396](https://github.com/c2melendez/precision-lab-plus/actions/runs/39448192396), h1d [39448192451](https://github.com/c2melendez/precision-lab-plus/actions/runs/39448192451) |

Test-first sin cambios de producto: el motor ya devolvía una factorización equivalente al original en ambos repos. Evidencia: `tests/algebra229AsB09.audit.test.ts` (fila fuente y diferencia exacta cero) y `backend/tests/test_algebra229_as_b09.py` (`/api/v1/factor` por HTTP, dos factores). Global OPEN.

**Siguiente único:** `ALGEBRA229-AS-B-10-TEST-FIRST` — `x^{3}+3x^{2}+3x+1` → `\left(x + 1\right)^{3}` (fila N2).

---

## 2026-10-20 UTC — AS-B-08 PASS_SCOPED bilateral (continuity r174)

**ALGEBRA229-AS-B-08** — factorizar `x^{4}-5x^{2}+4` → `\left(x - 2\right) \left(x - 1\right) \left(x + 1\right) \left(x + 2\right)` (fila fuente N2 en la matriz congelada Section B).

| Repo | Technical SHA | Gates (SUCCESS sobre el SHA exacto, evento push) |
|------|---------------|--------------------------------------------------|
| Plus | `92836fbfb8da98ffdafd71b0cb510aaf7bf4e905` | cumulative [39443976046](https://github.com/c2melendez/precision-lab-plus/actions/runs/39443976046), h1d [39443975882](https://github.com/c2melendez/precision-lab-plus/actions/runs/39443975882) |

Test-first sin cambios de producto: el motor ya devolvía una factorización equivalente al original en ambos repos. Evidencia: `tests/algebra229AsB08.audit.test.ts` (fila fuente y diferencia exacta cero) y `backend/tests/test_algebra229_as_b08.py` (`/api/v1/factor` por HTTP, cuatro factores). Global OPEN.

**Siguiente único:** `ALGEBRA229-AS-B-09-TEST-FIRST` — `6x^{2}+5x-4` → `\left(2 x - 1\right) \left(3 x + 4\right)` (fila N2).

---

## 2026-10-20 UTC — AS-B-07 PASS_SCOPED bilateral (continuity r173)

**ALGEBRA229-AS-B-07** — factorizar `x^{6}-1` → `\left(x - 1\right) \left(x + 1\right) \left(x^{2} - x + 1\right) \left(x^{2} + x + 1\right)` (fila fuente N2 en la matriz congelada Section B).

| Repo | Technical SHA | Gates (todos SUCCESS sobre el SHA exacto, evento push) | Conclusion |
|------|---------------|--------------------------------------------------------|------------|
| Lite | `89b7055fdf65dd1f239fc426eb33ee66fa282cd6` | cumulative [39434995883](https://github.com/c2melendez/precision-lab-lite/actions/runs/39434995883), scientific-ui [39434995961](https://github.com/c2melendez/precision-lab-lite/actions/runs/39434995961), h1d [39434995969](https://github.com/c2melendez/precision-lab-lite/actions/runs/39434995969) | SUCCESS |
| Plus | `da361aee09728e0e0525e43615b6418b4ec9fb14` | cumulative [39433181526](https://github.com/c2melendez/precision-lab-plus/actions/runs/39433181526), h1d [39433181543](https://github.com/c2melendez/precision-lab-plus/actions/runs/39433181543) | SUCCESS |

**Incidente de producto en Lite (resuelto):** en `6bafda3` el gate acumulado falló porque Algebrite `factor(x^6-1)` devolvía `(x-1)(x+1)(x^2+x+1)(x^2+1)`, no equivalente al original (diferencia `x^5+x^4-x^2-x`). Corrección en `89b7055`: `factor(...)` ahora se verifica contra su entrada; si el resultado es un polinomio entero no equivalente, se usa una factorización univariada sobre ℤ (Kronecker, `src/engine/polynomialFactorZ.ts`) solo si su equivalencia se comprueba. Resultados con radicales o fracciones no se reemplazan (AS-FAC-09 real). Plus no tuvo incidente (SymPy).

**Cambios de pruebas en Lite:** `tests/algebra114AsLim.audit.test.ts` AS-LIM-05 pasaba de `it.fails` (GAP conocido) a `it`, porque el GAP quedó cerrado; la aserción no cambió. Nuevas pruebas `tests/polynomialFactorZ.test.ts` (9 casos: x^6-1, x^4-1, x^4+4, x^3+27, 2x^2-2, irreducible, entradas no polinómicas, radicales, entrada no factor).

**Observación de carga (preexistente):** AS-FAC-09 (`factor(x^4+1)`) excede el timeout de 5 s de Vitest en corridas paralelas (~4.8 s aislado); la línea base del HEAD anterior también lo falla en la misma corrida agrupada. No es causado por este cambio.

Evidencia AS-B-07: `tests/algebra229AsB07.audit.test.ts` (fila fuente y factorización con diferencia exacta cero) y `backend/tests/test_algebra229_as_b07.py` (`/api/v1/factor` por HTTP, cuatro factores). Verificado por conclusión de runs vía API.

**Siguiente único:** `ALGEBRA229-AS-B-08-TEST-FIRST` — x^{4}-5x^{2}+4 → \left(x - 2\right) \left(x - 1\right) \left(x + 1\right) \left(x + 2\right) (fila N2) según la matriz congelada Section B (`qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz`).

Bloqueos sin cambio: H2-SG28-DIST-01..08, SECURITY-S25, SY-P-23, SY-X-04-PLUS-HTTP. Global **OPEN**.

**Nota de proceso:** los filtros `paths` de push/PR de cumulative y H1d no excluyen `qa/certification/CONTINUITY_NEXT_ACTION.json`; en commits documentales actualizar solo `continuity.json` y `.md` (ese JSON es un espejo no vinculante, quedó en r160).
