## 2026-10-23 UTC — r247: MV-E-01..12 producto Plus PASS (Lite pendiente)

**MV-E-01..12 (rango, núcleo, espacio columna, rango–nulidad) — PASS producto Plus.**

### Superficies de producto (Plus)

| Endpoint | Uso |
|----------|-----|
| `POST /matrix/rank` | E-01..08, E-12 (compose); `allow_symbolic=True` para E-08 |
| `POST /matrix/nullspace` | E-09, E-11 (base del ker; filas = vectores) |
| `POST /matrix/columnspace` | E-10 (columnas pivote como filas) |

Implementación: `backend/app/services/matrix_spaces.py` + router `matrix_spaces`; enums `MATRIX_NULLSPACE` / `MATRIX_COLUMNSPACE`. Suite permanente: `backend/tests/test_matrices_mv_e01_l12.py` (12 filas + meta JSONL/fuente).

### Evidencia CI (attempt=1, success)

| Gate | Run | HEAD |
|------|-----|------|
| Cumulative | [39904542863](https://github.com/c2melendez/precision-lab-plus/actions/runs/39904542863) **SUCCESS** | `544d8bd` |
| rank allow_symbolic fix | [544d8bd](https://github.com/c2melendez/precision-lab-plus/commit/544d8bdf2d7219c8b1ad186ad666d46267a91942) | — |
| S25 + S19 (sin regresión) | [39903153215](https://github.com/c2melendez/precision-lab-plus/actions/runs/39903153215) SUCCESS | `d917ea9` |

**Causa del fallo previo (39903153171):** `/matrix/rank` sin `allow_symbolic` → E-08 (`a`) rechazado. Corregido alineado con determinant/inverse.

**Lite:** aún sin `nullspace`/`columnspace` ni `matricesMvE01to12.audit.test.ts` → bilateral **OPEN** hasta paridad Lite.

**SECURITY-S25: CLEARED.** S19 baseline PASS. Global **OPEN**.

**Bloqueos restantes:** H2-SG28-DIST-01..08; SY-P-23; SY-X-04-PLUS-HTTP; ALGEBRA229-AS-B-29.

**Siguiente acción única:** completar **MV-E en Lite** (nullspace/columnspace + audit test anclado a la misma matriz) y registrar PASS_SCOPED_BILATERAL; luego **MV-F**.

---

## 2026-10-23 UTC — r246: MV-D-01..17 cerrado formalmente (PASS_SCOPED_BILATERAL)

**MV-D-01..17 (sistemas, rref, LU, Gram-Schmidt sin normalizar) — PASS_SCOPED_BILATERAL.**

Criterio de salida de campaña S25/S19 satisfecho; se registra el cierre formal diferido desde r239.

### Evidencia de producto (SHA técnico MV-D, attempt=1, success)

| Repo | SHA técnico | Gates |
|------|-------------|-------|
| Lite | `c28091c0173f951a2571ffcbb6084f566ced0034` | cumulative [39754424771](https://github.com/c2melendez/precision-lab-lite/actions/runs/39754424771), h1d [39754424829](https://github.com/c2melendez/precision-lab-lite/actions/runs/39754424829), scientific-ui [39754424596](https://github.com/c2melendez/precision-lab-lite/actions/runs/39754424596) |
| Plus | `91d7f7b499e1effaeef7c4a3bd9e04c0b3b6d6f5` | cumulative [39754425445](https://github.com/c2melendez/precision-lab-plus/actions/runs/39754425445), backend-isolation [39754425427](https://github.com/c2melendez/precision-lab-plus/actions/runs/39754425427), h1d [39754425636](https://github.com/c2melendez/precision-lab-plus/actions/runs/39754425636), native-syntax [39754425572](https://github.com/c2melendez/precision-lab-plus/actions/runs/39754425572), SG28 UI [39754425501](https://github.com/c2melendez/precision-lab-plus/actions/runs/39754425501) |

Suites de auditoría permanentes: Lite `tests/matricesMvD01to17.audit.test.ts`; Plus `backend/tests/test_matrices_mv_d01_l17.py`. Anclaje a `matriz_matrices_vectores.md.gz` / `matrices_ejecutables.jsonl` sección D.

**SECURITY-S25: CLEARED.** S19 frontend: PASS. Global **OPEN**.
