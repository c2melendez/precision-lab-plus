# EDCX-B5 — Capability Gap / OUT_OF_SCOPE (VC-LG-01..25)

**Status:** OUT_OF_SCOPE (capability) · **As of:** 2026-10-28 UTC · **Canonical branch:** `qa/syntax-audit-in625-a1`  
**Source matrix:** `qa/certification/edcx_ejecutables.jsonl` (bloque B5, 25 filas)  
**Primary decision document:** this file · **Index:** `qa/certification/continuity.json` (r339+)

## Decision rules applied

- Explicit OUT_OF_SCOPE is preferred over an open GAP when the row requires a product surface (endpoint, mode, or semantic output) that does not exist and is outside the single-host certification scope of the current audit.
- A green unit/API rejection or absence of crash is not certification PASS for geometric-locus description.
- No new product endpoints, graphing, or visual rendering were introduced solely to close this block.
- Parity with Lite (NO_EJECUTADO / no equivalent engine) is preserved.

## Inventory (25 rows)

All rows have empty `canal`. Theme: geometric loci / regions in the complex plane.

| ID | Level | Source exercise | Source expected |
|----|-------|-----------------|----------------|
| VC-LG-01 | N1 | `\|z\|=2` | circunferencia de centro `0` y radio `2` |
| VC-LG-02 | N1 | `\|z-1\|<2` | disco abierto de centro `1` y radio `2` |
| VC-LG-03 | N1 | `1<\|z\|≤2` | corona circular |
| VC-LG-04 | N1 | `Re z >1` | semiplano `x>1` |
| VC-LG-05 | N1 | `arg z = π/4` | semirrecta `y=x, x>0` |
| VC-LG-06 | N2 | `π/6 ≤ arg z ≤ π/3` | sector angular |
| VC-LG-07 | N2 | `Re(z²)=1` | hipérbola `x²-y²=1` |
| VC-LG-08 | N2 | `Im(z²)=2` | hipérbola `xy=1` |
| VC-LG-09 | N2 | `\|z-1\|=\|z+1\|` | eje imaginario `x=0` |
| VC-LG-10 | N3 | `\|z-1\|=2\|z+1\|` | circunferencia centro `-5/3` radio `4/3` |
| VC-LG-11 | N2 | `\|z-1\|+\|z+1\|=4` | elipse `x²/4 + y²/3 =1` |
| VC-LG-12 | N3 | `\|z-2\|-\|z+2\|=2` | rama izquierda de hipérbola |
| VC-LG-13 | N3 | (inequality involving \|z\| / Re) | disco / región acotada |
| VC-LG-14 | N3 | (inequality involving \|z\| / Re) | disco abierto |
| VC-LG-15 | N3 | `\|z\| < Re z +1` | interior de la parábola `y²<2x+1` |
| VC-LG-16 | N3 | `\|z\| = Re z +1` | parábola `y²=2x+1` |
| VC-LG-17 | N3 | `Re((z-1)/(z+1))=0` | circunferencia `\|z\|=1`, sin `z=-1` |
| VC-LG-18 | N2 | `(z-1)/(z+1) ∈ ℝ` | eje real, sin `z=-1` |
| VC-LG-19 | N2 | `z² ∈ ℝ` | ejes real e imaginario |
| VC-LG-20 | N2 | `Im(z²)>0` | 1.er y 3.er cuadrantes (`xy>0`) |
| VC-LG-21 | N2 | `Re(iz)>0` | semiplano inferior `y<0` |
| VC-LG-22 | N2 | curva `z=2e^{it}`, `t∈[0,π]` | semicircunferencia superior radio 2 |
| VC-LG-23 | N2 | curva `z=1+e^{it}`, `t∈[0,2π]` | circunferencia centro 1 radio 1 |
| VC-LG-24 | N2 | curva trigonométrica equivalente | semicircunferencia superior radio 2 |
| VC-LG-25 | N3 | `z=cosh t + i sinh t` | rama derecha de hipérbola `x²-y²=1` |

## Product capability audit (Plus)

Existing complex-analysis surface (`backend/app/routers/complex_analysis.py`):

- `POST /api/v1/complex/residue`
- `POST /api/v1/complex/singularities`

No other complex endpoints.  
`/api/v1/evaluate`, `/solve`, and related routers do not emit geometric-locus descriptions (textual, symbolic region, or set description).  
Code search for locus / geometric-region / arg-z / semiplano / circunferencia semantics yields no product implementation that satisfies the matrix expectations.

**Conclusion:** absence of both a dedicated channel (endpoint or mode) and the required semantic output type. This is a pure **capability gap**, not an incomplete implementation of an already-designed feature.

## Classification decision

**EDCX-B5 (VC-LG-01..25) → OUT_OF_SCOPE (capability)** for the current single-host certification scope.

Rationale (aligned with EN-SG-28, EN-SG-32, H2-SG28-DIST):

- Closing the rows as PASS would require a new product contract (input → canonical geometric description) plus optional visualization; that is architectural product work, not an audit gap that can be filled by tests alone.
- Leaving an open GAP indefinitely is less precise than an explicit, reversible OUT_OF_SCOPE decision.
- Lite remains NO_EJECUTADO / without equivalent engine; bilateral parity is preserved.
- No production stress tests, graphing engines, or new endpoints were introduced.

This is **not FAIL**. It is a scoped, documented decision that the geometric-locus description surface lies outside the certified single-host product surface of the present audit.

## Final counts for the block

- **OUT_OF_SCOPE:** 25 (VC-LG-01..25)
- **PASS / PARTIAL / GAP:** 0

## Continuity impact

- `continuity.json` blocker `EDCX-B5` status updated from `BLOCKED` to `OUT_OF_SCOPE`.
- Ledger note records the closure.
- Global certification remains **OPEN**.
- Next natural fronts remain ALGEBRA229-AS-B-29 (ON_HOLD), EDCX-B6 (REVIEW), or further PARTIAL EN-SG rows.

## Non-actions

- No product code changed.
- No CI dispatched for this documentary change.
- No modification of `edcx_ejecutables.jsonl` or the frozen source matrix.
- Future product work that adds a locus-description endpoint can re-open the block under a new acceptance revision.
