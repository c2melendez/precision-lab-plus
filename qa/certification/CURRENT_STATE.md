## 2026-10-23 UTC — r254: EDCX A1+A2 — PASS_SCOPED (Plus), capacidad Lite no ejecutada

**EDCX Parte A, bloques A1 (53 filas) y A2 (50 filas): 76 PASS + 27 BLOCKED en Plus.**
No es cierre bilateral: Lite no ejecuta estos bloques (gap de alcance de motor, ver
`MANUAL_CAPABILITY_GAPS.md`); la certificación global sigue `OPEN`.

| Bloque | Filas | PASS | BLOCKED | Canal |
|--------|-------|------|---------|-------|
| A1 primer orden | 53 | 47 | 6 | `/api/v1/ode` (prima `y'`) |
| A2 orden 2/superior | 50 | 29 | 21 | `/api/v1/ode` + `/api/v1/matrix/determinant` (Wronskianos) |

- A1: 47 familias verificadas por sustitución numérica; 8 filas F4 (familia
  correcta, sin soluciones singulares enumeradas). Límites acotados y registrados:
  ED-L-12 (canal `x(y)`), ED-X-02/X-03, ED-B-09, ED-C-02, ED-C-05.
- A2: 25 EDO por sustitución, 3 Wronskianos por determinante con oráculo de
  derivadas, ED-A-05 por renombrado documentado `T(t)→y(x)`; 21 bloqueadas por
  alcance medido (orden>2, una sola condición inicial, `yy''=y'^2`, celdas
  `exp/log` rechazadas por el parser de matrices).

### Evidencia CI Plus

| HEAD | Cumulative | H1d | Native |
|------|------------|-----|--------|
| `fdcf2d63` (A2) | [39924322798](https://github.com/c2melendez/precision-lab-plus/actions/runs/39924322798) **SUCCESS** | [39924322809](https://github.com/c2melendez/precision-lab-plus/actions/runs/39924322809) **SUCCESS** | — (sin rutas frontend) |
| `5a76477a` (fix pool) | [39922491068](https://github.com/c2melendez/precision-lab-plus/actions/runs/39922491068) **SUCCESS** | [39922491020](https://github.com/c2melendez/precision-lab-plus/actions/runs/39922491020) **SUCCESS** | [39922491000](https://github.com/c2melendez/precision-lab-plus/actions/runs/39922491000) **SUCCESS** |

Backend cumulative: **2113 passed, 1 skipped, 6 xfailed**, cobertura **87.92%**.

### Regresión real encontrada y corregida

`86241e40` introdujo el aislamiento acotado de `dsolve` con la anotación
`mp.pool.Pool` sin importar el submódulo: H1d `39921705215`, security
`39921705206` y native `39921705116` fallaron con `AttributeError`. Corregido en
`5a76477a` (`from multiprocessing import pool as mp_pool`); los tres workflows
quedaron verdes en ese SHA.

**Siguiente acción única:** EDCX A3 (sistemas y exponencial matricial, 16 filas).

---

## 2026-10-23 UTC — r253: MV-J-01..07 PASS_SCOPED_BILATERAL — CATÁLOGO MV COMPLETO

**MV-J (transformaciones geométricas) — PASS_SCOPED_BILATERAL.**

Con esto se cierra el catálogo congelado **Matrices/Vectores** (153 filas, secciones A–H + J):

| Sección | Tema | Estado |
|---------|------|--------|
| A–D | Aritmética, sistemas, det/inv, Gram-Schmidt | PASS formal bilateral (r≤249) |
| E | Espacios (null/col/rank simbólico) | PASS_SCOPED_BILATERAL |
| F | Potencias + eigen | PASS_SCOPED_BILATERAL |
| G | Vectores + geometría 3D | PASS_SCOPED_BILATERAL |
| H | Productos mixtos, Hilbert, límites | PASS_SCOPED_BILATERAL |
| **J** | Rotación / reflexión / shear / composición | **PASS_SCOPED_BILATERAL** |

### Evidencia CI MV-J

| Repo | HEAD | Cumulative |
|------|------|------------|
| Plus | `2fcd869` | [39914423538](https://github.com/c2melendez/precision-lab-plus/actions/runs/39914423538) **SUCCESS** |
| Lite | `40b000b` | [39914455096](https://github.com/c2melendez/precision-lab-lite/actions/runs/39914455096) **SUCCESS** |

### Notas
- J-01..05, J-07: API multiply / det / power.
- J-06 composición simbólica: oráculo SymPy (`R(θ)R(φ)=R(θ+φ)`); Lite proxy numérico R90²=R180.

**Siguiente acción única (fuera de MV):** retomar gates transversales del protocolo de continuidad (p. ej. ampliación Stryker / resto de dominios según CURRENT_STATE previo a la serie MV-E..J), o formalizar cierre del dominio Matrices/Vectores en el registro de certificación.

---

## 2026-10-23 UTC — r252: MV-H PASS_SCOPED_BILATERAL

Ver r252.
