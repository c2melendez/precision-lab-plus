# H2 EN-SG evidence audit R314 (Plus)

**Status:** PARTIAL · **As of:** 2026-10-28 UTC · **Last certified SHA (EN-SG-06/07):** `bd1742bd217d4b265d33f6d108098f04b5a789f9` · **Prior N3 tranche SHA:** `29fc1295d7087a40a34b2a7b611cf73a76e96df3`
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
| EN-SG-21 | N3 | Sum of 10k terms <2s | 422 at max_length=500 | **GAP** |
| EN-SG-23..27 | N3 | Astronomical powers / factorial / symbolic power | Backend bounds; CI `40609140000` | **PASS (scoped backend API)** |
| EN-SG-28 | N3 | Stop long calc + recovery | SG28 backend only | **GAP** |
| EN-SG-32 | N3 | Burst + conditional rate limit | No limiter | **GAP** |

## Execution record — 2026-10-28 (r333) EN-SG-06/07

**Product change** (`frontend/src/components/MathRenderer.tsx`, commit `8d5cda79`):

- Export `MAX_KATEX_EXPANSIONS = 1000` and pass it explicitly to `katex.renderToString` so the expansion bound is a product guarantee, not an implicit library default.
- On markup guard or KaTeX parse error, set `data-render-fallback="markup"|"syntax"` on the fallback text node for an observable clear-error signal.

**Tests** (`MathRenderer.test.tsx`, commits `8d5cda79` → `c0786d4e` → `bd1742bd`):

- EN-SG-06 (`\def\a{\a}\a`, `\def\x{\x\x}\x`) and EN-SG-07 (`\newcommand{\a}{\a}\a`, `\catcode`): assert elapsed &lt; 2 s, `data-render-fallback="syntax"`, no active HTML, literal textContent.
- EN-SG-07 `\let\a\b`: assert elapsed &lt; 2 s, no active HTML, and either syntax fallback or inert `.katex` (MathML annotation may still appear in textContent).
- Regression: finite `\def\a{x}\a` still renders via KaTeX.

**CI evidence:** Plus CI run [40651541570](https://github.com/c2melendez/precision-lab-plus/actions/runs/40651541570) on SHA `bd1742bd217d4b265d33f6d108098f04b5a789f9` — frontend job SUCCESS (typecheck, Unit and parity tests, production build). Scope: jsdom DOM only; not a real-browser session.

## Counts and next action

- PASS (scoped): 13 — EN-SG-01, 02, 03, 04, 05, **06**, **07**, 08, 23, 24, 25, 26, 27.
- PARTIAL: 16 — EN-SG-09..20, 22, 29, 30, 31.
- GAP: 3 — EN-SG-21, 28, 32.

Next: EN-SG-09..20 deeper probes where useful; EN-SG-28 needs UI stop/recovery; EN-SG-21 needs a contract decision; EN-SG-32 needs a product rate-limit decision or explicit OUT_OF_SCOPE. SECURITY-S25 remains BLOCKED (bilateral). Global OPEN. No production stress tests.
