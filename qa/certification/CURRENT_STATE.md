## 2026-10-23 UTC — r251: MV-G-01..22 PASS_SCOPED_BILATERAL

**MV-G (operaciones vectoriales + geometría 3D) — PASS_SCOPED_BILATERAL.**

### Superficies

| Operación | Plus | Lite |
|-----------|------|------|
| Suma / dot / cross | `/matrix/operations` | `addMatrices` / `dotProduct` / `crossProduct` |
| Norma | `/matrix/norm` | `vectorNorm` |
| Errores dim / 2D cross | `DIMENSION_MISMATCH` | throw |
| Proyección, ángulo, triple, plano, distancias, intersecciones | oráculo SymPy en suite | fórmulas exactas en suite |

### Evidencia CI

| Repo | HEAD | Cumulative |
|------|------|------------|
| Plus | `981924c` | [39912625355](https://github.com/c2melendez/precision-lab-plus/actions/runs/39912625355) **SUCCESS** |
| Lite | `0aba84c` | [39912143550](https://github.com/c2melendez/precision-lab-lite/actions/runs/39912143550) **SUCCESS** |

Suites: Plus `test_matrices_mv_g01_l22.py`; Lite `tests/matricesMvG01to22.audit.test.ts`.

**Siguiente acción única:** **MV-H** (siguiente sección de la matriz congelada).

---

## 2026-10-23 UTC — r250: MV-F PASS_SCOPED_BILATERAL

Plus full F-01..17; Lite powers + CH. Ver r249–r250.
