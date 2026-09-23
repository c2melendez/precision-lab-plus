# S25 — Seguridad de cadena de suministro y despliegue

Política del gate:
- npm audit: high/critical bloquean; moderate se reporta.
- pip-audit: cualquier vulnerabilidad reportada en dependencias runtime bloquea.
- Bandit: hallazgos medium/high con confianza medium/high bloquean.
- CORS debe preservarse en respuestas exitosas y de error controlado.
- API aplica X-Content-Type-Options: nosniff, Referrer-Policy: strict-origin-when-cross-origin y X-Frame-Options: DENY.
- API no-documentación aplica CSP restrictiva: default-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'.
- Swagger/ReDoc/OpenAPI se excluyen de esa CSP para no romper sus assets.

Caso centinela:
- sec(pi/2) nunca debe escapar como HTTP 500.
