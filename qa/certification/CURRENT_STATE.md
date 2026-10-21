## 2026-10-21 UTC — r231: EV-R-01..14 cerrado bilateralmente; EV-M diagnosticado

**EV-R-01..14 (radicales) — PASS_SCOPED_BILATERAL.**

- Lite `c7875936249e…`: cumulative [39683361872] — **SUCCESS**, 349 archivos, **2055 passed**, 8 expected fail, 34 todo; `tests/radicalsEvR01to14.audit.test.ts` **6/6**; guard `skip=false` («No reusable completed evidence found»). h1d [39683361229] y scientific-ui [39683361538] — SUCCESS.
- Plus `870766b99a02…`: cumulative [39683393101] — **SUCCESS**, **1824 passed**, 6 xfailed, cobertura 88.00%; `tests/test_radical_matrix_ev_r01_l14.py` **6/6 PASSED**; guard `skip=false`. h1d [39683393214], native-syntax [39683393055] y SG28 [39683393053]/[39683393210] — SUCCESS. El job `security/backend-security` del gate de seguridad también terminó SUCCESS; `mutation/plus-backend-mutmut` seguía en curso al cierre y es un gate independiente, ajeno a la evidencia EV-R.
- Producto Lite (`radicalRationalize.ts`): reescribe solo un resultado completo `1/(a±√b)` con enteros literales y `|b−a²| = 1` mediante la identidad conjugada exacta; `1/(√2+1)` pasa de `1/(1+2^(1/2))` a **`2^(1/2)-1`**. El resto de formas queda intacto.
- Producto Plus: (a) `parsing.py` convierte la notación radical de índice impar con radicando literal negativo a la **raíz real** (EV-R-03/05: `\sqrt[3]{-8} = -2`, `\sqrt[5]{-32} = -2`), sin tocar el resto de la sintaxis de potencia; (b) `routers/evaluate.py` aplica `sqrtdenest` solo a una raíz cuadrada completa cuyo radicando ya contiene otra raíz cuadrada, con lo que EV-R-11/12 devuelven `1+sqrt(2)` y `sqrt(2)+sqrt(3)`.
- Convenciones **declaradas antes de certificar** en `MANUAL_CAPABILITY_GAPS.md`: notación radical de índice impar = raíz real; potencia con exponente fraccionario = rama principal (`2(-1)^{1/3} = 1+\sqrt{3}i`, EV-R-14); `\sqrt{-4} = 2i` en la rama compleja declarada (EV-R-13); alcances acotados de la racionalización y del denesting.
- Sin regresiones locales: Lite 2050 passed con las 5 fallas patológicas ya conocidas (`algebra114AsFac08/09`, `algebra229AsB06/B18/B20`); CI es el oráculo y quedó verde.

**Siguiente objetivo — EV-M-01..13 (mixtas).** Sondeo local verificado en Lite: EV-M-01, 03, 05, 06, 07, 08, 09, 10, 11 y 12 ya devuelven la forma o el valor pedidos. Defectos detectados antes de certificar:

- **EV-M-02** `e^{2\ln 3}`: Lite devuelve `exp(2*log(3))`; falta la identidad exacta `exp(k·log r) = r^k` (el módulo EV-E solo cubre sumas de logaritmos sin coeficiente).
- **EV-M-04** `f(x)=\ln(x^{2}+1);\ f(\sqrt{e-1})`: error de parseo por `Carácter no reconocido: ";"` en la forma con `\left(...\right)` dentro de la definición (EV-M-05/06/07/08/12 sí resuelven la sustitución).
- **EV-M-13**: Lite devuelve `log(2-3^(1/2))+log(2+3^(1/2))`; falta la identidad `log a + log b = log(a·b)` para concluir `0`.
- Falta verificar la paridad Plus de las 13 filas.

## 2026-10-21 UTC — r230: EV-E-01..14 cerrado bilateralmente; EV-R diagnosticado

**EV-E-01..14 (exponenciales) — PASS_SCOPED_BILATERAL.**

- Lite `16e5ca750f10…`: cumulative [39681554692] — **SUCCESS**, 348 archivos, **2049 passed**, 8 expected fail, 34 todo; `tests/logExpEvE01to14.audit.test.ts` **6/6**; guard `skip=false` («No reusable completed evidence found»). h1d [39681554639] y scientific-ui [39681554580] — SUCCESS.
- Plus `9a06ae8da282…`: cumulative [39681592267] — **SUCCESS**, **1818 passed**, 6 xfailed, cobertura 88.06%; `tests/test_log_exp_matrix_ev_e01_l14.py` **6/6 PASSED**; guard `skip=false`. h1d [39681592361] — SUCCESS.
- Producto (solo Lite): `engine/expLogSimplify.ts` aplica únicamente la identidad exacta `exp(±log r1 ± log r2 …) = producto/cociente` de racionales literales, con enteros seguros y reducción por mcd; se engancha tras `simplifyLogResult`. `e^{ln 2+ln 3}` pasa de `exp(log(2)+log(3))` a **`6`**. Las formas no soportadas (términos no logarítmicos, argumentos simbólicos, magnitudes fuera del rango entero seguro) se devuelven intactas: sin aproximación ni heurística.
- Oráculos por fila: exactos EV-E-01/03/04/05/06/10/13; EV-E-02/07/08/09/11/12 contra las referencias de nueve decimales (EV-E-11 en relativo); EV-E-13 `-1` (la fila lo documenta en ℂ); EV-E-14 `1` bajo la convención declarada.
- Decisiones declaradas en `MANUAL_CAPABILITY_GAPS.md`: (a) `0^0 = 1` para EV-E-14; (b) EV-E-12 conserva como `result_text` la fracción exacta de ~3600 dígitos en **ambos** motores mientras el canal aproximado da `2.716923932` — limitación de presentación/complejidad, no matemática; el oráculo numérico de la fila se cumple.

**Siguiente objetivo — EV-R-01..14 (radicales).** Sondeo local verificado en Lite: EV-R-01..07, 09, 10, 11 y 12 ya devuelven la forma pedida. Defectos y convenciones a resolver antes de certificar:

- **EV-R-08** `1/(√2+1)`: Lite devuelve `1/(1+2^(1/2))` (valor correcto, forma sin racionalizar); la fila exige `√2−1`.
- **EV-R-13** `√−4`: Lite devuelve `2i`; la fila admite la rama compleja **solo si se declara** (en ℝ exige error claro).
- **EV-R-14** `(−8)^{1/3}`: Lite devuelve la forma principal `2*(-1)^(1/3)` (≈1+1.732i); la fila exige declarar real `−2` o principal.
- Falta verificar la paridad Plus de las 14 filas y fijar ambas convenciones antes de emitir PASS.

## 2026-10-21 UTC — r229: EV-L cerrado, EV-I-09/I-10 cerrados bilateralmente; EV-E diagnosticado

**Reconciliación previa:** el índice estaba en r228 (EV-I-07) mientras HEAD ya había avanzado con la implementación EV-L (Lite `86cd568b`, `47988786`; Plus `fd9158ff`…`6edbb54d`). Se verificó la evidencia real de esos SHA antes de heredar objetivo: guard `skip=false` ("No reusable completed evidence found") y pruebas EV-L ejecutadas y aprobadas, no omitidas.

**EV-L-01..14 (logarítmicas) — PASS_SCOPED_BILATERAL.**

- Lite `47988786a6340d434db67a7a627ff525ae697864`: cumulative [39651672489](https://github.com/c2melendez/precision-lab-lite/actions/runs/39651672489) — SUCCESS, 346 archivos, 2034 passed, 8 expected fail, 34 todo; `tests/trigonometryEvL01to14.audit.test.ts` 6/6. h1d [39651672506](https://github.com/c2melendez/precision-lab-lite/actions/runs/39651672506) y scientific-ui [39651672303](https://github.com/c2melendez/precision-lab-lite/actions/runs/39651672303) — SUCCESS.
- Plus `6edbb54d2b13e897e98c83f3a6872eefae869765`: cumulative [39661568080](https://github.com/c2melendez/precision-lab-plus/actions/runs/39661568080) — SUCCESS, backend 1806 passed, 6 xfailed, cobertura 88.08%; `tests/test_log_matrix_ev_l01_l14.py` 5/5 PASSED. h1d [39661568110](https://github.com/c2melendez/precision-lab-plus/actions/runs/39661568110), native-syntax [39661568063](https://github.com/c2melendez/precision-lab-plus/actions/runs/39661568063) y SG28 [39661568064](https://github.com/c2melendez/precision-lab-plus/actions/runs/39661568064) — SUCCESS.
- Alcance: EV-L-01/02/03/04/06/07/10 exactos; EV-L-05/08/11 con forma exacta y referencia redondeada a 9 decimales; EV-L-09 producto de logs en ASCII y LaTeX; EV-L-12 `DOMAIN_ERROR`; EV-L-13 `i*pi` (rama compleja que documenta la fila); EV-L-14 base inválida con error claro.

**EV-I-09 / EV-I-10 — PASS_SCOPED_BILATERAL.** Eran los dos defectos abiertos exclusivos de Lite.

- Producto (Lite): nuevo `engine/inverseTrigComposition.ts` conectado en `evaluate`. `arcsin(sin 2)` devuelve `-2+pi` (antes `2`, rama incorrecta) y `sin(arccos 3/5)` devuelve `4/5` (antes sin evaluar). Se cubren además las ramas principales de `arccos(cos t)` y `arctan(tan t)` (antes `2` en ambos) y las identidades pitagóricas `cos(arcsin u)`, `tan(arcsin u)`, `tan(arccos u)`. Solo actúa sobre una composición completa con argumento numérico; lo simbólico queda intacto.
- Hallazgo adicional: la validación G3 rechazaba los macros LaTeX contractuales (`\arcsin`, `\arccos`, `\arctan`, `\arcsec`, `\arccsc`, `\arccot` y las inversas hiperbólicas) con «Comando desconocido», de modo que las filas oficiales EV-I solo eran certificables por el canal ASCII. Corregido en `parsing/normalize.ts`.
- Lite `bd9c207c1b091bfd017fb8f3ca7ff8f21e06415b`: cumulative [39679799460](https://github.com/c2melendez/precision-lab-lite/actions/runs/39679799460) — SUCCESS, 347 archivos, 2043 passed, 8 expected fail, 34 todo; `tests/trigonometryEvI09I10.audit.test.ts` 9/9; h1d [39679798743](https://github.com/c2melendez/precision-lab-lite/actions/runs/39679798743) y scientific-ui [39679798735](https://github.com/c2melendez/precision-lab-lite/actions/runs/39679798735) — SUCCESS.
- Plus `996ed03026c95ced15443a579c35115f25d5e3c3`: cumulative [39679906072](https://github.com/c2melendez/precision-lab-plus/actions/runs/39679906072) — SUCCESS, backend 1812 passed, 6 xfailed, cobertura 88.08%; `tests/test_trigonometry_ev_i09_i10.py` 6/6 PASSED; h1d [39679906136](https://github.com/c2melendez/precision-lab-plus/actions/runs/39679906136) — SUCCESS. Sin cambio de producto: Plus ya devolvía `-2+pi` y `4/5`.

**Siguiente objetivo — EV-E-01..14 (exponenciales) de `matriz_log_exp_radicales`.** Sondeo local verificado en ambos motores: EV-E-01..09, EV-E-11 y EV-E-13 ya son correctos; **EV-E-10** `e^{ln 2+ln 3}` devuelve `6` en Plus pero queda simbólico `exp(log(2)+log(3))` en Lite (defecto de producto Lite); **EV-E-12** `(1+1/1000)^{1000}` devuelve una fracción exacta de ~3600 dígitos como `result_text` en **ambos** motores, mientras `result_approx` sí es `2.716923932` (defecto bilateral de presentación/complejidad); **EV-E-14** `0^{0}` devuelve `1` en ambos, valor que la fila admite solo bajo convención declarada (declarar en `MANUAL_CAPABILITY_GAPS.md`). No se declara ningún PASS de EV-E.

Certificación global continúa **OPEN** por los bloqueos independientes registrados (SG28/DIST, S25, SY-P-23, SY-X-04 Plus HTTP, Algebra229-AS-B-29).

---

## 2026-10-21 UTC — EV-I-07 cierre r228 y arranque de EV-L (logarítmicas)

**EV-I-07 — `arccot(-1) = 3π/4`: PASS_SCOPED_BILATERAL.** La matriz congelada exige el rango principal `(0, π)`; SymPy usaba `(-π/2, π/2]` (`acot(-1) = -π/4`).

- Cambio de producto: en `evaluate_service`, si la expresión contiene `acot` se reescribe a `π/2 − atan(x)` antes de evaluar (identidad exacta para todo real, incluido 0).
- Plus `f8bdd40a2bbd6016f412019a246e4dbce23835f1`: cumulative [39648580772](https://github.com/c2melendez/precision-lab-plus/actions/runs/39648580772) — SUCCESS, 1801 passed, 6 xfailed; h1d [39648579685](https://github.com/c2melendez/precision-lab-plus/actions/runs/39648579685) — SUCCESS.
- Lite `76e89a9b3546ad73b4be61fea4cd48de5905195f`: cumulative [39648569475](https://github.com/c2melendez/precision-lab-lite/actions/runs/39648569475) (2028 passed), h1d [39648569239](https://github.com/c2melendez/precision-lab-lite/actions/runs/39648569239) y scientific-ui [39648569417](https://github.com/c2melendez/precision-lab-lite/actions/runs/39648569417) — SUCCESS. Cierre bilateral completo.
- Resultado: `acot(-1)=3*pi/4`, `acot(0)=pi/2`, `acot(1)=pi/4`.

**EV-L (logarítmicas) — estado inicial del sondeo:** Plus ya resuelve exactamente `log(8)/log(2)=3`, `log(8)/log(4)=3/2`, `log(2)/log(8)=1/3`, `log(1000)/log(10)=3`, `ln(10^50)=50*ln(10)`; `log_1(5)` devuelve `PARSE_ERROR` (base inválida). Lite no simplifica esos cocientes, deja `ln(10^50)` sin reducir y `\log_1(5)` como división entre cero; además `\log_{2}(3)\cdot\log_{3}(4)` falla con error de `_`. El siguiente objetivo es implementar esas simplificaciones/guardas en Lite y cubrir EV-L-01..14 bilateralmente.

**Defectos EV-I abiertos (solo Lite):** `arcsin(sin 2)` devuelve `2` (correcto `π−2`); `sin(arccos(3/5))` queda sin evaluar (correcto `4/5`). Plus ya devuelve `-2 + pi` y `4/5`.

---

## 2026-10-21 UTC — EV-H cierre r227: PASS_SCOPED (canal numérico)

**EV-H-01..12 — PASS_SCOPED.** Gates SUCCESS sobre el SHA técnico `e7107279a0309e9c31114b3b725b51103cffbef7`:

- cumulative: [39596875855](https://github.com/c2melendez/precision-lab-plus/actions/runs/39596875855) — SUCCESS; 1798 passed, 6 xfailed.
- h1d: [39596875727](https://github.com/c2melendez/precision-lab-plus/actions/runs/39596875727) — SUCCESS.
- Alcance: EV-H-01..03 exactos; EV-H-04..09 verificados por `result_approx` contra las fracciones documentadas (`3/4`, `5/4`, `3/5`, `4/3`, `4/5`, `5/3`); EV-H-10/11 a 9 decimales; EV-H-12 identidad exacta `1`.
- Limitación registrada: Plus no simplifica `sinh(ln 2)` a `3/4`; `result_text` queda simbólico y el valor exacto se expone en `result_approx`.
- EV-I grupo A quedó cerrado bilateralmente (Lite cumulative/h1d/scientific-ui SUCCESS).
- Certificación global continúa OPEN por bloqueos independientes.
- Siguiente objetivo: EV-I-07 (rango principal de `arccot`) y los defectos Lite EV-I-09/I-10; después continuar con las matrices siguientes del protocolo (Log/Exp/Radicales).

---

## 2026-10-21 UTC — EV-I grupo A cierre r226; EV-H en ejecución

**EV-I-01..06, EV-I-08 y EV-I-11 — PASS_SCOPED_BILATERAL.** Gates Plus SUCCESS sobre `43738a0fd6387e99a71bdf0124e15fb5c698c877`:

- cumulative: [39596384431](https://github.com/c2melendez/precision-lab-plus/actions/runs/39596384431) — SUCCESS; 1794 passed, 6 xfailed; EV-I 3/3 pruebas PASSED.
- h1d: [39596384432](https://github.com/c2melendez/precision-lab-plus/actions/runs/39596384432) — SUCCESS.
- Lite: cumulative [39596378248](https://github.com/c2melendez/precision-lab-lite/actions/runs/39596378248) (2016 passed), h1d [39596378313](https://github.com/c2melendez/precision-lab-lite/actions/runs/39596378313) y scientific-ui [39596378121](https://github.com/c2melendez/precision-lab-lite/actions/runs/39596378121) — los tres SUCCESS; cierre bilateral completo.

**EV-H-01..12 (hiperbólicas) test-first publicado** — Plus `e7107279a0309e9c31114b3b725b51103cffbef7` / Lite `54f81f21806fbe02ebf4c40ed237ed244a667de4`; gates en ejecución.

- Alcance: EV-H-01..03 exactos; EV-H-04..09 certificables solo por canal numérico (`result_approx`) porque ningún motor muestra la fracción exacta (`sinh(ln 2)` queda simbólico en Plus; Lite imprime `0.75`, `0.6`, `1.333333...`); EV-H-10/11 a 9 decimales; EV-H-12 identidad exacta `1`.
- Limitación: la forma racional exacta de EV-H-04..09 no se muestra en `result_text`.

---

## 2026-10-21 UTC — AUD-SING cierre r225 y EV-I grupo A en ejecución

**AUD-SING — PASS_SCOPED (corrección de producto en Plus).** Gates SUCCESS sobre el SHA técnico `587aecc1f978e03bb976212f3c32fc632b76d0b0`:

- cumulative: [39595617829](https://github.com/c2melendez/precision-lab-plus/actions/runs/39595617829) — SUCCESS; 1791 passed, 6 xfailed.
- h1d: [39595617779](https://github.com/c2melendez/precision-lab-plus/actions/runs/39595617779) — SUCCESS; native syntax [39595617887](https://github.com/c2melendez/precision-lab-plus/actions/runs/39595617887) — SUCCESS; SG28 prototype [39595617826](https://github.com/c2melendez/precision-lab-plus/actions/runs/39595617826) — SUCCESS.
- **Corrección de producto:** `asin(2)`/`acos(2)` se devolvían ecoados como resultado válido; ahora `evaluate_service` rechaza la forma numérica fuera de `[-1, 1]` con `DOMAIN_ERROR` (argumentos simbólicos intactos). `acot(0)=pi/2`, `sec(90)` en grados, `cot(45)`, `csc(30)` ya eran correctos y quedan cubiertos por pruebas.

**EV-I grupo A en ejecución** — Plus `43738a0fd6387e99a71bdf0124e15fb5c698c877` / Lite `11d0192582c337e38ec3718940f5f620644e44f0`: EV-I-01..06, EV-I-08 (`acot(0)=π/2`) y EV-I-11 (`cos(atan 2)=√5/5`), con fila congelada verificada.

**Pendientes EV-I (el defecto es de Lite, no de Plus):**
- **EV-I-07** `arccot(-1)`: la matriz exige `3π/4`; ambos motores devuelven `-π/4` (convención SymPy `acot` y `arctan(1/x)`). Requiere decisión de contrato y corrección bilateral a rango principal (0, π).
- **EV-I-09** `arcsin(sin 2)`: Plus devuelve `-2 + pi` (correcto, `π-2`); Lite devuelve `2`. Defecto de producto pendiente en Lite.
- **EV-I-10** `sin(arccos(3/5))`: Plus devuelve `4/5` (correcto); Lite deja la expresión sin evaluar. Capacidad pendiente en Lite.

---

## 2026-10-21 UTC — EV-D-12 cierre r224 y auditoría de singularidades evitables (AUD-SING)

**EV-D-12 — `tan(π/2)` indefinida (error claro): PASS_SCOPED.** Fila congelada verificada; los dos gates Plus terminaron SUCCESS con `head_sha` exacto.

- cumulative: [39593883422](https://github.com/c2melendez/precision-lab-plus/actions/runs/39593883422) — SUCCESS; SHA `95601e5b13131af26f94b56028542b4feda56ec5`; EV-D-12 5/5 PASSED; backend 1783 passed, 6 xfailed, cobertura 88.05%.
- h1d: [39593883403](https://github.com/c2melendez/precision-lab-plus/actions/runs/39593883403) — SUCCESS; mismo SHA.
- Plus ya devolvía `DOMAIN_ERROR` para `tan(pi/2)`, `log(0)` y `sec(pi/2)`; el lote añade la cobertura bilateral y el caso `acot(0)=pi/2`.

**Auditoría AUD-SING en ejecución sobre Plus `587aecc1f978e03bb976212f3c32fc632b76d0b0`:**

- **EV-I-12:** `asin(2)`/`acos(2)` se devolvían ecoados como resultado válido; ahora `evaluate_service` rechaza la forma numérica fuera de `[-1, 1]` con `DOMAIN_ERROR` (argumentos simbólicos intactos).
- **Modo grados:** Plus ya convertía `sec/csc/cot` correctamente (`sec(90)`→`DOMAIN_ERROR`, `cot(45)`→1, `csc(30)`→2); se añade prueba de paridad bilateral.
- **Alias hiperbólicos:** Plus rechaza `arcsinh/arccosh/arctanh` con `PARSE_ERROR` (error claro, nunca un valor erróneo); Lite ahora los resuelve como funciones reales. Diferencia de capacidad documentada, sin resultado silencioso incorrecto en ninguno de los dos.
- Gates de este lote en ejecución; no se declara PASS hasta revisar conclusión y logs.

---

## 2026-10-21 UTC — EV-D-11 cierre r223: PASS_SCOPED_BILATERAL

**EV-D-11 — `sin²(π/8) + cos²(π/8) = 1`: PASS_SCOPED_BILATERAL.** Fila congelada verificada; los dos gates Plus terminaron SUCCESS con `head_sha` exacto.

- cumulative: [39583461368](https://github.com/c2melendez/precision-lab-plus/actions/runs/39583461368) — SUCCESS; SHA técnico `2f37ee2f10f8bac361eff592bbe3e0a5a3b654e9`; EV-D-11 2/2 PASSED; backend 1778 passed, 6 xfailed, cobertura 88.07%.
- h1d: [39583461494](https://github.com/c2melendez/precision-lab-plus/actions/runs/39583461494) — SUCCESS; mismo SHA.
- El canal HTTP devuelve `1` literal, sin necesidad de equivalencia adicional.
- Certificación global continúa OPEN por bloqueos independientes.
- Siguiente objetivo: TRIG-EV-D-12-TEST-FIRST (`tan(π/2)` indefinida: contrato de error claro). Verificar antes la fila fuente y el contrato de error vigente.

---

## 2026-10-21 UTC — EV-D-10 cierre r222: PASS_SCOPED_BILATERAL

**EV-D-10 — `cot(π/2) = 0`: PASS_SCOPED_BILATERAL.** Fila congelada verificada; los dos gates Plus terminaron SUCCESS con `head_sha` exacto. Sin cambio de producto: SymPy ya devuelve `0` exacto.

- cumulative: [39563436924](https://github.com/c2melendez/precision-lab-plus/actions/runs/39563436924) — SUCCESS; SHA técnico `b635db5fa6e00fab92a144d421398ff5d5df0763` exacto; EV-D-10 2/2 PASSED; backend 1776 passed, 6 xfailed, cobertura 88.00%.
- h1d: [39563436972](https://github.com/c2melendez/precision-lab-plus/actions/runs/39563436972) — SUCCESS; mismo SHA.
- El defecto equivalente de Lite (`cot` reescrito como `1/tan`) no existe en este motor; la corrección de producto es exclusiva de Lite (`4c92b797`).
- Certificación global continúa OPEN por bloqueos independientes.
- Siguiente objetivo en ejecución: TRIG-EV-D-11-TEST-FIRST (identidad pitagórica `sin²(π/8)+cos²(π/8)=1`), tests publicados en el SHA técnico `2f37ee2f10f8bac361eff592bbe3e0a5a3b654e9`.

---

## 2026-10-21 UTC — EV-D-09 cierre r221 y EV-D-10 en ejecución

**EV-D-09 — `cos(2) ≈ -0.416146837`: PASS_SCOPED_BILATERAL.** Fila congelada verificada; los dos gates Plus terminaron SUCCESS con `head_sha` exacto.

- cumulative: [39562389148](https://github.com/c2melendez/precision-lab-plus/actions/runs/39562389148) — SUCCESS; SHA técnico `efeba0caecfae5ce824c481d02b3b7bb21d05d76` exacto.
- h1d: [39562389051](https://github.com/c2melendez/precision-lab-plus/actions/runs/39562389051) — SUCCESS; mismo SHA.
- Pruebas EV-D-09: 3/3 PASSED; backend 1774 passed, 6 xfailed, cobertura 88.00%; frontend typecheck, regresión y production build SUCCESS.

**EV-D-10 — `cot(π/2) = 0`: cobertura publicada, sin cambio de producto (gate en ejecución).** SymPy ya devuelve `0` exacto para `cot(pi/2)`; el defecto equivalente de Lite (reescritura `1/tan`) no existe en este motor.

- SHA de pruebas: Plus `b635db5fa6e00fab92a144d421398ff5d5df0763`; Lite `b5bd0fa3b06da410d10b9a0fe2503756d7f6570a` (con corrección de producto `cot` → `cos/sin`).
- Gates EV-D-10 en ejecución; no se declara PASS hasta revisar conclusión y logs.
- Certificación global continúa OPEN por bloqueos independientes.

---

## 2026-10-21 UTC — EV-D-08 cierre r220: PASS_SCOPED_BILATERAL

**EV-D-08 — `sin(1) ≈ 0.841470985`: PASS_SCOPED_BILATERAL.** Se verificó la fila congelada `| EV-D-08 | \`\sin(1)\` | \`\approx 0.841470985\` |` y se documentó la convención de oráculo para filas `\approx` en `EXECUTION_PROTOCOL.md`. No se modificó código de producto.

- cumulative: [39561374700](https://github.com/c2melendez/precision-lab-plus/actions/runs/39561374700) — SUCCESS; SHA técnico `e532b9e20054580b0d2f8d2d6ea702d7b173a55d` exacto.
- h1d: [39561374699](https://github.com/c2melendez/precision-lab-plus/actions/runs/39561374699) — SUCCESS; mismo SHA.
- Pruebas EV-D-08: `test_ev_d08_source_row_present_and_frozen`, `test_ev_d08_documented_value_is_correct_rounding` y `test_ev_d08_sin_one_http_ascii_keeps_exact_form_and_matches_documented` PASSED; backend 1771 passed, 6 xfailed, cobertura 88.00%; frontend typecheck, regresión y production build SUCCESS.
- El motor conserva la forma exacta `sin(1)`; el oráculo exige equivalencia simbólica, referencia a 9 decimales con tolerancia 5e-10 y rechaza una salida solo decimal.
- Certificación global continúa OPEN por bloqueos independientes; este cierre solo certifica EV-D-08.
- Siguiente objetivo en ejecución: TRIG-EV-D-09-TEST-FIRST (`cos(2) ≈ -0.416146837`), tests publicados en el SHA técnico `efeba0caecfae5ce824c481d02b3b7bb21d05d76`.

---

## 2026-10-21 UTC — EV-D-07 cierre r219: PASS_SCOPED_BILATERAL

**EV-D-07 — `sin(5π/4) = -√2/2`: PASS_SCOPED_BILATERAL.** Se verificó la fila congelada `| EV-D-07 | \`\sin\left(\frac{5\pi}{4}\right)\` | \`-\frac{\sqrt{2}}{2}\` |`. Los dos gates requeridos terminaron SUCCESS con `head_sha` exacto; no se modificó código de producto.

- cumulative: [39560042890](https://github.com/c2melendez/precision-lab-plus/actions/runs/39560042890) — SUCCESS; SHA técnico `1717a160a5219a06d6542f26e87c94fe7de59fd5` exacto.
- h1d: [39560042860](https://github.com/c2melendez/precision-lab-plus/actions/runs/39560042860) — SUCCESS; mismo SHA.
- Pruebas EV-D-07: `test_ev_d07_source_row_present_and_frozen` y `test_ev_d07_sin_5pi_over_4_http_ascii` PASSED; backend 1768 passed, 6 xfailed, cobertura 88.00%; frontend typecheck, regresión y production build SUCCESS.
- El oráculo HTTP exige equivalencia simbólica con `-√2/2`, cercanía numérica y rechaza una salida decimal; no se modificó producto.
- Certificación global continúa OPEN por bloqueos independientes; este cierre solo certifica EV-D-07.
- Siguiente objetivo: TRIG-EV-D-08-TEST-FIRST (`sin(1) ≈ 0.841470985`). Antes de escribir pruebas, definir el oráculo contractual para filas con `\approx` (tolerancia y dígitos documentados) en ambos motores.

---

## 2026-10-21 UTC — EV-D-06 cierre r218: PASS_SCOPED_BILATERAL

**EV-D-06 — `cot(pi/4)=1`: PASS_SCOPED_BILATERAL.** Se verificó la fila de la matriz trigonométrica congelada. Todos los gates requeridos terminaron SUCCESS y sus `head_sha` coinciden con el SHA técnico indicado. No se modificó código de producto.

- cumulative: [39557484508](https://github.com/c2melendez/precision-lab-plus/actions/runs/39557484508) — SUCCESS; SHA técnico `6369a617e59f2f23fe73ac4e464683de310a688a` exacto.
- h1d: [39557484518](https://github.com/c2melendez/precision-lab-plus/actions/runs/39557484518) — SUCCESS; SHA técnico `6369a617e59f2f23fe73ac4e464683de310a688a` exacto.

- Pruebas específicas EV-D-06: fila fuente congelada y HTTP ASCII `cot(pi/4)` PASSED; backend 1766 passed, 6 xfailed, cobertura 88.05%; frontend typecheck, regresión y production build SUCCESS.
- Diagnóstico del primer intento Lite: la aserción no admitía el resultado `1` entre backticks como aparece en la matriz. Se corrigió únicamente el test. Producto sin cambios.
- Certificación global continúa OPEN por bloqueos independientes registrados; este cierre solo certifica EV-D-06.
- Siguiente objetivo pendiente de ejecución: TRIG-EV-D-07-TEST-FIRST. Antes de escribir pruebas, confirmar la fila EV-D-07 en la fuente congelada; no asumir expresión ni resultado.

---

## 2026-10-21 UTC — EV-D-06 actualización r217: Plus acumulativo PASS

- **Plus cumulative PASS** [39557484508](https://github.com/c2melendez/precision-lab-plus/actions/runs/39557484508), SHA técnico `6369a617e59f2f23fe73ac4e464683de310a688a`: backend 1766 passed, 6 xfailed, cobertura 88.05%; `test_ev_d06_source_row_present_and_frozen` y `test_ev_d06_cot_pi_over_4_http_ascii` PASSED. Frontend typecheck, regresión y production build SUCCESS.
- **Plus H1d PASS** [39557484518](https://github.com/c2melendez/precision-lab-plus/actions/runs/39557484518), mismo SHA.
- **Lite cumulative PASS** [39557479991](https://github.com/c2melendez/precision-lab-lite/actions/runs/39557479991): EV-D-06 3/3, 1975 passed, 8 expected fail, 34 TODO; typecheck/build SUCCESS. **Lite H1d PASS** [39557479974](https://github.com/c2melendez/precision-lab-lite/actions/runs/39557479974).
- Único gate pendiente para el cierre del objetivo: **Lite Scientific UI** [39557480008](https://github.com/c2melendez/precision-lab-lite/actions/runs/39557480008), todavía ejecutando Native desktop/tablet/mobile scientific result verification. EV-D-06 permanece IN_PROGRESS hasta que este gate termine; no se declara PASS bilateral todavía.
- Producto sin cambios. Certificación global OPEN.

---

## 2026-10-21 UTC — EV-D-06 checkpoint r216: gates parciales verificados

- **Lite cumulative PASS** [39557479991](https://github.com/c2melendez/precision-lab-lite/actions/runs/39557479991), SHA técnico `00892789a8cd5c6e12ba43cb47fce4d97f7b1bc8`: suite EV-D-06 3/3; 334/334 archivos Vitest, 1975 passed, 8 expected fail, 34 TODO; typecheck y production build SUCCESS.
- **Lite H1d PASS** [39557479974](https://github.com/c2melendez/precision-lab-lite/actions/runs/39557479974), mismo SHA. **Lite Scientific UI** [39557480008](https://github.com/c2melendez/precision-lab-lite/actions/runs/39557480008) continúa en el paso Native desktop/tablet/mobile scientific result verification.
- **Plus H1d PASS** [39557484518](https://github.com/c2melendez/precision-lab-plus/actions/runs/39557484518), SHA técnico `6369a617e59f2f23fe73ac4e464683de310a688a). **Plus cumulative** [39557484508](https://github.com/c2melendez/precision-lab-plus/actions/runs/39557484508): frontend SUCCESS; backend regression sigue IN_PROGRESS.
- La fila fuente está confirmada como `| EV-D-06 | `\\cot\\left(\\frac{\\pi}{4}\\right)` | `1` |`. Fallo inicial de Lite fue solo el regex que no aceptaba backticks; corregido. No se cambió producto.
- EV-D-06 permanece **IN_PROGRESS** hasta que terminen Lite Scientific UI y Plus cumulative y se revisen logs y SHA. Certificación global OPEN.

---

## 2026-10-21 UTC — EV-D-06 test-first checkpoint; gates pending

**Fuente congelada verificada:** la fila EV-D-06 es `cot(pi/4)=1`, representada como `\\cot\\left(\\frac{\\pi}{4}\\right)` con el resultado en backticks. Se agregó cobertura test-first en ambos motores; no se modificó código de producto.

- **Lite**: commit de pruebas corregido `00892789a8cd5c6e12ba43cb47fce4d97f7b1bc8`. La corrida acumulativa inicial [39557278838](https://github.com/c2melendez/precision-lab-lite/actions/runs/39557278838) falló únicamente porque la aserción del resultado no aceptaba los backticks del formato fuente. El log confirma que las pruebas ASCII y LaTeX sí pasaron; total previo a la corrección: 1974 passed, 1 failed (solo formato de la prueba), 8 expected fail, 34 TODO. Corregido para aceptar `1` y `1` con formato literal de matriz.
- **Plus**: test `backend/tests/test_trigonometry_ev_d06.py`; commit corregido `6369a617e59f2f23fe73ac4e464683de310a688a`, con el mismo ajuste para que la aserción fuente acepte el resultado documentado con backticks. No se ha observado ni autorizado cambio de producto.
- Gates del SHA final están en ejecución: Lite cumulative [39557479991](https://github.com/c2melendez/precision-lab-lite/actions/runs/39557479991), H1d [39557479974](https://github.com/c2melendez/precision-lab-lite/actions/runs/39557479974), Scientific UI [39557480008](https://github.com/c2melendez/precision-lab-lite/actions/runs/39557480008); Plus cumulative [39557484508](https://github.com/c2melendez/precision-lab-plus/actions/runs/39557484508), H1d [39557484518](https://github.com/c2melendez/precision-lab-plus/actions/runs/39557484518). Validar conclusión y SHA exacto antes de marcar PASS.
- **Estado EV-D-06: IN_PROGRESS.** Próxima acción: revisar todos los gates finales y logs, resolver solo fallos demostrados, luego cerrar bilateralmente. Certificación global continúa OPEN por bloqueos previos.

---

## 2026-10-21 UTC — r214: EV-D-05 PASS_SCOPED_BILATERAL; EV-D-06 preparado

**EV-D-05 — `sec(pi/3)=2`: PASS_SCOPED_BILATERAL.** La fila fuente de la matriz congelada y el resultado esperado fueron verificados en las pruebas de ambos motores. No se modificó código de producto.

- **Lite**, test commit `24871267ec1ee9f64bbd2d34fd449b41ee74f99c`: cumulative [39555164790](https://github.com/c2melendez/precision-lab-lite/actions/runs/39555164790), H1d [39555164686](https://github.com/c2melendez/precision-lab-lite/actions/runs/39555164686), Scientific UI [39555164730](https://github.com/c2melendez/precision-lab-lite/actions/runs/39555164730): todos SUCCESS con SHA exacto. El log acumulativo confirma el archivo `tests/trigonometryEvD05.audit.test.ts` con 3/3 pruebas aprobadas; 1972 passed, 8 expected fail y 34 TODO en el total de Vitest.
- **Plus**, test corregido commit `8885a3b47dc6509c52a08312bbc87d5f1651c6da`: cumulative [39556359520](https://github.com/c2melendez/precision-lab-plus/actions/runs/39556359520) y H1d [39556359572](https://github.com/c2melendez/precision-lab-plus/actions/runs/39556359572): ambos SUCCESS con SHA exacto. Backend: 1764 passed, 6 xfailed, cobertura 88.07%; tanto `test_ev_d05_source_row_present_and_frozen` como `test_ev_d05_sec_pi_over_3_http_ascii` PASSED. Frontend typecheck, regresión y build SUCCESS.
- Diagnóstico del intento inicial Plus `7be68dcfbcd9ed64b4f4ae98399276d01ede0034`: import incorrecto `backend.main`, corregido en el test sin alterar el producto. El primer cumulative [39555174858](https://github.com/c2melendez/precision-lab-plus/actions/runs/39555174858) fue FAIL de harness/colección, no fallo matemático; la nueva evidencia válida es la de `8885a3b`.
- Estado global de certificación permanece OPEN por bloqueos independientes registrados (SG28/DIST, S25, SY-P-23, SY-X-04 Plus HTTP y Algebra229-AS-B-29).

**Siguiente objetivo único: `TRIG-EV-D-06-TEST-FIRST` — READY.** Primero leer/verificar la fila EV-D-06 de la matriz congelada; después añadir pruebas test-first bilaterales según los canales contractuales (Lite parser ASCII+LaTeX; Plus HTTP ASCII), activar gates por push y no cambiar producto salvo que la prueba y la fuente demuestren un defecto. No asumir el resultado ni la expresión de EV-D-06 antes de leer la fila oficial.

---

## 2026-10-21 UTC — EV-D-05 actualización r213: H1d Plus PASS, acumulativo pendiente

- Plus H1d [39556359572](https://github.com/c2melendez/precision-lab-plus/actions/runs/39556359572) terminó SUCCESS sobre el SHA técnico `8885a3b47dc6509c52a08312bbc87d5f1651c6da`; se revisaron los pasos, incluido `Run IN625 H1d reentry`, ejecutado y aprobado.
- Plus cumulative [39556359520](https://github.com/c2melendez/precision-lab-plus/actions/runs/39556359520) continúa IN_PROGRESS en su job backend `Backend regression`; frontend finalizó SUCCESS (typecheck, unit/parity y production build). No declarar EV-D-05 cerrado hasta concluir backend, revisar logs y verificar que los tests nuevos pasaron.
- El cierre documental bilateral r212 ya está publicado; esta entrada refresca la evidencia dinámica sin provocar un nuevo gate técnico.

---

## 2026-10-21 UTC — EV-D-05 diagnóstico y gates pendientes

- Lite: commit de pruebas `24871267ec1ee9f64bbd2d34fd449b41ee74f99c`; cumulative [39555164790](https://github.com/c2melendez/precision-lab-lite/actions/runs/39555164790), H1d [39555164686](https://github.com/c2melendez/precision-lab-lite/actions/runs/39555164686) y Scientific UI [39555164730](https://github.com/c2melendez/precision-lab-lite/actions/runs/39555164730) terminaron SUCCESS sobre el SHA esperado.
- Plus: commit inicial `7be68dcfbcd9ed64b4f4ae98399276d01ede0034`; cumulative [39555174858](https://github.com/c2melendez/precision-lab-plus/actions/runs/39555174858) falló durante colección por `ModuleNotFoundError: No module named 'backend'` en el test nuevo. Esto es un fallo del harness/test import, no evidencia de fallo matemático. H1d [39555174838](https://github.com/c2melendez/precision-lab-plus/actions/runs/39555174838) SUCCESS.
- Corrección exclusiva del test en commit `8885a3b47dc6509c52a08312bbc87d5f1651c6da`: import `app.main`, aserción sobre `MathResponse.success/result_text` y comprobación de fila fuente congelada. Producto sin cambios.
- Validación de la corrección: Plus cumulative [39556359520](https://github.com/c2melendez/precision-lab-plus/actions/runs/39556359520) y H1d [39556359572](https://github.com/c2melendez/precision-lab-plus/actions/runs/39556359572), activadas por push con SHA exacto; ambas estaban IN_PROGRESS al redactar este registro.
- Estado: EV-D-05 sigue IN_PROGRESS. No declarar PASS hasta revisar conclusión, jobs/logs y fila fuente. Certificación global OPEN.

---

## 2026-10-21 UTC — r211: cierre EV-D-04 y arranque test-first EV-D-05

**EV-D-04 PASS_SCOPED bilateral** — `csc(pi/6)=2`. Cinco gates SUCCESS y SHA exactos:
- Lite cumulative [39554410679](https://github.com/c2melendez/precision-lab-lite/actions/runs/39554410679), H1d [39554410715](https://github.com/c2melendez/precision-lab-lite/actions/runs/39554410715), Scientific UI [39554410696](https://github.com/c2melendez/precision-lab-lite/actions/runs/39554410696), todos `head_sha=0467aa89c470abf6607d1b67e9c40191642d8df4`.
- Plus cumulative [39552906521](https://github.com/c2melendez/precision-lab-plus/actions/runs/39552906521) y H1d [39552906515](https://github.com/c2melendez/precision-lab-plus/actions/runs/39552906515), ambos `head_sha=f6756dc37bdf193a01de05a4bb9208b65cf47867`.
- No se modificó código de producto; el test Lite usa el parser oficial antes de evaluar.

**EV-D-05 test-first iniciado** — hipótesis a validar: `sec(pi/3)=2`. Añadidas pruebas en Lite `tests/trigonometryEvD05.audit.test.ts` (commit `24871267ec1ee9f64bbd2d34fd449b41ee74f99c`) y Plus `backend/tests/test_trigonometry_ev_d05.py` (commit `7be68dcfbcd9ed64b4f4ae98399276d01ede0034`). Las pruebas verifican también que la fila EV-D-05 y su resultado estén en la matriz congelada. No se cambió producto.

Corridas EV-D-05 actualmente en curso:
- Lite cumulative [39555164790](https://github.com/c2melendez/precision-lab-lite/actions/runs/39555164790), H1d [39555164686](https://github.com/c2melendez/precision-lab-lite/actions/runs/39555164686), Scientific UI [39555164730](https://github.com/c2melendez/precision-lab-lite/actions/runs/39555164730), SHA esperado `24871267ec1ee9f64bbd2d34fd449b41ee74f99c`.
- Plus cumulative [39555174858](https://github.com/c2melendez/precision-lab-plus/actions/runs/39555174858) y H1d [39555174838](https://github.com/c2melendez/precision-lab-plus/actions/runs/39555174838), SHA esperado `7be68dcfbcd9ed64b4f4ae98399276d01ede0034`.

EV-D-05 permanece `IN_PROGRESS`; no declarar PASS hasta verificar fila fuente, resultados y SHA exactos de los cinco gates. Certificación global: `OPEN`.

---

## 2026-10-21 UTC — r210: EV-D-04 diagnóstico y test corregido; cierre pendiente

La corrida acumulativa inicial de Lite [39552903560](https://github.com/c2melendez/precision-lab-lite/actions/runs/39552903560) falló solo en el nuevo test: este llamaba a `evaluate("csc(pi/6)")` directamente, evitando el pipeline oficial del parser. La salida observada fue `csc(1/6*pi)`, no `2`. El parser ya contiene la reescritura de `csc` a `1/sin`; el test debe pasar por `parseExpression` antes de `evaluate`.

Se corrigió únicamente el test Lite en commit `0467aa89c470abf6607d1b67e9c40191642d8df4`; **no se modificó código de producto**. El test Plus ya había pasado en las corridas [39552906521](https://github.com/c2melendez/precision-lab-plus/actions/runs/39552906521) y [39552906515](https://github.com/c2melendez/precision-lab-plus/actions/runs/39552906515), ambas con `head_sha=f6756dc37bdf193a01de05a4bb9208b65cf47867`.

Nuevas corridas de Lite para el SHA corregido `0467aa89c470abf6607d1b67e9c40191642d8df4`:
- cumulative [39554410679](https://github.com/c2melendez/precision-lab-lite/actions/runs/39554410679) — `in_progress`.
- h1d [39554410715](https://github.com/c2melendez/precision-lab-lite/actions/runs/39554410715) — `in_progress`.
- scientific-ui [39554410696](https://github.com/c2melendez/precision-lab-lite/actions/runs/39554410696) — `in_progress`.

No declarar EV-D-04 PASS hasta que terminen las tres corridas y se compruebe `head_sha`. Global certification: `OPEN`.

---

> Decisiones de alcance, de producto y de proceso: ver `qa/certification/ALGEBRA229_DECISIONS.md`.

## 2026-10-21 UTC — Cierre documental r208: gates D20 de r207 verificados

Los seis gates D20 del cierre documental r207 finalizaron en `completed/success`. Cada `head_sha` coincide exactamente con el commit documental r207 del repositorio correspondiente:
- Plus `cumulative`: [39551273508](https://github.com/c2melendez/precision-lab-plus/actions/runs/39551273508) — SUCCESS; `head_sha=bcfe2314ede6fc80b6ba78cd3c2b9c07e9715dd6` exacto.
- Plus `h1d`: [39551275603](https://github.com/c2melendez/precision-lab-plus/actions/runs/39551275603) — SUCCESS; `head_sha=bcfe2314ede6fc80b6ba78cd3c2b9c07e9715dd6` exacto.
- Plus `native-syntax`: [39551277795](https://github.com/c2melendez/precision-lab-plus/actions/runs/39551277795) — SUCCESS; `head_sha=bcfe2314ede6fc80b6ba78cd3c2b9c07e9715dd6` exacto.

**Escapado corregido:** la expresión oficial queda `\csc(\frac{\pi}{6}) → 2` (un solo nivel de escapado LaTeX dentro del código Markdown; sin llaves duplicadas alrededor de `\pi`).

**Siguiente acción sin cambios:** EV-D-04 (`TRIG-EV-D-04-TEST-FIRST`) permanece `READY`, **no iniciado**. No se ejecutaron pruebas de EV-D-04 ni se modificó producto. Global `OPEN`.

---

## 2026-10-21 UTC — r209: EV-D-04 test-first iniciado; gates en ejecución

Objetivo `TRIG-EV-D-04-TEST-FIRST`: `csc(pi/6)=2`. Se añadieron únicamente pruebas de aceptación, antes de modificar producto:
- Lite: `tests/trigonometryEvD04.audit.test.ts`, commit `f6756dc37bdf193a01de05a4bb9208b65cf47867`.
- Plus: `backend/tests/test_trigonometry_ev_d04.py`, commit `f6756dc37bdf193a01de05a4bb9208b65cf47867`.

Estado de las corridas al registrar este checkpoint:
- cumulative: [39552906521](https://github.com/c2melendez/precision-lab-plus/actions/runs/39552906521) — `in_progress`; esperado `head_sha=f6756dc37bdf193a01de05a4bb9208b65cf47867`.
- h1d: [39552906515](https://github.com/c2melendez/precision-lab-plus/actions/runs/39552906515) — `in_progress`; esperado `head_sha=f6756dc37bdf193a01de05a4bb9208b65cf47867`.

No se afirma PASS/FAIL todavía: las corridas siguen activas y el resultado de test-first está pendiente. No se cambió código de producto. Próxima acción: esperar conclusión de todos los gates, inspeccionar los resultados específicos de EV-D-04, corregir solo si las pruebas lo exigen y publicar el cierre final con SHA exactos. Global `OPEN`.

---


## 2026-10-21 UTC — Trigonometría EV-D-03 PASS_SCOPED bilateral (continuity r206)

**EV-D-03** — `\tan(\frac{\pi}{4}) → 1` (fila oficial de `ejercicios_trigonometria.md.gz`).

Evidencia (test-first, sin cambio de producto):
- **Lite** `f07afe1` (`tests/trigonometryEvD03.audit.test.ts`): cumulative [39549185561](https://github.com/c2melendez/precision-lab-lite/actions/runs/39549185561), h1d [39549185671](https://github.com/c2melendez/precision-lab-lite/actions/runs/39549185671), scientific-ui [39549185567](https://github.com/c2melendez/precision-lab-lite/actions/runs/39549185567); SUCCESS.
- **Plus** `fce235b` (`backend/tests/test_trigonometry_ev_d03.py`, HTTP ASCII `tan(pi/4)`): cumulative [39549187134](https://github.com/c2melendez/precision-lab-plus/actions/runs/39549187134), h1d [39549187120](https://github.com/c2melendez/precision-lab-plus/actions/runs/39549187120); SUCCESS.

Alcance: evaluación exacta de tan(π/4)=1. Plus solo en ASCII, igual que EV-D-01 y EV-D-02. No cierra el módulo trig completo. Global OPEN.

Gates documentales de r205 (D20, sobre `450edfc`): todos SUCCESS con `head_sha` exacto. Cumulative [39548187237](https://github.com/c2melendez/precision-lab-plus/actions/runs/39548187237), h1d [39548189438](https://github.com/c2melendez/precision-lab-plus/actions/runs/39548189438), Native Syntax [39548191234](https://github.com/c2melendez/precision-lab-plus/actions/runs/39548191234).

Gates documentales de r206 (commit de este cierre): se disparan con `workflow_dispatch` sobre el SHA documental (D20); sus resultados se registran en r207.

Siguiente: EV-D-04 `\csc(\frac{\pi}{6}) → 2`, `READY`; se ejecuta al recibir la siguiente instrucción. Global OPEN.

---

## 2026-10-21 UTC — Trigonometría EV-D-02 PASS_SCOPED bilateral (continuity r205)

**EV-D-02** — `\\cos(\\pi/3) → 1/2` (fila oficial de `ejercicios_trigonometria.md.gz`).

Evidencia (test-first, sin cambio de producto):
- **Lite** `0601287` (`tests/trigonometryEvD02.audit.test.ts`): cumulative [39547288506](https://github.com/c2melendez/precision-lab-lite/actions/runs/39547288506), h1d [39547288469](https://github.com/c2melendez/precision-lab-lite/actions/runs/39547288469), scientific-ui [39547288515](https://github.com/c2melendez/precision-lab-lite/actions/runs/39547288515); SUCCESS.
- **Plus** `c15349a` (`backend/tests/test_trigonometry_ev_d02.py`, HTTP ASCII `cos(pi/3)`): cumulative [39547294497](https://github.com/c2melendez/precision-lab-plus/actions/runs/39547294497), h1d [39547294494](https://github.com/c2melendez/precision-lab-plus/actions/runs/39547294494); SUCCESS.

Alcance: evaluación exacta de cos(π/3)=1/2. Plus solo en ASCII, igual que EV-D-01. No cierra el módulo trig completo. Global OPEN.

Excepción de proceso D20 (r204): los commits documentales de EV-D-01 (Lite `052cfa3`, `ed44453`, `cd73fb1`; Plus `9348420`, `a8e44ee`, `35cd5b1`) no tienen runs de gates. `workflow_dispatch` solo corre sobre el head de la rama, así que ya no pueden gatearse a posteriori. Queda registrado como excepción; el commit documental de r205 sí se gatea.

Gates documentales de r205 (commit de este cierre): se disparan con `workflow_dispatch` sobre el SHA documental (D20); sus resultados se registran en r206.

Siguiente: EV-D-03 `\\tan(\\frac{\\pi}{4}) → 1`, `READY`; se ejecuta al recibir la siguiente instrucción. Global OPEN.

## 2026-10-21 UTC — Trigonometría EV-D-01 PASS_SCOPED bilateral (continuity r204)

**EV-D-01** — `\\sin(\\pi/6) → 1/2` (fila oficial de `ejercicios_trigonometria.md.gz`).

Evidencia (test-first, sin cambio de producto):
- **Lite** SHA `13bdc7c`: cumulative [39545169322](https://github.com/c2melendez/precision-lab-lite/actions/runs/39545169322), h1d [39545169419](https://github.com/c2melendez/precision-lab-lite/actions/runs/39545169419), scientific-ui [39545169496](https://github.com/c2melendez/precision-lab-lite/actions/runs/39545169496) SUCCESS.
- **Plus** SHA `4e625d1` (HTTP ASCII; LaTeX raw fuera de alcance): cumulative [39545579931](https://github.com/c2melendez/precision-lab-plus/actions/runs/39545579931), h1d [39545579919](https://github.com/c2melendez/precision-lab-plus/actions/runs/39545579919) SUCCESS.

Alcance: evaluación exacta de sen(π/6)=1/2. Global OPEN. Siguiente: EV-D-02.

---

> Nota: AS-B-28 PASS_SCOPED permanece en r203; AS-B-29 ON_HOLD. `continuity.json` r204 es la fuente de next_action.
