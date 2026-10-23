## 2026-10-23 UTC — r249: MV-F-01..17 producto Plus PASS (Lite pendiente)

**MV-F-01..17 (valores/vectores propios, polinomio característico, Cayley–Hamilton, diagonalización, potencias) — PASS producto Plus.**

### Superficies Plus

| Caso | Superficie |
|------|------------|
| F-01..10 | `POST /matrix/eigen` (SymPy eigenvects) |
| F-11 | charpoly vía motor (det(λI−A)) |
| F-12 | Cayley–Hamilton vía `/matrix/power` |
| F-13 | diagonalize (oráculo + A=PDP⁻¹) |
| F-14..17 | `/matrix/power` (exponente hasta ±32; F-15 = A³⁰) |

Suite: `backend/tests/test_matrices_mv_f01_l17.py`. `MAX_MATRIX_POWER_EXPONENT = 32` y Pydantic `ge/le=±32`.

### Evidencia CI

| Gate | Run | HEAD |
|------|-----|------|
| Cumulative | [39910191954](https://github.com/c2melendez/precision-lab-plus/actions/runs/39910191954) **SUCCESS** | `929bc64` |

**Lite:** potencias F-14..17 vía `powerMatrix` (sin límite); eigen simbólico (i, √5) fuera de Fraction → paridad parcial en progreso.

**Siguiente acción única:** completar **MV-F Lite** (al menos potencias + autovalores racionales) → PASS_SCOPED_BILATERAL; luego **MV-G**.

---

## 2026-10-23 UTC — r248: MV-E-01..12 PASS_SCOPED_BILATERAL

Plus+Lite cumulative green (rank/nullspace/columnspace).
