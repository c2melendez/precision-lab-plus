# Algebra229 AS-B-30 — aceptación scoped bilateral (Plus)

**Resultado: PASS_SCOPED bilateral.** La certificación global continúa **OPEN**.

## Contrato y oráculos
- AS-B-30, N3, `valor`: `\text{¿es primo }1000000007?` → `sí, es primo`.
- Plus: `backend/tests/test_algebra229_as_b30.py`, 3/3 tests: ocho celdas exactas de la fila congelada; `POST /api/v1/evaluate` real con `result_text` exacto y `result_type=boolean`; oráculo independiente por división de prueba que confirma 1000000007 primo y rechaza el control compuesto 1000000008 con `no, es compuesto`.
- Lite (par bilateral): `tests/algebra229AsB30.audit.test.ts`, 4/4 tests: fila congelada; respuesta exacta de la pregunta; oráculo independiente por división de prueba y control compuesto; casos límite `primo(2)` y `primo(1)`.

## Implementación
- Plus: `backend/app/services/primality.py` reconoce solo la forma LaTeX congelada y la forma funcional `primo(n)`/`esprimo(n)`; responde con Miller-Rabin determinista de 64 bits (testigos 2..37, exacto para todo `n <= 2^64-1`). `evaluate_service` devuelve `text_result` y el router serializa `ResultType.BOOLEAN` sin pasar por `simplify()`.
- Lite: `src/engine/primality.ts` implementa la misma capacidad con `BigInt` y los mismos testigos; `evaluate()` la invoca antes del motor simbólico para las dos formas exactas.
- Alcance declarado: es una capacidad acotada de primalidad, no un intérprete general de lenguaje natural. El resto de entradas sigue el parser normal.

## Evidencia Plus — SHA `a831d31d5bc13193e470949eb8efb06cc4527533`
- Cumulative [42329897688](https://github.com/c2melendez/precision-lab-plus/actions/runs/42329897688) SUCCESS; backend y frontend SUCCESS; focal B30 3/3 PASS; guard `skip=false`, `evidence_run_id` vacío.
- CI [42329897714](https://github.com/c2melendez/precision-lab-plus/actions/runs/42329897714) SUCCESS; 2,811 passed, 1 skipped, 10 xfailed; cobertura 88.89%; frontend 1,055 passed.
- H1d [42329897684](https://github.com/c2melendez/precision-lab-plus/actions/runs/42329897684) SUCCESS; 38/38 Playwright; guard `skip=false`.
- Runner [42329897649](https://github.com/c2melendez/precision-lab-plus/actions/runs/42329897649) SUCCESS.
- Evidencia adicional del mismo SHA: Native Syntax [42329897759](https://github.com/c2melendez/precision-lab-plus/actions/runs/42329897759), SG28 Backend Isolation [42329897990](https://github.com/c2melendez/precision-lab-plus/actions/runs/42329897990) y SG28 UI Cancellation [42329898027](https://github.com/c2melendez/precision-lab-plus/actions/runs/42329898027) SUCCESS.

## Evidencia Lite (par bilateral) — SHA `99bbc9bc17b79d00c45299415b5f9d63a9d09c36`
- Cumulative [42329909267](https://github.com/c2melendez/precision-lab-lite/actions/runs/42329909267) SUCCESS; focal B30 4/4; 367 archivos, 2,271 passed, 8 expected fail, 34 TODO; guard `skip=false`.
- H1d [42329909190](https://github.com/c2melendez/precision-lab-lite/actions/runs/42329909190) SUCCESS; 22/22 Playwright.
- Scientific UI [42329909206](https://github.com/c2melendez/precision-lab-lite/actions/runs/42329909206) SUCCESS; 456/456 desktop/tablet/mobile.
- CI [42329909188](https://github.com/c2melendez/precision-lab-lite/actions/runs/42329909188) SUCCESS.
- Runner [42329909192](https://github.com/c2melendez/precision-lab-lite/actions/runs/42329909192) SUCCESS.

## Diagnóstico y clasificación
- Antes del cambio, `POST /api/v1/evaluate` con la entrada congelada devolvía `PARSE_ERROR`: gap real de **capability**, no fallo de harness ni de oráculo.
- Se corrigió la capa de producto (parser acotado + primalidad determinista) y se añadieron regresiones permanentes en ambos repositorios. No se relajó ningún oráculo matemático.
- El gate de seguridad `Certification dependency and security gates` sigue siendo un frente independiente (S25) y no se usa como evidencia de este bloque. SG28/H2/DIST permanece abierto. Global **OPEN**.

Siguiente: AS-C-01, N1, `simplificar` — `\frac{x^{2}-1}{x-1}` → `x + 1`, válido para `x \neq 1`. Test-first bilateral con fila congelada, simplificación exacta, equivalencia simbólica fuera del punto excluido y control de dominio en `x=1`.
