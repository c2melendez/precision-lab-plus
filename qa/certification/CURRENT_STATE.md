## 2026-10-23 UTC — r246: MV-D-01..17 cerrado formalmente (PASS_SCOPED_BILATERAL)

**MV-D-01..17 (sistemas, rref, LU, Gram-Schmidt sin normalizar) — PASS_SCOPED_BILATERAL.**

Criterio de salida de campaña S25/S19 satisfecho; se registra el cierre formal diferido desde r239.

### Evidencia de producto (SHA técnico MV-D, attempt=1, success)

| Repo | SHA técnico | Gates |
|------|-------------|-------|
| Lite | `c28091c0173f951a2571ffcbb6084f566ced0034` | cumulative [39754424771](https://github.com/c2melendez/precision-lab-lite/actions/runs/39754424771), h1d [39754424829](https://github.com/c2melendez/precision-lab-lite/actions/runs/39754424829), scientific-ui [39754424596](https://github.com/c2melendez/precision-lab-lite/actions/runs/39754424596) |
| Plus | `91d7f7b499e1effaeef7c4a3bd9e04c0b3b6d6f5` | cumulative [39754425445](https://github.com/c2melendez/precision-lab-plus/actions/runs/39754425445), backend-isolation [39754425427](https://github.com/c2melendez/precision-lab-plus/actions/runs/39754425427), h1d [39754425636](https://github.com/c2melendez/precision-lab-plus/actions/runs/39754425636), native-syntax [39754425572](https://github.com/c2melendez/precision-lab-plus/actions/runs/39754425572), SG28 UI [39754425501](https://github.com/c2melendez/precision-lab-plus/actions/runs/39754425501) |

Suites de auditoría permanentes: Lite `tests/matricesMvD01to17.audit.test.ts`; Plus `backend/tests/test_matrices_mv_d01_l17.py` (17 filas + meta JSONL/fuente congelada; sistemas vía `/solve/system`; rref D-14/15; LU D-16 + rechazo de pivote; Gram-Schmidt D-17 ortogonal sin normalizar). Anclaje a `matriz_matrices_vectores.md.gz` / `matrices_ejecutables.jsonl` sección D.

### Evidencia de campaña (post r244–r245)

| Gate | Run | Resultado |
|------|-----|-----------|
| S25 + S19 baseline | [39890525978](https://github.com/c2melendez/precision-lab-plus/actions/runs/39890525978) | SUCCESS; Stryker **21.10 %** ≥ 15.3 |
| S19 baseline restaurado | [39899659414](https://github.com/c2melendez/precision-lab-plus/actions/runs/39899659414) | SUCCESS (mutate fractionDisplay+unitConversion) |
| systemSplit re-entry | [39896676447](https://github.com/c2melendez/precision-lab-plus/actions/runs/39896676447) | 14.36 % — diferido (4.38 % en systemSplit) |

**SECURITY-S25: CLEARED.** S19 frontend: PASS en alcance certificado. Global **OPEN**.

**Bloqueos restantes:** H2-SG28-DIST-01..08 BLOCKED; SY-P-23 OPEN; SY-X-04-PLUS-HTTP BLOCKED; ALGEBRA229-AS-B-29 ON_HOLD.

**Siguiente acción única:** iniciar **MV-E** (siguiente sección de `matriz_matrices_vectores.md.gz`) — ampliar JSONL/ejecutor y tests de auditoría; no reabrir MV-A..D salvo regresión.

---

## 2026-10-23 UTC — r245: S19 baseline restaurado; systemSplit re-entry diferido

**Evidencia:** reintroducir `systemSplit` en mutate ([39896676447](https://github.com/c2melendez/precision-lab-plus/actions/runs/39896676447)) → score **14.36 %** (< break 15.3). Desglose: unitConversion 21.61 %, fractionDisplay 18.42 %, systemSplit **4.38 %** (7 killed / 151 survived).

**Decisión:** restaurar mutate certificado `fractionDisplay` + `unitConversion` (PASS [39890525978](https://github.com/c2melendez/precision-lab-plus/actions/runs/39890525978) / [39899659414](https://github.com/c2melendez/precision-lab-plus/actions/runs/39899659414), **21.10 %**). `break: 15.3` intacto.
