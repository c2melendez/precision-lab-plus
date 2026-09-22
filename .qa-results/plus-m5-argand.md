# QA Plus — M5 Argand gate

- SHA: 
- E2E: **failure**

~~~text
[1A[2K[WebServer] INFO:     Started server process [3167]

[1A[2K[WebServer] INFO:     Waiting for application startup.
[WebServer] INFO:     Application startup complete.

[1A[2K[WebServer] INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)


Running 6 tests using 2 workers

[1A[2K[1/6] [desktop-chromium] › e2e/exhaustive-module05-complex.spec.ts:20:1 › suite original módulo 5: inventario complejo compartido está activo
[1A[2K[2/6] [desktop-chromium] › e2e/exhaustive-module05-complex.spec.ts:40:1 › suite original módulo 5: Argand 3+4i usa ejes Re e Im
[1A[2K[3/6] [tablet-chromium] › e2e/exhaustive-module05-complex.spec.ts:20:1 › suite original módulo 5: inventario complejo compartido está activo
[1A[2K[4/6] [tablet-chromium] › e2e/exhaustive-module05-complex.spec.ts:40:1 › suite original módulo 5: Argand 3+4i usa ejes Re e Im
[1A[2K[5/6] [desktop-chromium] › e2e/exhaustive-module05-complex.spec.ts:40:1 › suite original módulo 5: Argand 3+4i usa ejes Re e Im (retry #1)
[1A[2K[6/6] [tablet-chromium] › e2e/exhaustive-module05-complex.spec.ts:40:1 › suite original módulo 5: Argand 3+4i usa ejes Re e Im (retry #1)
[1A[2K  1) [desktop-chromium] › e2e/exhaustive-module05-complex.spec.ts:40:1 › suite original módulo 5: Argand 3+4i usa ejes Re e Im 

    Error: [2mexpect([22m[31mreceived[39m[2m).[22mtoEqual[2m([22m[32mexpected[39m[2m) // deep equality[22m

    [32m- Expected  - 2[39m
    [31m+ Received  + 2[39m

    [2m  Object {[22m
    [32m-   "x": "Re",[39m
    [32m-   "y": "Im",[39m
    [31m+   "x": "Click to enter X axis title",[39m
    [31m+   "y": "Click to enter Y axis title",[39m
    [2m  }[22m

      81 |     };
      82 |   });
    > 83 |   expect(axisTitles).toEqual({ x: "Re", y: "Im" });
         |                      ^
      84 | });
      85 |
        at /home/runner/work/precision-lab-plus/precision-lab-plus/frontend/e2e/exhaustive-module05-complex.spec.ts:83:22

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

    Error: [2mexpect([22m[31mreceived[39m[2m).[22mtoEqual[2m([22m[32mexpected[39m[2m) // deep equality[22m

    [32m- Expected  - 2[39m
    [31m+ Received  + 2[39m

    [2m  Object {[22m
    [32m-   "x": "Re",[39m
    [32m-   "y": "Im",[39m
    [31m+   "x": "Click to enter X axis title",[39m
    [31m+   "y": "Click to enter Y axis title",[39m
    [2m  }[22m

      81 |     };
      82 |   });
    > 83 |   expect(axisTitles).toEqual({ x: "Re", y: "Im" });
         |                      ^
      84 | });
      85 |
        at /home/runner/work/precision-lab-plus/precision-lab-plus/frontend/e2e/exhaustive-module05-complex.spec.ts:83:22

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

    Error: [2mexpect([22m[31mreceived[39m[2m).[22mtoEqual[2m([22m[32mexpected[39m[2m) // deep equality[22m

    [32m- Expected  - 2[39m
    [31m+ Received  + 2[39m

    [2m  Object {[22m
    [32m-   "x": "Re",[39m
    [32m-   "y": "Im",[39m
    [31m+   "x": "Click to enter X axis title",[39m
    [31m+   "y": "Click to enter Y axis title",[39m
    [2m  }[22m

      81 |     };
      82 |   });
    > 83 |   expect(axisTitles).toEqual({ x: "Re", y: "Im" });
         |                      ^
      84 | });
      85 |
        at /home/runner/work/precision-lab-plus/precision-lab-plus/frontend/e2e/exhaustive-module05-complex.spec.ts:83:22

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

    Error: [2mexpect([22m[31mreceived[39m[2m).[22mtoEqual[2m([22m[32mexpected[39m[2m) // deep equality[22m

    [32m- Expected  - 2[39m
    [31m+ Received  + 2[39m

    [2m  Object {[22m
    [32m-   "x": "Re",[39m
    [32m-   "y": "Im",[39m
    [31m+   "x": "Click to enter X axis title",[39m
    [31m+   "y": "Click to enter Y axis title",[39m
    [2m  }[22m

      81 |     };
      82 |   });
    > 83 |   expect(axisTitles).toEqual({ x: "Re", y: "Im" });
         |                      ^
      84 | });
      85 |
        at /home/runner/work/precision-lab-plus/precision-lab-plus/frontend/e2e/exhaustive-module05-complex.spec.ts:83:22

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

    Error: [2mexpect([22m[31mreceived[39m[2m).[22mtoEqual[2m([22m[32mexpected[39m[2m) // deep equality[22m

    [32m- Expected  - 2[39m
    [31m+ Received  + 2[39m

    [2m  Object {[22m
    [32m-   "x": "Re",[39m
    [32m-   "y": "Im",[39m
    [31m+   "x": "Click to enter X axis title",[39m
    [31m+   "y": "Click to enter Y axis title",[39m
    [2m  }[22m

      81 |     };
      82 |   });
    > 83 |   expect(axisTitles).toEqual({ x: "Re", y: "Im" });
         |                      ^
      84 | });
      85 |
        at /home/runner/work/precision-lab-plus/precision-lab-plus/frontend/e2e/exhaustive-module05-complex.spec.ts:83:22

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

    Error: [2mexpect([22m[31mreceived[39m[2m).[22mtoEqual[2m([22m[32mexpected[39m[2m) // deep equality[22m

    [32m- Expected  - 2[39m
    [31m+ Received  + 2[39m

    [2m  Object {[22m
    [32m-   "x": "Re",[39m
    [32m-   "y": "Im",[39m
    [31m+   "x": "Click to enter X axis title",[39m
    [31m+   "y": "Click to enter Y axis title",[39m
    [2m  }[22m

      81 |     };
      82 |   });
    > 83 |   expect(axisTitles).toEqual({ x: "Re", y: "Im" });
         |                      ^
      84 | });
      85 |
        at /home/runner/work/precision-lab-plus/precision-lab-plus/frontend/e2e/exhaustive-module05-complex.spec.ts:83:22

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
  3 passed (20.3s)
~~~
