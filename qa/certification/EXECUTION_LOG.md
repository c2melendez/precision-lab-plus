## 2026-10-23 UTC — r247: MV-E Plus product PASS; rank allow_symbolic

- [544d8bd](https://github.com/c2melendez/precision-lab-plus/commit/544d8bdf2d7219c8b1ad186ad666d46267a91942): `/matrix/rank` con `allow_symbolic=True` (E-08).
- Cumulative [39904542863](https://github.com/c2melendez/precision-lab-plus/actions/runs/39904542863) **SUCCESS** (backend+frontend regression).
- Superficies: rank, nullspace, columnspace; suite `test_matrices_mv_e01_l12.py`.
- Lite MV-E aún pendiente (sin nullspace/columnspace ni audit test).
- Siguiente: paridad Lite → PASS_SCOPED_BILATERAL; luego MV-F.

---

## 2026-10-23 UTC — r246: cierre formal MV-D-01..17 PASS_SCOPED_BILATERAL

- Condición de campaña S25/S19 cumplida (39890525978, 39899659414 SUCCESS; score 21.10 %).
- Producto MV-D ya verde en Lite `c28091c` y Plus `91d7f7b`.
- Siguiente objetivo era MV-E (ahora r247).
