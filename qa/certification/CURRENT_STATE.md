## 2026-10-20 UTC — Algebra114 AS-CONV + AS-LIM cerrados (PARTIAL); siguiente Algebra 229

**AS-CONV-01..08 (sección L) — PARTIAL_BILATERAL.** 01–04 PASS bilateral. 05–08 CAPABILITY_GAP Lite / PASS Plus. 0^0 no literal y `/evaluate` sin warnings → strict xfail. Gates Plus `7eaf11b2` [39369323673](https://github.com/c2melendez/precision-lab-plus/actions/runs/39369323673), [39369323636](https://github.com/c2melendez/precision-lab-plus/actions/runs/39369323636); Lite `d0859f37` [39369325854](https://github.com/c2melendez/precision-lab-lite/actions/runs/39369325854).

**AS-LIM-01..06 (sección M) — PARTIAL_BILATERAL.** Plus **01–06 PASS** (05 vía `/api/v1/factor`). Lite 01/03/04 PASS; 02/06 hang Algebrite (`it.todo`); 05 factor incorrecto (`it.fails`). Gates exact-SHA: Plus `78f3236c4f8b5a2243cbebac8b425926d9265319` cumulative [39371074340](https://github.com/c2melendez/precision-lab-plus/actions/runs/39371074340) SUCCESS (backend 1663 PASS/6 XFAIL), H1d [39371074339](https://github.com/c2melendez/precision-lab-plus/actions/runs/39371074339) SUCCESS; Lite `1235b2a84cdaddcad939092af9cb23e089c5421c` [39371128983](https://github.com/c2melendez/precision-lab-lite/actions/runs/39371128983), [39371128973](https://github.com/c2melendez/precision-lab-lite/actions/runs/39371128973) SUCCESS.

**Algebra 114 (114 filas) — recorrido completo, certificación parcial.** No PASS global Algebra114.

**Álgebra 229 — fuente normativa localizada; gate de integridad pendiente.** Fuente original congelada en `qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz`; el verificador `qa/certification/check_algebra229_source.py` comprueba SHA-256 `8cd36ff08343f98f92abd83e2b162d565e0cbe5c59dc73f26b1c018f77d663c7`, 229 filas, 229 IDs, secciones A–L y niveles N1/N2/N3. Para recuperar la fuente Markdown exacta en un checkout: `python3 qa/certification/check_algebra229_source.py --restore`. Próximo paso único: `ALGEBRA229-SOURCE-INTEGRITY` hasta que el workflow específico pase; después `ALGEBRA229-FIXTURE-PROMOTE-VALIDATE` para validar/publicar el JSONL canónico sin alterar ningún oráculo. No inferir casos desde Module 2 ni Algebra114. Global **OPEN**; S19 null; SG28/DIST/H2, S25, SY-P-23, X04/X14 Plus sin cambios.

## Historial previo

AS-MUL y secciones anteriores: ver commits previos de este archivo y `EXECUTION_LOG.md`. Cabecera actual es la fotografía autoritativa.
