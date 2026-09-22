# QA E2E diagnostic — Plus

- outcome: success

## directed E2E
~~~text
[1A[2K[WebServer] INFO:     Started server process [3521]
[WebServer] INFO:     Waiting for application startup.

[1A[2K[WebServer] INFO:     Application startup complete.

[1A[2K[WebServer] INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)


Running 48 tests using 2 workers

[1A[2K[1/48] [desktop-chromium] › e2e/exhaustive-module03-calculus.spec.ts:20:1 › suite original módulo 3: inventario de Cálculo refleja capacidades actuales
[1A[2K[2/48] [desktop-chromium] › e2e/exhaustive-module03-calculus.spec.ts:43:1 › suite original módulo 3: productoria de 1 a 5 se evalúa a 120 desde la UI
[1A[2K[3/48] [desktop-chromium] › e2e/exhaustive-module03-calculus.spec.ts:55:1 › suite original módulo 3: sumatoria de 1 a 5 se evalúa a 15 desde la UI
[1A[2K[4/48] [desktop-chromium] › e2e/exhaustive-module09-graphing.spec.ts:12:1 › suite original módulo 9: modos gráficos están activos y 2D renderiza
[1A[2K[5/48] [desktop-chromium] › e2e/exhaustive-module09-graphing.spec.ts:25:1 › suite original módulo 9: múltiples curvas 2D se renderizan juntas
[1A[2K[6/48] [desktop-chromium] › e2e/exhaustive-module10-keyboard.spec.ts:15:1 › módulo 10: la tecla % calcula porcentaje real (50% = 0.5)
[1A[2K[7/48] [desktop-chromium] › e2e/exhaustive-module10-keyboard.spec.ts:30:1 › módulo 10: ±(5) produce dos ramas matemáticas distintas
[1A[2K[8/48] [desktop-chromium] › e2e/exhaustive-module10-keyboard.spec.ts:46:1 › módulo 10: Productoria Π ya no aparece como pendiente
[1A[2K[9/48] [desktop-chromium] › e2e/exhaustive-module10-keyboard.spec.ts:55:1 › módulo 10: acciones no aritméticas de Álgebra exponen tooltip
[1A[2K[10/48] [desktop-chromium] › e2e/exhaustive-module12-personalization-a11y.spec.ts:21:1 › M12: preferencias visuales se aplican y persisten tras recarga
[1A[2K[11/48] [desktop-chromium] › e2e/exhaustive-module12-personalization-a11y.spec.ts:79:1 › M12: tema Automático sigue prefers-color-scheme
[1A[2K[12/48] [desktop-chromium] › e2e/exhaustive-module12-personalization-a11y.spec.ts:91:1 › M12: Ajustes expone estado y cierra con Escape
[1A[2K[13/48] [desktop-chromium] › e2e/exhaustive-module12-personalization-a11y.spec.ts:100:1 › M12: teclado propio tiene diálogo nombrado y cierra con Escape
[1A[2K[14/48] [desktop-chromium] › e2e/exhaustive-module12-personalization-a11y.spec.ts:110:1 › M12: campo matemático principal tiene nombre accesible
[1A[2K[15/48] [desktop-chromium] › e2e/exhaustive-module12-personalization-a11y.spec.ts:118:1 › M12: resultado calculado queda dentro de una región anunciable
[1A[2K[16/48] [desktop-chromium] › e2e/exhaustive-module12-personalization-a11y.spec.ts:145:1 › M12: vibración y sonido guardan preferencia y sobreviven recarga
[1A[2K[17/48] [tablet-chromium] › e2e/exhaustive-module03-calculus.spec.ts:20:1 › suite original módulo 3: inventario de Cálculo refleja capacidades actuales
[1A[2K[18/48] [tablet-chromium] › e2e/exhaustive-module03-calculus.spec.ts:43:1 › suite original módulo 3: productoria de 1 a 5 se evalúa a 120 desde la UI
[1A[2K[19/48] [tablet-chromium] › e2e/exhaustive-module03-calculus.spec.ts:55:1 › suite original módulo 3: sumatoria de 1 a 5 se evalúa a 15 desde la UI
[1A[2K[20/48] [tablet-chromium] › e2e/exhaustive-module09-graphing.spec.ts:12:1 › suite original módulo 9: modos gráficos están activos y 2D renderiza
[1A[2K[21/48] [tablet-chromium] › e2e/exhaustive-module09-graphing.spec.ts:25:1 › suite original módulo 9: múltiples curvas 2D se renderizan juntas
[1A[2K[22/48] [tablet-chromium] › e2e/exhaustive-module10-keyboard.spec.ts:15:1 › módulo 10: la tecla % calcula porcentaje real (50% = 0.5)
[1A[2K[23/48] [tablet-chromium] › e2e/exhaustive-module10-keyboard.spec.ts:30:1 › módulo 10: ±(5) produce dos ramas matemáticas distintas
[1A[2K[24/48] [tablet-chromium] › e2e/exhaustive-module10-keyboard.spec.ts:46:1 › módulo 10: Productoria Π ya no aparece como pendiente
[1A[2K[25/48] [tablet-chromium] › e2e/exhaustive-module10-keyboard.spec.ts:55:1 › módulo 10: acciones no aritméticas de Álgebra exponen tooltip
[1A[2K[26/48] [tablet-chromium] › e2e/exhaustive-module12-personalization-a11y.spec.ts:21:1 › M12: preferencias visuales se aplican y persisten tras recarga
[1A[2K[27/48] [tablet-chromium] › e2e/exhaustive-module12-personalization-a11y.spec.ts:79:1 › M12: tema Automático sigue prefers-color-scheme
[1A[2K[28/48] [tablet-chromium] › e2e/exhaustive-module12-personalization-a11y.spec.ts:91:1 › M12: Ajustes expone estado y cierra con Escape
[1A[2K[29/48] [tablet-chromium] › e2e/exhaustive-module12-personalization-a11y.spec.ts:100:1 › M12: teclado propio tiene diálogo nombrado y cierra con Escape
[1A[2K[30/48] [tablet-chromium] › e2e/exhaustive-module12-personalization-a11y.spec.ts:110:1 › M12: campo matemático principal tiene nombre accesible
[1A[2K[31/48] [tablet-chromium] › e2e/exhaustive-module12-personalization-a11y.spec.ts:118:1 › M12: resultado calculado queda dentro de una región anunciable
[1A[2K[32/48] [tablet-chromium] › e2e/exhaustive-module12-personalization-a11y.spec.ts:145:1 › M12: vibración y sonido guardan preferencia y sobreviven recarga
[1A[2K[33/48] [mobile-chromium] › e2e/exhaustive-module03-calculus.spec.ts:20:1 › suite original módulo 3: inventario de Cálculo refleja capacidades actuales
[1A[2K[34/48] [mobile-chromium] › e2e/exhaustive-module03-calculus.spec.ts:43:1 › suite original módulo 3: productoria de 1 a 5 se evalúa a 120 desde la UI
[1A[2K[35/48] [mobile-chromium] › e2e/exhaustive-module03-calculus.spec.ts:55:1 › suite original módulo 3: sumatoria de 1 a 5 se evalúa a 15 desde la UI
[1A[2K[36/48] [mobile-chromium] › e2e/exhaustive-module09-graphing.spec.ts:12:1 › suite original módulo 9: modos gráficos están activos y 2D renderiza
[1A[2K[37/48] [mobile-chromium] › e2e/exhaustive-module09-graphing.spec.ts:25:1 › suite original módulo 9: múltiples curvas 2D se renderizan juntas
[1A[2K[38/48] [mobile-chromium] › e2e/exhaustive-module10-keyboard.spec.ts:15:1 › módulo 10: la tecla % calcula porcentaje real (50% = 0.5)
[1A[2K[39/48] [mobile-chromium] › e2e/exhaustive-module10-keyboard.spec.ts:30:1 › módulo 10: ±(5) produce dos ramas matemáticas distintas
[1A[2K[40/48] [mobile-chromium] › e2e/exhaustive-module10-keyboard.spec.ts:46:1 › módulo 10: Productoria Π ya no aparece como pendiente
[1A[2K[41/48] [mobile-chromium] › e2e/exhaustive-module10-keyboard.spec.ts:55:1 › módulo 10: acciones no aritméticas de Álgebra exponen tooltip
[1A[2K[42/48] [mobile-chromium] › e2e/exhaustive-module12-personalization-a11y.spec.ts:21:1 › M12: preferencias visuales se aplican y persisten tras recarga
[1A[2K[43/48] [mobile-chromium] › e2e/exhaustive-module12-personalization-a11y.spec.ts:79:1 › M12: tema Automático sigue prefers-color-scheme
[1A[2K[44/48] [mobile-chromium] › e2e/exhaustive-module12-personalization-a11y.spec.ts:91:1 › M12: Ajustes expone estado y cierra con Escape
[1A[2K[45/48] [mobile-chromium] › e2e/exhaustive-module12-personalization-a11y.spec.ts:100:1 › M12: teclado propio tiene diálogo nombrado y cierra con Escape
[1A[2K[46/48] [mobile-chromium] › e2e/exhaustive-module12-personalization-a11y.spec.ts:110:1 › M12: campo matemático principal tiene nombre accesible
[1A[2K[47/48] [mobile-chromium] › e2e/exhaustive-module12-personalization-a11y.spec.ts:118:1 › M12: resultado calculado queda dentro de una región anunciable
[1A[2K[48/48] [mobile-chromium] › e2e/exhaustive-module12-personalization-a11y.spec.ts:145:1 › M12: vibración y sonido guardan preferencia y sobreviven recarga
[1A[2K[49/48] (retries) [tablet-chromium] › e2e/exhaustive-module10-keyboard.spec.ts:30:1 › módulo 10: ±(5) produce dos ramas matemáticas distintas (retry #1)
[1A[2K  1) [tablet-chromium] › e2e/exhaustive-module10-keyboard.spec.ts:30:1 › módulo 10: ±(5) produce dos ramas matemáticas distintas 

    [31mTest timeout of 35000ms exceeded.[39m

    Error: page.waitForResponse: Test timeout of 35000ms exceeded.

      35 |   await dialog.getByRole("button", { name: "5", exact: true }).click();
      36 |
    > 37 |   const responsePromise = page.waitForResponse(r => r.url().includes("/api/v1/evaluate") && r.request().method() === "POST");
         |                                ^
      38 |   await dialog.getByRole("button", { name: "calcular", exact: true }).click();
      39 |   const body = await (await responsePromise).json();
      40 |   expect(body.success, JSON.stringify(body)).toBe(true);
        at /home/runner/work/precision-lab-plus/precision-lab-plus/frontend/e2e/exhaustive-module10-keyboard.spec.ts:37:32

    Error: locator.click: Test timeout of 35000ms exceeded.
    Call log:
    [2m  - waiting for getByRole('dialog', { name: 'Teclado matemático' }).getByRole('button', { name: 'calcular', exact: true })[22m
    [2m    - locator resolved to <button type="button" aria-label="calcular" title="ejecuta o resuelve la expresión actual" class="col-span-2 min-h-[38px] rounded-lg border shadow-sm transition-colors border-graph bg-graph text-paper a11y-key-sm font-semibold hover:bg-graph/90">…</button>[22m
    [2m  - attempting click action[22m
    [2m    2 × waiting for element to be visible, enabled and stable[22m
    [2m      - element is visible, enabled and stable[22m
    [2m      - scrolling into view if needed[22m
    [2m      - done scrolling[22m
    [2m      - <div tabindex="-1" id="ML__kw9z4t" aria-label="#@^{#0}}" data-keycap-value="#@^{#0}}" class="hide-shift MLK__keycap">…</div> from <div class="ML__keyboard is-visible is-math-mode can-undo can-paste">…</div> subtree intercepts pointer events[22m
    [2m    - retrying click action[22m
    [2m    - waiting 20ms[22m
    [2m    - waiting for element to be visible, enabled and stable[22m
    [2m    - element is visible, enabled and stable[22m
    [2m    - scrolling into view if needed[22m
    [2m    - done scrolling[22m
    [2m    - <div tabindex="-1" id="ML__kw9z4t" aria-label="#@^{#0}}" data-keycap-value="#@^{#0}}" class="hide-shift MLK__keycap">…</div> from <div class="ML__keyboard is-visible is-math-mode can-undo can-paste">…</div> subtree intercepts pointer events[22m
    [2m  2 × retrying click action[22m
    [2m      - waiting 100ms[22m
    [2m      - waiting for element to be visible, enabled and stable[22m
    [2m      - element is visible, enabled and stable[22m
    [2m      - scrolling into view if needed[22m
    [2m      - done scrolling[22m
    [2m      - <div class="MLK__rows">…</div> from <div class="ML__keyboard is-visible is-math-mode can-undo can-paste">…</div> subtree intercepts pointer events[22m
    [2m  15 × retrying click action[22m
    [2m       - waiting 500ms[22m
    [2m       - waiting for element to be visible, enabled and stable[22m
    [2m       - element is visible, enabled and stable[22m
    [2m       - scrolling into view if needed[22m
    [2m       - done scrolling[22m
    [2m       - <div tabindex="-1" id="ML__kw9z4t" aria-label="#@^{#0}}" data-keycap-value="#@^{#0}}" class="hide-shift MLK__keycap">…</div> from <div class="ML__keyboard is-visible is-math-mode can-undo can-paste">…</div> subtree intercepts pointer events[22m
    [2m     - retrying click action[22m
    [2m       - waiting 500ms[22m
    [2m       - waiting for element to be visible, enabled and stable[22m
    [2m       - element is visible, enabled and stable[22m
    [2m       - scrolling into view if needed[22m
    [2m       - done scrolling[22m
    [2m       - <div tabindex="-1" id="ML__kw9z4t" aria-label="#@^{#0}}" data-keycap-value="#@^{#0}}" class="hide-shift MLK__keycap">…</div> from <div class="ML__keyboard is-visible is-math-mode can-undo can-paste">…</div> subtree intercepts pointer events[22m
    [2m     - retrying click action[22m
    [2m       - waiting 500ms[22m
    [2m       - waiting for element to be visible, enabled and stable[22m
    [2m       - element is visible, enabled and stable[22m
    [2m       - scrolling into view if needed[22m
    [2m       - done scrolling[22m
    [2m       - <div class="MLK__rows">…</div> from <div class="ML__keyboard is-visible is-math-mode can-undo can-paste">…</div> subtree intercepts pointer events[22m
    [2m     - retrying click action[22m
    [2m       - waiting 500ms[22m
    [2m       - waiting for element to be visible, enabled and stable[22m
    [2m       - element is visible, enabled and stable[22m
    [2m       - scrolling into view if needed[22m
    [2m       - done scrolling[22m
    [2m       - <div class="MLK__rows">…</div> from <div class="ML__keyboard is-visible is-math-mode can-undo can-paste">…</div> subtree intercepts pointer events[22m
    [2m  - retrying click action[22m
    [2m    - waiting 500ms[22m
    [2m    - waiting for element to be visible, enabled and stable[22m
    [2m    - element is visible, enabled and stable[22m
    [2m    - scrolling into view if needed[22m
    [2m    - done scrolling[22m
    [2m    - <div tabindex="-1" id="ML__kw9z4t" aria-label="#@^{#0}}" data-keycap-value="#@^{#0}}" class="hide-shift MLK__keycap">…</div> from <div class="ML__keyboard is-visible is-math-mode can-undo can-paste">…</div> subtree intercepts pointer events[22m
    [2m  - retrying click action[22m
    [2m    - waiting 500ms[22m


      36 |
      37 |   const responsePromise = page.waitForResponse(r => r.url().includes("/api/v1/evaluate") && r.request().method() === "POST");
    > 38 |   await dialog.getByRole("button", { name: "calcular", exact: true }).click();
         |                                                                       ^
      39 |   const body = await (await responsePromise).json();
      40 |   expect(body.success, JSON.stringify(body)).toBe(true);
      41 |   const text = String(body.result_text ?? "").replace(/\s/g, "");
        at /home/runner/work/precision-lab-plus/precision-lab-plus/frontend/e2e/exhaustive-module10-keyboard.spec.ts:38:71

    attachment #1: screenshot (image/png) ──────────────────────────────────────────────────────────
    test-results/exhaustive-module10-keyboa-081b5-ramas-matemáticas-distintas-tablet-chromium/test-failed-1.png
    ────────────────────────────────────────────────────────────────────────────────────────────────

    Error Context: test-results/exhaustive-module10-keyboa-081b5-ramas-matemáticas-distintas-tablet-chromium/error-context.md

    attachment #3: trace (application/zip) ─────────────────────────────────────────────────────────
    test-results/exhaustive-module10-keyboa-081b5-ramas-matemáticas-distintas-tablet-chromium/trace.zip
    Usage:

        npx playwright show-trace test-results/exhaustive-module10-keyboa-081b5-ramas-matemáticas-distintas-tablet-chromium/trace.zip

    ────────────────────────────────────────────────────────────────────────────────────────────────


[1A[2K  1 flaky
    [tablet-chromium] › e2e/exhaustive-module10-keyboard.spec.ts:30:1 › módulo 10: ±(5) produce dos ramas matemáticas distintas 
  47 passed (1.1m)
~~~
