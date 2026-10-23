# EDCX-B6 — auditoría previa de canal (r267)

Estado: REVIEW; no medir todavía.

Plus contiene 53 filas B6 (VC-FE-01..53) en `qa/certification/edcx_ejecutables.jsonl`; las 53 tienen `canal` vacío. Lite no contiene ese JSONL ni motor equivalente de variable compleja, por lo que permanece NO_EJECUTADO.

Canal candidato para valores escalares: `POST /api/v1/evaluate`, por consistencia con el bloque previo B3. No se asigna automáticamente a todas las filas: VC-FE-11 exige valores multivaluados; VC-FE-45, 49 y 53 requieren declarar convención de rama/signo; VC-FE-12 compara la no aditividad del logaritmo principal; VC-FE-14 exige error de dominio. Además, la matriz usa `Log` y el producto distingue `log` base 10 de `ln` natural. Se requiere adaptador semántico explícito y oráculo independiente.

HEAD actual de la rama canónica: Plus `112e0a3908675bc99fa7295ed84b6d58b6c05d19`; Lite `7838ca80ff6dc899aaee9d1dc654519864dcf40c`. Las corridas workflow_dispatch r264 finalizaron SUCCESS, pero corresponden a SHA anteriores (`86f1ce84...` Plus y `912e3f8a...` Lite); no prueban B6 ni la ejecución sobre HEAD r266. B4 técnico Plus sigue respaldado por push cumulative `40014004350` y H1d `40014004348` sobre `7e501f5...`.

No se despachó CI: este paso es documental. Siguiente: definir formalmente canal/notación/ramas por fila; después harness test-first Plus con oráculo independiente y gates mínimos en SHA exacto. Lite NO_EJECUTADO; global OPEN.