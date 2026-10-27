# H2 EN-SG evidence audit R314 (Plus)

**Status:** PARTIAL · **As of:** 2026-10-27 UTC
**Canonical branch:** `qa/syntax-audit-in625-a1`
**Primary matrix:** `qa/certification/IN625_H2_MATRIX.md` (inventory, not PASS results)
**Primary harness:** `backend/tests/test_in625_h2_security.py` (in-process TestClient)

## Decision rules

- Matrix row expectations win over harness approximations.
- No extreme loads, rate bursts, or dynamic execution against production services.
- A green unit/API rejection is not global certification PASS for H2.
- Browser XSS/escape and UI stop/recovery require distinct evidence (not only API).
- A test added but not executed by the relevant CI run remains pending; do not promote it to PASS.

## Traceability

| ID | Level | Matrix theme | Evidence source | Classification |
|----|-------|--------------|-----------------|----------------|
| EN-SG-01 | N1 | `<script>alert(1)</script>` → escaped text, no execution | Exact-input frontend regression added in `frontend/src/__tests__/MathRenderer.test.tsx`; Unit/parity passed in CI `40601412886` on `9d13cd39227839099c1809ddd2c4eeed32ee4842`; backend job still running | **PARTIAL** (frontend evidence; full CI pending) |
| EN-SG-02 | N1 | `<img src=x onerror=alert(1)>` → escaped text, no execution | Exact-input frontend regression added in `frontend/src/__tests__/MathRenderer.test.tsx`; Unit/parity passed in CI `40601412886` on `9d13cd39227839099c1809ddd2c4eeed32ee4842`; backend job still running | **PARTIAL** (frontend evidence; full CI pending) |
| EN-SG-03 | N2 | `x^{2}\text{<b>hola</b>}` → literal, no bold/tags | Exact-source frontend regression passed in Plus CI `40599001729` (typecheck, Unit/parity and production build SUCCESS); original source SHA-256 `58fbc0ed04aef158148981fc28074d470e45ec07a67604f89b3847b55c625528` | **PASS** (exact frontend render behavior verified) |
| EN-SG-04 | N2 | `\href{javascript:alert(1)}{x}` | Exact-input regression asserts no anchor; follow-up no-anchor assertion in commit `2db9e7b1d15c49b22299d4007cfda01959c67efc`; CI `40601719487` pending | **PARTIAL** (frontend only, latest assertion pending CI) |
| EN-SG-05 | N2 | `\url`, `\includegraphics`, `\htmlClass`, `\htmlStyle` | Exact-input regressions assert no anchor or active HTML; follow-up commit `2db9e7b1d15c49b22299d4007cfda01959c67efc`; CI `40601719487` pending | **PARTIAL** (frontend only; no file/process probe) |
| EN-SG-06 | N2 | `\\def\\a{\\a}\\a` | Exact-input regression added; CI `40601412886` Unit/parity SUCCESS; no dedicated timeout/recovery assertion yet | **PARTIAL** |
| EN-SG-07 | N2 | `\\newcommand`, `\\let`, `\\catcode` | Exact-input regressions added; CI `40601412886` Unit/parity SUCCESS; clear-error expectations not yet fully asserted | **PARTIAL** |
| EN-SG-08 | N2 | `\\input`, `\\include`, `\\write18`, `\\openin` | Exact-input frontend regressions added; CI `40601412886` Unit/parity SUCCESS; file-access/process probes are not connected to these matrix rows | **GAP** (no file/exec probe evidence) |
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
| EN-SG-21 | N3 | Sum of 10k terms <2s | Not in harness | **GAP** (no extreme load in prod) |
| EN-SG-22 | N3 | ~100k char input | oversized expression → 422 | **PARTIAL** |
| EN-SG-23 | N3 | 10^(10^10) | Not in harness | **GAP** |
| EN-SG-24 | N3 | 9^(9^9) | Not in harness | **GAP** |
| EN-SG-25 | N3 | Factorial 1e6 | Not in harness | **GAP** |
| EN-SG-26 | N3 | (x+1)^10000 | Not in harness | **GAP** |
| EN-SG-27 | N3 | Nested powers of 2 | Not in harness | **GAP** |
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
5. Frontend test batch commit `9d13cd39227839099c1809ddd2c4eeed32ee4842` passed Typecheck, Unit/parity and production build in CI `40601412886`; backend job was still running. Follow-up commit `2db9e7b1d15c49b22299d4007cfda01959c67efc` strengthens EN-SG-04/05 by asserting no anchors at all; its CI must be inspected before promoting those cases. Do not claim EN-SG-08 PASS without file/process probes.

## Execution record — 2026-10-27

- Added an EN-SG-03 frontend regression in `frontend/src/__tests__/MathRenderer.test.tsx`: a supplied HTML `img/onerror` payload must fall back to a literal text node; no `img` or `svg` node may appear.
- Test commit: `58a395306cf90bfee81c2e5ae79c58ebf3105a85`.
- Corrected `.github/workflows/ci.yml` branch filters in Plus (commit `50fd09331f46122048ff479d099bfcb12b5faec5`) and Lite (commit `0f84d5a18a7684677fb1046efd1d75dc429990f3`) to include the verified canonical branch. Previously CI push filters named `main`, `master`, and `qa/exhaustive-suite-module-01`, but omitted `qa/syntax-audit-in625-a1`.
- Observed Actions run 40596662550 for Plus SHA `50fd09331f46122048ff479d099bfcb12b5faec5`: frontend `Unit and parity tests` failed because EN-SG-03 expected the payload exactly but KaTeX returned normalized/duplicated text; 149 test files passed, 1 failed; 1036 tests passed, 1 failed, 28 todo. This exposes a product-side gap: markup-like input did not force the plain-text fallback. Corrective renderer guard committed as `21eccd6ff4612afc73b78bfac816052de360c9ee`; awaiting its CI run. Lite run 40596658330 passed its frontend job (not evidence for Plus EN-SG-03).
- No production service was targeted and no extreme payloads were run.

## Counts and next action

- PARTIAL: 22 (including frontend-only evidence for EN-SG-01/02/04..07)
- GAP: 9 (including EN-SG-08 and cases without sufficient matrix evidence)
- PENDING EXECUTION: 1 (new Plus CI for commit `2db9e7b1d15c49b22299d4007cfda01959c67efc` queued/in progress)
- Matrix-complete PASS: 1 (EN-SG-03 exact frontend behavior)

Next: inspect CI for `2db9e7b1d15c49b22299d4007cfda01959c67efc`; add file-access/process-launch probes for EN-SG-08; only then address Runner orchestration mismatches. Exact-source EN-SG-03 is PASS for frontend render behavior; global certification remains OPEN. Keep `next_action` = `H2-EN-SG-CASE-EVIDENCE-AUDIT-R314`. Security job in dependency/security workflow `40597214739` was SKIPPED, not PASS; SECURITY-S25 remains BLOCKED. No production stress tests.
