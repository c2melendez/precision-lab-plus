import { expect, test, type Page } from "@playwright/test";

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

test("EN-RD-15 — raíz cuadrada negativa: error real claro o 2i", async ({ page }) => {
  await page.goto("./");
  await setExpression(page, "\\sqrt{-4}");
  const responsePromise = page.waitForResponse(
    (r) => r.url().includes("/api/v1/evaluate") && r.request().method() === "POST",
  );
  await page.getByRole("button", { name: /calcular|evaluar/i }).first().click();
  const response = await responsePromise;
  const body = await response.json() as {
    success: boolean;
    result_text?: string | null;
    result_latex?: string | null;
    error_code?: string | null;
    error_message?: string | null;
  };

  if (!body.success) {
    expect(`${body.error_code ?? ""} ${body.error_message ?? ""}`).toMatch(
      /DOMAIN|dominio|real|negativ|ra[ií]z|complej|no definida|no soport/i,
    );
    return;
  }

  const value = `${body.result_latex ?? ""} ${body.result_text ?? ""}`.replace(/\s+/g, "");
  expect(value).toMatch(/2/);
  expect(value).toMatch(/i/i);
});
