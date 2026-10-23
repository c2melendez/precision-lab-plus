## 2026-10-23 UTC — r245: systemSplit re-entry fallido; baseline S19 restaurado

- [39896676447](https://github.com/c2melendez/precision-lab-plus/actions/runs/39896676447) SHA `889e942`: S25 SUCCESS; plus-frontend-stryker **FAILURE** score **14.36 %** (systemSplit 4.38 %, 7/151 killed).
- Decisión: no bajar `break: 15.3`. Restaurar mutate a fractionDisplay + unitConversion (PASS histórico 21.10 % en 39890525978). Tests systemSplit se conservan en el repo para trabajo futuro.
- Siguiente: revalidar gate en baseline; luego MV-D formal / MV-E.

---

## 2026-10-23 UTC — r244: S25 npm + S19 Plus frontend mutation PASS

- Gate [39890525978](https://github.com/c2melendez/precision-lab-plus/actions/runs/39890525978) SHA `720976e`: **SUCCESS** (todos los jobs).
- S25: frontend-audit 0 high/critical (overrides braces/@franciscosolis, postcss-selector-parser, fast-uri, js-yaml + lockfile heal); backend-security SUCCESS.
- S19 Plus Stryker: **score 21.10 %** ≥ break 15.3; mutate = fractionDisplay + unitConversion; coverageAnalysis all; 15 s. Artifact 12474657175.
- S19 backend mutmut + Lite Stryker harness: SUCCESS.
- Camino de remediación registrado: timeout 2627 mutantes → scope → perTest 3.65 % → all+focused 13.85 % (systemSplit 3.13 %) → drop systemSplit → 21.10 % PASS.
- SECURITY-S25 marcado CLEARED en continuidad; global sigue OPEN. Siguiente: reintroducir systemSplit con tests de mutación o cierre formal MV-D / MV-E.
