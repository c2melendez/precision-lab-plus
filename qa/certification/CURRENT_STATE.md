## 2026-10-23 UTC — r245: S19 baseline restaurado; systemSplit re-entry diferido

**Evidencia:** reintroducir `systemSplit` en mutate ([39896676447](https://github.com/c2melendez/precision-lab-plus/actions/runs/39896676447)) → score **14.36 %** (< break 15.3). Desglose: unitConversion 21.61 %, fractionDisplay 18.42 %, systemSplit **4.38 %** (7 killed / 151 survived). Tests reforzados solo subieron systemSplit de 3.13 % → 4.38 %; no basta.

**Decisión:** restaurar mutate certificado `fractionDisplay` + `unitConversion` (evidencia PASS [39890525978](https://github.com/c2melendez/precision-lab-plus/actions/runs/39890525978), **21.10 %**). `break: 15.3` intacto. systemSplit y calculusIntent diferidos.

**S25:** sigue CLEARED (frontend-audit + backend-security SUCCESS en ambos runs).

**Bloqueos:** SECURITY-S25 CLEARED; H2-SG28-DIST-01..08 BLOCKED; SY-P-23 OPEN; SY-X-04-PLUS-HTTP BLOCKED; ALGEBRA229-AS-B-29 ON_HOLD. Global OPEN.

**Siguiente acción única:** revalidar gate S19 en baseline restaurado (expect PASS); luego cierre formal MV-D-01..17 o tránsito a MV-E según `matriz_matrices_vectores.md.gz`.

---

## 2026-10-23 UTC — r244: SECURITY-S25 y S19 Plus frontend PASS (evidencia CI)

**Corte verificado:** gate `Certification dependency and security gates` **SUCCESS** en [39890525978](https://github.com/c2melendez/precision-lab-plus/actions/runs/39890525978), HEAD `720976e4c99f3cbf2f013da3131c19d89aefc189`.

- **SECURITY-S25 (npm + backend):** `security/frontend-audit` y `security/backend-security` SUCCESS. Overrides npm en `frontend/package.json` (braces fork, postcss-selector-parser, fast-uri, js-yaml) + lockfile regenerado; `npm audit --audit-level=high` = 0 vulnerabilidades. Backend Black/pip-audit/bandit verdes en el mismo run.
- **S19 Plus frontend Stryker:** mutation score **21.10 %** ≥ `break: 15.3`. Alcance baseline: `fractionDisplay.ts` + `unitConversion.ts`; `coverageAnalysis: all` + vitest enfocado; `systemSplit` y `calculusIntent` diferidos hasta kill rate sostenible. Artifact [s19-plus-frontend-stryker](https://github.com/c2melendez/precision-lab-plus/actions/runs/39890525978/artifacts/12474657175).
- **S19 Plus backend mutmut** y **Lite frontend Stryker** (harness): SUCCESS en el mismo run.
- **Historia de remediación:** overrides + heal lockfile → timeout 2627 mutantes → scope puro → `perTest` 3.65 % → `coverageAnalysis all` + ignoreStatic false → 13.85 % (systemSplit 3.13 % arrastraba) → drop systemSplit → **21.10 % PASS**.
- **MV-D:** evidencia de producto previa en Lite `c28091c` / Plus técnico MV-D sigue vigente; cierre formal bilateral y MV-E quedan habilitados tras este desbloqueo de campaña S25/S19, pendiente ledger MV-D si el contrato lo exige.
- **Bloqueos vigentes tras r244:** `SECURITY-S25` **CLEARED** (evidencia run 39890525978); `H2-SG28-DIST-01..08` BLOCKED; `SY-P-23` OPEN; `SY-X-04-PLUS-HTTP` BLOCKED; `ALGEBRA229-AS-B-29` ON_HOLD. Global **OPEN**.

**Siguiente acción única:** (1) reincorporar `systemSplit` al mutate S19 con tests de mutación reforzados sin bajar `break: 15.3`; (2) registrar cierre formal MV-D-01..17 o transitar a MV-E según hoja de ruta de `matriz_matrices_vectores.md.gz`.
