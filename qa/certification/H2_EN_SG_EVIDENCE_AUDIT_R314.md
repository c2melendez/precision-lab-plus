# H2 EN-SG evidence audit R314 (Plus)

**Status:** COMPLETE (scoped) · **As of:** 2026-10-29 UTC · **Last certified SHA (EN-SG-32):** `1959b2b7d3ffc839153500431a6d09a3fbd17bab` · **Last certified SHA (EN-SG-06/07):** `bd1742bd217d4b265d33f6d108098f04b5a789f9` · **Prior N3 tranche SHA:** `29fc1295d7087a40a34b2a7b611cf73a76e96df3`
**Canonical branch:** `qa/syntax-audit-in625-a1`
**Primary matrix:** `qa/certification/IN625_H2_MATRIX.md` (inventory, not PASS results)
**Primary harness:** `backend/tests/test_in625_h2_security.py` (in-process TestClient) + `frontend/src/__tests__/MathRenderer.test.tsx`

## Decision rules

- Matrix row expectations win over harness approximations.
- No extreme loads, rate bursts, or dynamic execution against production services.
- A green unit/API rejection is not global certification PASS for H2.
- Browser XSS/escape and UI stop/recovery require distinct evidence (not only API).
- A test added but not executed by the relevant CI run remains pending; do not promote it to PASS.
- `PASS (scoped ...)` is row-level only: it states what the cited job actually executed. It never closes H2 or the global certification.
- Product bounds introduced to satisfy a row are certified together with regression guards for already-certified behavior on the same surface (e.g. certified factorials).
- Explicit OUT_OF_SCOPE is preferred over leaving a GAP when the row requires multi-tenant, distributed, or UI features outside the single-host certification scope.

## Traceability

| ID | Level | Matrix theme | Evidence source | Classification |
|----|-------|--------------|-----------------|----------------|
| EN-SG-01 | N1 | `<script>alert(1)</script>` → escaped text, no execution | Exact-payload DOM regression in `MathRenderer.test.tsx`; CI `40609140000` / `40651541570` | **PASS (scoped frontend DOM)** |
| EN-SG-02 | N1 | `<img src=x onerror=alert(1)>` → escaped text, no execution | Same | **PASS (scoped frontend DOM)** |
| EN-SG-03 | N2 | `x^{2}\text{<b>hola</b>}` → literal, no bold/tags | Exact-source frontend regression; CI `40599001729` | **PASS** |
| EN-SG-04 | N2 | `\href{javascript:alert(1)}{x}` | No anchor / no script; CI `40609140000` / `40651541570` | **PASS (scoped frontend DOM)** |
| EN-SG-05 | N2 | `\url`, `\includegraphics`, `\htmlClass`, `\htmlStyle` | No active HTML; CI `40609140000` / `40651541570` | **PASS (scoped frontend DOM)** |
| EN-SG-06 | N2 | `\def\a{\a}\a` | `maxExpand=1000` product pin + `<2s` + `data-render-fallback="syntax"` + literal text; CI `40651541570` frontend SUCCESS on `bd1742bd` | **PASS (scoped frontend DOM)** |
| EN-SG-07 | N2 | `\newcommand`, `\let`, `\catcode` | Same bound for recursive `\newcommand`/`\catcode`; `\let` inert/safe path (syntax fallback or inert `.katex`); CI `40651541570` | **PASS (scoped frontend DOM)** |
| EN-SG-08 | N2 | `\input` / `\include` / `\write18` / `\openin` | Backend probes; CI `40602481512` | **PASS** |
| EN-SG-09..20, 22, 29..31 | N2/N3 | various | Existing harness PARTIAL coverage | **PARTIAL** |
| EN-SG-21 | N3 | Sum of 10k terms <2s | Request schema `max_length=500` rejects at validation boundary (422 VALIDATION_ERROR); test records the contract | **PASS (scoped request-length contract)** |
| EN-SG-23..27 | N3 | Astronomical powers / factorial / symbolic power | Backend bounds; CI `40609140000` | **PASS (scoped backend API)** |
| EN-SG-28 | N3 | Stop long calc + recovery | No certified UI stop button / recovery flow; safety via preemptive bounds; distributed aspects already OUT_OF_SCOPE_SINGLE_HOST | **OUT_OF_SCOPE** |
| EN-SG-32 | N3 | Burst + conditional rate limit | Opt-in fixed-window limiter (`backend/app/services/rate_limit.py`); 429 + `Retry-After`; disabled by default; 12 tests, all PASSED in CI `40812736234` | **PASS (scoped backend API)** |

## Execution record — 2026-10-28 (r333) EN-SG-06/07

**Product change** (`frontend/src/components/MathRenderer.tsx`, commit `8d5cda79`):

- Export `MAX_KATEX_EXPANSIONS = 1000` and pass it explicitly to `katex.renderToString` so the expansion bound is a product guarantee, not an implicit library default.
- On markup guard or KaTeX parse error, set `data-render-fallback="markup"|"syntax"` on the fallback text node for an observable clear-error signal.

**Tests** (`MathRenderer.test.tsx`, commits `8d5cda79` → `c0786d4e` → `bd1742bd`):

- EN-SG-06 (`\def\a{\a}\a`, `\def\x{\x\x}\x`) and EN-SG-07 (`\newcommand{\a}{\a}\a`, `\catcode`): assert elapsed < 2 s, `data-render-fallback="syntax"`, no active HTML, literal textContent.
- EN-SG-07 `\let\a\b`: assert elapsed < 2 s, no active HTML, and either syntax fallback or inert `.katex` (MathML annotation may still appear in textContent).
- Regression: finite `\def\a{x}\a` still renders via KaTeX.

**CI evidence:** Plus CI run [40651541570](https://github.com/c2melendez/precision-lab-plus/actions/runs/40651541570) on SHA `bd1742bd217d4b265d33f6d108098f04b5a789f9` — frontend job SUCCESS (typecheck, Unit and parity tests, production build). Scope: jsdom DOM only; not a real-browser session.

## Execution record — 2026-10-29 (r342) EN-SG-32 rate limit

**Decision change:** the r336 closure recorded EN-SG-32 as OUT_OF_SCOPE (no limiter existed, parity with Lite). With the operator's explicit decision, the row is reopened and certified against a real opt-in control instead of a scope exception.

**Product change** (`backend/app/services/rate_limit.py`, `backend/app/main.py`, `backend/app/core/config.py`):

- `FixedWindowRateLimiter`: fixed window per client key, injectable monotonic clock, bounded table (10 000 keys, least-recently-seen evicted first).
- Disabled by default (`RATE_LIMIT_REQUESTS=0`): no 429 and no `X-RateLimit-*` headers, so a deployment that has not opted in keeps the previous behaviour byte for byte.
- `RATE_LIMIT_WINDOW_SECONDS` (default 60). `RATE_LIMIT_TRUST_FORWARDED_FOR` (default `false`): a client-forged `X-Forwarded-For` cannot mint a fresh bucket unless the operator opts in behind a proxy that overwrites the header.
- Rejection: HTTP 429 with `error_code: "RATE_LIMITED"`, `Retry-After`, `X-RateLimit-Limit/Remaining/Reset`, `X-Request-ID` and the baseline security headers. The check runs in `request_context_middleware` before routing, body reading and validation, alongside the existing 413 guard.
- Exempt: `/api/v1/health`, `/api/v1/docs`, `/api/v1/redoc`, `/api/v1/openapi.json`, and CORS `OPTIONS` preflight (throttling preflight would surface as a CORS failure, not a 429).

**Tests** (`backend/tests/test_in625_h2_rate_limit.py`, 12 cases): shipped default disabled (20 rapid calls, no 429, no headers); burst `N+1` → 429 with headers and `< 2 s`; window recovery at expiry (still blocked at 9.9 s of a 10 s window); exempt endpoints and preflight; exemptions matched exactly, so traffic ending in `/docs` or `/openapi.json` is still throttled; per-client isolation; `X-Forwarded-For` ignored by default and honoured only when trusted, including comma chains (left-most entry); bounded tracking plus eviction; invalid configuration rejected; environment parsing including defaults.

**CI evidence:** Plus cumulative gate run [40812736234](https://github.com/c2melendez/precision-lab-plus/actions/runs/40812736234) on SHA `1959b2b7d3ffc839153500431a6d09a3fbd17bab`: the 12 EN-SG-32 tests appear individually as `PASSED` in the backend job log (job `123246625130`) and the frontend job is SUCCESS. That run and the `CI` workflow run [40812736236](https://github.com/c2melendez/precision-lab-plus/actions/runs/40812736236) end in `failure` for exactly one reason: `tests/test_algebra229_as_b29.py::test_as_b29_factor_123456789_http`, the published ALGEBRA229-AS-B-29 **test-first** red owned by another workstream (see `next_action` in `continuity.json`). No EN-SG-32 test failed and no other backend test failed: `1 failed, 2738 passed, 1 skipped, 10 xfailed`, coverage 88.90% against the 75% gate.

**Incident recorded:** the first push (`ea1319ce`) shipped `backend/app/main.py` with cp1252 mojibake and a BOM because the edit round-tripped through PowerShell; CI caught it in `test_health::test_app_starts_without_error` (`1 failed, 2737 passed`). Commit `26bfd6f9` rebuilt the file from the committed blob and re-applied only the EN-SG-32 insertions; `1959b2b7` additionally documents the eviction limitation and asserts it. The certified SHA is `1959b2b7`.

**Local full suite (Windows, `CORS_ORIGINS` pinned as in CI):** 2 717 passed, 17 skipped, 10 xfailed, 5 failed, 2 errors. None is EN-SG-32: AS-B-29 (expected red above), `test_edcx_ed_a1_01_l53[ED-H-06]` and `test_edcx_ed_a7_01_l25` (timing/order; both pass when run alone), `test_in625_sg28_interruptible` (Windows subprocess timing), `test_syntax309_syx16_http` (the guard normalises to `\etc\passwd`, so it cannot match `/etc/passwd` on Windows); the 2 `EN-SG-22` errors are pytest's `_update_current_test_var` hitting the 32 767-character Windows environment limit. All of them are green in the Linux CI runs cited above.

**Limits recorded:** the counter is in-process, so multi-worker or multi-host enforcement needs a shared store and remains `OUT_OF_SCOPE_SINGLE_HOST` under `H2-SG28-DIST-01..08`. The tracked-client table is bounded (10 000 keys, least-recently-seen evicted first); an evicted client starts a fresh window, which is asserted by the suite as a documented limitation of a fixed-window counter without shared state, not as a safe direction. The frontend has no dedicated 429 UX; that path is inert while the default stays disabled.

## Closure record — 2026-10-28 (r336) EN-SG-21 / 28 / 32

### EN-SG-21 — length contract decision

Matrix expects a 10 000-term sum to complete in < 2 s.  
Product contract (`EvaluateRequest` and related schemas) is `max_length=500`.  
A literal 10k-term sum is ~19 999 characters and is rejected at the Pydantic validation boundary with HTTP 422 / `VALIDATION_ERROR` before any CAS work.  

**Decision:** Keep the existing 500-character request contract (project rule: contracts are not redefined without explicit authorization).  
**Classification:** **PASS (scoped request-length contract)**.  
Evidence: `test_in625_h2_sg21_ten_thousand_terms_meet_the_request_length_contract` asserts 422, error_code, mention of 500, and elapsed < 2 s.

### EN-SG-28 — UI stop + recovery

No certified «Detener cálculo» button or end-to-end recovery flow exists in the current frontend.  
Backend has interruptible / cancellation primitives and an opt-in isolation flag, but they are not wired to a user-facing stop control under the single-host certification scope.  
Distributed SG28 rows remain OUT_OF_SCOPE_SINGLE_HOST.  
Lite already classified the same row as OUT_OF_SCOPE (preemptive bounds only).

**Decision:** OUT_OF_SCOPE for single-host H2 certification. Safety is provided by existing complexity / length / timeout bounds.

### EN-SG-32 — rate limit

**Superseded by r342.** At r336 no rate-limiting middleware, dependency, or product feature was present, Lite marked the row N/A, and a real limiter looked like a multi-tenant / architectural addition outside the single-host audit, so the row was closed as OUT_OF_SCOPE (parity with Lite).

The operator then authorized an opt-in control. The r342 execution record above certifies the implementation: disabled by default, so the shipped behaviour is unchanged, and scoped to the backend API of a single host. Distributed enforcement is still not certified and stays under `H2-SG28-DIST-01..08` (`OUT_OF_SCOPE_SINGLE_HOST`).

**Decision:** **PASS (scoped backend API)** — supersedes the r336 OUT_OF_SCOPE row.

## Final counts

- **PASS (scoped):** 15 — EN-SG-01, 02, 03, 04, 05, 06, 07, 08, **21**, 23, 24, 25, 26, 27, **32**.
- **PARTIAL:** 16 — EN-SG-09..20, 22, 29, 30, 31.
- **OUT_OF_SCOPE:** 1 — EN-SG-28.
- **GAP:** 0.

SECURITY-S25: ACCEPTED_BILATERAL (2026-10-28, Plus `bd1742bd` + Lite `11f8a5f4`; `allow_reuse=false` retained), no longer BLOCKED.  
Global certification: OPEN.  
No production stress tests were executed.
