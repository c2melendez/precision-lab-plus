## 2026-10-23 UTC — r248: MV-E-01..12 PASS_SCOPED_BILATERAL

**MV-E-01..12 (rango, núcleo, espacio columna, rango–nulidad) — PASS_SCOPED_BILATERAL.**

### Superficies

| Repo | Superficie |
|------|------------|
| Plus | `POST /matrix/rank` (allow_symbolic), `/matrix/nullspace`, `/matrix/columnspace` |
| Lite | `rank()`, `nullspace()`, `columnspace()` en `matrixOps` / `matrixSpaces` |

Suites: Plus `backend/tests/test_matrices_mv_e01_l12.py`; Lite `tests/matricesMvE01to12.audit.test.ts`. Anclaje a `matriz_matrices_vectores.md.gz` / `matrices_ejecutables.jsonl` sección E.

### Evidencia CI (attempt=1, success)

| Repo | HEAD | Cumulative |
|------|------|------------|
| Plus | `544d8bd` (rank fix) | [39904542863](https://github.com/c2melendez/precision-lab-plus/actions/runs/39904542863) **SUCCESS** |
| Lite | `4f2abd9` | [39905437848](https://github.com/c2melendez/precision-lab-lite/actions/runs/39905437848) **SUCCESS** (typecheck + unit/parity + build) |

**SECURITY-S25: CLEARED.** S19 baseline PASS. Global **OPEN**.

**Bloqueos restantes:** H2-SG28-DIST-01..08; SY-P-23; SY-X-04-PLUS-HTTP; ALGEBRA229-AS-B-29.

**Siguiente acción única:** iniciar **MV-F** (siguiente sección de la matriz congelada).

---

## 2026-10-23 UTC — r247: MV-E producto Plus PASS (Lite pendiente)

Plus cumulative [39904542863] SUCCESS tras fix rank allow_symbolic. Lite completado en r248.
