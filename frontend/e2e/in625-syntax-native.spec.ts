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

async function evaluate(page: Page, field: Locator, source: string, expected: number) {
  await enter(field, source);
  const responsePromise = page.waitForResponse((response) =>
    response.url().endsWith("/api/v1/evaluate") && response.request().method() === "POST");
  await page.getByRole("button", { name: "Evaluar", exact: true }).click();
  const response = await responsePromise;
  expect(response.status()).toBe(200);
  expect(response.request().postDataJSON().expression).toBe(source);
  const body = await response.json();
  expect(body.success).toBe(true);
  expect(body.result_approx).toBe(expected);
  expect(body.request_id).toBeTruthy();
  await expect(page.locator('[aria-live="polite"] .a11y-scale-result-lg .katex-html').last()).toHaveText(String(expected));
  await expect(page.getByRole("alert")).toHaveCount(0);
  expect(body.result_latex).toBe(String(expected));
  return {requestId: body.request_id as string, reentry: body.result_latex as string};
}

for (const id of ["SY-X-01", "SY-X-02", "SY-X-03"]) {
  test(`${id} native source, readable local rejection and two real HTTP recoveries`, async ({ page }, testInfo) => {
    const pageErrors: string[] = [];
    const sent: Array<{ url: string; body: unknown }> = [];
    page.on("pageerror", (error) => pageErrors.push(error.message));
    page.on("request", (request) => {
      if (request.url().includes("/api/v1/") && request.method() === "POST") {
        sent.push({ url: request.url(), body: request.postDataJSON() });
      }
    });
    await page.goto("/");
    const field = page.locator("math-field").first();
    await expect(field).toBeVisible();
    const canonical = fixture(id);
    if (id === "SY-X-01") expect(canonical).toBe("*(vacía)*");
    const source = id === "SY-X-01" ? "" : canonical;
    for (let cycle = 0; cycle < 2; cycle += 1) {
      const before = sent.length;
      await enter(field, source);
      await page.getByRole("button", { name: "Evaluar", exact: true }).click();
      const alert = page.getByRole("alert");
      await expect(alert).toContainText(id === "SY-X-03" ? "Sintaxis incompleta" : "La expresión no puede estar vacía.");
      if (id === "SY-X-03") await expect(alert).not.toContainText("vacía");
      expect(sent).toHaveLength(before); // local validation must not fabricate backend evidence
      const expected = cycle === 0 ? 5 : 9;
      const first = await evaluate(page, field, cycle === 0 ? "2+3" : "4+5", expected);
      const second = await evaluate(page, field, first.reentry, expected);
      expect(second.requestId).not.toBe(first.requestId);
      expect(sent).toHaveLength(before + 2);
      expect(pageErrors).toEqual([]);
    }
    await testInfo.attach(`${id}-native-http-evidence`, {
      body: JSON.stringify({ id, project: testInfo.project.name, canonical, source, sent, pageErrors }, null, 2),
      contentType: "application/json",
    });
  });
}
