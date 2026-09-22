# QA fast CI diagnostic — Plus

- npm_ci: 0
- typecheck: 2
- unit: 0
- build: 2

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

src/components/NaturalMathField.tsx(26,5): error TS2687: All declarations of 'mathVirtualKeyboard' must have identical modifiers.
src/components/NaturalMathField.tsx(26,5): error TS2717: Subsequent property declarations must have the same type.  Property 'mathVirtualKeyboard' must be of type 'VirtualKeyboardInterface & EventTarget', but here has type '{ hide: () => void; } | undefined'.
src/components/NaturalMathField.tsx(334,7): error TS18047: 'el' is possibly 'null'.
~~~

## unit
~~~text

> precision-lab-frontend@0.1.0 test
> vitest run


[1m[7m[36m RUN [39m[27m[22m [36mv2.1.9 [39m[90m/home/runner/work/precision-lab-plus/precision-lab-plus/frontend[39m

 [32m✓[39m src/__tests__/ResultPanel.test.tsx [2m([22m[2m19 tests[22m[2m)[22m[33m 408[2mms[22m[39m
 [32m✓[39m src/__tests__/GraphMode.test.tsx [2m([22m[2m7 tests[22m[2m)[22m[33m 934[2mms[22m[39m
 [32m✓[39m src/__tests__/BasicMode.test.tsx [2m([22m[2m16 tests[22m[2m)[22m[33m 856[2mms[22m[39m
 [32m✓[39m src/__tests__/calculusIntent.test.ts [2m([22m[2m20 tests[22m[2m)[22m[90m 262[2mms[22m[39m
 [32m✓[39m src/__tests__/MatrixMode.test.tsx [2m([22m[2m5 tests[22m[2m)[22m[33m 403[2mms[22m[39m
 [32m✓[39m src/__tests__/exhaustive-module10-keyboard-parity.test.ts [2m([22m[2m25 tests[22m[2m)[22m[90m 43[2mms[22m[39m
 [32m✓[39m src/__tests__/e2e.test.tsx [2m([22m[2m1 test[22m[2m)[22m[33m 540[2mms[22m[39m
   [33m[2m✓[22m[39m E2E mínimo — Derivada (sección 15)[2m > [22mx**2 en Derivada -> MathResponse real -> steps renderizados -> historial -> reuseEntry reejecuta [33m539[2mms[22m[39m
 [32m✓[39m src/__tests__/historyStore.test.ts [2m([22m[2m8 tests[22m[2m)[22m[90m 11[2mms[22m[39m
 [32m✓[39m src/__tests__/SystemMode.test.tsx [2m([22m[2m4 tests[22m[2m)[22m[33m 619[2mms[22m[39m
 [32m✓[39m src/__tests__/IntegralMode.test.tsx [2m([22m[2m5 tests[22m[2m)[22m[33m 661[2mms[22m[39m
 [32m✓[39m src/__tests__/useRecentKeysStore.test.ts [2m([22m[2m9 tests[22m[2m)[22m[90m 8[2mms[22m[39m
 [32m✓[39m src/__tests__/unitConversion.test.ts [2m([22m[2m22 tests[22m[2m)[22m[90m 10[2mms[22m[39m
 [32m✓[39m src/__tests__/EquationMode.test.tsx [2m([22m[2m5 tests[22m[2m)[22m[33m 580[2mms[22m[39m
 [32m✓[39m src/__tests__/LimitMode.test.tsx [2m([22m[2m5 tests[22m[2m)[22m[33m 593[2mms[22m[39m
 [32m✓[39m src/__tests__/KeyboardBasicPanelV5.test.tsx [2m([22m[2m5 tests[22m[2m)[22m[33m 442[2mms[22m[39m
 [32m✓[39m src/__tests__/NaturalMathField.test.ts [2m([22m[2m13 tests[22m[2m)[22m[90m 33[2mms[22m[39m
 [32m✓[39m src/__tests__/contract.test.ts [2m([22m[2m4 tests[22m[2m)[22m[90m 4[2mms[22m[39m
 [32m✓[39m src/__tests__/DerivativeMode.test.tsx [2m([22m[2m4 tests[22m[2m)[22m[33m 440[2mms[22m[39m
[90mstderr[2m | src/__tests__/GraphViewer.test.tsx[2m > [22m[2mGraphViewer[2m > [22m[2mel botón 'Descargar PNG' llama a Plotly.toImage
[22m[39mError: Not implemented: navigation (except hash changes)
    at module.exports (/home/runner/work/precision-lab-plus/precision-lab-plus/frontend/node_modules/jsdom/lib/jsdom/browser/not-implemented.js:9:17)
    at navigateFetch (/home/runner/work/precision-lab-plus/precision-lab-plus/frontend/node_modules/jsdom/lib/jsdom/living/window/navigation.js:77:3)
    at exports.navigate (/home/runner/work/precision-lab-plus/precision-lab-plus/frontend/node_modules/jsdom/lib/jsdom/living/window/navigation.js:55:3)
    at Timeout._onTimeout (/home/runner/work/precision-lab-plus/precision-lab-plus/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLHyperlinkElementUtils-impl.js:81:7)
    at listOnTimeout (node:internal/timers:585:17)
    at processTimers (node:internal/timers:521:7) [90mundefined[39m

 [32m✓[39m src/__tests__/GraphViewer.test.tsx [2m([22m[2m4 tests[22m[2m)[22m[33m 350[2mms[22m[39m
 [32m✓[39m src/__tests__/client.test.ts [2m([22m[2m6 tests[22m[2m)[22m[90m 9[2mms[22m[39m
 [32m✓[39m src/__tests__/History.test.tsx [2m([22m[2m4 tests[22m[2m)[22m[90m 145[2mms[22m[39m
 [32m✓[39m src/__tests__/MathKeyboard.test.tsx [2m([22m[2m4 tests[22m[2m)[22m[33m 383[2mms[22m[39m
 [32m✓[39m src/__tests__/KeyboardParityV5.test.ts [2m([22m[2m5 tests[22m[2m)[22m[90m 5[2mms[22m[39m
 [32m✓[39m src/__tests__/exhaustive-module10-keyboard-inventory.test.ts [2m([22m[2m5 tests[22m[2m)[22m[90m 15[2mms[22m[39m
 [32m✓[39m src/__tests__/KeyboardInventoryV5.test.ts [2m([22m[2m6 tests[22m[2m)[22m[90m 11[2mms[22m[39m
 [32m✓[39m src/exhaustive-module08-units.test.ts [2m([22m[2m5 tests[22m[2m)[22m[90m 7[2mms[22m[39m
 [32m✓[39m src/__tests__/exhaustive-module14-branding-natural-text.test.tsx [2m([22m[2m1 test[22m[2m)[22m[90m 207[2mms[22m[39m
 [32m✓[39m src/__tests__/BrandingV521.test.tsx [2m([22m[2m1 test[22m[2m)[22m[90m 98[2mms[22m[39m
 [32m✓[39m src/__tests__/MathRenderer.test.tsx [2m([22m[2m3 tests[22m[2m)[22m[90m 58[2mms[22m[39m
 [32m✓[39m src/__tests__/fractionDisplay.test.ts [2m([22m[2m9 tests[22m[2m)[22m[90m 7[2mms[22m[39m
 [32m✓[39m src/__tests__/systemSplit.test.ts [2m([22m[2m6 tests[22m[2m)[22m[90m 6[2mms[22m[39m
 [32m✓[39m src/__tests__/exhaustive-module11-layout-responsive.test.ts [2m([22m[2m2 tests[22m[2m)[22m[90m 3[2mms[22m[39m
 [32m✓[39m src/__tests__/LayoutDefaultV521.test.ts [2m([22m[2m2 tests[22m[2m)[22m[90m 7[2mms[22m[39m

[2m Test Files [22m [1m[32m33 passed[39m[22m[90m (33)[39m
[2m      Tests [22m [1m[32m240 passed[39m[22m[90m (240)[39m
[2m   Start at [22m 05:20:34
[2m   Duration [22m 13.03s[2m (transform 913ms, setup 5.21s, collect 2.09s, tests 8.16s, environment 14.96s, prepare 2.94s)[22m

~~~

## build
~~~text

> precision-lab-frontend@0.1.0 build
> tsc --noEmit && vite build

src/components/NaturalMathField.tsx(26,5): error TS2687: All declarations of 'mathVirtualKeyboard' must have identical modifiers.
src/components/NaturalMathField.tsx(26,5): error TS2717: Subsequent property declarations must have the same type.  Property 'mathVirtualKeyboard' must be of type 'VirtualKeyboardInterface & EventTarget', but here has type '{ hide: () => void; } | undefined'.
src/components/NaturalMathField.tsx(334,7): error TS18047: 'el' is possibly 'null'.
~~~
