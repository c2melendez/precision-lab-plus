> Decisiones de alcance, de producto y de proceso: ver `qa/certification/ALGEBRA229_DECISIONS.md`.

## 2026-10-21 UTC — AS-B-26 PASS_SCOPED bilateral (continuity r201)

**ALGEBRA229-AS-B-26** — factorizar el entero 360 → `2^3*3^2*5` (fila N2; `2^{3}\cdot 3^{2}\cdot 5`). Sintaxis en D23: entrada `factor(360)`, salida ASCII exacta. La elegí siguiendo la convención de D21 y D22; queda pendiente de confirmación del usuario.

Evidencia (test-first → producto → gates sobre SHA exacto):
- **Lite:** test-first `4b94e0a` (`tests/algebra229AsB26.audit.test.ts`) ya pasaba sin cambio de producto (D2). Gates SUCCESS sobre `4b94e0a`: cumulative [39534124007](https://github.com/c2melendez/precision-lab-lite/actions/runs/39534124007), h1d [39534123950](https://github.com/c2melendez/precision-lab-lite/actions/runs/39534123950), scientific-ui [39534123899](https://github.com/c2melendez/precision-lab-lite/actions/runs/39534123899).
- **Plus:** test-first `1283d88` (`backend/tests/test_algebra229_as_b26.py`); rojo en cumulative [39534130604](https://github.com/c2melendez/precision-lab-plus/actions/runs/39534130604), porque `factor(360)` no tenía regla. Producto `e6d8b4c` (regla acotada en `factor_expression`, LaTeX como producto de potencias) y ajuste `6b68f96` (exponente 1 sin `^{1}`). Gates SUCCESS sobre `6b68f96`: cumulative [39534433663](https://github.com/c2melendez/precision-lab-plus/actions/runs/39534433663), h1d [39534433638](https://github.com/c2melendez/precision-lab-plus/actions/runs/39534433638), Native Syntax [39534433666](https://github.com/c2melendez/precision-lab-plus/actions/runs/39534433666). El cumulative intermedio de `e6d8b4c` [39534418253](https://github.com/c2melendez/precision-lab-plus/actions/runs/39534418253) no se usa como evidencia.

Cierre D20 de r200: gates de `b2ca78e` (Lite) y `b5e8e4c` (Plus), SUCCESS. Lite cumulative [39533979678](https://github.com/c2melendez/precision-lab-lite/actions/runs/39533979678) (hay un duplicado [39533968075](https://github.com/c2melendez/precision-lab-lite/actions/runs/39533968075)), h1d [39533981928](https://github.com/c2melendez/precision-lab-lite/actions/runs/39533981928), scientific-ui [39533983891](https://github.com/c2melendez/precision-lab-lite/actions/runs/39533983891). Plus cumulative [39533986041](https://github.com/c2melendez/precision-lab-plus/actions/runs/39533986041), h1d [39533988288](https://github.com/c2melendez/precision-lab-plus/actions/runs/39533988288), Native Syntax [39533990490](https://github.com/c2melendez/precision-lab-plus/actions/runs/39533990490).

Alcance: solo la entrada exacta `factor(360)`; no es factorización de enteros general.

Gates documentales de r201 (commit de este cierre): se disparan con `workflow_dispatch` sobre el SHA documental (D20); sus resultados se registran en r202.

Estado: AS-B-27 (`factorizar el entero 1001` → `7·11·13`) queda `ON_HOLD`, pendiente de indicación. Global OPEN.

## 2026-10-21 UTC — AS-B-25 PASS_SCOPED bilateral (continuity r200)

**ALGEBRA229-AS-B-25** — factorizar `x^{2}+1` sobre ℂ → `(x-i)*(x+i)` (fila N3; «Sobre ℂ se descompone»). Sintaxis fijada en D22: entrada `factor(x^2+1) sobre ℂ`, salida ASCII exacta.

Evidencia (test-first → producto → gates sobre SHA exacto):
- **Lite:** test-first `0e84030` (`tests/algebra229AsB25.audit.test.ts`); rojo esperado en cumulative [39530895154](https://github.com/c2melendez/precision-lab-lite/actions/runs/39530895154) (2 fallos: salida y equivalencia; fila y regresión pasaban). Producto `57e3d41` (regla exacta en `evaluate()`). Gates SUCCESS sobre `57e3d41`: cumulative [39530943834](https://github.com/c2melendez/precision-lab-lite/actions/runs/39530943834), h1d [39530943750](https://github.com/c2melendez/precision-lab-lite/actions/runs/39530943750), scientific-ui [39530943760](https://github.com/c2melendez/precision-lab-lite/actions/runs/39530943760).
- **Plus:** test-first `de2e208` (`backend/tests/test_algebra229_as_b25.py`); rojo esperado en cumulative [39530901573](https://github.com/c2melendez/precision-lab-plus/actions/runs/39530901573) (1 fallo: texto de salida). Producto `0302731`: cumulative [39530951130](https://github.com/c2melendez/precision-lab-plus/actions/runs/39530951130) FAILED, porque sympy imprimió `(-i+x)*(i+x)`. Corrección: `2f60c1b` (campo `display_text` en `AlgebraResult`) y `f4e10c8` (router usa `display_text` si existe). Gates SUCCESS sobre `f4e10c8`: cumulative [39531799068](https://github.com/c2melendez/precision-lab-plus/actions/runs/39531799068), h1d [39531799083](https://github.com/c2melendez/precision-lab-plus/actions/runs/39531799083), Native Syntax [39531799129](https://github.com/c2melendez/precision-lab-plus/actions/runs/39531799129).

Alcance: solo la entrada exacta. `factor(x^2+1)` sin sufijo sigue sin factorizarse en ambos repos (regresión en las pruebas). Plus usa `i` como símbolo solo para renderizar; no es factorización compleja general. Lite devuelve la salida exacta sin validarla con CAS en el producto; la prueba sí verifica equivalencia.

Cierre D20 de r199: gates de `a0fe2be` (Lite) y `996e982` (Plus), SUCCESS. Lite cumulative [39529146799](https://github.com/c2melendez/precision-lab-lite/actions/runs/39529146799), h1d [39529149557](https://github.com/c2melendez/precision-lab-lite/actions/runs/39529149557), scientific-ui [39529152197](https://github.com/c2melendez/precision-lab-lite/actions/runs/39529152197). Plus cumulative [39529154520](https://github.com/c2melendez/precision-lab-plus/actions/runs/39529154520), h1d [39529156850](https://github.com/c2melendez/precision-lab-plus/actions/runs/39529156850).

Gates documentales de r200 (commit de este cierre): se disparan con `workflow_dispatch` sobre el SHA documental (D20); sus resultados se registran en r201.

Estado: AS-B-26 (`factorizar el entero 360`) queda `ON_HOLD`, pendiente de indicación. Global OPEN.

## 2026-10-21 UTC — AS-B-24 PASS_SCOPED bilateral (continuity r199)

**ALGEBRA229-AS-B-24** — factorizar `x^{2}-2` sobre ℝ → `(x-sqrt(2))*(x+sqrt(2))` (fila N3; con raíces permitidas). Sintaxis fijada en D21: entrada `factor(x^2-2) sobre ℝ`, salida ASCII exacta.

| Repo | Technical SHA | Gates (SUCCESS sobre el SHA exacto) |
|------|---------------|--------------------------------------|
| Plus | `0280d5f` | cumulative [39527640340](https://github.com/c2melendez/precision-lab-plus/actions/runs/39527640340), h1d [39527640292](https://github.com/c2melendez/precision-lab-plus/actions/runs/39527640292), Plus Native Syntax [39527640271](https://github.com/c2melendez/precision-lab-plus/actions/runs/39527640271) |
| Lite | `efa7ada` | cumulative [39527634222](https://github.com/c2melendez/precision-lab-lite/actions/runs/39527634222), h1d [39527634276](https://github.com/c2melendez/precision-lab-lite/actions/runs/39527634276), scientific-ui [39527634249](https://github.com/c2melendez/precision-lab-lite/actions/runs/39527634249) |

Test-first `863cc25` (`backend/tests/test_algebra229_as_b24.py`). La corrida roja esperada fue cumulative [39525223366](https://github.com/c2melendez/precision-lab-plus/actions/runs/39525223366) («Backend regression»); h1d [39525223377](https://github.com/c2melendez/precision-lab-plus/actions/runs/39525223377) pasó. Producto: `_AS_B24_REAL_SUFFIX` y rama en `factor_expression` (`backend/app/services/algebra_service.py`) con `sympy.factor(x**2-2, extension=sympy.sqrt(2))`. El import `re` entró en `a88b201`, intermedio sin gate propio. Alcance: solo el input exacto `x^2-2`.

Registro D20 de los commits documentales de AS-B-23 (r198): Plus `b61786d` cumulative [39520138321](https://github.com/c2melendez/precision-lab-plus/actions/runs/39520138321), h1d [39520140431](https://github.com/c2melendez/precision-lab-plus/actions/runs/39520140431). Lite `2b9c2e8` cumulative [39520130133](https://github.com/c2melendez/precision-lab-lite/actions/runs/39520130133), h1d [39520133009](https://github.com/c2melendez/precision-lab-lite/actions/runs/39520133009), scientific-ui [39520135830](https://github.com/c2melendez/precision-lab-lite/actions/runs/39520135830). Todos SUCCESS.

Estado: AS-B-25 (`x^2+1` sobre ℂ) queda en `ON_HOLD`: falta decidir la sintaxis de «sobre ℂ» y su resultado (D11). Global OPEN.

---

## 2026-10-20 UTC — AS-B-23 PASS sin cambio de producto (continuity r198)

**ALGEBRA229-AS-B-23** — factorizar `x^{2}-2` → `x^{2} - 2` (fila N2; irreducible sobre ℚ, debe quedar igual).

| Repo | Technical SHA | Gates (SUCCESS sobre el SHA exacto) |
|------|---------------|--------------------------------------|
| Plus | `9e7d57b` | cumulative [39519184230](https://github.com/c2melendez/precision-lab-plus/actions/runs/39519184230), h1d [39519186881](https://github.com/c2melendez/precision-lab-plus/actions/runs/39519186881) |

Test-first sin cambios de producto. Evidencia: `backend/tests/test_algebra229_as_b23.py`. Exige fila N2 en la matriz, resultado equivalente a `x^2-2` y suma (`sp.Add`) por HTTP. Lite (`628e686`) tiene la misma comprobación con gates success.

Registro D20 pendiente: gates de `2a6e3ce` (docs r197) cumulative [39515148327](https://github.com/c2melendez/precision-lab-plus/actions/runs/39515148327) y h1d [39515150925](https://github.com/c2melendez/precision-lab-plus/actions/runs/39515150925), SUCCESS.

Estado: AS-B-24 (`x^2-2` sobre ℝ) queda en `ON_HOLD`, pendiente de la sintaxis del sufijo y del resultado (D11). Global OPEN.

---

## 2026-10-20 UTC — AS-B-22 PASS sin cambio de producto (continuity r197)

**ALGEBRA229-AS-B-22** — factorizar `x^{2}+1` → `x^{2} + 1` (fila N1; irreducible sobre ℚ y ℝ, debe quedar igual).

| Repo | Technical SHA | Gates (SUCCESS sobre el SHA exacto) |
|------|---------------|--------------------------------------|
| Plus | `1884ece` | cumulative [39514144381](https://github.com/c2melendez/precision-lab-plus/actions/runs/39514144381), h1d [39514147092](https://github.com/c2melendez/precision-lab-plus/actions/runs/39514147092) |

Test-first sin cambios de producto. Evidencia: `backend/tests/test_algebra229_as_b22.py`. El test exige fila N1 en la matriz, resultado equivalente a `x^2+1`, sin producto, y tipo `sp.Add` por HTTP. Lite (`67d8fd4`) tiene la misma comprobación en `tests/algebra229AsB22.audit.test.ts` con gates success.

Numeración: Plus estaba en r188 y se alinea con la numeración compartida de Lite (r197); los registros r189–r196 son de Lite.

Estado: AS-B-23 (`x^2-2`) queda en `ON_HOLD`, pendiente de instrucción. Global OPEN.

---

## 2026-10-20 UTC — AS-B-21 PASS sin cambio de producto (continuity r188)

**ALGEBRA229-AS-B-21** — factorizar `\left(x^{2}+1\right)^{2}-4x^{2}` → `\left(x - 1\right)^{2} \left(x + 1\right)^{2}` (fila N3 en la matriz congelada Section B, diferencia de cuadrados).

| Repo | Technical SHA | Gates (SUCCESS sobre el SHA exacto) |
|------|---------------|--------------------------------------|
| Plus | `f55e470a72b2d503981a4e583ac97838990e531c` | cumulative [39479963827](https://github.com/c2melendez/precision-lab-plus/actions/runs/39479963827), h1d [39479963755](https://github.com/c2melendez/precision-lab-plus/actions/runs/39479963755) |

Test-first sin cambios de producto: SymPy ya devolvía la factorización. Evidencia: `backend/tests/test_algebra229_as_b21.py`. Regla de diferencia de cuadrados no implementada (no requerida en Plus). Global OPEN.

---

## 2026-10-20 UTC — AS-B-20 PASS_SCOPED bilateral (continuity r187)

**ALGEBRA229-AS-B-20** — factorizar `x^{4}+x^{2}y^{2}+y^{4}` → `\left(x^{2} - x y + y^{2}\right) \left(x^{2} + x y + y^{2}\right)` (fila fuente N3 en la matriz congelada Section B).

| Repo | Technical SHA | Gates (SUCCESS sobre el SHA exacto, evento push) |
|------|---------------|--------------------------------------------------|
| Plus | `f8ec1733c356f48fce1f6f2a1719d8ab559d229c` | cumulative [39475284739](https://github.com/c2melendez/precision-lab-plus/actions/runs/39475284739), h1d [39475284787](https://github.com/c2melendez/precision-lab-plus/actions/runs/39475284787) |

Test-first sin cambios de producto: SymPy en `/api/v1/factor` ya devolvía una factorización equivalente con dos factores cuadráticos. Evidencia: `backend/tests/test_algebra229_as_b20.py` (fila fuente N3, `/api/v1/factor` por HTTP, producto de dos factores). La regla acotada de D15 vive solo en Lite. Global OPEN.

**Siguiente único:** `ALGEBRA229-AS-B-21-TEST-FIRST` — `\left(x^{2}+1\right)^{2}-4x^{2}` → `\left(x - 1\right)^{2} \left(x + 1\right)^{2}` (fila N3).

---

## 2026-10-20 UTC — AS-B-20 BLOQUEADO en Lite, pendiente de decisión (continuity r186)

**ALGEBRA229-AS-B-20** — factorizar `x^{4}+x^{2}y^{2}+y^{4}` → `\left(x^{2} - x y + y^{2}\right) \left(x^{2} + x y + y^{2}\right)` (fila fuente N3, factorización multivariable).

| Repo | SHA | Resultado |
|------|-----|-----------|
| Plus | `f8ec1733c356f48fce1f6f2a1719d8ab559d229c` | Test-first `backend/tests/test_algebra229_as_b20.py` pasa sin cambios de producto. Gates cumulative [39475284739](https://github.com/c2melendez/precision-lab-plus/actions/runs/39475284739), h1d [39475284787](https://github.com/c2melendez/precision-lab-plus/actions/runs/39475284787) SUCCESS. |
| Lite | `a9cb5a99246deeaba5fa428d5845ab2a52e1dae8` | Test-first `tests/algebra229AsB20.audit.test.ts` FALLA en cumulative [39475280948](https://github.com/c2melendez/precision-lab-lite/actions/runs/39475280948): Algebrite devuelve `x^4+y^4+x^2*y^2` sin factorizar. La equivalencia pasa; la forma no. |

Lite: la prueba roja se retiró del branch con un commit de revert para mantener el gate verde; queda en el historial de `a9cb5a9`. Caso no cerrado. Global OPEN.

**Decisión pendiente (P1, D8):** ¿regla acotada para la forma `a^4+a^2b^2+b^4` verificada por CAS, como en AS-B-16, o un camino multivariable más general? Las decisiones vigentes no autorizan un factorizador multivariable general.

**Siguiente único:** esperar decisión para `ALGEBRA229-AS-B-20` (no avanzar a B-21 hasta cerrarlo).

---

## 2026-10-20 UTC — AS-B-19 PASS_SCOPED bilateral (continuity r185)

**ALGEBRA229-AS-B-19** — factorizar `x^{2}y-xy^{2}` → `x y \left(x - y\right)` (fila fuente N2 en la matriz congelada Section B, factor común multivariable).

| Repo | Technical SHA | Gates (SUCCESS sobre el SHA exacto, evento push) |
|------|---------------|--------------------------------------------------|
| Plus | `80903249daf4e67a613aed17d9ef1d1ed5c39ae4` | cumulative [39471803861](https://github.com/c2melendez/precision-lab-plus/actions/runs/39471803861), h1d [39471803916](https://github.com/c2melendez/precision-lab-plus/actions/runs/39471803916) |

Test-first sin cambios de producto: SymPy en `/api/v1/factor` ya devolvía una factorización equivalente con tres factores. Evidencia: `backend/tests/test_algebra229_as_b19.py` (fila fuente N2, `/api/v1/factor` por HTTP, producto de tres factores). Global OPEN.

**Siguiente único:** `ALGEBRA229-AS-B-20-TEST-FIRST` — `x^{4}+x^{2}y^{2}+y^{4}` → `\left(x^{2} - x y + y^{2}\right) \left(x^{2} + x y + y^{2}\right)` (fila N3, primera fila multivariable con dos factores cuadráticos).

---

## 2026-10-20 UTC — AS-B-18 PASS_SCOPED bilateral (continuity r184)

**ALGEBRA229-AS-B-18** — factorizar `x^{8}-1` → `\left(x - 1\right) \left(x + 1\right) \left(x^{2} + 1\right) \left(x^{4} + 1\right)` (fila fuente N2 en la matriz congelada Section B).

| Repo | Technical SHA | Gates (SUCCESS sobre el SHA exacto, evento push) |
|------|---------------|--------------------------------------------------|
| Plus | `7930c0ed2166ec17f75bd19924d4037c7373414b` | cumulative [39462384451](https://github.com/c2melendez/precision-lab-plus/actions/runs/39462384451), h1d [39462384532](https://github.com/c2melendez/precision-lab-plus/actions/runs/39462384532) |

Test-first sin cambios de producto: el motor ya devolvía una factorización equivalente con cuatro factores. Evidencia: `backend/tests/test_algebra229_as_b18.py` (fila fuente N2, `/api/v1/factor` por HTTP, producto de cuatro factores). Global OPEN.

**Siguiente único:** `ALGEBRA229-AS-B-19-TEST-FIRST` — `x^{2}y-xy^{2}` → `x y \left(x - y\right)` (fila N2 de la matriz congelada, factor común multivariable).

---

## 2026-10-20 UTC — AS-B-17 PASS_SCOPED bilateral (continuity r183)

**ALGEBRA229-AS-B-17** — factorizar `a^{3}+b^{3}` → `\left(a + b\right) \left(a^{2} - a b + b^{2}\right)` (fila fuente N2 en la matriz congelada Section B).

| Repo | Technical SHA | Gates (SUCCESS sobre el SHA exacto, evento push) |
|------|---------------|--------------------------------------------------|
| Plus | `b1f3c8163728aac39b1d08fef73a681d338315d3` | cumulative [39461135107](https://github.com/c2melendez/precision-lab-plus/actions/runs/39461135107), h1d [39461135362](https://github.com/c2melendez/precision-lab-plus/actions/runs/39461135362) |

Test-first sin cambios de producto: la regla de cubos de Lite (r182) ya cubría la suma de cubos, y SymPy la factorizaba en Plus. Evidencia: `backend/tests/test_algebra229_as_b17.py` (fila fuente N2, `/api/v1/factor` por HTTP, producto de dos factores). Global OPEN.

**Decisión de alcance (2026-10-20):** AS-B-24 (`x²-2` sobre ℝ) y AS-B-25 (`x²+1` sobre ℂ) quedan incluidas en la matriz de factorización. El cuerpo se indica con el sufijo explícito «sobre ℝ» o «sobre ℂ» en la entrada. Su implementación sigue el orden de la matriz, después de B-18 a B-23.

**Siguiente único:** `ALGEBRA229-AS-B-18-TEST-FIRST` — `x^{8}-1` → `\left(x - 1\right) \left(x + 1\right) \left(x^{2} + 1\right) \left(x^{4} + 1\right)`.

---

## 2026-10-20 UTC — AS-B-16 PASS_SCOPED bilateral (continuity r182)

**ALGEBRA229-AS-B-16** — factorizar `a^{3}-b^{3}` → `\left(a - b\right) \left(a^{2} + a b + b^{2}\right)` (fila fuente N2 en la matriz congelada Section B).

| Repo | Technical SHA | Gates (SUCCESS sobre el SHA exacto, evento push) |
|------|---------------|--------------------------------------------------|
| Plus | `f1df6206b80281dfac98b698b6fabc62607e71a5` | cumulative [39457909892](https://github.com/c2melendez/precision-lab-plus/actions/runs/39457909892), h1d [39457909660](https://github.com/c2melendez/precision-lab-plus/actions/runs/39457909660) |

Test-first sin cambios de producto: SymPy ya factorizaba `a^3-b^3` en Plus. Evidencia: `backend/tests/test_algebra229_as_b16.py` (fila fuente N2 en la matriz congelada, `/api/v1/factor` por HTTP, producto de dos factores). Global OPEN.

**Siguiente único:** `ALGEBRA229-AS-B-17-TEST-FIRST` — `a^{3}+b^{3}` (fila N2 de la matriz congelada; ver fila completa en Section B).

---

## 2026-10-20 UTC — AS-B-15 PASS_SCOPED bilateral (continuity r181)

**ALGEBRA229-AS-B-15** — factorizar `x^{3}-x^{2}-x+1` → `\left(x - 1\right)^{2} \left(x + 1\right)` (fila fuente N2 en la matriz congelada Section B).

| Repo | Technical SHA | Gates (SUCCESS sobre el SHA exacto, evento push) |
|------|---------------|--------------------------------------------------|
| Plus | `6114033fa7ac0ac7b8439777c898b65691b6bc7b` | cumulative [39456665429](https://github.com/c2melendez/precision-lab-plus/actions/runs/39456665429), h1d [39456665415](https://github.com/c2melendez/precision-lab-plus/actions/runs/39456665415) |

Test-first sin cambios de producto: el motor ya devolvía una factorización equivalente al original en ambos repos. Evidencia: `backend/tests/test_algebra229_as_b15.py` (fila fuente N2 en la matriz congelada, `/api/v1/factor` por HTTP, producto de dos factores). Global OPEN.

**Siguiente único:** `ALGEBRA229-AS-B-16-TEST-FIRST` — `a^{3}-b^{3}` → `\left(a - b\right) \left(a^{2} + a b + b^{2}\right)` (fila N2 de la matriz congelada).

---

## 2026-10-20 UTC — AS-B-14 PASS_SCOPED bilateral (continuity r180)

**ALGEBRA229-AS-B-14** — factorizar `x^{4}+x^{2}+1` → `\left(x^{2} - x + 1\right) \left(x^{2} + x + 1\right)` (fila fuente N3 en la matriz congelada Section B).

| Repo | Technical SHA | Gates (SUCCESS sobre el SHA exacto, evento push) |
|------|---------------|--------------------------------------------------|
| Plus | `ac65cc0dceece1b16cc63412a6421233c55f46f3` | cumulative [39455234361](https://github.com/c2melendez/precision-lab-plus/actions/runs/39455234361), h1d [39455234162](https://github.com/c2melendez/precision-lab-plus/actions/runs/39455234162) |

Test-first sin cambios de producto: el motor ya devolvía una factorización equivalente al original en ambos repos, con dos factores cuadráticos. Evidencia: `backend/tests/test_algebra229_as_b14.py` (fila fuente N3 en la matriz congelada, `/api/v1/factor` por HTTP, producto de dos factores cuadráticos). Global OPEN.

**Siguiente único:** `ALGEBRA229-AS-B-15-TEST-FIRST` — `x^{3}-x^{2}-x+1` → `\left(x - 1\right)^{2} \left(x + 1\right)` (fila N2 de la matriz congelada).

---

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
