# SG28 — revisión técnica del contrato propuesto (r287)

**Estado:** `REVIEW_REQUIRED`; no constituye aprobación de backend/infraestructura.  
**Alcance:** contraste documental de `SG28_LOGICAL_REQUEST_LEASE_CONTRACT_PROPOSAL_v1.md` contra `SG28_INTEGRATION_EXIT_CRITERIA.md`. Sin cambios de producto, sin activar flags, sin corridas nuevas.

## Resultado ejecutivo

La propuesta cubre los seis temas obligatorios, pero **todavía no los resuelve como decisiones implementables**. El endpoint no debe cablearse. El bloqueo no es solo la disponibilidad de dos hosts: la exclusión efectiva del trabajo viejo y el protocolo de recuperación siguen sin estar definidos.

| Decisión exigida | Evaluación actual | Qué falta para aprobar |
|---|---|---|
| Presupuesto lógico total | Parcial | Definir deadline absoluto de la solicitud, subpresupuestos y reserva de cleanup; explicar cómo se aplican los límites de cálculo (6 s) y presentación (4 s) sin sumar 10 s y omitir admisión/red/limpieza. |
| Renovación/ACK perdido | Parcial | Definir mensaje de renovación, idempotencia, identificador de operación, vencimiento de respuesta y qué hace cliente/autoridad si se pierde el ACK de grant, renew o release. |
| Autoridad de reloj/reinicio | Parcial | Separar reloj monotónico de ejecución del reloj de persistencia del coordinador; especificar reinicio, salto de reloj, restauración de backup y leases cuyo propietario no puede confirmarse. |
| Fencing del trabajo real | No resuelto | El token y la validación antes de fase no detienen a un proceso suspendido que reanuda. Especificar mecanismo de terminación supervisada y condición para no conceder sucesor mientras el proceso viejo pueda consumir CPU/memoria/recurso protegido. |
| HTTP/MathResponse | Parcial | Tabla normativa de status/código/cuerpo para rechazo de cuota, coordinador no disponible, grant incierto y deadline; preservar el contrato público existente y evitar fallback local. |
| Evidencia distribuida | Parcial | Separar prueba local de integración y DIST-01..08; fijar dos o más hosts independientes, IDs correlacionados, pruebas de partición/suspensión/reinicio y evidencia ligada a SHA. |

## Recomendaciones de diseño para la revisión

Estas recomendaciones son propuestas para que backend e infraestructura las acepten o rechacen explícitamente; no son decisiones ya aprobadas.

1. **Una sola admisión por solicitud lógica.** El mismo `request_id` y generación cubren admisión, cálculo, presentación y cleanup. No adquirir un segundo lease para la fase de presentación.
2. **Deadline de solicitud distinto del TTL del registro.** El supervisor calcula su deadline local con reloj monotónico. La autoridad persiste estado duradero y aplica una política de reloj documentada. Un TTL vencido, por sí solo, no permite reutilizar la cuota.
3. **Fail-closed en incertidumbre.** Si el cliente no sabe si una operación fue aceptada, no reintentar con una identidad nueva ni ejecutar localmente. Consultar el estado idempotente con el mismo identificador; si no puede reconciliarse, rechazar la solicitud.
4. **Renewal no reemplaza fencing.** Si se adopta renovación, establecer una regla explícita de cuándo deja de admitirse trabajo nuevo y cuándo se ordena terminar el hijo. No conceder generación sucesora solo porque venció el timestamp.
5. **Regla de exclusión antes de sucesor.** Para CPU local, el coordinador debe tener evidencia de que el worker anterior terminó y fue recolectado; ante host inaccesible, conservar la cuota como incierta/bloqueada antes que afirmar K=1. Si se necesita recuperación automática, el equipo debe demostrar un mecanismo de fencing que realmente impida al worker anterior consumir el recurso.
6. **Códigos públicos estables.** Mantener separados error de entrada matemática, rechazo de admisión, indisponibilidad/estado incierto del coordinador y deadline. No exponer detalles de mTLS ni del backend de coordinación.
7. **Pruebas en escalones.** Primero unitarias del protocolo; luego integración HTTP de un host con fail-closed/cleanup; solo después hosts independientes para DIST. Un test de SQLite loopback no puede certificar K=1 multinodo.

## Criterio de salida documental

Antes de implementar, el responsable debe aprobar una versión del contrato que incluya:
- ecuación y valores explícitos de presupuesto total/subpresupuestos;
- máquina de estados de grant/renew/release con comportamiento ante ACK perdido;
- autoridad de reloj y recuperación tras reinicio;
- punto exacto de fencing del proceso hijo y regla de concesión sucesora;
- tabla HTTP/MathResponse;
- topología y pruebas requeridas, con límites de cada afirmación.

Hasta entonces: `H2-SG28-DIST-01..08 = BLOCKED`; `SY-X-04-PLUS-HTTP = BLOCKED`; global certification `OPEN`; PR #29 permanece abierto. No lanzar suites por este documento.
