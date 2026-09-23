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


## Baseline backend certificado — corrida 35849315017

Runner observado:
- CPU: Intel(R) Xeon(R) 6973P-C, 4 vCPU.
- RAM total: 16,765,378,560 bytes (~15.6 GiB).
- Python: 3.12.14.
- RSS máximo del proceso backend: 90,726,400 bytes (~86.5 MiB).

Rutas cortas, 25 repeticiones:
- mediana: 2.326 ms.
- p95: 3.064 ms.
- máximo observado: 12.863 ms.

Centinelas:
- expresión soportada de 90 términos: 9.543 ms, success.
- expresión de 200 términos: 11.511 ms, COMPLEXITY_LIMIT por límite AST de 200 nodos.
- sumatoria 100,000: 2.298 ms, COMPLEXITY_LIMIT.
- productoria 100,000: 2.145 ms, COMPLEXITY_LIMIT.
- sumatoria 10,000: 37.926 ms, resultado 50,005,000.
- productoria 10,000 de unos: 2.625 ms, resultado 1.
- determinante 6x6: 15.328 ms.
- media de 200 valores: 14.111 ms.

Estos valores son baseline del runner, no SLA universal. La política posterior debe
comparar sobre runners equivalentes y evitar regresiones porcentuales sostenidas.
