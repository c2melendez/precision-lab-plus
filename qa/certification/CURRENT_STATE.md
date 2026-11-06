# Actualización de certificación — 2026-11-06 UTC (r435)

## Algebra229 AS-B-24 — IN_PROGRESS (Plus gates aprobados; pendiente H1d Lite)

**Contrato:** `factor(x^2-2) sobre ℝ` → `(x-sqrt(2))*(x+sqrt(2))` (N3). Se conserva la distinción con AS-B-23, donde `x^2-2` permanece irreducible sobre ℚ.

### Plus — SHA técnico `5d8d78f8e35d02830bfbce63c107fe5990904cd1`
- Test `backend/tests/test_algebra229_as_b24.py`: 3/3 PASS; fila fuente exacta, endpoint HTTP `POST /api/v1/factor`, forma ASCII, equivalencia SymPy y oráculo AST independiente en diez muestras enteras.
- Cumulative [42221909462](https://github.com/c2melendez/precision-lab-plus/actions/runs/42221909462) SUCCESS; frontend/backend SUCCESS; focal 3/3; backend 2,803 passed, 1 skipped, 10 xfailed.
- H1d [42221909235](https://github.com/c2melendez/precision-lab-plus/actions/runs/42221909235) SUCCESS, 38/38 Playwright.
- CI [42221909164](https://github.com/c2melendez/precision-lab-plus/actions/runs/42221909164) SUCCESS; frontend/backend SUCCESS; backend 2,803 passed, 1 skipped, 10 xfailed.
- Runner [42221910347](https://github.com/c2melendez/precision-lab-plus/actions/runs/42221910347) SUCCESS, fingerprint push-only.

### Evidencia bilateral de Lite (pendiente un gate)
- SHA técnico `2342cbd5ac2de6e9a7b1fbf42ddb9df4ee1f9c8d`; test `tests/algebra229AsB24.audit.test.ts` 4/4 PASS en acumulativo y CI.
- Cumulative [42222060038](https://github.com/c2melendez/precision-lab-lite/actions/runs/42222060038) SUCCESS (366/366 archivos); CI [42222060154](https://github.com/c2melendez/precision-lab-lite/actions/runs/42222060154) SUCCESS (366/366; focal 4/4); Scientific UI [42222060025](https://github.com/c2melendez/precision-lab-lite/actions/runs/42222060025) SUCCESS (456/456 desktop/tablet/mobile).
- H1d [42222060032](https://github.com/c2melendez/precision-lab-lite/actions/runs/42222060032) **IN_PROGRESS**: job 127906273506 permanece en `Install Chromium`; la prueba H1d no ha comenzado.

### Diagnóstico del harness y decisión
Los intentos intermedios detectaron y corrigieron únicamente aserciones de la fila congelada: 8 posiciones delimitadas, entrada/salida LaTeX y texto literal `\sqrt{2}` con llaves. Los tests focales de los SHA finales pasan; no hubo cambio de motor/producto. La aceptación bilateral queda pendiente solo del H1d de Lite, que ya está activo. No despachar duplicado. Global **OPEN**.

---

# Actualización de certificación — 2026-11-06 UTC (r434)

## Algebra229 AS-B-23 — PASS_SCOPED bilateral (r434)

- Lite HEAD técnico `f99fff6c06d7950ff14a8711e88035f9c7afd881`: Cumulative 42218347585 SUCCESS (focal 3/3 PASS; 366 archivos, 2,261 passed, 8 expected fail y 34 TODO); H1d 42218347590 SUCCESS (22/22); Scientific UI 42218347639 SUCCESS (456/456 desktop/tablet/mobile); CI 42218347555 SUCCESS; Runner 42218347616 SUCCESS, solo fingerprint de push.
- Plus HEAD técnico `120184413febf16d6471ee0b72a30cabe467fa0c`: Cumulative 42218368185 SUCCESS (frontend/backend SUCCESS; focal 3/3 PASS; backend 2,802 passed, 1 skipped y 10 xfailed); H1d 42218368203 SUCCESS (38/38); CI 42218368283 SUCCESS (frontend/backend SUCCESS); Runner 42218368207 SUCCESS, solo fingerprint de push.
- Acceptance bilateral: `ALGEBRA229_AS_B_23_ACCEPTANCE_2026-11-06.md`. Solo se reforzaron tests; no hubo cambios de motor/producto.
- **Siguiente:** AS-B-24 `factor(x^2-2) sobre ℝ` → `(x-sqrt(2))*(x+sqrt(2))` (N3, se permiten raíces reales). Global **OPEN**.

---

# Actualización de certificación — 2026-11-06 UTC (r433)

## Algebra229 AS-B-22 — PASS_SCOPED bilateral (r433)

- Lite HEAD técnico `b385d88845d9f1e257cbce03295c73273cf4446b`: Cumulative 42211290550 SUCCESS (focal 3/3 PASS; 366 archivos, 2,260 passed, 8 expected fail, 34 TODO); H1d 42211290765 SUCCESS (22/22); Scientific UI 42211290551 SUCCESS (456/456 desktop/tablet/mobile); CI 42211290654 SUCCESS. Runner 42211290975 SUCCESS, solo fingerprint de push.
- Plus HEAD técnico `c2bc727e04d12867bfff1b718c072fe735cf1003`: Cumulative 42211299152 SUCCESS (frontend y backend; focal 3/3 PASS; backend 2,801 passed, 1 skipped, 10 xfailed); H1d 42211299254 SUCCESS (38/38); CI 42211299150 SUCCESS. Runner 42211299262 SUCCESS, solo fingerprint de push.
- En los seis jobs de gates aplicables: guard `skip=false`, `evidence_run_id=""`; pruebas ejecutadas realmente en el SHA de este caso, sin REUSE.
- Acceptance bilateral: `ALGEBRA229_AS_B_22_ACCEPTANCE_2026-11-06.md`. Solo se reforzaron tests; ningún cambio de producto/motor.
- **Siguiente:** AS-B-23 `x^{2}-2` → `x^{2} - 2` (N2, irreducible sobre ℚ: debe quedar igual). Global **OPEN**.

**Reconciliación documental:** Lite mantenía índice/CURRENT_STATE r420 mientras su EXECUTION_LOG ya tenía r432; Plus estaba sincronizado en r432; se sincronizan ambos productos a r433. La certificación global y los gaps externos no cambian.

---

# Actualización de certificación — 2026-11-06 UTC (r432)

## Algebra229 AS-B-21 — PASS_SCOPED bilateral (r432)

- Plus HEAD técnico `768c7539650c91ffb1f51e85ff292aabd8e9a6a6` (test reforzado): Cumulative 42209061963 con focal 2/2 PASS; H1d 42209061958, CI 42209062038 y Runner 42209061955 SUCCESS.
- Lite HEAD técnico `4ab22e5565255bc0d0a451dfae3debf24f8521fa` (test reforzado): Cumulative 42209065420 con focal 3/3 PASS; H1d 42209065464, Scientific UI 42209065501, Runner 42209065402 y CI 42209065433 SUCCESS.
- Acceptance: `ALGEBRA229_AS_B_21_ACCEPTANCE_2026-11-06.md`. Sin cambio de producto.
- **Siguiente:** AS-B-22 `x^{2}+1` → `x^{2} + 1` (N1, irreducible sobre ℚ y ℝ: debe quedar igual). Global **OPEN**.

---

# Actualización de certificación — 2026-11-06 UTC (r431)

## Algebra229 AS-B-20 — PASS_SCOPED bilateral (r431)

- Plus HEAD técnico `fecbf483992095a937f680a1ddab8807b065f166` (test reforzado): Cumulative 42206944853 con focal 2/2 PASS; H1d 42206944896, CI 42206944888 y Runner 42206944815 SUCCESS.
- Lite HEAD técnico `b92f75b9121462bb4e720f554a6b440ea5fef64b` (test reforzado): Cumulative 42206950541 con focal 3/3 PASS; H1d 42206950644, Scientific UI 42206950607, Runner 42206950545 y CI 42206950542 SUCCESS.
- Acceptance: `ALGEBRA229_AS_B_20_ACCEPTANCE_2026-11-06.md`. Sin cambio de producto.
- **Siguiente:** AS-B-21 `(x^{2}+1)^{2}-4x^{2}` → `(x - 1)^{2} (x + 1)^{2}`. Global **OPEN**.

---

# Actualización de certificación — 2026-11-06 UTC (r430)

## Algebra229 AS-B-19 — PASS_SCOPED bilateral (r430)

- Plus HEAD técnico `f5109b537005943738ad9797908bef340d23a5b6` (test reforzado): Cumulative 42202185841 con focal 2/2 PASS; H1d 42202185915, CI 42202185876 y Runner 42202185863 SUCCESS.
- Lite HEAD técnico `7cec57d31bdc78ce5ba0d48c1f7a6f42d7608977` (test reforzado): Cumulative 42202183460 con focal 2/2 PASS; H1d 42202183400, Scientific UI 42202183396, Runner 42202183405 y CI 42202183478 SUCCESS.
- Acceptance: `ALGEBRA229_AS_B_19_ACCEPTANCE_2026-11-06.md`. Sin cambio de producto.
- **Siguiente:** AS-B-20 `x^{4}+x^{2}y^{2}+y^{4}` → `(x^2 - x y + y^2)(x^2 + x y + y^2)`. Global **OPEN**.

---

# Actualización de certificación — 2026-11-06 UTC (r429)

## Algebra229 AS-B-18 — PASS_SCOPED bilateral (r429)

- Plus HEAD técnico `1fab6d5507822c922288c63ba9454f7536d3aead` (test reforzado): Cumulative 42199349315 con focal 2/2 PASS; H1d 42199349400, CI 42199349335 y Runner 42199349956 SUCCESS.
- Lite HEAD técnico `bb159a449f2d320d607b65503310bb8741cf16b2` (test reforzado): Cumulative 42199356489 con focal 2/2 PASS; H1d 42199356467, Scientific UI 42199356498, Runner 42199356546 y CI 42199356505 SUCCESS.
- Acceptance: `ALGEBRA229_AS_B_18_ACCEPTANCE_2026-11-06.md`. Sin cambio de producto.
- **Siguiente:** AS-B-19 `x^{2}y-xy^{2}` → `x y \left(x - y\right)`. Global **OPEN**.

---

## Algebra229 AS-B-17 — PASS_SCOPED bilateral (r428)

- Plus HEAD técnico `5d3df39fbfb19bc209b47f5f5bedb02a7212c19a` (test reforzado): Cumulative 42197922106 con focal 2/2 PASS; H1d 42197922135, CI 42197922387 y Runner 42197922120 SUCCESS.
- Lite HEAD técnico `47b381c81f899dd9f5e3a073b4de6cd726ccda1c` (test reforzado): Cumulative 42197934523 con focal 2/2 PASS; H1d 42197934472, Scientific UI 42197934467, Runner 42197934461 y CI 42197934400 SUCCESS.
- Acceptance: `ALGEBRA229_AS_B_17_ACCEPTANCE_2026-11-06.md`. Sin cambio de producto.
- **Siguiente:** AS-B-18 `x^8-1` → `(x-1)(x+1)(x^2+1)(x^4+1)`. Global **OPEN**.

---

## Algebra229 AS-B-16 — PASS_SCOPED bilateral (r427)

- Plus HEAD técnico `481cb08d99d95124d4e8528162fe787d89206244` (test reforzado): Cumulative 42159166321 con focal 2/2 PASS; H1d 42159166336, CI 42159166327 y Runner 42159166344 SUCCESS.
- Lite HEAD `e2007be51f848a33e0b9881dff3c6a2689991672`: focal 2/2 PASS; Cumulative 42194172938, H1d 42194172980, Scientific UI 42194172930, Runner 42194172934 y CI 42194172999 SUCCESS.
- Acceptance: `ALGEBRA229_AS_B_16_ACCEPTANCE_2026-11-06.md`. Sin cambio de producto.
- **Siguiente:** AS-B-17 `a^3+b^3` → `(a+b)(a^2-ab+b^2)`. Global **OPEN**.

---

# Actualización de certificación — 2026-11-06 UTC (r426)

## Algebra229 AS-B-14 y AS-B-15 — PASS_SCOPED bilateral

- Plus HEAD `8a0015f6803599449dffcc9a35b51428978335cc`: Cumulative/H1d/CI/Runner SUCCESS.
- Lite HEAD `0f0d0296069d3a710d98f77f33d18a30a63b2420`: Cumulative/H1d/Scientific UI/Runner SUCCESS.
- **Siguiente:** AS-B-16 `a^3-b^3` → `(a-b)(a^2+ab+b^2)`. Global **OPEN**.


