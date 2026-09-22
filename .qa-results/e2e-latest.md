# QA E2E diagnostic — Plus

- outcome: failure

## directed E2E
~~~text
    test-results/exhaustive-module03-calcul-c5c08-se-evalúa-a-120-desde-la-UI-desktop-chromium-retry1/video.webm
    ────────────────────────────────────────────────────────────────────────────────────────────────

    Error Context: test-results/exhaustive-module03-calcul-c5c08-se-evalúa-a-120-desde-la-UI-desktop-chromium-retry1/error-context.md

    attachment #4: trace (application/zip) ─────────────────────────────────────────────────────────
    test-results/exhaustive-module03-calcul-c5c08-se-evalúa-a-120-desde-la-UI-desktop-chromium-retry1/trace.zip
    Usage:

        npx playwright show-trace test-results/exhaustive-module03-calcul-c5c08-se-evalúa-a-120-desde-la-UI-desktop-chromium-retry1/trace.zip

    ────────────────────────────────────────────────────────────────────────────────────────────────


[1A[2K[6/48] [desktop-chromium] › e2e/exhaustive-module09-graphing.spec.ts:12:1 › suite original módulo 9: modos gráficos están activos y 2D renderiza
[1A[2K  2) [desktop-chromium] › e2e/exhaustive-module03-calculus.spec.ts:55:1 › suite original módulo 3: sumatoria de 1 a 5 se evalúa a 15 desde la UI 

    Error: [2mexpect([22m[31mlocator[39m[2m).[22mtoContainText[2m([22m[32mexpected[39m[2m)[22m failed

    Locator: getByRole('region', { name: 'Resultado', exact: true })
    Expected string: [32m"15"[39m
    Received string: [31m"BásicoRADsum  _(i=1)^5i—i=1∑5​i✕→PARSE_ERRORIdentificador no permitido: 'sum'.GráficaGraficarEjemplos:2x + √9sin(π/4)(3+4)²log(100)Opciones avanzadas (sustituciones)Sustituciones (opcional, solo aplica a expresiones simples)+ Añadir sustitución"[39m
    Timeout: 12000ms

    Call log:
    [2m  - Expect "toContainText" with timeout 12000ms[22m
    [2m  - waiting for getByRole('region', { name: 'Resultado', exact: true })[22m
    [2m    16 × locator resolved to <section aria-live="polite" aria-label="Resultado" class="mx-auto max-w-md lg:max-w-none">…</section>[22m
    [2m       - unexpected value "BásicoRADsum  _(i=1)^5i—i=1∑5​i✕→PARSE_ERRORIdentificador no permitido: 'sum'.GráficaGraficarEjemplos:2x + √9sin(π/4)(3+4)²log(100)Opciones avanzadas (sustituciones)Sustituciones (opcional, solo aplica a expresiones simples)+ Añadir sustitución"[22m


      62 |
      63 |   const result = page.getByRole("region", { name: "Resultado", exact: true });
    > 64 |   await expect(result).toContainText("15", { timeout: 12000 });
         |                        ^
      65 | });
      66 |
        at /home/runner/work/precision-lab-plus/precision-lab-plus/frontend/e2e/exhaustive-module03-calculus.spec.ts:64:24

    attachment #1: screenshot (image/png) ──────────────────────────────────────────────────────────
    test-results/exhaustive-module03-calcul-ca131--se-evalúa-a-15-desde-la-UI-desktop-chromium/test-failed-1.png
    ────────────────────────────────────────────────────────────────────────────────────────────────

    attachment #2: video (video/webm) ──────────────────────────────────────────────────────────────
    test-results/exhaustive-module03-calcul-ca131--se-evalúa-a-15-desde-la-UI-desktop-chromium/video.webm
    ────────────────────────────────────────────────────────────────────────────────────────────────

    Error Context: test-results/exhaustive-module03-calcul-ca131--se-evalúa-a-15-desde-la-UI-desktop-chromium/error-context.md

    attachment #4: trace (application/zip) ─────────────────────────────────────────────────────────
    test-results/exhaustive-module03-calcul-ca131--se-evalúa-a-15-desde-la-UI-desktop-chromium/trace.zip
    Usage:

        npx playwright show-trace test-results/exhaustive-module03-calcul-ca131--se-evalúa-a-15-desde-la-UI-desktop-chromium/trace.zip

    ────────────────────────────────────────────────────────────────────────────────────────────────

    Retry #1 ───────────────────────────────────────────────────────────────────────────────────────

    Error: [2mexpect([22m[31mlocator[39m[2m).[22mtoContainText[2m([22m[32mexpected[39m[2m)[22m failed

    Locator: getByRole('region', { name: 'Resultado', exact: true })
    Expected string: [32m"15"[39m
    Received string: [31m"BásicoRADsum  _(i=1)^5i—i=1∑5​i✕→PARSE_ERRORIdentificador no permitido: 'sum'.GráficaGraficarEjemplos:2x + √9sin(π/4)(3+4)²log(100)Opciones avanzadas (sustituciones)Sustituciones (opcional, solo aplica a expresiones simples)+ Añadir sustitución"[39m
    Timeout: 12000ms

    Call log:
    [2m  - Expect "toContainText" with timeout 12000ms[22m
    [2m  - waiting for getByRole('region', { name: 'Resultado', exact: true })[22m
    [2m    16 × locator resolved to <section aria-live="polite" aria-label="Resultado" class="mx-auto max-w-md lg:max-w-none">…</section>[22m
    [2m       - unexpected value "BásicoRADsum  _(i=1)^5i—i=1∑5​i✕→PARSE_ERRORIdentificador no permitido: 'sum'.GráficaGraficarEjemplos:2x + √9sin(π/4)(3+4)²log(100)Opciones avanzadas (sustituciones)Sustituciones (opcional, solo aplica a expresiones simples)+ Añadir sustitución"[22m


      62 |
      63 |   const result = page.getByRole("region", { name: "Resultado", exact: true });
    > 64 |   await expect(result).toContainText("15", { timeout: 12000 });
         |                        ^
      65 | });
      66 |
        at /home/runner/work/precision-lab-plus/precision-lab-plus/frontend/e2e/exhaustive-module03-calculus.spec.ts:64:24

    attachment #1: screenshot (image/png) ──────────────────────────────────────────────────────────
    test-results/exhaustive-module03-calcul-ca131--se-evalúa-a-15-desde-la-UI-desktop-chromium-retry1/test-failed-1.png
    ────────────────────────────────────────────────────────────────────────────────────────────────

    attachment #2: video (video/webm) ──────────────────────────────────────────────────────────────
    test-results/exhaustive-module03-calcul-ca131--se-evalúa-a-15-desde-la-UI-desktop-chromium-retry1/video.webm
    ────────────────────────────────────────────────────────────────────────────────────────────────

    Error Context: test-results/exhaustive-module03-calcul-ca131--se-evalúa-a-15-desde-la-UI-desktop-chromium-retry1/error-context.md

    attachment #4: trace (application/zip) ─────────────────────────────────────────────────────────
    test-results/exhaustive-module03-calcul-ca131--se-evalúa-a-15-desde-la-UI-desktop-chromium-retry1/trace.zip
    Usage:

        npx playwright show-trace test-results/exhaustive-module03-calcul-ca131--se-evalúa-a-15-desde-la-UI-desktop-chromium-retry1/trace.zip

    ────────────────────────────────────────────────────────────────────────────────────────────────


[1A[2K[7/48] [desktop-chromium] › e2e/exhaustive-module09-graphing.spec.ts:25:1 › suite original módulo 9: múltiples curvas 2D se renderizan juntas
[1A[2K[8/48] [desktop-chromium] › e2e/exhaustive-module10-keyboard.spec.ts:15:1 › módulo 10: la tecla % calcula porcentaje real (50% = 0.5)
[1A[2K[9/48] [desktop-chromium] › e2e/exhaustive-module10-keyboard.spec.ts:30:1 › módulo 10: ±(5) produce dos ramas matemáticas distintas
[1A[2K[10/48] [desktop-chromium] › e2e/exhaustive-module10-keyboard.spec.ts:46:1 › módulo 10: Productoria Π ya no aparece como pendiente
[1A[2K[11/48] [desktop-chromium] › e2e/exhaustive-module10-keyboard.spec.ts:55:1 › módulo 10: acciones no aritméticas de Álgebra exponen tooltip
[1A[2K[12/48] [desktop-chromium] › e2e/exhaustive-module12-personalization-a11y.spec.ts:21:1 › M12: preferencias visuales se aplican y persisten tras recarga
[1A[2K[13/48] [desktop-chromium] › e2e/exhaustive-module12-personalization-a11y.spec.ts:79:1 › M12: tema Automático sigue prefers-color-scheme
[1A[2K[14/48] [desktop-chromium] › e2e/exhaustive-module12-personalization-a11y.spec.ts:91:1 › M12: Ajustes expone estado y cierra con Escape
[1A[2K[15/48] [desktop-chromium] › e2e/exhaustive-module12-personalization-a11y.spec.ts:100:1 › M12: teclado propio tiene diálogo nombrado y cierra con Escape
[1A[2K[16/48] [desktop-chromium] › e2e/exhaustive-module12-personalization-a11y.spec.ts:110:1 › M12: campo matemático principal tiene nombre accesible
[1A[2K[17/48] [desktop-chromium] › e2e/exhaustive-module12-personalization-a11y.spec.ts:118:1 › M12: resultado calculado queda dentro de una región anunciable
[1A[2K[18/48] [desktop-chromium] › e2e/exhaustive-module12-personalization-a11y.spec.ts:145:1 › M12: vibración y sonido guardan preferencia y sobreviven recarga
[1A[2K[19/48] [tablet-chromium] › e2e/exhaustive-module03-calculus.spec.ts:20:1 › suite original módulo 3: inventario de Cálculo refleja capacidades actuales
[1A[2K[20/48] [tablet-chromium] › e2e/exhaustive-module03-calculus.spec.ts:43:1 › suite original módulo 3: productoria de 1 a 5 se evalúa a 120 desde la UI
[1A[2K[21/48] [tablet-chromium] › e2e/exhaustive-module03-calculus.spec.ts:55:1 › suite original módulo 3: sumatoria de 1 a 5 se evalúa a 15 desde la UI
[1A[2K[22/48] [tablet-chromium] › e2e/exhaustive-module03-calculus.spec.ts:43:1 › suite original módulo 3: productoria de 1 a 5 se evalúa a 120 desde la UI (retry #1)
[1A[2K[23/48] [tablet-chromium] › e2e/exhaustive-module03-calculus.spec.ts:55:1 › suite original módulo 3: sumatoria de 1 a 5 se evalúa a 15 desde la UI (retry #1)
[1A[2K  3) [tablet-chromium] › e2e/exhaustive-module03-calculus.spec.ts:43:1 › suite original módulo 3: productoria de 1 a 5 se evalúa a 120 desde la UI 

    Error: [2mexpect([22m[31mlocator[39m[2m).[22mtoContainText[2m([22m[32mexpected[39m[2m)[22m failed

    Locator: getByRole('region', { name: 'Resultado', exact: true })
    Expected string: [32m"120"[39m
    Received string: [31m"BásicoRADprod  _(i=1)^5i—i=1∏5​i✕→PARSE_ERRORIdentificador inválido (debe empezar con letra): '_'.GráficaGraficarEjemplos:2x + √9sin(π/4)(3+4)²log(100)Opciones avanzadas (sustituciones)Sustituciones (opcional, solo aplica a expresiones simples)+ Añadir sustitución"[39m
    Timeout: 12000ms

    Call log:
    [2m  - Expect "toContainText" with timeout 12000ms[22m
    [2m  - waiting for getByRole('region', { name: 'Resultado', exact: true })[22m
    [2m    16 × locator resolved to <section aria-live="polite" aria-label="Resultado" class="mx-auto max-w-md lg:max-w-none">…</section>[22m
    [2m       - unexpected value "BásicoRADprod  _(i=1)^5i—i=1∏5​i✕→PARSE_ERRORIdentificador inválido (debe empezar con letra): '_'.GráficaGraficarEjemplos:2x + √9sin(π/4)(3+4)²log(100)Opciones avanzadas (sustituciones)Sustituciones (opcional, solo aplica a expresiones simples)+ Añadir sustitución"[22m


      50 |
      51 |   const result = page.getByRole("region", { name: "Resultado", exact: true });
    > 52 |   await expect(result).toContainText("120", { timeout: 12000 });
         |                        ^
      53 | });
      54 |
      55 | test("suite original módulo 3: sumatoria de 1 a 5 se evalúa a 15 desde la UI", async ({ page }) => {
        at /home/runner/work/precision-lab-plus/precision-lab-plus/frontend/e2e/exhaustive-module03-calculus.spec.ts:52:24

    attachment #1: screenshot (image/png) ──────────────────────────────────────────────────────────
    test-results/exhaustive-module03-calcul-c5c08-se-evalúa-a-120-desde-la-UI-tablet-chromium/test-failed-1.png
    ────────────────────────────────────────────────────────────────────────────────────────────────

    attachment #2: video (video/webm) ──────────────────────────────────────────────────────────────
    test-results/exhaustive-module03-calcul-c5c08-se-evalúa-a-120-desde-la-UI-tablet-chromium/video.webm
    ────────────────────────────────────────────────────────────────────────────────────────────────

    Error Context: test-results/exhaustive-module03-calcul-c5c08-se-evalúa-a-120-desde-la-UI-tablet-chromium/error-context.md

    attachment #4: trace (application/zip) ─────────────────────────────────────────────────────────
    test-results/exhaustive-module03-calcul-c5c08-se-evalúa-a-120-desde-la-UI-tablet-chromium/trace.zip
    Usage:

        npx playwright show-trace test-results/exhaustive-module03-calcul-c5c08-se-evalúa-a-120-desde-la-UI-tablet-chromium/trace.zip

    ────────────────────────────────────────────────────────────────────────────────────────────────

    Retry #1 ───────────────────────────────────────────────────────────────────────────────────────

    Error: [2mexpect([22m[31mlocator[39m[2m).[22mtoContainText[2m([22m[32mexpected[39m[2m)[22m failed

    Locator: getByRole('region', { name: 'Resultado', exact: true })
    Expected string: [32m"120"[39m
    Received string: [31m"BásicoRADprod  _(i=1)^5i—i=1∏5​i✕→PARSE_ERRORIdentificador inválido (debe empezar con letra): '_'.GráficaGraficarEjemplos:2x + √9sin(π/4)(3+4)²log(100)Opciones avanzadas (sustituciones)Sustituciones (opcional, solo aplica a expresiones simples)+ Añadir sustitución"[39m
    Timeout: 12000ms

    Call log:
    [2m  - Expect "toContainText" with timeout 12000ms[22m
    [2m  - waiting for getByRole('region', { name: 'Resultado', exact: true })[22m
    [2m    16 × locator resolved to <section aria-live="polite" aria-label="Resultado" class="mx-auto max-w-md lg:max-w-none">…</section>[22m
    [2m       - unexpected value "BásicoRADprod  _(i=1)^5i—i=1∏5​i✕→PARSE_ERRORIdentificador inválido (debe empezar con letra): '_'.GráficaGraficarEjemplos:2x + √9sin(π/4)(3+4)²log(100)Opciones avanzadas (sustituciones)Sustituciones (opcional, solo aplica a expresiones simples)+ Añadir sustitución"[22m


      50 |
      51 |   const result = page.getByRole("region", { name: "Resultado", exact: true });
    > 52 |   await expect(result).toContainText("120", { timeout: 12000 });
         |                        ^
      53 | });
      54 |
      55 | test("suite original módulo 3: sumatoria de 1 a 5 se evalúa a 15 desde la UI", async ({ page }) => {
        at /home/runner/work/precision-lab-plus/precision-lab-plus/frontend/e2e/exhaustive-module03-calculus.spec.ts:52:24

    attachment #1: screenshot (image/png) ──────────────────────────────────────────────────────────
    test-results/exhaustive-module03-calcul-c5c08-se-evalúa-a-120-desde-la-UI-tablet-chromium-retry1/test-failed-1.png
    ────────────────────────────────────────────────────────────────────────────────────────────────

    attachment #2: video (video/webm) ──────────────────────────────────────────────────────────────
    test-results/exhaustive-module03-calcul-c5c08-se-evalúa-a-120-desde-la-UI-tablet-chromium-retry1/video.webm
    ────────────────────────────────────────────────────────────────────────────────────────────────

    Error Context: test-results/exhaustive-module03-calcul-c5c08-se-evalúa-a-120-desde-la-UI-tablet-chromium-retry1/error-context.md

    attachment #4: trace (application/zip) ─────────────────────────────────────────────────────────
    test-results/exhaustive-module03-calcul-c5c08-se-evalúa-a-120-desde-la-UI-tablet-chromium-retry1/trace.zip
    Usage:

        npx playwright show-trace test-results/exhaustive-module03-calcul-c5c08-se-evalúa-a-120-desde-la-UI-tablet-chromium-retry1/trace.zip

    ────────────────────────────────────────────────────────────────────────────────────────────────


[1A[2K  4) [tablet-chromium] › e2e/exhaustive-module03-calculus.spec.ts:55:1 › suite original módulo 3: sumatoria de 1 a 5 se evalúa a 15 desde la UI 

    Error: [2mexpect([22m[31mlocator[39m[2m).[22mtoContainText[2m([22m[32mexpected[39m[2m)[22m failed

    Locator: getByRole('region', { name: 'Resultado', exact: true })
    Expected string: [32m"15"[39m
    Received string: [31m"BásicoRADsum  _(i=1)^5i—i=1∑5​i✕→PARSE_ERRORIdentificador no permitido: 'sum'.GráficaGraficarEjemplos:2x + √9sin(π/4)(3+4)²log(100)Opciones avanzadas (sustituciones)Sustituciones (opcional, solo aplica a expresiones simples)+ Añadir sustitución"[39m
    Timeout: 12000ms

    Call log:
    [2m  - Expect "toContainText" with timeout 12000ms[22m
    [2m  - waiting for getByRole('region', { name: 'Resultado', exact: true })[22m
    [2m    16 × locator resolved to <section aria-live="polite" aria-label="Resultado" class="mx-auto max-w-md lg:max-w-none">…</section>[22m
    [2m       - unexpected value "BásicoRADsum  _(i=1)^5i—i=1∑5​i✕→PARSE_ERRORIdentificador no permitido: 'sum'.GráficaGraficarEjemplos:2x + √9sin(π/4)(3+4)²log(100)Opciones avanzadas (sustituciones)Sustituciones (opcional, solo aplica a expresiones simples)+ Añadir sustitución"[22m


      62 |
      63 |   const result = page.getByRole("region", { name: "Resultado", exact: true });
    > 64 |   await expect(result).toContainText("15", { timeout: 12000 });
         |                        ^
      65 | });
      66 |
        at /home/runner/work/precision-lab-plus/precision-lab-plus/frontend/e2e/exhaustive-module03-calculus.spec.ts:64:24

    attachment #1: screenshot (image/png) ──────────────────────────────────────────────────────────
    test-results/exhaustive-module03-calcul-ca131--se-evalúa-a-15-desde-la-UI-tablet-chromium/test-failed-1.png
    ────────────────────────────────────────────────────────────────────────────────────────────────

    attachment #2: video (video/webm) ──────────────────────────────────────────────────────────────
    test-results/exhaustive-module03-calcul-ca131--se-evalúa-a-15-desde-la-UI-tablet-chromium/video.webm
    ────────────────────────────────────────────────────────────────────────────────────────────────

    Error Context: test-results/exhaustive-module03-calcul-ca131--se-evalúa-a-15-desde-la-UI-tablet-chromium/error-context.md

    attachment #4: trace (application/zip) ─────────────────────────────────────────────────────────
    test-results/exhaustive-module03-calcul-ca131--se-evalúa-a-15-desde-la-UI-tablet-chromium/trace.zip
    Usage:

        npx playwright show-trace test-results/exhaustive-module03-calcul-ca131--se-evalúa-a-15-desde-la-UI-tablet-chromium/trace.zip

    ────────────────────────────────────────────────────────────────────────────────────────────────

    Retry #1 ───────────────────────────────────────────────────────────────────────────────────────

    Error: [2mexpect([22m[31mlocator[39m[2m).[22mtoContainText[2m([22m[32mexpected[39m[2m)[22m failed

    Locator: getByRole('region', { name: 'Resultado', exact: true })
    Expected string: [32m"15"[39m
    Received string: [31m"BásicoRADsum  _(i=1)^5i—i=1∑5​i✕→PARSE_ERRORIdentificador no permitido: 'sum'.GráficaGraficarEjemplos:2x + √9sin(π/4)(3+4)²log(100)Opciones avanzadas (sustituciones)Sustituciones (opcional, solo aplica a expresiones simples)+ Añadir sustitución"[39m
    Timeout: 12000ms

    Call log:
    [2m  - Expect "toContainText" with timeout 12000ms[22m
    [2m  - waiting for getByRole('region', { name: 'Resultado', exact: true })[22m
    [2m    16 × locator resolved to <section aria-live="polite" aria-label="Resultado" class="mx-auto max-w-md lg:max-w-none">…</section>[22m
    [2m       - unexpected value "BásicoRADsum  _(i=1)^5i—i=1∑5​i✕→PARSE_ERRORIdentificador no permitido: 'sum'.GráficaGraficarEjemplos:2x + √9sin(π/4)(3+4)²log(100)Opciones avanzadas (sustituciones)Sustituciones (opcional, solo aplica a expresiones simples)+ Añadir sustitución"[22m


      62 |
      63 |   const result = page.getByRole("region", { name: "Resultado", exact: true });
    > 64 |   await expect(result).toContainText("15", { timeout: 12000 });
         |                        ^
      65 | });
      66 |
        at /home/runner/work/precision-lab-plus/precision-lab-plus/frontend/e2e/exhaustive-module03-calculus.spec.ts:64:24

    attachment #1: screenshot (image/png) ──────────────────────────────────────────────────────────
    test-results/exhaustive-module03-calcul-ca131--se-evalúa-a-15-desde-la-UI-tablet-chromium-retry1/test-failed-1.png
    ────────────────────────────────────────────────────────────────────────────────────────────────

    attachment #2: video (video/webm) ──────────────────────────────────────────────────────────────
    test-results/exhaustive-module03-calcul-ca131--se-evalúa-a-15-desde-la-UI-tablet-chromium-retry1/video.webm
    ────────────────────────────────────────────────────────────────────────────────────────────────

    Error Context: test-results/exhaustive-module03-calcul-ca131--se-evalúa-a-15-desde-la-UI-tablet-chromium-retry1/error-context.md

    attachment #4: trace (application/zip) ─────────────────────────────────────────────────────────
    test-results/exhaustive-module03-calcul-ca131--se-evalúa-a-15-desde-la-UI-tablet-chromium-retry1/trace.zip
    Usage:

        npx playwright show-trace test-results/exhaustive-module03-calcul-ca131--se-evalúa-a-15-desde-la-UI-tablet-chromium-retry1/trace.zip

    ────────────────────────────────────────────────────────────────────────────────────────────────


[1A[2K[24/48] [tablet-chromium] › e2e/exhaustive-module09-graphing.spec.ts:12:1 › suite original módulo 9: modos gráficos están activos y 2D renderiza
[1A[2K[25/48] [tablet-chromium] › e2e/exhaustive-module09-graphing.spec.ts:25:1 › suite original módulo 9: múltiples curvas 2D se renderizan juntas
[1A[2K[26/48] [tablet-chromium] › e2e/exhaustive-module10-keyboard.spec.ts:15:1 › módulo 10: la tecla % calcula porcentaje real (50% = 0.5)
[1A[2K[27/48] [tablet-chromium] › e2e/exhaustive-module10-keyboard.spec.ts:30:1 › módulo 10: ±(5) produce dos ramas matemáticas distintas
[1A[2K[28/48] [tablet-chromium] › e2e/exhaustive-module10-keyboard.spec.ts:46:1 › módulo 10: Productoria Π ya no aparece como pendiente
[1A[2K[29/48] [tablet-chromium] › e2e/exhaustive-module10-keyboard.spec.ts:55:1 › módulo 10: acciones no aritméticas de Álgebra exponen tooltip
[1A[2K[30/48] [tablet-chromium] › e2e/exhaustive-module12-personalization-a11y.spec.ts:21:1 › M12: preferencias visuales se aplican y persisten tras recarga
[1A[2K[31/48] [tablet-chromium] › e2e/exhaustive-module12-personalization-a11y.spec.ts:79:1 › M12: tema Automático sigue prefers-color-scheme
[1A[2K[32/48] [tablet-chromium] › e2e/exhaustive-module12-personalization-a11y.spec.ts:91:1 › M12: Ajustes expone estado y cierra con Escape
[1A[2K[33/48] [tablet-chromium] › e2e/exhaustive-module12-personalization-a11y.spec.ts:100:1 › M12: teclado propio tiene diálogo nombrado y cierra con Escape
[1A[2K[34/48] [tablet-chromium] › e2e/exhaustive-module12-personalization-a11y.spec.ts:110:1 › M12: campo matemático principal tiene nombre accesible
[1A[2K[35/48] [tablet-chromium] › e2e/exhaustive-module12-personalization-a11y.spec.ts:118:1 › M12: resultado calculado queda dentro de una región anunciable
[1A[2K[36/48] [tablet-chromium] › e2e/exhaustive-module12-personalization-a11y.spec.ts:145:1 › M12: vibración y sonido guardan preferencia y sobreviven recarga
[1A[2K[37/48] [mobile-chromium] › e2e/exhaustive-module03-calculus.spec.ts:20:1 › suite original módulo 3: inventario de Cálculo refleja capacidades actuales
[1A[2K[38/48] [mobile-chromium] › e2e/exhaustive-module03-calculus.spec.ts:43:1 › suite original módulo 3: productoria de 1 a 5 se evalúa a 120 desde la UI
[1A[2K[39/48] [mobile-chromium] › e2e/exhaustive-module03-calculus.spec.ts:55:1 › suite original módulo 3: sumatoria de 1 a 5 se evalúa a 15 desde la UI
[1A[2K[40/48] [mobile-chromium] › e2e/exhaustive-module03-calculus.spec.ts:43:1 › suite original módulo 3: productoria de 1 a 5 se evalúa a 120 desde la UI (retry #1)
[1A[2K[41/48] [mobile-chromium] › e2e/exhaustive-module03-calculus.spec.ts:55:1 › suite original módulo 3: sumatoria de 1 a 5 se evalúa a 15 desde la UI (retry #1)
[1A[2K  5) [mobile-chromium] › e2e/exhaustive-module03-calculus.spec.ts:43:1 › suite original módulo 3: productoria de 1 a 5 se evalúa a 120 desde la UI 

    Error: [2mexpect([22m[31mlocator[39m[2m).[22mtoContainText[2m([22m[32mexpected[39m[2m)[22m failed

    Locator: getByRole('region', { name: 'Resultado', exact: true })
    Expected string: [32m"120"[39m
    Received string: [31m"BásicoRADprod  _(i=1)^5i—i=1∏5​i✕→PARSE_ERRORIdentificador inválido (debe empezar con letra): '_'.GráficaGraficarEjemplos:2x + √9sin(π/4)(3+4)²log(100)Opciones avanzadas (sustituciones)Sustituciones (opcional, solo aplica a expresiones simples)+ Añadir sustitución"[39m
    Timeout: 12000ms

    Call log:
    [2m  - Expect "toContainText" with timeout 12000ms[22m
    [2m  - waiting for getByRole('region', { name: 'Resultado', exact: true })[22m
    [2m    16 × locator resolved to <section aria-live="polite" aria-label="Resultado" class="mx-auto max-w-md lg:max-w-none">…</section>[22m
    [2m       - unexpected value "BásicoRADprod  _(i=1)^5i—i=1∏5​i✕→PARSE_ERRORIdentificador inválido (debe empezar con letra): '_'.GráficaGraficarEjemplos:2x + √9sin(π/4)(3+4)²log(100)Opciones avanzadas (sustituciones)Sustituciones (opcional, solo aplica a expresiones simples)+ Añadir sustitución"[22m


      50 |
      51 |   const result = page.getByRole("region", { name: "Resultado", exact: true });
    > 52 |   await expect(result).toContainText("120", { timeout: 12000 });
         |                        ^
      53 | });
      54 |
      55 | test("suite original módulo 3: sumatoria de 1 a 5 se evalúa a 15 desde la UI", async ({ page }) => {
        at /home/runner/work/precision-lab-plus/precision-lab-plus/frontend/e2e/exhaustive-module03-calculus.spec.ts:52:24

    attachment #1: screenshot (image/png) ──────────────────────────────────────────────────────────
    test-results/exhaustive-module03-calcul-c5c08-se-evalúa-a-120-desde-la-UI-mobile-chromium/test-failed-1.png
    ────────────────────────────────────────────────────────────────────────────────────────────────

    attachment #2: video (video/webm) ──────────────────────────────────────────────────────────────
    test-results/exhaustive-module03-calcul-c5c08-se-evalúa-a-120-desde-la-UI-mobile-chromium/video.webm
    ────────────────────────────────────────────────────────────────────────────────────────────────

    Error Context: test-results/exhaustive-module03-calcul-c5c08-se-evalúa-a-120-desde-la-UI-mobile-chromium/error-context.md

    attachment #4: trace (application/zip) ─────────────────────────────────────────────────────────
    test-results/exhaustive-module03-calcul-c5c08-se-evalúa-a-120-desde-la-UI-mobile-chromium/trace.zip
    Usage:

        npx playwright show-trace test-results/exhaustive-module03-calcul-c5c08-se-evalúa-a-120-desde-la-UI-mobile-chromium/trace.zip

    ────────────────────────────────────────────────────────────────────────────────────────────────

    Retry #1 ───────────────────────────────────────────────────────────────────────────────────────

    Error: [2mexpect([22m[31mlocator[39m[2m).[22mtoContainText[2m([22m[32mexpected[39m[2m)[22m failed

    Locator: getByRole('region', { name: 'Resultado', exact: true })
    Expected string: [32m"120"[39m
    Received string: [31m"BásicoRADprod  _(i=1)^5i—i=1∏5​i✕→PARSE_ERRORIdentificador inválido (debe empezar con letra): '_'.GráficaGraficarEjemplos:2x + √9sin(π/4)(3+4)²log(100)Opciones avanzadas (sustituciones)Sustituciones (opcional, solo aplica a expresiones simples)+ Añadir sustitución"[39m
    Timeout: 12000ms

    Call log:
    [2m  - Expect "toContainText" with timeout 12000ms[22m
    [2m  - waiting for getByRole('region', { name: 'Resultado', exact: true })[22m
    [2m    16 × locator resolved to <section aria-live="polite" aria-label="Resultado" class="mx-auto max-w-md lg:max-w-none">…</section>[22m
    [2m       - unexpected value "BásicoRADprod  _(i=1)^5i—i=1∏5​i✕→PARSE_ERRORIdentificador inválido (debe empezar con letra): '_'.GráficaGraficarEjemplos:2x + √9sin(π/4)(3+4)²log(100)Opciones avanzadas (sustituciones)Sustituciones (opcional, solo aplica a expresiones simples)+ Añadir sustitución"[22m


      50 |
      51 |   const result = page.getByRole("region", { name: "Resultado", exact: true });
    > 52 |   await expect(result).toContainText("120", { timeout: 12000 });
         |                        ^
      53 | });
      54 |
      55 | test("suite original módulo 3: sumatoria de 1 a 5 se evalúa a 15 desde la UI", async ({ page }) => {
        at /home/runner/work/precision-lab-plus/precision-lab-plus/frontend/e2e/exhaustive-module03-calculus.spec.ts:52:24

    attachment #1: screenshot (image/png) ──────────────────────────────────────────────────────────
    test-results/exhaustive-module03-calcul-c5c08-se-evalúa-a-120-desde-la-UI-mobile-chromium-retry1/test-failed-1.png
    ────────────────────────────────────────────────────────────────────────────────────────────────

    attachment #2: video (video/webm) ──────────────────────────────────────────────────────────────
    test-results/exhaustive-module03-calcul-c5c08-se-evalúa-a-120-desde-la-UI-mobile-chromium-retry1/video.webm
    ────────────────────────────────────────────────────────────────────────────────────────────────

    Error Context: test-results/exhaustive-module03-calcul-c5c08-se-evalúa-a-120-desde-la-UI-mobile-chromium-retry1/error-context.md

    attachment #4: trace (application/zip) ─────────────────────────────────────────────────────────
    test-results/exhaustive-module03-calcul-c5c08-se-evalúa-a-120-desde-la-UI-mobile-chromium-retry1/trace.zip
    Usage:

        npx playwright show-trace test-results/exhaustive-module03-calcul-c5c08-se-evalúa-a-120-desde-la-UI-mobile-chromium-retry1/trace.zip

    ────────────────────────────────────────────────────────────────────────────────────────────────


[1A[2K  6) [mobile-chromium] › e2e/exhaustive-module03-calculus.spec.ts:55:1 › suite original módulo 3: sumatoria de 1 a 5 se evalúa a 15 desde la UI 

    Error: [2mexpect([22m[31mlocator[39m[2m).[22mtoContainText[2m([22m[32mexpected[39m[2m)[22m failed

    Locator: getByRole('region', { name: 'Resultado', exact: true })
    Expected string: [32m"15"[39m
    Received string: [31m"BásicoRADsum  _(i=1)^5i—i=1∑5​i✕→PARSE_ERRORIdentificador no permitido: 'sum'.GráficaGraficarEjemplos:2x + √9sin(π/4)(3+4)²log(100)Opciones avanzadas (sustituciones)Sustituciones (opcional, solo aplica a expresiones simples)+ Añadir sustitución"[39m
    Timeout: 12000ms

    Call log:
    [2m  - Expect "toContainText" with timeout 12000ms[22m
    [2m  - waiting for getByRole('region', { name: 'Resultado', exact: true })[22m
    [2m    16 × locator resolved to <section aria-live="polite" aria-label="Resultado" class="mx-auto max-w-md lg:max-w-none">…</section>[22m
    [2m       - unexpected value "BásicoRADsum  _(i=1)^5i—i=1∑5​i✕→PARSE_ERRORIdentificador no permitido: 'sum'.GráficaGraficarEjemplos:2x + √9sin(π/4)(3+4)²log(100)Opciones avanzadas (sustituciones)Sustituciones (opcional, solo aplica a expresiones simples)+ Añadir sustitución"[22m


      62 |
      63 |   const result = page.getByRole("region", { name: "Resultado", exact: true });
    > 64 |   await expect(result).toContainText("15", { timeout: 12000 });
         |                        ^
      65 | });
      66 |
        at /home/runner/work/precision-lab-plus/precision-lab-plus/frontend/e2e/exhaustive-module03-calculus.spec.ts:64:24

    attachment #1: screenshot (image/png) ──────────────────────────────────────────────────────────
    test-results/exhaustive-module03-calcul-ca131--se-evalúa-a-15-desde-la-UI-mobile-chromium/test-failed-1.png
    ────────────────────────────────────────────────────────────────────────────────────────────────

    attachment #2: video (video/webm) ──────────────────────────────────────────────────────────────
    test-results/exhaustive-module03-calcul-ca131--se-evalúa-a-15-desde-la-UI-mobile-chromium/video.webm
    ────────────────────────────────────────────────────────────────────────────────────────────────

    Error Context: test-results/exhaustive-module03-calcul-ca131--se-evalúa-a-15-desde-la-UI-mobile-chromium/error-context.md

    attachment #4: trace (application/zip) ─────────────────────────────────────────────────────────
    test-results/exhaustive-module03-calcul-ca131--se-evalúa-a-15-desde-la-UI-mobile-chromium/trace.zip
    Usage:

        npx playwright show-trace test-results/exhaustive-module03-calcul-ca131--se-evalúa-a-15-desde-la-UI-mobile-chromium/trace.zip

    ────────────────────────────────────────────────────────────────────────────────────────────────

    Retry #1 ───────────────────────────────────────────────────────────────────────────────────────

    Error: [2mexpect([22m[31mlocator[39m[2m).[22mtoContainText[2m([22m[32mexpected[39m[2m)[22m failed

    Locator: getByRole('region', { name: 'Resultado', exact: true })
    Expected string: [32m"15"[39m
    Received string: [31m"BásicoRADsum  _(i=1)^5i—i=1∑5​i✕→PARSE_ERRORIdentificador no permitido: 'sum'.GráficaGraficarEjemplos:2x + √9sin(π/4)(3+4)²log(100)Opciones avanzadas (sustituciones)Sustituciones (opcional, solo aplica a expresiones simples)+ Añadir sustitución"[39m
    Timeout: 12000ms

    Call log:
    [2m  - Expect "toContainText" with timeout 12000ms[22m
    [2m  - waiting for getByRole('region', { name: 'Resultado', exact: true })[22m
    [2m    16 × locator resolved to <section aria-live="polite" aria-label="Resultado" class="mx-auto max-w-md lg:max-w-none">…</section>[22m
    [2m       - unexpected value "BásicoRADsum  _(i=1)^5i—i=1∑5​i✕→PARSE_ERRORIdentificador no permitido: 'sum'.GráficaGraficarEjemplos:2x + √9sin(π/4)(3+4)²log(100)Opciones avanzadas (sustituciones)Sustituciones (opcional, solo aplica a expresiones simples)+ Añadir sustitución"[22m


      62 |
      63 |   const result = page.getByRole("region", { name: "Resultado", exact: true });
    > 64 |   await expect(result).toContainText("15", { timeout: 12000 });
         |                        ^
      65 | });
      66 |
        at /home/runner/work/precision-lab-plus/precision-lab-plus/frontend/e2e/exhaustive-module03-calculus.spec.ts:64:24

    attachment #1: screenshot (image/png) ──────────────────────────────────────────────────────────
    test-results/exhaustive-module03-calcul-ca131--se-evalúa-a-15-desde-la-UI-mobile-chromium-retry1/test-failed-1.png
    ────────────────────────────────────────────────────────────────────────────────────────────────

    attachment #2: video (video/webm) ──────────────────────────────────────────────────────────────
    test-results/exhaustive-module03-calcul-ca131--se-evalúa-a-15-desde-la-UI-mobile-chromium-retry1/video.webm
    ────────────────────────────────────────────────────────────────────────────────────────────────

    Error Context: test-results/exhaustive-module03-calcul-ca131--se-evalúa-a-15-desde-la-UI-mobile-chromium-retry1/error-context.md

    attachment #4: trace (application/zip) ─────────────────────────────────────────────────────────
    test-results/exhaustive-module03-calcul-ca131--se-evalúa-a-15-desde-la-UI-mobile-chromium-retry1/trace.zip
    Usage:

        npx playwright show-trace test-results/exhaustive-module03-calcul-ca131--se-evalúa-a-15-desde-la-UI-mobile-chromium-retry1/trace.zip

    ────────────────────────────────────────────────────────────────────────────────────────────────


[1A[2K[42/48] [mobile-chromium] › e2e/exhaustive-module09-graphing.spec.ts:12:1 › suite original módulo 9: modos gráficos están activos y 2D renderiza
[1A[2K[43/48] [mobile-chromium] › e2e/exhaustive-module09-graphing.spec.ts:25:1 › suite original módulo 9: múltiples curvas 2D se renderizan juntas
[1A[2K[44/48] [mobile-chromium] › e2e/exhaustive-module10-keyboard.spec.ts:15:1 › módulo 10: la tecla % calcula porcentaje real (50% = 0.5)
[1A[2K[45/48] [mobile-chromium] › e2e/exhaustive-module10-keyboard.spec.ts:30:1 › módulo 10: ±(5) produce dos ramas matemáticas distintas
[1A[2K[46/48] [mobile-chromium] › e2e/exhaustive-module10-keyboard.spec.ts:46:1 › módulo 10: Productoria Π ya no aparece como pendiente
[1A[2K[47/48] [mobile-chromium] › e2e/exhaustive-module10-keyboard.spec.ts:55:1 › módulo 10: acciones no aritméticas de Álgebra exponen tooltip
[1A[2K[48/48] [mobile-chromium] › e2e/exhaustive-module12-personalization-a11y.spec.ts:21:1 › M12: preferencias visuales se aplican y persisten tras recarga
[1A[2K[49/48] (retries) [mobile-chromium] › e2e/exhaustive-module12-personalization-a11y.spec.ts:79:1 › M12: tema Automático sigue prefers-color-scheme
[1A[2K[50/48] (retries) [mobile-chromium] › e2e/exhaustive-module12-personalization-a11y.spec.ts:91:1 › M12: Ajustes expone estado y cierra con Escape
[1A[2K[51/48] (retries) [mobile-chromium] › e2e/exhaustive-module12-personalization-a11y.spec.ts:100:1 › M12: teclado propio tiene diálogo nombrado y cierra con Escape
[1A[2K[52/48] (retries) [mobile-chromium] › e2e/exhaustive-module12-personalization-a11y.spec.ts:110:1 › M12: campo matemático principal tiene nombre accesible
[1A[2K[53/48] (retries) [mobile-chromium] › e2e/exhaustive-module12-personalization-a11y.spec.ts:118:1 › M12: resultado calculado queda dentro de una región anunciable
[1A[2K[54/48] (retries) [mobile-chromium] › e2e/exhaustive-module12-personalization-a11y.spec.ts:145:1 › M12: vibración y sonido guardan preferencia y sobreviven recarga
[1A[2K  6 failed
    [desktop-chromium] › e2e/exhaustive-module03-calculus.spec.ts:43:1 › suite original módulo 3: productoria de 1 a 5 se evalúa a 120 desde la UI 
    [desktop-chromium] › e2e/exhaustive-module03-calculus.spec.ts:55:1 › suite original módulo 3: sumatoria de 1 a 5 se evalúa a 15 desde la UI 
    [tablet-chromium] › e2e/exhaustive-module03-calculus.spec.ts:43:1 › suite original módulo 3: productoria de 1 a 5 se evalúa a 120 desde la UI 
    [tablet-chromium] › e2e/exhaustive-module03-calculus.spec.ts:55:1 › suite original módulo 3: sumatoria de 1 a 5 se evalúa a 15 desde la UI 
    [mobile-chromium] › e2e/exhaustive-module03-calculus.spec.ts:43:1 › suite original módulo 3: productoria de 1 a 5 se evalúa a 120 desde la UI 
    [mobile-chromium] › e2e/exhaustive-module03-calculus.spec.ts:55:1 › suite original módulo 3: sumatoria de 1 a 5 se evalúa a 15 desde la UI 
  42 passed (2.1m)
~~~
