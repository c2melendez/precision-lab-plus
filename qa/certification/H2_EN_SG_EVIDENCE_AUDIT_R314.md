# H2 EN-SG evidence audit R314 (Plus)

**Status:** PARTIAL · **As of:** 2026-10-28 UTC · **Last certified SHA:** `29fc1295d7087a40a34b2a7b611cf73a76e96df3`
**Canonical branch:** `qa/syntax-audit-in625-a1`
**Primary matrix:** `qa/certification/IN625_H2_MATRIX.md` (inventory, not PASS results)
**Primary harness:** `backend/tests/test_in625_h2_security.py` (in-process TestClient)

## Decision rules

- Matrix row expectations win over harness approximations.
- No extreme loads, rate bursts, or dynamic execution against production services.
- A green unit/API rejection is not global certification PASS for H2.
- Browser XSS/escape and UI stop/recovery require distinct evidence (not only API).
- A test added but not executed by the relevant CI run remains pending; do not promote it to PASS.
- `PASS (scoped ...)` is row-level only: it states what the cited job actually executed. It never closes H2 or the global certification.
- Product bounds introduced to satisfy a row are certified together with regression guards for already-certified behavior on the same surface (e.g. certified factorials).

## Traceability

| ID | Level | Matrix theme | Evidence source | Classification |
|----|-------|--------------|-----------------|----------------|
| EN-SG-01 | N1 | `<script>alert(1)</script>` → escaped text, no execution | Exact-payload DOM regression in `frontend/src/__tests__/MathRenderer.test.tsx` asserts no `script/img/svg` node and exact text node; executed in Plus CI `40609140000` (backend 2,721 passed / frontend 1,053 passed, SHA `29fc1295`) | **PASS (scoped frontend DOM)** (jsdom render only; no real-browser session) |
| EN-SG-02 | N1 | `<img src=x onerror=alert(1)>` → escaped text, no execution | Same regression batch; asserts no `script/img/svg` node and exact text node; executed in Plus CI `40609140000` (backend 2,721 passed / frontend 1,053 passed, SHA `29fc1295`) | **PASS (scoped frontend DOM)** (jsdom render only; no real-browser session) |
| EN-SG-03 | N2 | `x^{2}\text{<b>hola</b>}` → literal, no bold/tags | Exact-source frontend regression passed in Plus CI `40599001729` (typecheck, Unit/parity and production build SUCCESS); original source SHA-256 `58fbc0ed04aef158148981fc28074d470e45ec07a67604f89b3847b55c625528` | **PASS** (exact frontend render behavior verified) |
| EN-SG-04 | N2 | `\href{javascript:alert(1)}{x}` | Regression asserts no anchor and no script node for the exact payload; executed in Plus CI `40609140000` (backend 2,721 passed / frontend 1,053 passed, SHA `29fc1295`) | **PASS (scoped frontend DOM)** |
| EN-SG-05 | N2 | `\url`, `\includegraphics`, `\htmlClass`, `\htmlStyle` | Four exact-payload regressions assert no anchor and no `script/img/iframe/object/embed`; executed in Plus CI `40609140000` (backend 2,721 passed / frontend 1,053 passed, SHA `29fc1295`) | **PASS (scoped frontend DOM)** |
| EN-SG-06 | N2 | `\\def\\a{\\a}\\a` | Exact-input regression added; CI `40601412886` Unit/parity SUCCESS; no dedicated timeout/recovery assertion yet | **PARTIAL** |
| EN-SG-07 | N2 | `\\newcommand`, `\\let`, `\\catcode` | Exact-input regressions added; CI `40601412886` Unit/parity SUCCESS; clear-error expectations not yet fully asserted | **PARTIAL** |
| EN-SG-08 | N2 | `\\input{/etc/passwd}`, `\\include{x}`, `\\write18{ls}`, `\\openin1=x` | Backend probe-backed test in `backend/tests/test_in625_h2_security.py`, using `file_access_probe.py` and `process_launch_probe.py`; CI `40602481512` backend tests SUCCESS (2,711 passed, 1 skipped, 10 xfailed; 88.82% coverage) | **PASS** (probe-backed backend regression passed in CI `40602481512`; frontend checks/build also passed) |
| EN-SG-09 | N3 | Python introspection/exec rejection | `test_in625_h2_rejects_python_constructs…` | **PARTIAL** (API reject) |
| EN-SG-10 | N3 | Python file read rejection | same | **PARTIAL** |
| EN-SG-11 | N3 | Python class introspection | same | **PARTIAL** |
| EN-SG-12 | N3 | Lambda rejection | same | **PARTIAL** |
| EN-SG-13 | N3 | exec/eval rejection | same (+ variants) | **PARTIAL** |
| EN-SG-14 | N3 | import os / os.system | same (+ variants) | **PARTIAL** |
| EN-SG-15 | N3 | Dunder attributes | same (+ variants) | **PARTIAL** |
| EN-SG-16 | N3 | Engine constructors | same (+ variants) | **PARTIAL** |
| EN-SG-17 | N2 | Assignment isolation across calls | `test_in625_h2_sg17_…` | **PARTIAL** |
| EN-SG-18 | N3 | Reserved words inert | multiple `sg18` tests | **PARTIAL** |
| EN-SG-19 | N2 | 50 parens → 1 | `sg19_sg20` test | **PARTIAL** |
| EN-SG-20 | N3 | 1000 parens controlled depth | 422 at `max_length=500` | **PARTIAL** (boundary, not depth guard) |
| EN-SG-21 | N3 | Sum of 10k terms <2s | `test_in625_h2_sg21_ten_thousand_terms_meet_the_request_length_contract`; a literal 10,000-term sum is 19,999 characters, so the 500-character request contract rejects it with 422 `VALIDATION_ERROR` before any timing budget applies | **GAP** (product/contract conflict recorded; not a PASS) |
| EN-SG-22 | N3 | ~100k char input | oversized expression → 422 | **PARTIAL** |
| EN-SG-23 | N3 | 10^(10^10) | `test_in625_h2_sg23_sg24_sg27_astronomical_powers_are_rejected_before_evaluation`; `10^(10^10)` and `10**(10**10)` return 200 with `success=false`, `COMPLEXITY_LIMIT`, no traceback, under a 2 s budget; executed in Plus CI `40609140000` (backend 2,721 passed / frontend 1,053 passed, SHA `29fc1295`) | **PASS (scoped backend API)** |
| EN-SG-24 | N3 | 9^(9^9) | Same parametrized test; `9^(9^9)` returns 200 with `COMPLEXITY_LIMIT` before evaluation, under a 2 s budget; executed in Plus CI `40609140000` (backend 2,721 passed / frontend 1,053 passed, SHA `29fc1295`) | **PASS (scoped backend API)** |
| EN-SG-25 | N3 | Factorial 1e6 | `test_in625_h2_sg25_huge_factorial_hits_a_clear_limit_quickly` (1000000! → `COMPLEXITY_LIMIT`, under 2 s) plus `test_in625_h2_sg25_certified_factorials_still_succeed` (100!/170!/5!/0! still exact); executed in Plus CI `40609140000` (backend 2,721 passed / frontend 1,053 passed, SHA `29fc1295`) | **PASS (scoped backend API)** |
| EN-SG-26 | N3 | (x+1)^10000 | `test_in625_h2_sg26_symbolic_power_10000_is_bounded`; returns 200 in ~13 ms with the exact unevaluated power (`\left(x + 1\right)^{10000}`), a presentation warning, no traceback, and the service answers `2+3=5` immediately afterwards; executed in Plus CI `40609140000` (backend 2,721 passed / frontend 1,053 passed, SHA `29fc1295`) | **PASS (scoped backend API)** |
| EN-SG-27 | N3 | Nested powers of 2 | Three tests: rejection above the bound (`2^(2^10000)` → `COMPLEXITY_LIMIT`), exact value below it (`2^(2^(2^2))` = `65536`), and overflow display (`2^(2^(2^(2^2)))` → `success=true`, `result_latex=null`, explicit "demasiado grande" warning, no crash); executed in Plus CI `40609140000` (backend 2,721 passed / frontend 1,053 passed, SHA `29fc1295`) | **PASS (scoped backend API)** |
| EN-SG-28 | N3 | Stop long calc + recovery | SG28 interrupt/cancel tests only | **GAP** (UI not closed) |
| EN-SG-29 | N3 | 20 concurrent + last input | backend ThreadPool test | **PARTIAL** (no frontend) |
| EN-SG-30 | N3 | JSON special characters | multiple sg30 tests | **PARTIAL** |
| EN-SG-31 | N3 | 5 MiB → 413 | `sg31` tests | **PARTIAL** |
| EN-SG-32 | N3 | Burst + conditional rate limit | Not in harness | **GAP** |

## EN-SG-01..08 — exact-input frontend regression batch

1. Original Part H.2 source recovered from `Matrices.zip`: `matriz_entrada_sintaxis_calculadora.md`, SHA-256 `58fbc0ed04aef158148981fc28074d470e45ec07a67604f89b3847b55c625528`, rows EN-SG-01..32 at source lines 864–901.
2. EN-SG-03 exact-source regression passed in Plus CI `40599001729` (typecheck, Unit/parity and production build all SUCCESS).
3. For 01–04: frontend/render tests if browser-first; do not claim API coverage alone.
4. For 05–08: parser rejection tests with audit hooks (`file_access_probe` / `process_launch_probe`) asserting zero open/exec attempts.
5. Frontend test batch commit `9d13cd39227839099c1809ddd2c4eeed32ee4842` passed Typecheck, Unit/parity and production build in CI `40601412886`; backend job was still running. Follow-up commit `2db9e7b1d15c49b22299d4007cfda01959c67efc` strengthens EN-SG-04/05 by asserting no anchors at all. That evidence is now certified: CI `40609140000` executed `MathRenderer.test.tsx` (20 tests) with 150 files / 1,053 tests passing, so EN-SG-01/02/04/05 are `PASS (scoped frontend DOM)`. EN-SG-06/07 stay PARTIAL: the batch only proves no active HTML is produced, not recursion timeout or a clear error message. EN-SG-08 PASS still rests on the file/process probes, not on the render batch.

## Execution record — 2026-10-28 (r332)

Commit `29fc1295d7087a40a34b2a7b611cf73a76e96df3` (`fix(h2): bound EN-SG-25/26 resource cases and add N3 regression tranche`) on the canonical branch, certified by Plus CI [40609140000](https://github.com/c2melendez/precision-lab-plus/actions/runs/40609140000) (backend + frontend SUCCESS; backend 2,721 passed, 1 skipped, 10 xfailed, 88.78% coverage; frontend 150 files / 1,053 passed, 28 todo) and cumulative gate [40609140346](https://github.com/c2melendez/precision-lab-plus/actions/runs/40609140346) SUCCESS.

Observed behavior before the change (local probes at the parent SHA, in-process TestClient, no production target):

| Input | Before | After |
|---|---|---|
| `10^(10^10)`, `9^(9^9)`, `2^(2^10000)` | `COMPLEXITY_LIMIT` | `COMPLEXITY_LIMIT` (now asserted in CI) |
| `1000000!` | 7.96 s, then `DOMAIN_ERROR` | `COMPLEXITY_LIMIT` with an explicit factorial message in <2 s |
| `1000!` | slow path | `COMPLEXITY_LIMIT` (literal exceeds the 64-digit rule) |
| `(x+1)^10000` | hung >60 s in presentation | 13 ms, exact unevaluated power + presentation warning |
| `(x+1)^201` | full `sympy.simplify()` | exact unevaluated power + same warning (guard threshold 200) |
| `2^(2^(2^2))` | `65536` | `65536` |
| `2^(2^(2^(2^2)))` | result too large warning | unchanged: `success=true`, `result_latex=null`, explicit warning |

Product changes (test-first, minimal, no DDL, no permission change):

1. `backend/app/services/ast_validator.py` — factorial argument limit `1000` and a bit-length-based digit estimate so huge factorials are rejected before evaluation.
2. `backend/app/services/parsing.py` — text-level factorial pre-check in `_parse_side` so the rejection happens at parse time, with the same user-facing code.
3. `backend/app/routers/evaluate.py` — `_MAX_SIMPLIFY_POWER_EXPONENT = 200`: symbolic integer powers above that magnitude skip `sympy.simplify()` in presentation and emit `Presentación sin simplificar: potencia simbólica de exponente elevado.`

Regression tranche (10 tests appended to `backend/tests/test_in625_h2_security.py`): EN-SG-23/24/27 pre-evaluation rejection with a 2 s budget, EN-SG-27 exactness at `65536`, EN-SG-27 overflow-display omission with warning, EN-SG-25 clear limit, EN-SG-25 certified factorials (`100!`, `170!`, `5!`, `0!`, `171!` through the finite-aggregate path), EN-SG-26 bounded symbolic power plus recovery (`2+3=5`), and EN-SG-21 recorded as a 422 `VALIDATION_ERROR` contract boundary.

The 10 new tests pass locally in 1.71 s, and CI backend reported exactly +10 tests over the previous run `40602481512` (2,711 → 2,721 passed).

Frontend evidence for EN-SG-01/02/04/05 is the `MathRenderer.test.tsx` batch (20 tests) inside the same frontend job; it asserts the exact payload is rendered as a text node with no `script/img/svg` and, for `\href`, no anchor at all. This is jsdom DOM evidence, not a real-browser session.

Scope limits: no production service was targeted; no real-browser E2E; EN-SG-21/28/32 remain open; the security/backend-security job of [40609140075](https://github.com/c2melendez/precision-lab-plus/actions/runs/40609140075) passed (pip-audit + Bandit + CORS/security regressions) but SECURITY-S25 stays BLOCKED because its exit condition requires explicit bilateral acceptance and Lite's npm audit gate is still red.

## Execution record — 2026-10-27 (r314)

- Added an EN-SG-03 frontend regression in `frontend/src/__tests__/MathRenderer.test.tsx`: a supplied HTML `img/onerror` payload must fall back to a literal text node; no `img` or `svg` node may appear.
- Test commit: `58a395306cf90bfee81c2e5ae79c58ebf3105a85`.
- Corrected `.github/workflows/ci.yml` branch filters in Plus (commit `50fd09331f46122048ff479d099bfcb12b5faec5`) and Lite (commit `0f84d5a18a7684677fb1046efd1d75dc429990f3`) to include the verified canonical branch. Previously CI push filters named `main`, `master`, and `qa/exhaustive-suite-module-01`, but omitted `qa/syntax-audit-in625-a1`.
- Observed Actions run 40596662550 for Plus SHA `50fd09331f46122048ff479d099bfcb12b5faec5`: frontend `Unit and parity tests` failed because EN-SG-03 expected the payload exactly but KaTeX returned normalized/duplicated text; 149 test files passed, 1 failed; 1036 tests passed, 1 failed, 28 todo. This exposes a product-side gap: markup-like input did not force the plain-text fallback. Corrective renderer guard committed as `21eccd6ff4612afc73b78bfac816052de360c9ee`; awaiting its CI run. Lite run 40596658330 passed its frontend job (not evidence for Plus EN-SG-03).
- No production service was targeted and no extreme payloads were run.

## Counts and next action

- PASS (scoped): 11 — EN-SG-01, 02, 03, 04, 05, 08, 23, 24, 25, 26, 27. Each one is bounded to the cited job and the tested surface.
- PARTIAL: 18 — EN-SG-06, 07, 09..20, 22, 29, 30, 31.
- GAP: 3 — EN-SG-21 (request contract conflict), EN-SG-28 (UI stop/recovery), EN-SG-32 (no rate limiter exists).
- PENDING EXECUTION: none.

Next: continue with EN-SG-06/07 (recursion timeout and clear-error assertions) and EN-SG-09..20 deeper side-effect probes, then EN-SG-31/32 boundary work. EN-SG-28 needs frontend stop/recovery evidence and EN-SG-21 needs a contract decision on the 500-character request limit; neither may be forced green. Keep `next_action` = `H2-EN-SG-CASE-EVIDENCE-AUDIT-R314`. SECURITY-S25 remains BLOCKED (bilateral, Lite npm audit red); global certification remains OPEN. No production stress tests.
