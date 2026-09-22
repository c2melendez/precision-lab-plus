# QA fast CI diagnostic — Plus

- npm_ci: 0
- typecheck: 0
- unit: 1
- build: 0

## npm-ci
~~~text
npm warn deprecated inflight@1.0.6: This module is not supported, and leaks memory. Do not use it. Check out lru-cache if you want a good and tested way to coalesce async requests by a key value, which is much more comprehensive and powerful.
npm warn deprecated @humanwhocodes/config-array@0.13.0: Use @eslint/config-array instead
npm warn deprecated rimraf@3.0.2: Rimraf versions prior to v4 are no longer supported
npm warn deprecated whatwg-encoding@3.1.1: Use @exodus/bytes instead for a more spec-conformant and faster implementation
npm warn deprecated glob@7.2.3: Old versions of glob are not supported, and contain widely publicized security vulnerabilities, which have been fixed in the current version. Please update. Support for old versions may be purchased (at exorbitant rates) by contacting i@izs.me
npm warn deprecated @humanwhocodes/object-schema@2.0.3: Use @eslint/object-schema instead
npm warn deprecated glob@11.1.0: Old versions of glob are not supported, and contain widely publicized security vulnerabilities, which have been fixed in the current version. Please update. Support for old versions may be purchased (at exorbitant rates) by contacting i@izs.me
npm warn deprecated eslint@8.57.1: This version is no longer supported. Please see https://eslint.org/version-support for other options.

added 640 packages, and audited 641 packages in 5s

171 packages are looking for funding
  run `npm fund` for details

8 vulnerabilities (3 moderate, 4 high, 1 critical)

To address issues that do not require attention, run:
  npm audit fix

To address all issues (including breaking changes), run:
  npm audit fix --force

Run `npm audit` for details.
~~~

## typecheck
~~~text

> precision-lab-frontend@0.1.0 typecheck
> tsc --noEmit

~~~

## unit
~~~text

> precision-lab-frontend@0.1.0 test
> vitest run


[1m[7m[36m RUN [39m[27m[22m [36mv2.1.9 [39m[90m/home/runner/work/precision-lab-plus/precision-lab-plus/frontend[39m

 [32m✓[39m src/__tests__/ResultPanel.test.tsx [2m([22m[2m19 tests[22m[2m)[22m[33m 433[2mms[22m[39m
 [32m✓[39m src/__tests__/GraphMode.test.tsx [2m([22m[2m7 tests[22m[2m)[22m[33m 1178[2mms[22m[39m
 [32m✓[39m src/__tests__/BasicMode.test.tsx [2m([22m[2m16 tests[22m[2m)[22m[33m 1015[2mms[22m[39m
   [33m[2m✓[22m[39m BasicMode[2m > [22marma el payload correcto contra /evaluate [33m324[2mms[22m[39m
 [32m✓[39m src/__tests__/calculusIntent.test.ts [2m([22m[2m20 tests[22m[2m)[22m[90m 267[2mms[22m[39m
 [32m✓[39m src/__tests__/MatrixMode.test.tsx [2m([22m[2m5 tests[22m[2m)[22m[33m 436[2mms[22m[39m
 [31m❯[39m src/__tests__/exhaustive-module10-keyboard-parity.test.ts [2m([22m[2m25 tests[22m[2m | [22m[31m1 failed[39m[2m)[22m[90m 56[2mms[22m[39m
[31m   [31m×[31m Suite exhaustiva original — Módulo 10: teclado ↔ motor (Plus frontend)[2m > [22msumatoria/productoria sobreviven serialización alternativa de MathLive[90m 21[2mms[22m[31m[39m
[31m     → expected 's u m_(i=1)^5i' to be 'sum(i,i,1,5)' // Object.is equality[39m
 [32m✓[39m src/__tests__/e2e.test.tsx [2m([22m[2m1 test[22m[2m)[22m[33m 657[2mms[22m[39m
   [33m[2m✓[22m[39m E2E mínimo — Derivada (sección 15)[2m > [22mx**2 en Derivada -> MathResponse real -> steps renderizados -> historial -> reuseEntry reejecuta [33m656[2mms[22m[39m
 [32m✓[39m src/__tests__/historyStore.test.ts [2m([22m[2m8 tests[22m[2m)[22m[90m 22[2mms[22m[39m
 [32m✓[39m src/__tests__/IntegralMode.test.tsx [2m([22m[2m5 tests[22m[2m)[22m[33m 812[2mms[22m[39m
 [32m✓[39m src/__tests__/SystemMode.test.tsx [2m([22m[2m4 tests[22m[2m)[22m[33m 889[2mms[22m[39m
   [33m[2m✓[22m[39m SystemMode[2m > [22marma el payload correcto contra /solve/system con 2 ecuaciones y 2 variables [33m371[2mms[22m[39m
 [32m✓[39m src/__tests__/useRecentKeysStore.test.ts [2m([22m[2m9 tests[22m[2m)[22m[90m 21[2mms[22m[39m
 [32m✓[39m src/__tests__/unitConversion.test.ts [2m([22m[2m22 tests[22m[2m)[22m[90m 22[2mms[22m[39m
 [32m✓[39m src/__tests__/EquationMode.test.tsx [2m([22m[2m5 tests[22m[2m)[22m[33m 830[2mms[22m[39m
   [33m[2m✓[22m[39m EquationMode[2m > [22marma el payload correcto contra /solve sin variable (inferencia automática) [33m312[2mms[22m[39m
 [32m✓[39m src/__tests__/LimitMode.test.tsx [2m([22m[2m5 tests[22m[2m)[22m[33m 986[2mms[22m[39m
   [33m[2m✓[22m[39m LimitMode[2m > [22marma el payload correcto contra /limit con un punto finito [33m337[2mms[22m[39m
 [32m✓[39m src/__tests__/NaturalMathField.test.ts [2m([22m[2m13 tests[22m[2m)[22m[90m 33[2mms[22m[39m
 [32m✓[39m src/__tests__/KeyboardBasicPanelV5.test.tsx [2m([22m[2m5 tests[22m[2m)[22m[33m 703[2mms[22m[39m
   [33m[2m✓[22m[39m KeyboardBasicPanel V5[2m > [22mmantiene el inventario básico acordado y usa Enter en doble columna [33m441[2mms[22m[39m
 [32m✓[39m src/__tests__/contract.test.ts [2m([22m[2m4 tests[22m[2m)[22m[90m 10[2mms[22m[39m
 [32m✓[39m src/__tests__/DerivativeMode.test.tsx [2m([22m[2m4 tests[22m[2m)[22m[33m 707[2mms[22m[39m
[90mstderr[2m | src/__tests__/GraphViewer.test.tsx[2m > [22m[2mGraphViewer[2m > [22m[2mel botón 'Descargar PNG' llama a Plotly.toImage
[22m[39mError: Not implemented: navigation (except hash changes)
    at module.exports (/home/runner/work/precision-lab-plus/precision-lab-plus/frontend/node_modules/jsdom/lib/jsdom/browser/not-implemented.js:9:17)
    at navigateFetch (/home/runner/work/precision-lab-plus/precision-lab-plus/frontend/node_modules/jsdom/lib/jsdom/living/window/navigation.js:77:3)
    at exports.navigate (/home/runner/work/precision-lab-plus/precision-lab-plus/frontend/node_modules/jsdom/lib/jsdom/living/window/navigation.js:55:3)
    at Timeout._onTimeout (/home/runner/work/precision-lab-plus/precision-lab-plus/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLHyperlinkElementUtils-impl.js:81:7)
    at listOnTimeout (node:internal/timers:585:17)
    at processTimers (node:internal/timers:521:7) [90mundefined[39m

 [32m✓[39m src/__tests__/GraphViewer.test.tsx [2m([22m[2m4 tests[22m[2m)[22m[33m 402[2mms[22m[39m
 [32m✓[39m src/__tests__/client.test.ts [2m([22m[2m6 tests[22m[2m)[22m[90m 11[2mms[22m[39m
 [32m✓[39m src/__tests__/History.test.tsx [2m([22m[2m4 tests[22m[2m)[22m[90m 230[2mms[22m[39m
 [32m✓[39m src/__tests__/MathKeyboard.test.tsx [2m([22m[2m4 tests[22m[2m)[22m[33m 383[2mms[22m[39m
 [32m✓[39m src/__tests__/KeyboardParityV5.test.ts [2m([22m[2m5 tests[22m[2m)[22m[90m 5[2mms[22m[39m
 [32m✓[39m src/__tests__/exhaustive-module10-keyboard-inventory.test.ts [2m([22m[2m5 tests[22m[2m)[22m[90m 23[2mms[22m[39m
 [32m✓[39m src/__tests__/KeyboardInventoryV5.test.ts [2m([22m[2m6 tests[22m[2m)[22m[90m 19[2mms[22m[39m
 [32m✓[39m src/exhaustive-module08-units.test.ts [2m([22m[2m5 tests[22m[2m)[22m[90m 7[2mms[22m[39m
 [32m✓[39m src/__tests__/exhaustive-module14-branding-natural-text.test.tsx [2m([22m[2m1 test[22m[2m)[22m[90m 227[2mms[22m[39m
 [32m✓[39m src/__tests__/BrandingV521.test.tsx [2m([22m[2m1 test[22m[2m)[22m[90m 126[2mms[22m[39m
 [32m✓[39m src/__tests__/MathRenderer.test.tsx [2m([22m[2m3 tests[22m[2m)[22m[90m 77[2mms[22m[39m
 [32m✓[39m src/__tests__/fractionDisplay.test.ts [2m([22m[2m9 tests[22m[2m)[22m[90m 15[2mms[22m[39m
 [32m✓[39m src/__tests__/systemSplit.test.ts [2m([22m[2m6 tests[22m[2m)[22m[90m 8[2mms[22m[39m
 [32m✓[39m src/__tests__/exhaustive-module11-layout-responsive.test.ts [2m([22m[2m2 tests[22m[2m)[22m[90m 4[2mms[22m[39m
 [32m✓[39m src/__tests__/LayoutDefaultV521.test.ts [2m([22m[2m2 tests[22m[2m)[22m[90m 6[2mms[22m[39m

[31m⎯⎯⎯⎯⎯⎯⎯[1m[7m Failed Tests 1 [27m[22m⎯⎯⎯⎯⎯⎯⎯[39m

[31m[1m[7m FAIL [27m[22m[39m src/__tests__/exhaustive-module10-keyboard-parity.test.ts[2m > [22mSuite exhaustiva original — Módulo 10: teclado ↔ motor (Plus frontend)[2m > [22msumatoria/productoria sobreviven serialización alternativa de MathLive
[31m[1mAssertionError[22m: expected 's u m_(i=1)^5i' to be 'sum(i,i,1,5)' // Object.is equality[39m

Expected: [32m"s[7mum(i,i,1,5)[27m"[39m
Received: [31m"s[7m u m_(i=1)^5i[27m"[39m

[36m [2m❯[22m src/__tests__/exhaustive-module10-keyboard-parity.test.ts:[2m46:52[22m[39m
    [90m 44| [39m
    [90m 45| [39m  [34mit[39m([32m"sumatoria/productoria sobreviven serialización alternativa de Ma[39m…
    [90m 46| [39m    [34mexpect[39m([34mlatexToBackendSyntax[39m([32m"sum_{i=1}^{5}i"[39m))[33m.[39m[34mtoBe[39m([32m"sum(i,i,1,5)"[39m…
    [90m   | [39m                                                   [31m^[39m
    [90m 47| [39m    [34mexpect[39m([34mlatexToBackendSyntax[39m([32m"prod_{i=1}^{5}i"[39m))[33m.[39m[34mtoBe[39m([32m"product(i,i,[39m…
    [90m 48| [39m  })[33m;[39m

[31m[2m⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯[1/1]⎯[22m[39m

[2m Test Files [22m [1m[31m1 failed[39m[22m[2m | [22m[1m[32m32 passed[39m[22m[90m (33)[39m
[2m      Tests [22m [1m[31m1 failed[39m[22m[2m | [22m[1m[32m239 passed[39m[22m[90m (240)[39m
[2m   Start at [22m 05:10:02
[2m   Duration [22m 17.96s[2m (transform 1.11s, setup 7.49s, collect 2.66s, tests 10.62s, environment 20.99s, prepare 3.88s)[22m


::error file=/home/runner/work/precision-lab-plus/precision-lab-plus/frontend/src/__tests__/exhaustive-module10-keyboard-parity.test.ts,title=src/__tests__/exhaustive-module10-keyboard-parity.test.ts > Suite exhaustiva original — Módulo 10%3A teclado ↔ motor (Plus frontend) > sumatoria/productoria sobreviven serialización alternativa de MathLive,line=46,column=52::AssertionError: expected 's u m_(i=1)^5i' to be 'sum(i,i,1,5)' // Object.is equality%0A%0AExpected: "sum(i,i,1,5)"%0AReceived: "s u m_(i=1)^5i"%0A%0A ❯ src/__tests__/exhaustive-module10-keyboard-parity.test.ts:46:52%0A%0A
~~~

## build
~~~text

> precision-lab-frontend@0.1.0 build
> tsc --noEmit && vite build

[36mvite v5.4.21 [32mbuilding for production...[36m[39m
transforming...
[32m✓[39m 103 modules transformed.
rendering chunks...
computing gzip size...
[2mdist/[22m[32mmanifest.webmanifest                             [39m[1m[2m    0.46 kB[22m[1m[22m
[2mdist/[22m[32mindex.html                                       [39m[1m[2m    1.15 kB[22m[1m[22m[2m │ gzip:     0.55 kB[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Size3-Regular-CTq5MqoE.woff         [39m[1m[2m    4.42 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Size4-Regular-Dl5lxZxV.woff2        [39m[1m[2m    4.93 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Size2-Regular-Dy4dx90m.woff2        [39m[1m[2m    5.21 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Size1-Regular-mCD8mA8B.woff2        [39m[1m[2m    5.47 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Size4-Regular-BF-4gkZK.woff         [39m[1m[2m    5.98 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Size2-Regular-oD1tc_U0.woff         [39m[1m[2m    6.19 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Size1-Regular-C195tn64.woff         [39m[1m[2m    6.50 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Caligraphic-Regular-Di6jR-x-.woff2  [39m[1m[2m    6.91 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Caligraphic-Bold-Dq_IR9rO.woff2     [39m[1m[2m    6.91 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Size3-Regular-DgpXs0kz.ttf          [39m[1m[2m    7.59 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Caligraphic-Regular-CTRA-rTL.woff   [39m[1m[2m    7.66 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Caligraphic-Bold-BEiXGLvX.woff      [39m[1m[2m    7.72 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Script-Regular-D3wIWfF6.woff2       [39m[1m[2m    9.64 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_SansSerif-Regular-DDBCnlJ7.woff2    [39m[1m[2m   10.34 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Size4-Regular-DWFBv043.ttf          [39m[1m[2m   10.36 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Script-Regular-D5yQViql.woff        [39m[1m[2m   10.59 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Fraktur-Regular-CTYiF6lA.woff2      [39m[1m[2m   11.32 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Fraktur-Bold-CL6g_b3V.woff2         [39m[1m[2m   11.35 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Size2-Regular-B7gKUWhC.ttf          [39m[1m[2m   11.51 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_SansSerif-Italic-C3H0VqGB.woff2     [39m[1m[2m   12.03 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_SansSerif-Bold-D1sUS0GD.woff2       [39m[1m[2m   12.22 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Size1-Regular-Dbsnue_I.ttf          [39m[1m[2m   12.23 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_SansSerif-Regular-CS6fqUqJ.woff     [39m[1m[2m   12.32 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Caligraphic-Regular-wX97UBjC.ttf    [39m[1m[2m   12.34 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Caligraphic-Bold-ATXxdsX0.ttf       [39m[1m[2m   12.37 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Fraktur-Regular-Dxdc4cR9.woff       [39m[1m[2m   13.21 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Fraktur-Bold-BsDP51OF.woff          [39m[1m[2m   13.30 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Typewriter-Regular-CO6r4hn1.woff2   [39m[1m[2m   13.57 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_SansSerif-Italic-DN2j7dab.woff      [39m[1m[2m   14.11 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_SansSerif-Bold-DbIhKOiC.woff        [39m[1m[2m   14.41 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Typewriter-Regular-C0xS9mPB.woff    [39m[1m[2m   16.03 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Math-BoldItalic-CZnvNsCZ.woff2      [39m[1m[2m   16.40 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Math-Italic-t53AETM-.woff2          [39m[1m[2m   16.44 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Script-Regular-C5JkGWo-.ttf         [39m[1m[2m   16.65 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Main-BoldItalic-DxDJ3AOS.woff2      [39m[1m[2m   16.78 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Main-Italic-NWA7e6Wa.woff2          [39m[1m[2m   16.99 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Math-BoldItalic-iY-2wyZ7.woff       [39m[1m[2m   18.67 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Math-Italic-DA0__PXp.woff           [39m[1m[2m   18.75 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Main-BoldItalic-SpSLRI95.woff       [39m[1m[2m   19.41 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_SansSerif-Regular-BNo7hRIc.ttf      [39m[1m[2m   19.44 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Fraktur-Regular-CB_wures.ttf        [39m[1m[2m   19.57 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Fraktur-Bold-BdnERNNW.ttf           [39m[1m[2m   19.58 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Main-Italic-BMLOBm91.woff           [39m[1m[2m   19.68 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_SansSerif-Italic-YYjJ1zSn.ttf       [39m[1m[2m   22.36 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_SansSerif-Bold-CFMepnvq.ttf         [39m[1m[2m   24.50 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Main-Bold-Cx986IdX.woff2            [39m[1m[2m   25.32 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Main-Regular-B22Nviop.woff2         [39m[1m[2m   26.27 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Typewriter-Regular-D3Ib7_Hf.ttf     [39m[1m[2m   27.56 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_AMS-Regular-BQhdFMY1.woff2          [39m[1m[2m   28.08 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Main-Bold-Jm3AIy58.woff             [39m[1m[2m   29.91 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Main-Regular-Dr94JaBh.woff          [39m[1m[2m   30.77 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Math-BoldItalic-B3XSjfu4.ttf        [39m[1m[2m   31.20 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Math-Italic-flOr_0UB.ttf            [39m[1m[2m   31.31 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Main-BoldItalic-DzxPMmG6.ttf        [39m[1m[2m   32.97 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_AMS-Regular-DMm9YOAa.woff           [39m[1m[2m   33.52 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Main-Italic-3WenGoN9.ttf            [39m[1m[2m   33.58 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Main-Bold-waoOVXN0.ttf              [39m[1m[2m   51.34 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Main-Regular-ypZvNtVU.ttf           [39m[1m[2m   53.58 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_AMS-Regular-DRggAlZN.ttf            [39m[1m[2m   63.63 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[35mindex-CB_OEzbf.css                        [39m[1m[2m   66.01 kB[22m[1m[22m[2m │ gzip:    15.78 kB[22m
[2mdist/[22m[2massets/[22m[36mGraphViewer-J28Oqi_U.js                   [39m[1m[2m    2.57 kB[22m[1m[22m[2m │ gzip:     1.25 kB[22m
[2mdist/[22m[2massets/[22m[36mworkbox-window.prod.es5-BqEJf4Xk.js       [39m[1m[2m    5.71 kB[22m[1m[22m[2m │ gzip:     2.34 kB[22m
[2mdist/[22m[2massets/[22m[36mindex-BbVFWqWW.js                         [39m[1m[33m2,808.77 kB[39m[22m[2m │ gzip:   783.84 kB[22m
[2mdist/[22m[2massets/[22m[36mplotly.min-DYID_LBQ.js                    [39m[1m[33m4,840.47 kB[39m[22m[2m │ gzip: 1,468.44 kB[22m
[33m
(!) Some chunks are larger than 500 kB after minification. Consider:
- Using dynamic import() to code-split the application
- Use build.rollupOptions.output.manualChunks to improve chunking: https://rollupjs.org/configuration-options/#output-manualchunks
- Adjust chunk size limit for this warning via build.chunkSizeWarningLimit.[39m
[32m✓ built in 22.21s[39m

[36mPWA v1.3.0[39m
mode      [35mgenerateSW[39m
precache  [32m10 entries[39m [2m(7554.88 KiB)[22m
files generated
  [2mdist/sw.js[22m
  [2mdist/workbox-9c191d2f.js[22m
~~~
