# Compass — revisión de acceso y plan de remediación

Corte: 2026-10-29 UTC. **Solo propuesta; no aplicada.**

La inspección de catálogo encontró acceso amplio de los roles de cliente sobre tres tablas internas del Bridge. El rol de servicio usado por los handlers de servidor tiene sus permisos. La protección por fila está activada, pero no se observaron políticas, y esa protección no sustituye una lista de permisos de tabla mínima.

Plan sujeto a revisión:
1. Confirmar que ningún cliente de navegador necesita consultar directamente las tablas internas; los handlers revisados usan el cliente de servicio en servidor.
2. En una migración revisada, retirar permisos de cliente innecesarios de las cuatro tablas internas, conservar el acceso requerido del rol de servicio y mantener la protección por fila habilitada.
3. Examinar por separado los permisos que se aplican automáticamente a objetos nuevos; su alcance incluye el esquema público completo y no debe cambiarse sin inventariar otros consumidores.
4. Confirmar con el propietario de la plataforma la finalidad del rol de ejecución interno adicional, que aparece con inicio de sesión y bypass de la protección por fila. No cambiarlo hasta conocer su función.
5. Después de la aprobación, validar permisos de lectura y escritura para roles de cliente y servicio, las rutas del Bridge y el estado de las políticas. No generar ejecuciones de Actions durante estas pruebas.

Bloqueo de lookup: las tres solicitudes antiguas citadas en CURRENT_STATE pertenecen a una clave ya revocada. La clave activa actual pertenece a otro propietario y no debe usarse para eludir el aislamiento. No se modificará la propiedad de las solicitudes ni se restablecerá la clave sin autorización explícita. Hace falta una vía de recuperación de estado autenticada y auditable.

Procedencia: el proveedor marca el proyecto como publicado y la última revisión fuente como `b0442cca4f1c47f2f4d71d02ded75b63fc539428`. La sesión anterior informa un SHA local distinto y una lectura en vivo, pero el proveedor no ofrece un SHA independiente del artefacto desplegado. La conexión entre el último origen y el artefacto publicado sigue pendiente de verificación independiente.

No se han cambiado datos, permisos, políticas ni despliegue. Compass sigue OPEN / NO CERTIFICADO.

## Criterios explícitos de salida de Compass P0 (revisión 2026-10-29)

**Resultado de esta revisión: NO CUMPLIDOS — P0 permanece WAIT.** La revisión fue de solo lectura. No se realizaron POST, dispatches, DDL, cambios de grants/policies, rotación de claves ni cambios de despliegue.

| ID | Criterio verificable de salida | Evidencia observada | Estado |
|---|---|---|---|
| P0-A | Recuperar los tres registros históricos exclusivamente mediante una ruta autenticada, auditable y autorizada por el propietario original; conservar el control de propiedad y no repetir workflows. | Los registros vinculados a 40461232174, 40461306085 y 40463419492 están bloqueados para lookup de propietario porque la credencial asociada figura revocada. La clave activa observada pertenece a otro propietario. | BLOCKED_AUTH |
| P0-B | Obtener decisión aprobada sobre el plan de mínimo privilegio antes de cambiar permisos; después validar grants efectivos de las cuatro tablas Bridge para roles cliente y servicio. | La revisión previa registró RLS habilitado y ausencia de policies devueltas; `anon`/`authenticated` conservan grants amplios sobre `bridge_calls`, `bridge_keys` y `bridge_runs`. No se ha aprobado ni aplicado migración; no se ejecutó una prueba directa de acceso a tablas. | REVIEW_REQUIRED |
| P0-C | Atribuir el rol interno adicional con login y bypass de RLS y confirmar su necesidad/alcance con el propietario de la plataforma antes de modificarlo. | El rol está señalado en la revisión previa, pero su finalidad no está confirmada. | BLOCKED_OWNER_CONFIRMATION |
| P0-D | Confirmar que las tablas internas no requieren acceso directo desde el navegador y que las rutas públicas usan handlers del servidor con autenticación adecuada. | En el SHA fuente de Lovable `3ac765f1d133cc2a02b66664d55612e38d847161`, las rutas de lookup/estado importan módulos `.server`; `GET /api/runs/lookup` requiere `X-Bridge-Key` e `Idempotency-Key`; `GET /api/run` responde 405. Esto es inspección de código, no prueba dinámica de permisos ni inventario completo de consumidores. | PARTIAL |
| P0-E | Conciliar procedencia del despliegue: demostrar con evidencia independiente qué SHA de fuente corresponde al artefacto publicado, sin equiparar referencias históricas distintas. | Lovable informa latest source commit `b0442cca4f1c47f2f4d71d02ded75b63fc539428` en el registro previo y el acceso actual informa latest commit `3ac765f1d133cc2a02b66664d55612e38d847161`; no se dispone de SHA independiente del artefacto live. | BLOCKED_PROVENANCE |
| P0-F | Mantener la recuperación sin nuevas ejecuciones: no usar `GET /api/run`, no reenviar `POST /api/runs`, no cambiar hashes/propietarios de claves y no repetir B3/B6 para reparar el ledger. | La ruta `GET /api/run` devuelve 405 en el SHA inspeccionado. No se enviaron solicitudes ni workflows en esta revisión. | PASS_SCOPED (control de esta revisión) |

### Regla de salida

P0 solo puede pasar de `WAIT` cuando P0-A, P0-B y P0-C tengan resolución aprobada y evidencia verificable; P0-D debe quedar confirmado mediante revisión completa de consumidores/rutas; P0-E debe resolverse o recibir una excepción formal y acotada del responsable con aceptación explícita del riesgo. P0-F debe mantenerse como restricción operativa durante la remediación. Una propuesta escrita no equivale a aprobación, y un cambio de grants requiere migración revisada y validación posterior.

**Separación de alcance:** superar esta revisión P0 únicamente habilita reconsiderar el siguiente paso del protocolo. No certifica Compass v1.1 ni cierra D1–D7/E2/E3, no corrige automáticamente registros históricos y no cambia la certificación global `OPEN / NO CERTIFICADO`.

### Acciones pendientes que requieren autorización del propietario

1. Designar una recuperación autenticada y auditable para los tres registros, respetando la propiedad original; no reutilizar una clave ajena.
2. Aprobar (o rechazar motivadamente) una migración de mínimo privilegio y su plan de validación/rollback.
3. Identificar el rol con bypass de RLS y decidir su tratamiento.
4. Aportar evidencia del proveedor que vincule fuente y artefacto desplegado, o aceptar formalmente la limitación de procedencia.
