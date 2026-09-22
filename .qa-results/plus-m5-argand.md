# QA Plus — M5 Argand gate

- SHA: 
- E2E: **failure**

~~~text
[1A[2K[WebServer] INFO:     Started server process [3499]
[WebServer] INFO:     Waiting for application startup.

[1A[2K[WebServer] INFO:     Application startup complete.

[1A[2K[WebServer] INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)


Running 6 tests using 2 workers

[1A[2K[1/6] [desktop-chromium] › e2e/exhaustive-module05-complex.spec.ts:40:1 › suite original módulo 5: Argand 3+4i usa ejes Re e Im
[1A[2K[2/6] [desktop-chromium] › e2e/exhaustive-module05-complex.spec.ts:20:1 › suite original módulo 5: inventario complejo compartido está activo
[1A[2K[3/6] [tablet-chromium] › e2e/exhaustive-module05-complex.spec.ts:20:1 › suite original módulo 5: inventario complejo compartido está activo
[1A[2K[4/6] [tablet-chromium] › e2e/exhaustive-module05-complex.spec.ts:40:1 › suite original módulo 5: Argand 3+4i usa ejes Re e Im
[1A[2K[5/6] [desktop-chromium] › e2e/exhaustive-module05-complex.spec.ts:40:1 › suite original módulo 5: Argand 3+4i usa ejes Re e Im (retry #1)
[1A[2K[6/6] [tablet-chromium] › e2e/exhaustive-module05-complex.spec.ts:40:1 › suite original módulo 5: Argand 3+4i usa ejes Re e Im (retry #1)
[1A[2K  1) [desktop-chromium] › e2e/exhaustive-module05-complex.spec.ts:40:1 › suite original módulo 5: Argand 3+4i usa ejes Re e Im 

    Error: [2mexpect([22m[31mlocator[39m[2m).[22mtoBeVisible[2m()[22m failed

    Locator:  getByText('Re', { exact: true }).first()
    Expected: visible
    Received: <element(s) not found>
    Timeout:  12000ms

    Call log:
    [2m  - Expect "toBeVisible" with timeout 12000ms[22m
    [2m  - waiting for getByText('Re', { exact: true }).first()[22m


      67 |   expect(body.graph_data?.y_axis_label).toBe("Im");
      68 |
    > 69 |   await expect(page.getByText("Re", { exact: true }).first()).toBeVisible({ timeout: 12000 });
         |                                                               ^
      70 |   await expect(page.getByText("Im", { exact: true }).first()).toBeVisible({ timeout: 12000 });
      71 | });
      72 |
        at /home/runner/work/precision-lab-plus/precision-lab-plus/frontend/e2e/exhaustive-module05-complex.spec.ts:69:63

    attachment #1: screenshot (image/png) ──────────────────────────────────────────────────────────
    test-results/exhaustive-module05-comple-ee4ee-rgand-3-4i-usa-ejes-Re-e-Im-desktop-chromium/test-failed-1.png
    ────────────────────────────────────────────────────────────────────────────────────────────────

    attachment #2: video (video/webm) ──────────────────────────────────────────────────────────────
    test-results/exhaustive-module05-comple-ee4ee-rgand-3-4i-usa-ejes-Re-e-Im-desktop-chromium/video.webm
    ────────────────────────────────────────────────────────────────────────────────────────────────

    Error Context: test-results/exhaustive-module05-comple-ee4ee-rgand-3-4i-usa-ejes-Re-e-Im-desktop-chromium/error-context.md

    attachment #4: trace (application/zip) ─────────────────────────────────────────────────────────
    test-results/exhaustive-module05-comple-ee4ee-rgand-3-4i-usa-ejes-Re-e-Im-desktop-chromium/trace.zip
    Usage:

        npx playwright show-trace test-results/exhaustive-module05-comple-ee4ee-rgand-3-4i-usa-ejes-Re-e-Im-desktop-chromium/trace.zip

    ────────────────────────────────────────────────────────────────────────────────────────────────

    Retry #1 ───────────────────────────────────────────────────────────────────────────────────────

    Error: [2mexpect([22m[31mlocator[39m[2m).[22mtoBeVisible[2m()[22m failed

    Locator:  getByText('Re', { exact: true }).first()
    Expected: visible
    Received: <element(s) not found>
    Timeout:  12000ms

    Call log:
    [2m  - Expect "toBeVisible" with timeout 12000ms[22m
    [2m  - waiting for getByText('Re', { exact: true }).first()[22m


      67 |   expect(body.graph_data?.y_axis_label).toBe("Im");
      68 |
    > 69 |   await expect(page.getByText("Re", { exact: true }).first()).toBeVisible({ timeout: 12000 });
         |                                                               ^
      70 |   await expect(page.getByText("Im", { exact: true }).first()).toBeVisible({ timeout: 12000 });
      71 | });
      72 |
        at /home/runner/work/precision-lab-plus/precision-lab-plus/frontend/e2e/exhaustive-module05-complex.spec.ts:69:63

    attachment #1: screenshot (image/png) ──────────────────────────────────────────────────────────
    test-results/exhaustive-module05-comple-ee4ee-rgand-3-4i-usa-ejes-Re-e-Im-desktop-chromium-retry1/test-failed-1.png
    ────────────────────────────────────────────────────────────────────────────────────────────────

    attachment #2: video (video/webm) ──────────────────────────────────────────────────────────────
    test-results/exhaustive-module05-comple-ee4ee-rgand-3-4i-usa-ejes-Re-e-Im-desktop-chromium-retry1/video.webm
    ────────────────────────────────────────────────────────────────────────────────────────────────

    Error Context: test-results/exhaustive-module05-comple-ee4ee-rgand-3-4i-usa-ejes-Re-e-Im-desktop-chromium-retry1/error-context.md

    attachment #4: trace (application/zip) ─────────────────────────────────────────────────────────
    test-results/exhaustive-module05-comple-ee4ee-rgand-3-4i-usa-ejes-Re-e-Im-desktop-chromium-retry1/trace.zip
    Usage:

        npx playwright show-trace test-results/exhaustive-module05-comple-ee4ee-rgand-3-4i-usa-ejes-Re-e-Im-desktop-chromium-retry1/trace.zip

    ────────────────────────────────────────────────────────────────────────────────────────────────


[1A[2K[7/6] (retries) [mobile-chromium] › e2e/exhaustive-module05-complex.spec.ts:20:1 › suite original módulo 5: inventario complejo compartido está activo
[1A[2K[8/6] (retries) [mobile-chromium] › e2e/exhaustive-module05-complex.spec.ts:40:1 › suite original módulo 5: Argand 3+4i usa ejes Re e Im
[1A[2K  2) [tablet-chromium] › e2e/exhaustive-module05-complex.spec.ts:40:1 › suite original módulo 5: Argand 3+4i usa ejes Re e Im 

    Error: [2mexpect([22m[31mlocator[39m[2m).[22mtoBeVisible[2m()[22m failed

    Locator:  getByText('Re', { exact: true }).first()
    Expected: visible
    Received: <element(s) not found>
    Timeout:  12000ms

    Call log:
    [2m  - Expect "toBeVisible" with timeout 12000ms[22m
    [2m  - waiting for getByText('Re', { exact: true }).first()[22m


      67 |   expect(body.graph_data?.y_axis_label).toBe("Im");
      68 |
    > 69 |   await expect(page.getByText("Re", { exact: true }).first()).toBeVisible({ timeout: 12000 });
         |                                                               ^
      70 |   await expect(page.getByText("Im", { exact: true }).first()).toBeVisible({ timeout: 12000 });
      71 | });
      72 |
        at /home/runner/work/precision-lab-plus/precision-lab-plus/frontend/e2e/exhaustive-module05-complex.spec.ts:69:63

    attachment #1: screenshot (image/png) ──────────────────────────────────────────────────────────
    test-results/exhaustive-module05-comple-ee4ee-rgand-3-4i-usa-ejes-Re-e-Im-tablet-chromium/test-failed-1.png
    ────────────────────────────────────────────────────────────────────────────────────────────────

    attachment #2: video (video/webm) ──────────────────────────────────────────────────────────────
    test-results/exhaustive-module05-comple-ee4ee-rgand-3-4i-usa-ejes-Re-e-Im-tablet-chromium/video.webm
    ────────────────────────────────────────────────────────────────────────────────────────────────

    Error Context: test-results/exhaustive-module05-comple-ee4ee-rgand-3-4i-usa-ejes-Re-e-Im-tablet-chromium/error-context.md

    attachment #4: trace (application/zip) ─────────────────────────────────────────────────────────
    test-results/exhaustive-module05-comple-ee4ee-rgand-3-4i-usa-ejes-Re-e-Im-tablet-chromium/trace.zip
    Usage:

        npx playwright show-trace test-results/exhaustive-module05-comple-ee4ee-rgand-3-4i-usa-ejes-Re-e-Im-tablet-chromium/trace.zip

    ────────────────────────────────────────────────────────────────────────────────────────────────

    Retry #1 ───────────────────────────────────────────────────────────────────────────────────────

    Error: [2mexpect([22m[31mlocator[39m[2m).[22mtoBeVisible[2m()[22m failed

    Locator:  getByText('Re', { exact: true }).first()
    Expected: visible
    Received: <element(s) not found>
    Timeout:  12000ms

    Call log:
    [2m  - Expect "toBeVisible" with timeout 12000ms[22m
    [2m  - waiting for getByText('Re', { exact: true }).first()[22m


      67 |   expect(body.graph_data?.y_axis_label).toBe("Im");
      68 |
    > 69 |   await expect(page.getByText("Re", { exact: true }).first()).toBeVisible({ timeout: 12000 });
         |                                                               ^
      70 |   await expect(page.getByText("Im", { exact: true }).first()).toBeVisible({ timeout: 12000 });
      71 | });
      72 |
        at /home/runner/work/precision-lab-plus/precision-lab-plus/frontend/e2e/exhaustive-module05-complex.spec.ts:69:63

    attachment #1: screenshot (image/png) ──────────────────────────────────────────────────────────
    test-results/exhaustive-module05-comple-ee4ee-rgand-3-4i-usa-ejes-Re-e-Im-tablet-chromium-retry1/test-failed-1.png
    ────────────────────────────────────────────────────────────────────────────────────────────────

    attachment #2: video (video/webm) ──────────────────────────────────────────────────────────────
    test-results/exhaustive-module05-comple-ee4ee-rgand-3-4i-usa-ejes-Re-e-Im-tablet-chromium-retry1/video.webm
    ────────────────────────────────────────────────────────────────────────────────────────────────

    Error Context: test-results/exhaustive-module05-comple-ee4ee-rgand-3-4i-usa-ejes-Re-e-Im-tablet-chromium-retry1/error-context.md

    attachment #4: trace (application/zip) ─────────────────────────────────────────────────────────
    test-results/exhaustive-module05-comple-ee4ee-rgand-3-4i-usa-ejes-Re-e-Im-tablet-chromium-retry1/trace.zip
    Usage:

        npx playwright show-trace test-results/exhaustive-module05-comple-ee4ee-rgand-3-4i-usa-ejes-Re-e-Im-tablet-chromium-retry1/trace.zip

    ────────────────────────────────────────────────────────────────────────────────────────────────


[1A[2K[9/6] (retries) [mobile-chromium] › e2e/exhaustive-module05-complex.spec.ts:40:1 › suite original módulo 5: Argand 3+4i usa ejes Re e Im (retry #1)
[1A[2K  3) [mobile-chromium] › e2e/exhaustive-module05-complex.spec.ts:40:1 › suite original módulo 5: Argand 3+4i usa ejes Re e Im 

    Error: [2mexpect([22m[31mlocator[39m[2m).[22mtoBeVisible[2m()[22m failed

    Locator:  getByText('Re', { exact: true }).first()
    Expected: visible
    Received: <element(s) not found>
    Timeout:  12000ms

    Call log:
    [2m  - Expect "toBeVisible" with timeout 12000ms[22m
    [2m  - waiting for getByText('Re', { exact: true }).first()[22m


      67 |   expect(body.graph_data?.y_axis_label).toBe("Im");
      68 |
    > 69 |   await expect(page.getByText("Re", { exact: true }).first()).toBeVisible({ timeout: 12000 });
         |                                                               ^
      70 |   await expect(page.getByText("Im", { exact: true }).first()).toBeVisible({ timeout: 12000 });
      71 | });
      72 |
        at /home/runner/work/precision-lab-plus/precision-lab-plus/frontend/e2e/exhaustive-module05-complex.spec.ts:69:63

    attachment #1: screenshot (image/png) ──────────────────────────────────────────────────────────
    test-results/exhaustive-module05-comple-ee4ee-rgand-3-4i-usa-ejes-Re-e-Im-mobile-chromium/test-failed-1.png
    ────────────────────────────────────────────────────────────────────────────────────────────────

    attachment #2: video (video/webm) ──────────────────────────────────────────────────────────────
    test-results/exhaustive-module05-comple-ee4ee-rgand-3-4i-usa-ejes-Re-e-Im-mobile-chromium/video.webm
    ────────────────────────────────────────────────────────────────────────────────────────────────

    Error Context: test-results/exhaustive-module05-comple-ee4ee-rgand-3-4i-usa-ejes-Re-e-Im-mobile-chromium/error-context.md

    attachment #4: trace (application/zip) ─────────────────────────────────────────────────────────
    test-results/exhaustive-module05-comple-ee4ee-rgand-3-4i-usa-ejes-Re-e-Im-mobile-chromium/trace.zip
    Usage:

        npx playwright show-trace test-results/exhaustive-module05-comple-ee4ee-rgand-3-4i-usa-ejes-Re-e-Im-mobile-chromium/trace.zip

    ────────────────────────────────────────────────────────────────────────────────────────────────

    Retry #1 ───────────────────────────────────────────────────────────────────────────────────────

    Error: [2mexpect([22m[31mlocator[39m[2m).[22mtoBeVisible[2m()[22m failed

    Locator:  getByText('Re', { exact: true }).first()
    Expected: visible
    Received: <element(s) not found>
    Timeout:  12000ms

    Call log:
    [2m  - Expect "toBeVisible" with timeout 12000ms[22m
    [2m  - waiting for getByText('Re', { exact: true }).first()[22m


      67 |   expect(body.graph_data?.y_axis_label).toBe("Im");
      68 |
    > 69 |   await expect(page.getByText("Re", { exact: true }).first()).toBeVisible({ timeout: 12000 });
         |                                                               ^
      70 |   await expect(page.getByText("Im", { exact: true }).first()).toBeVisible({ timeout: 12000 });
      71 | });
      72 |
        at /home/runner/work/precision-lab-plus/precision-lab-plus/frontend/e2e/exhaustive-module05-complex.spec.ts:69:63

    attachment #1: screenshot (image/png) ──────────────────────────────────────────────────────────
    test-results/exhaustive-module05-comple-ee4ee-rgand-3-4i-usa-ejes-Re-e-Im-mobile-chromium-retry1/test-failed-1.png
    ────────────────────────────────────────────────────────────────────────────────────────────────

    attachment #2: video (video/webm) ──────────────────────────────────────────────────────────────
    test-results/exhaustive-module05-comple-ee4ee-rgand-3-4i-usa-ejes-Re-e-Im-mobile-chromium-retry1/video.webm
    ────────────────────────────────────────────────────────────────────────────────────────────────

    Error Context: test-results/exhaustive-module05-comple-ee4ee-rgand-3-4i-usa-ejes-Re-e-Im-mobile-chromium-retry1/error-context.md

    attachment #4: trace (application/zip) ─────────────────────────────────────────────────────────
    test-results/exhaustive-module05-comple-ee4ee-rgand-3-4i-usa-ejes-Re-e-Im-mobile-chromium-retry1/trace.zip
    Usage:

        npx playwright show-trace test-results/exhaustive-module05-comple-ee4ee-rgand-3-4i-usa-ejes-Re-e-Im-mobile-chromium-retry1/trace.zip

    ────────────────────────────────────────────────────────────────────────────────────────────────


[1A[2K  3 failed
    [desktop-chromium] › e2e/exhaustive-module05-complex.spec.ts:40:1 › suite original módulo 5: Argand 3+4i usa ejes Re e Im 
    [tablet-chromium] › e2e/exhaustive-module05-complex.spec.ts:40:1 › suite original módulo 5: Argand 3+4i usa ejes Re e Im 
    [mobile-chromium] › e2e/exhaustive-module05-complex.spec.ts:40:1 › suite original módulo 5: Argand 3+4i usa ejes Re e Im 
  3 passed (1.1m)
~~~
