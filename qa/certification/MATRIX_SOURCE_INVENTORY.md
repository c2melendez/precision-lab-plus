# Inventario de fuentes — 9/9 Matrices.zip en producto

**Corte:** 2026-10-20. MANIFEST + import + check en ambos repos.

| Key | Canonical | Estado |
|-----|-----------|--------|
| AS229 | matriz_algebra_simbolica.md.gz | CONGELADO (binario + fixture builder) |
| AS114 | matriz_algebra_simbolica_estres_114.md.gz | MANIFEST; materializar con import |
| IN309 | matriz_sintaxis_entrada_309.md.gz | MANIFEST; materializar con import |
| IN625 | matriz_entrada_sintaxis_625.md.gz | MANIFEST; materializar con import |
| TR324 | ejercicios_trigonometria.md.gz | MANIFEST; materializar con import |
| LER | matriz_log_exp_radicales.md.gz | MANIFEST; materializar con import |
| MV153 | matriz_matrices_vectores.md.gz | MANIFEST; materializar con import |
| EDCX | matriz_edo_variable_compleja.md.gz | MANIFEST; materializar con import |
| GR519 | matriz_graficacion.md.gz | MANIFEST; materializar con import |

```bash
python3 qa/certification/import_from_matrices_zip.py Matrices.zip
python3 qa/certification/check_legacy_sources.py
```

Siguiente ejecucion de producto: ALGEBRA229-AS-A-01-TEST-FIRST (no cambia por este freeze).
