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


test("B6 expone siete familias y mantiene el núcleo permanente", async ({ page }) => {
  await page.goto("./");
  await openKeyboard(page);

  for (const tab of ["Álgebra", "Trigonométricas", "Cálculo", "Complejos", "Símbolos", "Unidades", "Más"]) {
    await expect(page.getByRole("tab", { name: tab })).toBeVisible();
  }

  await expect(page.getByRole("tab", { name: "Álgebra" })).toHaveAttribute("aria-selected", "true");
  await expect(page.getByTestId("keyboard-b6-core")).toBeVisible();
  expect((await page.getByRole("tab").allTextContents()).map((value) => value.trim())).toEqual([
    "Álgebra",
    "Trigonométricas",
    "Cálculo",
    "Complejos",
    "Símbolos",
    "Unidades",
    "Más",
  ]);
  await expect(page.getByRole("tab", { name: "Básico" })).toHaveCount(0);
});

test("Plus mantiene ∂/∂x y Π activas en Cálculo", async ({ page }) => {
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
  await expect(page.getByText(/productoria: todavía no disponible/i)).toHaveCount(0);
});
