> **AVISO: DOCUMENTO HISTÓRICO SUPERADO (2026-10-28 UTC).** El estado vigente es [BRIDGE_CERT_COMPASS_V1_1_STATUS_2026-10-28.md](BRIDGE_CERT_COMPASS_V1_1_STATUS_2026-10-28.md). Las anotaciones antiguas que muestran D1 como bloqueado o D4 pendiente fueron superadas por la revisión posterior. Los fragmentos de claves de acceso se sustituyeron por marcadores de redacción; no recuperar ni copiar valores del historial.

---

# Cert Runner Compass v1.1 — sesión de certificación (2026-10-27)

**Espejo documental** del informe en precision-lab-lite.  
**Estado del Bridge:** OPEN / **NO CERTIFICADO**.  
Detalle completo: ver el mismo path en Lite o la tabla de runs allí.

## Resumen

Fase 2 ejecutada con autorización del titular sobre **Lite** (`h1d`): B3–B6, C1–C3 OK; D2/D3/D5 OK; **D1 BLOCKED**; **D4 PENDIENTE**. Runs runner 40461232174 (B3), 40461306085 (B6), 40461473176 (C1) + gate 40461496350. Camino feliz demostrado; sin sello de certificación.

## Bloqueos residuales

D1 (lookup Idempotency-Key), `GET /api/run` con dispatch, D4 (rechazo GitHub controlado), rotación de claves, D-07 correlación.

**Prioridad canónica:** no reabrir Bridge como `next_action` automáticamente; motores / EN-SG según índice vigente.

---

## Addendum: origen de los runs extra (27 oct 2026, UTC)

Registrado el 28 de octubre de 2026 a partir de la revisión de GitHub y del registro del Bridge (solo lectura).

Runs del runner en Lite entre 06:27 y 06:51 UTC del 27 de octubre: **5** (límite: 3). Runs del gate: **1** (límite: 1).

| Run | Hora UTC | Origen verificado | Modo |
|---|---|---|---|
| 40461232174 | 06:27:38 | Bridge, B3 (clave activa `[valor omitido; clave expuesta]`) | dry_run |
| 40461306085 | 06:28:26 | Bridge, B6 (misma clave) | dry_run |
| 40461473176 | 06:30:08 | Bridge, C1 (misma clave); lanzó el gate `40461496350` | dry_run=false |
| 40463419492 | 06:49:43 | Bridge, POST de 06:49:44 con `correlation_id` `cert-20261027-probe-only` (misma clave) | dry_run |
| 40463536599 | 06:50:54 | Sin registro en el Bridge | dry_run |

**Conclusiones**

- Cuatro de los cinco runs pasaron por el Bridge con la clave activa `[valor omitido; clave expuesta]`. Esa clave es compartida y el Bridge no identifica la sesión que la usó.
- El run 40463419492 excede el presupuesto. Lo originó una llamada etiquetada `probe-only`, que no estaba en el plan de pruebas documentado.
- El run 40463536599 no tiene registro en el Bridge. La única identidad visible es la cuenta `c2melendez`, que también usa el Bridge, así que no se atribuye a ninguna sesión concreta.
- El archivo de sesión `ses_e8024a7ceffeqltmqqjs51hw3z.json` se creó el 28 de octubre a las 00:14 UTC, después de ambos runs, y no menciona sus IDs. No los originó.
- Los runs dry-run no generan costo en repositorios públicos, pero cuentan contra el presupuesto. El presupuesto del 27 de octubre quedó excedido en dos runs del runner.
- Los GET a `/api/run` registrados entre 20:19 y 20:54 UTC fueron rechazados con 401 y no dispararon runs.
- Hubo un 401 a las 06:49:33 UTC con una clave que empieza por `cert-20261…`, usada como `X-Bridge-Key`. Una sesión confundió la Idempotency-Key con la clave de acceso.

**Acciones pendientes**

1. Revocar y rotar `[valor omitido; clave expuesta]`.
2. Asignar una clave por sesión y registrar la sesión en `correlation_id`.
3. No dar por eliminado el límite de presupuesto sin una autorización escrita con fecha y nuevo límite.
