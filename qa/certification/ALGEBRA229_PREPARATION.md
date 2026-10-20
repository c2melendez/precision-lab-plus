# Algebra 229 — preparación de matriz y trazabilidad

Estado: **SOURCE_INTEGRITY_PASS / FIXTURE_PROMOTE_PENDING** (2026-10-20). Certificación global **OPEN**.

## Fuente normativa recuperada

| Campo | Valor |
|---|---|
| Original | `matriz_algebra_simbolica.md` (Matrices.zip) |
| Congelado | `qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz` |
| SHA-256 | `8cd36ff08343f98f92abd83e2b162d565e0cbe5c59dc73f26b1c018f77d663c7` |
| Filas / IDs | **229 / 229** (N1=43 N2=132 N3=54; secciones A–L) |
| Validador | `check_algebra229_source.py` |
| Gate | [39381871764](https://github.com/c2melendez/precision-lab-plus/actions/runs/39381871764) SUCCESS @ `1f2c0958…` |

Coincide byte a byte con el adjunto `Matrices.zip`. JSONL del handoff (raw/promoted, 229) es **candidato**, no fixture canónico de producto hasta `ALGEBRA229-FIXTURE-PROMOTE-VALIDATE`.

## Siguiente único

1. Comparar ID/entrada/oráculo/comparación Markdown ↔ JSONL.  
2. Publicar fixture canónico bilateral.  
3. Validador de esquema.  
4. Primer caso test-first (p. ej. AS-A-01) + gates exact-SHA.

No inventar filas; global OPEN; bloqueos Syntax/S25/S19/SG28 sin cambios. Detalle de inventario de las 9 fuentes: `MATRIX_SOURCE_INVENTORY.md` (Lite; mismo contenido aplicable).
