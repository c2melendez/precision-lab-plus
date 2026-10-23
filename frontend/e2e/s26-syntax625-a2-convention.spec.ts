import { expect, test, type Page } from "@playwright/test";

type EvaluateBody = {
  success: boolean;
  result_text?: string | null;
  result_approx?: number | string | null;
  result_kind?: string | null;
  error_message?: string | null;
};

async function setExpression(page: Page, value: string) {
  await page.evaluate(() => customElements.whenDefined("math-field"));
  const field = page.locator("math-field").first();
  await expect(field).toBeVisible();
  await field.evaluate((node, v) => {
    const el = node as HTMLElement & { value: string };
    el.value = v as string;
    el.dispatchEvent(new Event("input", { bubbles: true }));
  }, value);
}

async function evaluate(page: Page, input: string): Promise<EvaluateBody> {
  await page.goto("./");
  await setExpression(page, input);
  const wait = page.waitForResponse((r) => r.url().includes("/api/v1/evaluate") && r.request().method() === "POST");
  await page.getByRole("button", { name: /calcular|evaluar/i }).first().click();
  return (await (await wait).json()) as EvaluateBody;
}

test("EN-DL-03 — llaves agrupación o error claro", async ({ page }) => {
  const body = await evaluate(page, "2\\left\\{3+4\\right\\}");
  if (!body.success) {
    expect(body.error_message ?? "").toMatch(/llave|conjunto|agrup|sintax|no soport/i);
  } else {
    expect(Number(body.result_approx ?? body.result_text)).toBeCloseTo(14, 5);
  }
});

for (const tc of [
  { id: "EN-DL-18", input: "\\left(1,3\\right]" },
  { id: "EN-DL-19", input: "[1,3)" },
]) {
  test(`${tc.id} — intervalo semiabierto no se confunde con desbalance`, async ({ page }) => {
    const body = await evaluate(page, tc.input);
    if (!body.success) {
      const msg = body.error_message ?? "";
      expect(msg).not.toMatch(/desbalance|sin balance|cierre.*par[eé]nt|par[eé]ntesis.*cierre/i);
      expect(msg).toMatch(/interval|no soport|sintax|entrada/i);
    }
  });
}

test("EN-DL-20 — norma vectorial 3-4-5 o error claro", async ({ page }) => {
  const body = await evaluate(page, "\\lVert\\begin{pmatrix}3\\\\4\\end{pmatrix}\\rVert");
  if (!body.success) {
    expect(body.error_message ?? "").toMatch(/norma|vector|matriz|no soport|sintax/i);
  } else {
    expect(Number(body.result_approx ?? body.result_text)).toBeCloseTo(5, 5);
  }
});
