# S26 — Prompt de continuidad actualizado

Proyecto: **Precision Lab Plus**  
Branch: `qa/s26-execution`  
HEAD de código certificado B4: `40fcf3b3aa2d83fa58943fec603198dd0bb291bb`

## INSTRUCCIÓN DE ARRANQUE
**No empieces implementando el Bloque 5.**

Primero ejecuta el Checkpoint de Paridad S26.3R — Bloques 1–4.

Lee:
1. `PARITY_CHECKPOINT_B1_B4.md`
2. `RESULT_FORMATS.md`
3. `ROADMAP.md`
4. final de `EXECUTION_LOG.md`
5. `DESIGN_TARGET.md`
6. `KEYBOARD_CONTRACT.md`
7. `MATHEMATICAL_INTEGRITY_POLICY.md`

Estado:
- B1 PASS DEFINITIVO
- B2 PASS DEFINITIVO
- B3 PASS DEFINITIVO
- B4 PASS DEFINITIVO
- B5 pendiente y bloqueado hasta cerrar paridad B1–B4.

Clasifica diferencias como PARIDAD / DIFERENCIA INTENCIONAL / GAP.

Regla angular:
- grados → solo DD y DMS;
- DD usa °;
- DMS usa °, ′, ″;
- RAD conserva formatos normales.

Diferencias intencionales:
- Plus: SymPy/backend, Pasos, Resumen, warnings, Copiar, resultados estructurados.
- Lite: cálculo local y fallback numérico.

Después de corregir GAPs, recertifica si tocaste código y actualiza log/roadmap/checkpoint.

Luego iniciar B5: teclado global shell/open-close/responsive.
