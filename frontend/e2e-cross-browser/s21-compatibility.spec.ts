import { expect, test } from "@playwright/test";

function collectBrowserProblems(page: import("@playwright/test").Page) {
  const problems: string[] = [];
  page.on("console", (message) => {
    if (message.type() === "error") problems.push(`console.error: ${message.text()}`);
  });
  page.on("pageerror", (error) => problems.push(`pageerror: ${error.message}`));
  page.on("response", (response) => {
    if (response.status() >= 500) problems.push(`HTTP ${response.status()}: ${response.url()}`);
  });
  return problems;
}

async function setExpression(page: import("@playwright/test").Page, value: string) {
  await page.evaluate(() => customElements.whenDefined("math-field"));
  const field = page.locator("math-field").first();
  await expect(field).toBeVisible();
  await field.focus();
  await field.evaluate((node, v) => {
    const el = node as HTMLElement & { value: string };
    el.value = v as string;
    el.dispatchEvent(new Event("input", { bubbles: true }));
  }, value);
}

test("S21: smoke y 2+2 funcionan fuera de Chromium", async ({ page, request }) => {
  const health = await request.get("http://127.0.0.1:8000/api/v1/health");
  expect(health.ok()).toBeTruthy();

  const problems = collectBrowserProblems(page);
  await page.goto("./", { waitUntil: "networkidle" });
  await expect(page.locator("body")).toContainText(/Precision Lab/i);

  await setExpression(page, "2+2");

  const entry = page.getByRole("region", { name: "Entrada", exact: true });
  const calculate = entry.getByRole("button", { name: "Calcular", exact: true });
  await expect(calculate).toBeEnabled();

  const responsePromise = page.waitForResponse(
    (r) => r.url().includes("/api/v1/evaluate") && r.request().method() === "POST",
  );
  await calculate.click();
  const body = await (await responsePromise).json();
  expect(body.success, JSON.stringify(body)).toBe(true);
  expect(Number(body.result_approx ?? body.result_text)).toBeCloseTo(4, 12);

  await expect(page.getByRole("button", { name: "Copiar resultado", exact: true })).toBeVisible();
  expect(problems).toEqual([]);
});

test("S21: teclado abre, navega y cierra fuera de Chromium", async ({ page }) => {
  await page.goto("./");

  const opener = page.getByRole("button", { name: /abrir teclado|expandir teclado/i }).first();
  await expect(opener).toBeVisible();
  await opener.click();

  const dialog = page.getByRole("dialog", { name: "Teclado matemático" });
  await expect(dialog).toBeVisible();

  const basic = dialog.getByRole("tab", { name: "Básico", exact: true });
  const algebra = dialog.getByRole("tab", { name: "Álgebra", exact: true });
  await expect(basic).toHaveAttribute("aria-selected", "true");
  await algebra.click();
  await expect(algebra).toHaveAttribute("aria-selected", "true");

  await page.keyboard.press("Escape");
  await expect(dialog).toBeHidden();
});
