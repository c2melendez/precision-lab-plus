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


test("el teclado desplegado coincide con las seis pestañas V5 aprobadas", async ({ page }) => {
  await page.goto("./");
  await openKeyboard(page);

  for (const tab of ["Básico", "Símbolos", "Álgebra", "Trigonométricas", "Cálculo", "Complejos"]) {
    await expect(page.getByRole("tab", { name: tab })).toBeVisible();
  }

  await expect(page.getByRole("tab", { name: "Básico" })).toHaveAttribute("aria-selected", "true");
});

test("Plus mantiene ∂/∂x activa y Π como única pendiente de Cálculo", async ({ page }) => {
  await page.goto("./");
  await openKeyboard(page);
  await page.getByRole("tab", { name: "Cálculo" }).click();

  const partial = page.getByRole("button", { name: "derivada parcial" });
  await expect(partial).toBeVisible();
  await partial.click();
  await expect(page.getByText(/derivada parcial: todavía no disponible/i)).toHaveCount(0);

  const product = page.getByRole("button", { name: "productoria" });
  await expect(product).toBeVisible();
  await product.click();
  await expect(page.getByText(/productoria: todavía no disponible/i)).toBeVisible();
});
