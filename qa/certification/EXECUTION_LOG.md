# Registro de ejecución — índice vigente

## 2026-10-20 UTC — Reconciliación cerrada (AS-A-01..05 + ledger AS-A-06)

Evidencia tabular: [EXECUTION_LOG_AS229_SECTION_A.md](./EXECUTION_LOG_AS229_SECTION_A.md).

| Caso | Lite cumulative | Plus cumulative |
|------|-----------------|-----------------|
| AS-A-01 | [39392408916](https://github.com/c2melendez/precision-lab-lite/actions/runs/39392408916) | [39392421243](https://github.com/c2melendez/precision-lab-plus/actions/runs/39392421243) |
| AS-A-02 | [39392889929](https://github.com/c2melendez/precision-lab-lite/actions/runs/39392889929) | [39392902252](https://github.com/c2melendez/precision-lab-plus/actions/runs/39392902252) |
| AS-A-03 | [39395561487](https://github.com/c2melendez/precision-lab-lite/actions/runs/39395561487) | [39395572574](https://github.com/c2melendez/precision-lab-plus/actions/runs/39395572574) |
| AS-A-04 | [39396680764](https://github.com/c2melendez/precision-lab-lite/actions/runs/39396680764) | [39396699584](https://github.com/c2melendez/precision-lab-plus/actions/runs/39396699584) |
| AS-A-05 | [39397703380](https://github.com/c2melendez/precision-lab-lite/actions/runs/39397703380) | [39397716265](https://github.com/c2melendez/precision-lab-plus/actions/runs/39397716265) |

**Ledger:** `continuity.json` r153 `next_action` = **AS-A-06**.

**CI post-reconcile:** cumulative [39402444356](https://github.com/c2melendez/precision-lab-plus/actions/runs/39402444356) SUCCESS; H1d [39402444394](https://github.com/c2melendez/precision-lab-plus/actions/runs/39402444394) SUCCESS.

Global **OPEN**. **Siguiente:** AS-A-06 expand `(x+y+z)^2`.

---

## 2026-10-20 UTC — AS-A-10 PASS_SCOPED bilateral (continuity r158)

Commit técnico Lite `373702e` / Plus `a82daab` (test-first fila AS-A-10 `(x^2+x+1)^3`). Runs Cumulative Lite 39410230278, H1d 39410230284; Plus 39410227638, H1d 39410227610 — todos SUCCESS sobre el SHA exacto. Evidencia ampliada en `EXECUTION_LOG_AS229_SECTION_A.md`. Siguiente único: ALGEBRA229-AS-A-11-TEST-FIRST `(a+b+c)^3`.

---

## 2026-10-20 UTC — AS-A-12 PASS_SCOPED bilateral (continuity r160)

Commit técnico Lite `aacb5c3` (test-first AS-A-12 `(x^2-1)^2`, vitest 2 passed) / Plus `663c9f8` (pytest AS-A-12 HTTP 2 passed). Runs sobre el SHA exacto — Lite: cumulative 39414422310, scientific-ui 39414422330, h1d 39414422305; Plus: cumulative 39414425350, h1d 39414425369. Todos SUCCESS (push). Global OPEN. Siguiente: AS-A-13.

---

## 2026-10-20 UTC — AS-A-13 PASS_SCOPED bilateral (continuity r161)

Commit técnico Lite `3120dc5` (test-first AS-A-13 `(x+h)^3-x^3`, vitest 2 passed) / Plus `e27d0d0` (pytest AS-A-13 HTTP 2 passed). Runs sobre el SHA exacto — Lite: cumulative 39416212022, scientific-ui 39416211907, h1d 39416211887; Plus: cumulative 39416218253, h1d 39416218107. Todos SUCCESS (push). Global OPEN. Siguiente: AS-A-13.

---

## 2026-10-20 UTC — AS-A-14 PASS_SCOPED bilateral (continuity r162)

Commit técnico Lite `655ab02` (test-first AS-A-14, vitest 2 passed) / Plus `45435c0` (pytest AS-A-14 HTTP 2 passed). Runs sobre el SHA exacto — Lite: cumulative 39418368131, scientific-ui 39418368033, h1d 39418368058; Plus: cumulative 39418372218, h1d 39418372114. Todos SUCCESS (push). Global OPEN. Siguiente: AS-A-15.

---

## 2026-10-20 UTC — AS-A-15 PASS_SCOPED bilateral (continuity r163)

Commit técnico Lite `7be68cb` (test-first AS-A-15 `(x+1/x)^3`) / Plus `dbf6cf6` (pytest AS-A-15 HTTP). Runs sobre el SHA exacto — Lite: cumulative 39419446051, scientific-ui 39419445961, h1d 39419445944; Plus: cumulative 39419450009, h1d 39419449888. Todos SUCCESS (push). Global OPEN. Siguiente: AS-A-16.

---

## 2026-10-20 UTC — AS-A-16 PASS_SCOPED bilateral (continuity r164)

Commit técnico Lite `a08db76` (test-first AS-A-16 `(1+i)^4`) / Plus `c26e2cf` (pytest AS-A-16 HTTP). Runs sobre el SHA exacto — Lite: cumulative 39420901531, scientific-ui 39420901831, h1d 39420901417; Plus: cumulative 39420913944, h1d 39420913777. Todos SUCCESS (push). Global OPEN. Siguiente: AS-A-17.

---

## 2026-10-20 UTC — AS-A-17 PASS_SCOPED bilateral; sección A completa (continuity r165)

Commit técnico Lite `72bf8e0` (test-first AS-A-17 `(2x-y)^5`) / Plus `795afd0` (pytest AS-A-17 HTTP). Runs sobre el SHA exacto — Lite: cumulative 39422323741, scientific-ui 39422323909, h1d 39422323671; Plus: cumulative 39422333606, h1d 39422333812. Todos SUCCESS (push). Sección A completa (AS-A-01..17). Global OPEN. Siguiente: AS-B-01 (factorizar).

---

## 2026-10-20 UTC — AS-B-01 PASS_SCOPED bilateral (continuity r166)

Commit técnico Lite `aaf9e7d` (test-first AS-B-01 `factor x^2-5x+6`) / Plus `186699a` (pytest AS-B-01 HTTP). Runs sobre el SHA exacto — Lite: cumulative 39423612063, scientific-ui 39423612133, h1d 39423612136; Plus: cumulative 39423621287, h1d 39423621325. Todos SUCCESS (push). Global OPEN. Siguiente: AS-B-02.

---

## 2026-10-20 UTC — AS-B-02 PASS_SCOPED bilateral (continuity r167)

Commit técnico Lite `20f228e` (test-first AS-B-02 `factor x^2-9`) / Plus `300d73f` (pytest AS-B-02 HTTP). Runs sobre el SHA exacto — Lite: cumulative 39424822522, scientific-ui 39424822635, h1d 39424822528; Plus: cumulative 39424832850, h1d 39424833210. Todos SUCCESS (push). Global OPEN. Siguiente: AS-B-03.

---

## 2026-10-20 UTC — AS-B-03 PASS_SCOPED bilateral (continuity r168)

Commit técnico Lite `5be7b01` (test-first AS-B-03 `factor x^3-8`) / Plus `ab3ead0` (pytest AS-B-03 HTTP). Runs sobre el SHA exacto — Lite: cumulative 39425818360, scientific-ui 39425818757, h1d 39425818572; Plus: cumulative 39425828486, h1d 39425828468. Todos SUCCESS (push). Global OPEN. Siguiente: AS-B-04.

---

## 2026-10-20 UTC — AS-B-04 PASS_SCOPED bilateral (continuity r169)

Commit técnico Lite `56ec7ea` (test-first AS-B-04 `factor x^3+27`) / Plus `82cc071` (pytest AS-B-04 HTTP). Runs sobre el SHA exacto — Lite: cumulative 39426977672, scientific-ui 39426977392, h1d 39426977717; Plus: cumulative 39426990236, h1d 39426990101. Todos SUCCESS (push). Global OPEN. Siguiente: AS-B-05.

---

## 2026-10-20 UTC — AS-B-05 PASS_SCOPED bilateral (continuity r170)

Commit técnico Lite `72b00bd` (test-first AS-B-05 `factor x^4-1`) / Plus `21672c6` (pytest AS-B-05 HTTP). Runs sobre el SHA exacto — Lite: cumulative 39428243384, scientific-ui 39428243353, h1d 39428243346; Plus: cumulative 39428253897, h1d 39428253880. Todos SUCCESS (push). Global OPEN. Siguiente: AS-B-06.

---

## 2026-10-20 UTC — AS-B-06 PASS_SCOPED bilateral (continuity r171)

Commit técnico Lite `8339acf` (test-first AS-B-06 `factor x^4+4`) / Plus `63dec80` (pytest AS-B-06 HTTP + corrección de temporización SG28 tras fallo de `2cf4209`, ver CURRENT_STATE). Runs sobre el SHA exacto — Lite: cumulative 39429477924, scientific-ui 39429477795, h1d 39429477800; Plus: cumulative 39431271219, SG28 backend isolation 39431271237, h1d 39431271249. Runs rojos previos en Plus: 39429492475 (cumulative, SG28 timing) y 39430648591/39430648632 (cumulative/SG28, `ValueError` del tope de 10 s en `f9d4fce`); Todos los SUCCESS citados son push. Global OPEN. Siguiente: AS-B-07.

---

## 2026-10-20 UTC — AS-B-07: Plus PASS, Lite FAIL_PRODUCT (continuity r172)

Commit técnico Lite `6bafda3` (test-first AS-B-07 `factor x^6-1`) / Plus `da361ae` (pytest AS-B-07 HTTP). Lite: cumulative 39433167930 **failure** (producto: Algebrite `factor(x^6-1)` incorrecto), scientific-ui 39433167821 success, h1d 39433168379 success. Plus: cumulative 39433181526 success, h1d 39433181543 success. Global OPEN. Siguiente: decisión sobre corrección de factorización verificada en Lite (ALGEBRA229-AS-B-07-LITE-FACTOR).

---

## 2026-10-20 UTC — AS-B-07 PASS_SCOPED bilateral (continuity r173)

Lite: test-first `6bafda3` (acumulativo 39433167930 **failure**: Algebrite `factor(x^6-1)` incorrecto), corrección `89b7055` (factor verificado + respaldo univariado; cumulative 39434995883, scientific-ui 39434995961, h1d 39434995969 SUCCESS). Plus: test-first `da361ae` (cumulative 39433181526, h1d 39433181543 SUCCESS). AS-LIM-05 pasa de GAP (`it.fails`) a `it`. Global OPEN. Siguiente: AS-B-08.

---

## 2026-10-20 UTC — AS-B-08 PASS_SCOPED bilateral (continuity r174)

Commit técnico Plus `92836fb` (test-first AS-B-08 `factor x^4-5x^2+4`, sin cambios de producto). Runs sobre el SHA exacto: cumulative [39443976046](https://github.com/c2melendez/precision-lab-plus/actions/runs/39443976046), h1d [39443975882](https://github.com/c2melendez/precision-lab-plus/actions/runs/39443975882). Todos SUCCESS (push). Global OPEN. Siguiente: AS-B-09.

---

## 2026-10-20 UTC — AS-B-09 PASS_SCOPED bilateral (continuity r175)

Commit técnico Plus `df59c1e` (test-first AS-B-09 `factor 6x^2+5x-4`, sin cambios de producto). Runs sobre el SHA exacto: cumulative [39448192396](https://github.com/c2melendez/precision-lab-plus/actions/runs/39448192396), h1d [39448192451](https://github.com/c2melendez/precision-lab-plus/actions/runs/39448192451). Todos SUCCESS (push). Global OPEN. Siguiente: AS-B-10.

---

## 2026-10-20 UTC — AS-B-10 PASS_SCOPED bilateral (continuity r176)

Commit técnico Plus `f6edeca` (test-first AS-B-10 `factor x^3+3x^2+3x+1`, sin cambios de producto). Runs sobre el SHA exacto: cumulative [39449552737](https://github.com/c2melendez/precision-lab-plus/actions/runs/39449552737), h1d [39449552940](https://github.com/c2melendez/precision-lab-plus/actions/runs/39449552940). Todos SUCCESS (push). Global OPEN. Siguiente: AS-B-11.

---

## 2026-10-20 UTC — AS-B-11 PASS_SCOPED bilateral (continuity r177)

Commit técnico Plus `cdc2bf7` (test-first AS-B-11 `factor ax+ay+bx+by`, sin cambios de producto). Runs sobre el SHA exacto: cumulative [39450890699](https://github.com/c2melendez/precision-lab-plus/actions/runs/39450890699), h1d [39450890712](https://github.com/c2melendez/precision-lab-plus/actions/runs/39450890712). Todos SUCCESS (push). Global OPEN. Siguiente: AS-B-12.

---

## 2026-10-20 UTC — AS-B-12 PASS_SCOPED bilateral (continuity r178)

Commit técnico Plus `ccbcdb5` (test-first AS-B-12 `factor x^5-x`, sin cambios de producto). Runs sobre el SHA exacto: cumulative [39452217842](https://github.com/c2melendez/precision-lab-plus/actions/runs/39452217842), h1d [39452217825](https://github.com/c2melendez/precision-lab-plus/actions/runs/39452217825). Todos SUCCESS (push). Global OPEN. Siguiente: AS-B-13.

---

## 2026-10-20 UTC — AS-B-13 PASS_SCOPED bilateral (continuity r179)

Commit técnico Plus `7ea3435` (test-first AS-B-13 `factor 2x^3-x^2-13x-6`, sin cambios de producto). Runs sobre el SHA exacto: cumulative [39453858654](https://github.com/c2melendez/precision-lab-plus/actions/runs/39453858654), h1d [39453858516](https://github.com/c2melendez/precision-lab-plus/actions/runs/39453858516). Todos SUCCESS (push). Global OPEN. Siguiente: AS-B-14.

---

## 2026-10-20 UTC — AS-B-14 PASS_SCOPED bilateral (continuity r180)

Commit técnico Plus `ac65cc0` (test-first AS-B-14 `factor x^4+x^2+1`, sin cambios de producto). Runs sobre el SHA exacto: cumulative [39455234361](https://github.com/c2melendez/precision-lab-plus/actions/runs/39455234361), h1d [39455234162](https://github.com/c2melendez/precision-lab-plus/actions/runs/39455234162). Todos SUCCESS (push). Global OPEN. Siguiente: AS-B-15.

---

## 2026-10-20 UTC — AS-B-15 PASS_SCOPED bilateral (continuity r181)

Commit técnico Plus `6114033` (test-first AS-B-15 `factor x^3-x^2-x+1`, sin cambios de producto). Runs sobre el SHA exacto: cumulative [39456665429](https://github.com/c2melendez/precision-lab-plus/actions/runs/39456665429), h1d [39456665415](https://github.com/c2melendez/precision-lab-plus/actions/runs/39456665415). Todos SUCCESS (push). Global OPEN. Siguiente: AS-B-16.

---

## 2026-10-20 UTC — AS-B-16 PASS_SCOPED bilateral (continuity r182)

Commit técnico Plus `f1df620` (test-first AS-B-16 `factor a^3-b^3`). Runs sobre el SHA exacto: cumulative [39457909892](https://github.com/c2melendez/precision-lab-plus/actions/runs/39457909892), h1d [39457909660](https://github.com/c2melendez/precision-lab-plus/actions/runs/39457909660). Todos SUCCESS (push). Global OPEN. Siguiente: AS-B-17.

---

## 2026-10-20 UTC — AS-B-17 PASS_SCOPED bilateral (continuity r183)

Commit técnico Plus `b1f3c81` (test-first AS-B-17 `factor a^3+b^3`, sin cambios de producto). Runs sobre el SHA exacto: cumulative [39461135107](https://github.com/c2melendez/precision-lab-plus/actions/runs/39461135107), h1d [39461135362](https://github.com/c2melendez/precision-lab-plus/actions/runs/39461135362). Todos SUCCESS (push). Decisión de alcance: B-24 y B-25 incluidas con sufijo «sobre ℝ» / «sobre ℂ»; implementación en orden de matriz. Global OPEN. Siguiente: AS-B-18.

---

## 2026-10-20 UTC — AS-B-18 PASS_SCOPED bilateral (continuity r184)

Commit técnico Plus `7930c0e` (test-first AS-B-18 `factor x^8-1`, sin cambios de producto). Runs sobre el SHA exacto: cumulative [39462384451](https://github.com/c2melendez/precision-lab-plus/actions/runs/39462384451), h1d [39462384532](https://github.com/c2melendez/precision-lab-plus/actions/runs/39462384532). Todos SUCCESS (push). Global OPEN. Siguiente: AS-B-19.

---

## 2026-10-20 UTC — AS-B-19 PASS_SCOPED bilateral (continuity r185)

Commit técnico Plus `8090324` (test-first AS-B-19 `factor x^2y-xy^2`, sin cambios de producto). Runs sobre el SHA exacto: cumulative [39471803861](https://github.com/c2melendez/precision-lab-plus/actions/runs/39471803861), h1d [39471803916](https://github.com/c2melendez/precision-lab-plus/actions/runs/39471803916). Todos SUCCESS (push). Global OPEN. Siguiente: AS-B-20.

---

## 2026-10-20 UTC — AS-B-20 BLOQUEADO en Lite (continuity r186)

Test-first Lite `a9cb5a9` falló cumulative 39475280948 (Algebrite sin factorizar). Test-first Plus `f8ec173` pasó (cumulative 39475284739, h1d 39475284787). Revert Lite retira la prueba roja para mantener el branch verde. Decisión pendiente: regla acotada CAS vs camino multivariable general. Global OPEN.

---

## 2026-10-20 UTC — AS-B-20 PASS_SCOPED bilateral (continuity r187)

Commit técnico Plus `f8ec173` (test-first AS-B-20, sin cambios de producto). Runs sobre el SHA exacto: cumulative [39475284739](https://github.com/c2melendez/precision-lab-plus/actions/runs/39475284739), h1d [39475284787](https://github.com/c2melendez/precision-lab-plus/actions/runs/39475284787). Todos SUCCESS (push). Global OPEN. Siguiente: AS-B-21.

---

## 2026-10-20 UTC — AS-B-21 PASS sin cambio de producto (continuity r188)

- Plus `f55e470a72b2d503981a4e583ac97838990e531c`: test-first `backend/tests/test_algebra229_as_b21.py` pasa en cumulative 39479963827 y h1d 39479963755 (SUCCESS).
- Sin cambio de producto. Commit de decisión D16 y alcance: `59d49dd`.

## 2026-10-20 UTC — AS-B-22 PASS sin cambio de producto (continuity r197)

**ALGEBRA229-AS-B-22** — factorizar `x^{2}+1` → `x^{2} + 1` (fila N1; irreducible sobre ℚ y ℝ, debe quedar igual).

| Repo | Technical SHA | Gates (SUCCESS sobre el SHA exacto) |
|------|---------------|--------------------------------------|
| Plus | `1884ece` | cumulative [39514144381](https://github.com/c2melendez/precision-lab-plus/actions/runs/39514144381), h1d [39514147092](https://github.com/c2melendez/precision-lab-plus/actions/runs/39514147092) |

Test-first sin cambios de producto. Evidencia: `backend/tests/test_algebra229_as_b22.py`. El test exige fila N1 en la matriz, resultado equivalente a `x^2+1`, sin producto, y tipo `sp.Add` por HTTP. Lite (`67d8fd4`) tiene la misma comprobación en `tests/algebra229AsB22.audit.test.ts` con gates success.

Numeración: Plus estaba en r188 y se alinea con la numeración compartida de Lite (r197); los registros r189–r196 son de Lite.

Estado: AS-B-23 (`x^2-2`) queda en `ON_HOLD`, pendiente de instrucción. Global OPEN.

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

## 2026-10-21 UTC — AS-B-24 PASS_SCOPED bilateral (continuity r199)

**ALGEBRA229-AS-B-24** — factorizar `x^{2}-2` sobre ℝ → `(x-sqrt(2))*(x+sqrt(2))`. Test-first `863cc25` (roja esperada: cumulative [39525223366](https://github.com/c2melendez/precision-lab-plus/actions/runs/39525223366)); producto `a88b201` + `0280d5f` (D21). Gates SUCCESS sobre `0280d5f`: cumulative [39527640340](https://github.com/c2melendez/precision-lab-plus/actions/runs/39527640340), h1d [39527640292](https://github.com/c2melendez/precision-lab-plus/actions/runs/39527640292), Native Syntax [39527640271](https://github.com/c2melendez/precision-lab-plus/actions/runs/39527640271). Lite `efa7ada`: cumulative [39527634222](https://github.com/c2melendez/precision-lab-lite/actions/runs/39527634222), h1d [39527634276](https://github.com/c2melendez/precision-lab-lite/actions/runs/39527634276), scientific-ui [39527634249](https://github.com/c2melendez/precision-lab-lite/actions/runs/39527634249). Registro D20 de r198: Plus `b61786d` y Lite `2b9c2e8`, SUCCESS. Estado: AS-B-25 `ON_HOLD`. Global OPEN.

---

## Histórico AS-PAR / Syntax

Blob previo Plus `c0f7925d01cce81f69e64c3dcb56f69982854076` / commit `4e0974d1…`.

---

## 2026-10-20 UTC — AS-A-11 PASS_SCOPED bilateral + triage preexistentes PLUS (continuity r159)

Commit técnico Lite `4fab5b1` (test-first AS-A-11 `(a+b+c)^3`, vitest 2 passed) / Plus `82059fa` (pytest AS-A-11 HTTP 2 passed + fixes de triage: fallback 422 starlette-pin en exception_handlers, import pathlib en sg28 multi-process, CORS_ORIGINS pinned en s25). Runs sobre el SHA exacto — Lite: cumulative 39412487217, scientific-ui 39412487075, h1d 39412487020; Plus: backend 39412482980, h1d 39412482960, security/mutation 39412483056 (mutmut success), syntax-native/host_identity success. Los fallos preexistentes S17/S25/SG28 quedan cerrados con evidencia verde. AS-A-01…11 PASS_SCOPED. Global OPEN. Siguiente único: ALGEBRA229-AS-A-12-TEST-FIRST (matriz congelada Section A).
