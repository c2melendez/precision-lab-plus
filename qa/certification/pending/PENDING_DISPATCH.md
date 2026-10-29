# Paquete técnico pendiente de despacho — Plus SY-X-04 fix

**Estado:** listo para publicación vía Certification Runner v3 (Lite, rama predeterminada `main`).
Este paquete es **técnico** (tests), por lo que el runner **no** lo publica (la operación `docs`
solo admite `qa/certification/**.md` y `continuity.json`). Debe publicarse con un push directo
a la rama canónica de Plus o mediante una extensión autorizada del runner.

## Insumos verificados (2026-10-29)

| Campo | Valor |
|---|---|
| Repositorio destino | `c2melendez/precision-lab-plus` |
| Rama canónica | `qa/syntax-audit-in625-a1` |
| `docs_expected_base_sha` (HEAD al preparar) | `f1fa2a49082593398e75fc1296e1650bca59b4c3` |
| Archivo | `0001-plus-SY-X-04-oracle-CORS-fix.patch` |
| SHA-256 | `eecb1d815b8bb1fe3f05b3eef763e4179d3e97e4c723b063f3f9c86f46fa2723` |
| Commit dentro del paquete | `68d148bd2a2aeb1ef53432c92c7eebdd7be649c0` (pre-push; el SHA final se conoce solo tras aplicar) |
| Rutas tocadas | `backend/tests/conftest.py` (nuevo), `backend/tests/test_sy_x04_http.py` |
| Aplicación | `git apply --check` limpio sobre HEAD real de GitHub (verificado en clon fresco) |
| Evidencia local | suite completa 2725 passed / 1 skipped / 10 xfailed (pre-fix: 3 failed) |

## Motivo (capas oráculo + harness; producto sin cambios)

1. ORÁCULO: `test_sy_x04_functional_subset_within_length_contract_yields_nx` asumía 200 términos
   → `200*x`, pero el contrato Etapa 9 s7 (`MAX_AST_NODES=200`) rechaza 200 términos con
   `COMPLEXITY_LIMIT` (verificado ejecutando el endpoint real: 199→`199*x`, 200→rechazo). Fix:
   subset funcional al máximo caso intra-contrato (199 términos) + test explícito del régimen
   `COMPLEXITY_LIMIT`. Ningún umbral de producto relajado.
2. HARNESS: fallos order-dependientes de CORS en suite completa (`test_s25_deployment_security`)
   por pinning de `CORS_ORIGINS` con `setdefault` por módulo; nuevo `conftest.py` establece la
   allow-list canónica antes de cualquier import.

Fallan hoy sobre este mismo insumo: CI run 40775454881 y acumulativo 40775454859 (SHA `1e4c5293`).

## Publicación — Opción A (recomendada): push autorizado

```bash
git clone --branch qa/syntax-audit-in625-a1 https://github.com/c2melendez/precision-lab-plus
cd precision-lab-plus
git checkout -q f1fa2a49082593398e75fc1296e1650bca59b4c3
git am /path/to/0001-plus-SY-X-04-oracle-CORS-fix.patch   # debe reportar 68d148bd…
# CAS: rechazar si origin ya no está en f1fa2a49
NEW=$(git rev-parse HEAD)
git push https://<token>@github.com/c2melendez/precision-lab-plus \
  "+$NEW:refs/heads/qa/syntax-audit-in625-a1" --force-with-lease=qa/syntax-audit-in625-a1:f1fa2a49082593398e75fc1296e1650bca59b4c3
```

El push activa automáticamente (filtros YAML verificados en HEAD):
- `ci.yml` (push a rama canónica; `paths-ignore` no excluye `backend/tests/**`; job backend usa
  `pytest -q --cov-fail-under=75` — cubre exactamente los pasos que fallaron en 40775454881).
- `in625-cumulative-certification.yml` (`paths: '**'` menos md/continuity.json).

## Publicación — Opción B: runner `gate` (sin publicar el fix aún — NO recomendada)

Dispatch en Lite `main`: operation=`gate`, target_repo=`plus`, gate=`cumulative`, dry_run=false.
Reutilizará/observará la evidencia del HEAD actual (rojo) y registrará el fallo; útil solo como
confirmación independiente del diagnóstico, no como cierre.

## Post-publicación (obligatorio, en orden)

1. Buscar runs de `ci.yml` y acumulativo en Plus con `head_sha == NEW`; esperar conclusión; revisar
   logs del job `backend` (pasos realmente ejecutados, tests omitidos).
2. Solo con ambos verdes: actualizar índices documentales —
   - Plus `continuity.json` r340: `SY-X-04-PLUS-HTTP = PASS_SCOPED` con run/job/log/huella del NEW;
     CURRENT_STATE/EXECUTION_LOG correspondientes.
   - Lite r328: nota documental espejo (S25-style traceability).
   Publicar esos commits `.md`/`continuity.json` vía runner v3 operación `docs` (un paquete por repo,
   `target_repo=plus` primero, luego `lite`; base = HEAD fresco en cada momento, CAS automático).
3. Si algún run queda rojo: clasificar capa, corregir, repetir. No restaurar `PASS_SCOPED` sobre
   `1e4c5293` bajo ninguna circunstancia.

## Aviso operativo

La rama canónica avanzó a `f1fa2a49…` después de `1e4c5293…` (commits documentales posteriores).
Si al intentar la publicación origin ≠ `f1fa2a49…`, volver a derivar el patch desde el HEAD fresco
(`git checkout <fresh>; git cherry-pick 68d148bd… || re-aplicar`) antes de despachar. Nunca forzar
sobre un HEAD desconocido.
