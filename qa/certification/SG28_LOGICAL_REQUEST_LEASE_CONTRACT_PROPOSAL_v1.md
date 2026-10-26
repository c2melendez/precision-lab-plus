# SG28 — Contrato propuesto de vigencia de solicitud lógica, lease y fencing

**Versión:** 1.0  
**Estado:** `PROPOSED / REVIEW_REQUIRED`  
**Fecha:** 2026-10-24  
**Alcance:** diseño previo a integración HTTP; no autoriza despliegue, activar el flag experimental ni aceptar integración distribuida.

## 1. Unidad de admisión y presupuesto

La unidad de admisión es la solicitud lógica HTTP completa, no cada fase de cálculo/presentación por separado. El presupuesto total incluye admisión, transporte, cálculo, presentación, cancelación, recolección del hijo y liberación. Los límites actuales de cálculo (hasta 6 s) y presentación (hasta 4 s) no constituyen por sí solos un deadline total de 10 s.

El supervisor impone un deadline monotónico local, con margen explícito de limpieza. El coordinador entrega un lease que identifica solicitud, propietario, generación, deadline autoritativo y política de renovación. Los valores de plazos y márgenes requieren revisión; no se aumenta el TTL para ocultar la falta de fencing.

## 2. Renovación y fail-closed

Si la concesión no puede verificarse, la renovación vence o se pierde contacto con la autoridad, no se inicia ninguna fase nueva y no hay fallback local. El supervisor solicita cancelación y confirma la terminación/recolección de los hijos asociados antes de devolver capacidad.

La autoridad no concede una generación sucesora mientras la anterior pueda seguir ejecutándose, salvo que un mecanismo de fencing verificable impida que la generación anterior continúe consumiendo el recurso protegido. La concesión o liberación incierta se trata como no concedida/no liberada hasta reconciliar el estado.

## 3. Reloj, persistencia y reinicio

Los plazos de duración local se miden con reloj monotónico. La autoridad debe definir un dominio de reloj para deadlines persistidos, comportamiento ante saltos de reloj y reinicios. Un reinicio no puede borrar ni revivir leases por defecto. Los propietarios ambiguos permanecen sin capacidad hasta una reconciliación segura; se prefiere indisponibilidad temporal a solapamiento de trabajo.

## 4. Fencing de ejecución efectiva

Cada trabajo recibe un token no reutilizable `(request_id, owner_id, generation, deadline)`. El supervisor valida su vigencia antes de cada fase; el hijo coopera con deadline y cancelación; la liberación valida propietario y generación.

Una comprobación previa no basta frente a la suspensión de un proceso que pueda reanudarse después del vencimiento. Para afirmar K=1, la arquitectura debe demostrar que una generación antigua no puede continuar consumiendo el recurso protegido tras admitir una nueva. Si el entorno no garantiza esto, se requiere un worker/recurso con fencing efectivo o se mantiene el gate bloqueado. La expiración del registro no demuestra terminación.

## 5. Contrato HTTP/MathResponse

Fallo del coordinador, concesión incierta, deadline agotado o rechazo de admisión se traducen a códigos HTTP y `MathResponse` estables. La ruta experimental sigue deshabilitada por defecto y no usa fallback local ante errores de coordinación. Los logs correlacionan `request_id`, generación y código público sin exponer secretos, certificados ni tokens.

## 6. Topología y salida

SQLite/mTLS loopback es un prototipo de un host, no evidencia multinodo. Antes de cablear el endpoint se requiere revisión técnica que confirme: autoridad de lease/reloj; presupuesto y renovación; fencing frente a pausa/partición/reinicio; fail-closed y recuperación; mapeo HTTP/MathResponse; y una prueba K=1 en hosts independientes con logs correlacionados y evidencia reproducible.

**Decisión pendiente:** backend e infraestructura deben revisar este contrato contra `SG28_INTEGRATION_EXIT_CRITERIA.md`. Hasta entonces permanece `PROPOSED / REVIEW_REQUIRED`; `H2-SG28-DIST-01..08` continúa BLOCKED.
