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
| EN-SG-01 | N1 | HTML script invalid/escape/no exec | No dedicated harness row | **GAP** |
| EN-SG-02 | N1 | HTML image event | No dedicated harness row | **GAP** |
| EN-SG-03 | N2 | Math text containing HTML → literal | `frontend/src/__tests__/MathRenderer.test.tsx`, regression added in commit `58a395306cf90bfee81c2e5ae79c58ebf3105a85`; CI execution not yet verified | **PENDING EXECUTION** |
| EN-SG-04 | N2 | Unsafe LaTeX hyperlink | No dedicated harness row | **GAP** |
| EN-SG-05 | N2 | URL/image/HTML macros blocked | No dedicated harness row | **GAP** |
| EN-SG-06 | N2 | Recursive macro definition | No dedicated harness row | **GAP** |
| EN-SG-07 | N2 | New macros/alias/catcode error | No dedicated harness row | **GAP** |
| EN-SG-08 | N2 | File/shell macros never open files | Probes exist; not matrix-row tests | **GAP** (probe-only) |
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

## EN-SG-01..08 — test-first, no product change yet

1. Locate original Part H.2 rows for exact inputs (project library matrix).
2. For 01–04: frontend/render tests if browser-first; do not claim API coverage alone.
3. For 05–08: parser rejection tests with audit hooks (`file_access_probe` / `process_launch_probe`) asserting zero open/exec attempts.
4. Do not implement until exact matrix literals are versioned beside the test.

## Execution record — 2026-10-27

- Added an EN-SG-03 frontend regression in `frontend/src/__tests__/MathRenderer.test.tsx`: a supplied HTML `img/onerror` payload must fall back to a literal text node; no `img` or `svg` node may appear.
- Test commit: `58a395306cf90bfee81c2e5ae79c58ebf3105a85`.
- Corrected `.github/workflows/ci.yml` branch filters in Plus (commit `50fd09331f46122048ff479d099bfcb12b5faec5`) and Lite (commit `0f84d5a18a7684677fb1046efd1d75dc429990f3`) to include the verified canonical branch. Previously CI push filters named `main`, `master`, and `qa/exhaustive-suite-module-01`, but omitted `qa/syntax-audit-in625-a1`.
- The available workflow-run lookup returned no runs for these SHAs and the commit-status lookup returned no statuses. The run-list connector is PR-only; this is **not evidence that push CI passed or failed**. Inspect the actual Actions page/run for each SHA before promoting EN-SG-03.
- No production service was targeted and no extreme payloads were run.

## Counts and next action

- PARTIAL (existing API/harness evidence): 15
- GAP (unimplemented or not matrix-complete): 16
- PENDING EXECUTION: 1 (EN-SG-03)
- Matrix-complete PASS: 0

Next: retrieve and inspect the CI run triggered on Plus SHA `50fd09331f46122048ff479d099bfcb12b5faec5` and Lite SHA `0f84d5a18a7684677fb1046efd1d75dc429990f3`; verify the Plus frontend job executed the new EN-SG-03 test. Then continue EN-SG-01/02/04..08 using exact source-matrix literals. Keep `next_action` = `H2-EN-SG-CASE-EVIDENCE-AUDIT-R314` until evidence is reconciled. Parallel candidate: SECURITY-S25 only with local npm.
