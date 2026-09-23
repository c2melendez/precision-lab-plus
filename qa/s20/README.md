# S20 — Rendimiento y robustez

Fuente normativa: Suite exhaustiva v2.0, Fase 15.

Esta fase mide y limita:
- p50/p95 de evaluación normal;
- expresiones grandes;
- sumatorias/productorias de alta cardinalidad;
- matrices y estadística en sus límites soportados;
- memoria/lifecycle del worker de Lite;
- cancelación/interrupción;
- recuperación después de timeout/cancelación.

## Política del primer baseline

La primera ejecución en GitHub Actions registra CPU/RAM, SHAs y métricas reales.
No se inventa un umbral porcentual inicial. Los únicos límites duros del primer
run son anti-hang/timeout y los contratos ya existentes del producto.

Tras obtener el primer baseline estable, este archivo se actualizará con los
p50/p95 y memoria observados y se fijará la política porcentual de no-regresión.

## Centinelas

- Plus: `sum(i,i,1,100000)` y `product(i,i,1,100000)` deben responder
  `COMPLEXITY_LIMIT` dentro del presupuesto duro.
- Lite: `sum(...,100000)` debe rechazarse antes de entrar a Algebrite.
- Lite: abandonar un modo termina su worker; volver a Científica debe crear
  un worker nuevo y un cálculo posterior debe completar.
- Plus frontend: una solicitud que excede 15 s debe abortarse y la llamada
  siguiente debe funcionar.

## Evidencia

Los JSON de métricas y reportes Playwright se suben como artefactos del
workflow `S20 Performance Robustness`.
