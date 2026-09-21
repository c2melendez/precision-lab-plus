import { expect, test } from "@playwright/test";

async function openKeyboard(page: import("@playwright/test").Page) {
  const opener = page.getByRole("button", { name: /abrir teclado|expandir teclado/i }).first();
  if (await opener.isVisible().catch(() => false)) await opener.click();
}

test("el teclado V5 conserva los contratos básicos", async ({ page }) => {
  await page.goto("./");
  await openKeyboard(page);

  await expect(page.getByRole("button", { name: /calcular|evaluar/i }).first()).toBeVisible();
  await expect(page.getByRole("button", { name: /borrar/i }).first()).toBeVisible();
  await expect(page.getByRole("button", { name: /igual|=/i }).first()).toBeVisible();
});

test("abrir/cerrar teclado no genera excepciones", async ({ page }) => {
  const errors: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  await page.goto("./");
  await openKeyboard(page);
  const closer = page.getByRole("button", { name: /cerrar teclado/i }).first();
  if (await closer.isVisible().catch(() => false)) await closer.click();
  expect(errors).toEqual([]);
});
