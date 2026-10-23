## 2026-10-23 UTC — r252: MV-H-01..12 PASS_SCOPED_BILATERAL

**MV-H (productos mixtos, 1×1, hermítica, estructuras 10×10, Hilbert, límites) — PASS_SCOPED_BILATERAL.**

### Cobertura

| Caso | Plus | Lite |
|------|------|------|
| H-01..05, H-12 | API multiply/inverse/power + PARSE | engine multiply/invert/power |
| H-06 hermítica | SymPy `Matrix.H` | — (complejos) |
| H-07 rank a_ij=i+j | SymPy 10×10 = 2 | proxy 6×6 rank 2 |
| H-08 tridiagonal det | SymPy 10×10 = 11 | 6×6 det = 7 (n+1) |
| H-09 det simbólico 4×4 | 24 términos Leibniz | — |
| H-10 Hilbert | 8×8 entero + 4×4 API | 4×4 inverse entero |
| H-11 oversize | 422 sin hang (max 6) | — |

### Evidencia CI

| Repo | HEAD | Cumulative |
|------|------|------------|
| Plus | `a6a28e4` | [39913600442](https://github.com/c2melendez/precision-lab-plus/actions/runs/39913600442) **SUCCESS** |
| Lite | `1ecfbb0` | [39913642080](https://github.com/c2melendez/precision-lab-lite/actions/runs/39913642080) **SUCCESS** |

**Siguiente acción única:** **MV-J** (última sección de la matriz; no hay I en el JSONL).

---

## 2026-10-23 UTC — r251: MV-G PASS_SCOPED_BILATERAL

Vectores + geometría 3D. Ver r251.
