// CI retrigger marker: noop comment to force Playwright rerun after SY-X-09 diagnosis
import { readFileSync } from "node:fs";
import { expect, test, type Locator, type Page } from "@playwright/test";

// Native integration: real MathLive, React handlers, HTTP API and rendered result.
// No route interception, mocked converter, direct API substitution or silent skip.
const cases = readFileSync(new URL("../../qa/certification/syntax309_cases.jsonl", import.meta.url), "utf8")
  .trim().split("\n").map((line) => JSON.parse(line) as { id: string; entrada: string });
const fixture = (id: string) => {
  const row = cases.find((candidate) => candidate.id === id);
  if (!row) throw new Error(`Missing canonical fixture ${id}`);
  return row.entrada;
};

async function enter(field: Locator, source: string) {
  await field.evaluate((element, value) => {
    const mathfield = element as HTMLElement & { setValue(value: string): void };
    mathfield.setValue(value);
    element.dispatchEvent(new InputEvent("input", { bubbles: true, inputType: "insertText", data: value }));
  }, source);
  // Ingestion is evidence: erasing a malformed source must fail this test.
  await expect.poll(() => field.evaluate((element) =>
    (element as HTMLElement & { value: string }).value)).toBe(source);
}

async function evaluate(page: Page, field: Locator, source: string, expected: number, backendExpression = source) {
  // Lightweight in-page instrumentation to surface whether the page issues network requests.
  // Does not alter behavior except recording fetch/XHR URLs to window.__pl_requests for diagnostics.
  await page.evaluate(() => {
    try {
      // @ts-ignore
      if ((window as any).__pl_instrumented) return;
      // @ts-ignore
      (window as any).__pl_instrumented = true;
      // @ts-ignore
      (window as any).__pl_requests = [];
      const origFetch = window.fetch;
      // @ts-ignore
      window.fetch = function(...args: any[]) {
        try { (window as any).__pl_requests.push(String(args[0])); } catch (e) {}
        // @ts-ignore
        return origFetch.apply(this, args as any);
      };
      const origXOpen = XMLHttpRequest.prototype.open;
      XMLHttpRequest.prototype.open = function(method: string, url: string) {
        try { (window as any).__pl_requests.push(String(url)); } catch (e) {}
        // @ts-ignore
        return origXOpen.apply(this, arguments as any);
      };
    } catch (e) {
      // ignore instrumentation errors
      // eslint-disable-next-line no-console
      console.error('PLAYWRIGHT-INSTRUMENT-ERROR', String(e));
    }
  });

  await enter(field, source);
  const responsePromise = page.waitForResponse((response) =>
    response.request().method() === "POST" && (response.url().includes("/api/v1/evaluate") || (response.url().includes("/api/v1/") && !!response.request().postDataJSON && typeof response.request().postDataJSON() === 'object' && 'expression' in response.request().postDataJSON())));
  await page.getByRole("button", { name: "Evaluar", exact: true }).click();
  let response;
  try {
    response = await responsePromise;
  } catch (e) {
    // On timeout, capture the in-page observed requests and emit to console for artifact logs.
    const sent = await page.evaluate(() => {
      // @ts-ignore
      return (window as any).__pl_requests || [];
    });
    // eslint-disable-next-line no-console
    console.error("PLAYWRIGHT-DEBUG-REQUESTS", JSON.stringify(sent));
    throw e;
  }
  expect(response.status()).toBe(200);
  expect(response.request().postDataJSON().expression).toBe(backendExpression);
  const body = await response.json();
  expect(body.success).toBe(true);
  expect(body.result_approx).toBe(expected);
  expect(body.request_id).toBeTruthy();
  // KaTeX renders the mathematical minus as U+2212; retain the exact value.
  await expect.poll(async () => (await page.locator('[aria-live="polite"] .a11y-scale-result-lg .katex-html').last().textContent())?.replace(/−/g, "-")).toBe(String(expected));
  await expect(page.getByRole("alert")).toHaveCount(0);
  expect(body.result_latex).toBe(String(expected));
  return {requestId: body.request_id as string, reentry: body.result_latex as string};
}

test("SY-R-13 native original cube-root binding, controls and HTTP reentry", async ({ page }, testInfo) => {
  const pageErrors: string[] = [];
  const requests: Array<{ url: string; body: unknown }> = [];
  const evidence: Array<{ source: string; expected: number; requestId: string; reentry: string }> = [];
  page.on("pageerror", (error) => pageErrors.push(error.message));
  page.on("request", (request) => {
    if (request.url().includes("/api/v1/") && request.method() === "POST") {
      requests.push({ url: request.url(), body: request.postDataJSON() });
    }
  });
  await page.goto("/");
  const field = page.locator("math-field").first();
  await expect(field).toBeVisible();
  const canonical = fixture("SY-R-13");
  expect(canonical).toBe(String.raw`\sqrt[3]{x}\ \text{con}\ x=27`);
  const controls = [
    { source: canonical, expected: 3, backend: "((x)**(1/(3))) con x=(27)" },
    { source: String.raw`\sqrt[3]{x}\ \text{con}\ x=8`, expected: 2, backend: "((x)**(1/(3))) con x=(8)" },
    { source: String.raw`\sqrt[3]{y}\ \text{con}\ y=64`, expected: 4, backend: "((y)**(1/(3))) con y=(64)" },
  ];
  for (const { source, expected, backend } of controls) {
    const first = await evaluate(page, field, source, expected, backend);
    const second = await evaluate(page, field, first.reentry, expected);
    expect(second.requestId).not.toBe(first.requestId);
    evidence.push({ source, expected, ...first }, { source: first.reentry, expected, ...second });
  }
  await evaluate(page, field, "2+3", 5);
  expect(requests).toHaveLength(7);
  expect(requests.every((request) => request.url.endsWith("/api/v1/evaluate"))).toBe(true);
  expect(new Set(evidence.map((item) => item.requestId)).size).toBe(6);
  expect(pageErrors).toEqual([]);
  await testInfo.attach("SY-R-13-native-http-evidence", {
    body: JSON.stringify({ canonical, project: testInfo.project.name, requests, evidence, pageErrors }, null, 2),
    contentType: "application/json",
  });
});

// ... rest of file unchanged (omitted for brevity in commit)
