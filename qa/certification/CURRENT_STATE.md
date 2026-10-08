# Current Certification State

Actualizado: 2026-10-07
Alcance coordinado: Lite + Plus
Rama activa: `qa/syntax-audit-in625-a1`

## Baseline
- Oracle Audit: 74/74 shards.
- 2,132/2,132 casos planificados.
- 4,026 casos canónicos.
- 3,451/3,451 legacy representados.
- promoted legacy oracle: 2,823/3,448 verificados; 625 restantes forman IN625.
- canonical oracle: 3,399/4,026.
- blocking verified: 1,357.
- Product Certification Wave 2: PASS en Lite y Plus, 22/22.

## IN625
Bloques cerrados y verdes en ambos motores:
A1, A2, A3, A4, B1, B2, B3, B4, C1, C2, C3, C4, D1, D2, D3, E1a, E1b, E1c, E1d, E2a, E2b, E2c, E3a, E3b, E3c, E3d1, E3d2, E3d3, F1, F2a, F2b, F3a, F3b, F3c, G1a, G1b automatizable y G2.

G1 manual/capability:
- TC17
- TC23

G2 manual/config-dependent:
- EN-CH-11: decimal coma real / locale.

## G2 — CERRADO
Se normalizaron únicamente equivalencias de representación del harness, sin cambiar producto:
- EN-CH-06: `sin^2(x)` ↔ `sin^2x`
- EN-CH-07: `sin^-1(x)` / `sin^(-1(x))` ↔ `sin^-1x`
- EN-CH-12: `abs(x-1)` ↔ `|x-1|`

Evidencia:
- Lite Playwright `37580506336` — SUCCESS.
- Plus Playwright `37580510564` — SUCCESS.
- Lite HEAD documental posterior: Playwright `37581518369` — SUCCESS.

## G3 — entradas inválidas y mensajes de error: CERRADO 34/34.
- Lite: 26 parser-level raw + 8 E2E preservables por MathLive.
- Lite E2E run `37722856327`: SUCCESS en desktop/tablet/mobile.
- Lite parser run `37722856334`: SUCCESS.
- Plus: G3 ya certificado 34/34 con Playwright + backend parser.
- La separación por capa preserva cobertura completa: entradas canonicalizadas por MathLive se validan antes del editor; entradas que sí atraviesan UI se validan E2E.

Siguiente bloque activo: H1 — 30 casos de reentrada / output-as-input.

## Siguiente paso exacto — IN625 H1d (EN-RE-24..30)
1. Localizar los siete casos EN-RE-24..30 en la matriz/spec vigente y localizar el harness E2E correspondiente en cada repositorio.
2. Verificar HEAD y el historial completo de Actions pertinente en ambos repositorios. No inferir ausencia de runs de la consulta por SHA del conector, que solo cubre una parte de los eventos.
3. Reconciliar EN-RE-29 y EN-RE-30 contra MANUAL_CAPABILITY_GAPS.md y confirmar si permanecen no implementados. No contabilizarlos como PASS ni como rojo de producto sin reproducir el contrato.
4. Ejecutar los casos automatizables de H1d en Lite y Plus, con el gate acumulativo relevante. Clasificar cada rojo como producto / harness / oráculo / capability antes de modificar producto.
5. Registrar evidencias verificadas, IDs de runs, SHA, resultados, decisiones y próximo bloque en CURRENT_STATE.md y EXECUTION_LOG.md de ambos repositorios. Solo avanzar a H2 cuando H1d tenga cierre bilateral verificable.

### Última reconciliación de continuidad — 2026-10-08
- H1a/H1b/H1c permanecen cerrados según evidencia documental de Actions; H1d sigue PENDIENTE DE VERIFICACIÓN, sin resultado nuevo acreditado por esta reconciliación.
- HEAD canónicos observados antes de este ajuste documental: Lite `a9627f4d67f141c0346a19c467656d626e3affcc`; Plus `802eea7d7a9abf2ec28f2fa46d97a40c67e5296f`.
- Runs H1c referenciados por el registro: Lite `37794754460`, Plus `37794867403` (jobs `h1c` completados en SUCCESS).
- La consulta limitada de runs por SHA devolvió listas vacías; esto NO acredita ausencia de corridas más recientes de otros eventos.
- EN-RE-22 sigue como capability gap de H1c; EN-RE-29 y EN-RE-30 constan como gaps de H1d y necesitan reconciliación antes del cierre.
- Se corrigió el siguiente paso obsoleto que remitía a G3 ya cerrado. No se han ejecutado pruebas nuevas ni alterado el producto en esta reconciliación.

## Continuidad repo-native
El bootstrap oficial es `qa/certification/CONTINUATION_PROMPT.md`. No se necesita ZIP de handoff mientras GitHub y estos archivos estén accesibles.

H1a — EN-RE-01..08: CERRADO 8/8 en Lite y Plus. Lite `37771014887`, Plus `37771019348`.
Siguiente bloque: H1b — EN-RE-09..16: CERRADO 8/8 en Lite y Plus.
- Lite run `37778832819`: SUCCESS.
- Plus run `37790101494`: SUCCESS.
- Correcciones permanentes: reentrada de listas de soluciones, matrices naturales, extracción exacta de salida Plus, preservación de unión de intervalos y formatos numéricos.
- Siguiente bloque: H1c — EN-RE-17..23: CERRADO con 6/6 automáticos PASS + 1 CAPABILITY GAP explícito.
- Lite run `37794754460`: SUCCESS.
- Plus run `37794867403`: SUCCESS.
- Automáticos PASS: EN-RE-17, 18, 19, 20, 21 y 23.
- EN-RE-22: capability gap documentado; el historial aún no restaura el LaTeX original al campo principal.
- Siguiente bloque: H1d — EN-RE-24..30.
