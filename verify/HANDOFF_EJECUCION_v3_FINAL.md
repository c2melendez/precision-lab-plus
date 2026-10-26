# HANDOFF DE EJECUCIÓN — Instalación verificada Certification Runner v3 (Lite + Plus)

**Fecha:** 27 de octubre de 2026 · **Sesión sin credenciales GitHub** (verificación solo por API pública).
**Certificación global:** OPEN. Este documento NO declara gates aprobados; registra evidencia verificada y la próxima acción autorizada única.

## 1. Qué se verificó en vivo (todos los datos son de api.github.com, no asumidos)

### Runner v3 (contenido canónico)
- Blob `23e42cf6dad30b281036cbbb63eff938c6646fde` = `.github/workflows/certification-runner.yml` versión v3.
- SHA-256 del contenido: `c85eb1d4b89606a51904ec792c7ca8bb141dd9ee9ca0f15b1d0eddc82815e0d7` (coincide con la huella anotada en el handoff previo).
- Validaciones locales del archivo obtenido: YAML parsea; 16 pasos; 5 heredocs Python compilan (`compile()` OK); 15 bloques `run:` pasan `bash -n`; inputs `workflow_dispatch`: operation(gate|docs), target_repo, gate, dry_run, docs_patch_url, docs_patch_sha256, docs_expected_base_sha, docs_patch_hosts. Operación docs presente (format-patch + CAS). No contiene marcadores `[skip ci]`.
- Copia local idéntica confirmada: `/workspace/.github/workflows/certification-runner.yml` (commit c701df7) → mismo sha256.

### Dónde está instalado v3 vs. dónde queda v2 (inconsistencia detectada)
| Repo | Rama | HEAD actual | Blob runner | Versión |
|---|---|---|---|---|
| Lite | main | `4507082a101fbc5a196cfbfe335db6e83c2cb6d0` | `bcaef28a…` | **v2** |
| Lite | qa/syntax-audit-in625-a1 (canónica) | `0a3137670d51d85644066a24acc46b88af3d9103` | `5863f93e…` | **v2** |
| Plus | main | `5b9c31bc959e241c13985952592a7ade831ae093` | `bcaef28a…` | **v2** |
| Plus | qa/syntax-audit-in625-a1 (canónica) | `cb0cea5d1f97bb6c5523cdf7cdaba9d448c5cd72` | `169066f6…` | **v2** |
| Lite | rama PR #54 `workflow-certification-runner-installation-6d470` | head `c26a88536551fa256113ba7da3d9f872fea189f9` (base main `11806ba5…`) | `23e42cf6…` | **v3** ✔ |
| Plus | rama PR #33 `ci/runner-v3-docs` | head `c701df748d9c8834c7e09ac1073c2afbaf419725` (base `903e44ac…`) | `23e42cf6…` | **v3** ✔ (también replica en `lite/.github/…`, ver §4) |

Conclusión: **v3 aún NO está integrado en ninguna rama permanente de Lite/Plus.** Los merges citados en sesiones previas ("PR #55/#32 integrados") corresponden a un estado anterior o a ramas que luego avanzaron; hoy main y la rama canónica de ambos repos tienen v2. No repetir gates "porque sí": la corrección pendiente es de integración, no de ejecución.

### Continuity.json (rama canónica)
- Lite rev **301**, blob `f52253ab92cc7624165fb62b75a514878d98b8fa`; Plus rev **314**, blob `32a5ca8ca10311ad93602eb3cd91dfaae9c62bf1`.
- Ninguno contiene `docs_workflows` (campo requerido por v3). Esto bloquea cualquier operación `docs` real sobre las ramas canónicas hasta publicarlo.
- `prose_only_paths` presentes en ambos; Lite excluye `qa/certification/continuity.json` del fingerprint técnico, Plus lo incluye (ambos con `runner/**` fuera vía paths-ignore; coherente con fin del bucle RECONCILE por registros).

### PRs abiertos relevantes (comprobado hoy)
- Lite: **#54** (instalar v3, mergeable=True, state unstable), #53, #51, #49–#45 etc. muchos antiguos hacia main.
- Plus: **#36** (H2 EN-SG fixes, base canónica), **#35** (auditoría evidencia H2, base canónica), **#34** (repair/runner-policy, base canónica), **#33** (instalar v3, base main, mergeable=True).

## 2. Correcciones preparadas (artefactos listos para publicar)

Generados desde los blobs reales de la rama canónica (no reescritos a mano):
- `lite-continuity-new.json` — Lite rev 301 + clave `docs_workflows` (entradas main y canónica con blob/sha256/historial PR) + nota en `next_action`. SHA-256: `5e10cb565313ea2248ad0c6cfcbcbb540e413426108bff0aba16cee5e0a4cb48` (123404 bytes).
- `plus-continuity-new.json` — idem sobre rev 314. SHA-256: `2efd24f084a68a2f055632424f0e0c83296b314c66fab86223dd6bbe83cccd84` (159331 bytes).

Ambos conservan todo el historial existente; solo añaden `docs_workflows` y anotan `next_action`. Son inputs documentales permitidos por la política docs de v3 (`qa/certification/continuity.json`).

## 3. Orden de ejecución recomendado (una sola pasada, sin duplicar Actions)

1. **Plus #36** → verificar runs finales por SHA (40381076250 cumulative / 40381076420 Playwright al HEAD final del PR) y mergear a la canónica.
2. **Plus #34** → rebase contra la canónica post-#36 (resuelve conflicto en continuity.json adoptando el registro generado tras #36) y mergear; cerrar como redundante si #33+pasos 3–4 cubren su alcance.
3. **Lite #54 y Plus #33** → mergear (instalan v3 en main de ambos). Antes de mergear #54: limpiar la rama (12.820 archivos/+2,57 M líneas: `node_modules/`, `dist/`, `work/` basura de sesión) dejando solo `.github/workflows/certification-runner.yml` (blob 23e42cf) y `HANDOFF_EJECUCION_v3_FINAL.md`. Alternativa limpia: recrear rama desde main con ese único archivo.
4. **Publicar continuity corregido** usando el propio runner v3 ya integrado: dispatch `operation=docs, target_repo=lite` y luego `plus`, con patch URL (raw de la rama o gist) apuntando a los dos JSON de §2, `docs_patch_sha256` = huellas de §2, `docs_expected_base_sha` = HEAD canónico del momento (Lite `0a313767…`+post-merge; Plus `cb0cea5d…`+post-#36). Primero `dry_run=true`, luego `dry_run=false`. Esto activa fingerprint/gates por diseño (sin `[skip ci]`), y `paths-ignore` evita bucles del runner sobre sí mismo.
5. Solo entonces: `GET /v1/status?repo=both` en Render debe dejar de advertir runner desactualizado; decidir gate técnico únicamente si el planificador responde RUN y no existe run verde del mismo workflow+SHA+inputs.

## 4. Advertencias honestas

- El árbol de PR #33 coloca además `lite/.github/workflows/certification-runner.yml` (misma huella v3) dentro del repo Plus: ruta muerta/confusa que podría confundir a planners externos. Recomendar quitarla antes del merge o documentarla como intencional.
- Las sesiones previas afirmaron merges de runner v3 ya integrados; el estado vivo de hoy lo contradice (main/canónica = v2). Registrar aquí qué quedó sin validación: ningún run actual valida v3 en ramas permanentes porque todavía no existe en ellas.
- Esta sesión **no despachó gates ni creó PRs** (sin credenciales). Nada de esto cambia revisiones de continuity ni fingerprints hasta ejecutar §3.

## 5. Siguiente paso único

Ejecutar §3 paso 1 (verificar runs del HEAD final de Plus #36 y mergear), con credenciales, respetando el protocolo anti-duplicación. Certificación global permanece OPEN.
