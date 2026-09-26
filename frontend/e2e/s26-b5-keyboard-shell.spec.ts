import { expect, test } from "@playwright/test";

test("S26.3R B5: shell global del teclado abre, cierra y respeta el viewport", async ({ page }) => {
  await page.goto("./");

  const dialog = page.getByRole("dialog", { name: "Teclado matemático" });
  await expect(dialog).toBeHidden();

  const opener = page
    .getByRole("button", { name: /abrir teclado|expandir teclado|^teclado$/i })
    .first();
  await expect(opener).toBeVisible();
  await opener.click();
  await expect(dialog).toBeVisible();

  const viewport = page.viewportSize();
  const bounds = await dialog.boundingBox();
  expect(viewport).not.toBeNull();
  expect(bounds).not.toBeNull();
  expect(bounds!.x).toBeGreaterThanOrEqual(0);
  expect(bounds!.y).toBeGreaterThanOrEqual(0);
  expect(bounds!.x + bounds!.width).toBeLessThanOrEqual(viewport!.width + 1);
  expect(bounds!.y + bounds!.height).toBeLessThanOrEqual(viewport!.height + 1);

  if (viewport!.width >= 1440) {
    const sidebar = await page.locator('aside[aria-label="Navegación principal"]').boundingBox();
    const dock = await page.getByTestId("keyboard-dock").boundingBox();
    expect(sidebar).not.toBeNull();
    expect(dock).not.toBeNull();
    expect(bounds!.x).toBeGreaterThanOrEqual(sidebar!.x + sidebar!.width);
    expect(bounds!.height).toBeLessThanOrEqual(viewport!.height * 0.45 + 1);
    expect(dock!.y - (bounds!.y + bounds!.height)).toBeCloseTo(12, 0);
  } else if (viewport!.width >= 1024) {
    expect(bounds!.height).toBeLessThanOrEqual(viewport!.height * 0.45 + 1);
  } else if (viewport!.width >= 768) {
    expect(bounds!.height).toBeLessThanOrEqual(viewport!.height * 0.55 + 1);
  } else {
    expect(bounds!.height).toBeLessThanOrEqual(viewport!.height * 0.66 + 2);
  }

  await dialog.getByRole("button", { name: "Cerrar teclado", exact: true }).click();
  await expect(dialog).toBeHidden();

  await opener.click();
  await expect(dialog).toBeVisible();
  await page.keyboard.press("Escape");
  await expect(dialog).toBeHidden();
});


test("S26.3R B5: teclado global es alcanzable desde los seis módulos", async ({ page }) => {
  await page.goto("./");

  for (const name of ["Científica", "Gráficas", "Matrices", "Estadística", "Geometría", "Unidades"]) {
    const navigation = page.locator("nav").getByRole("button", { name, exact: true });
    await navigation.click();
    await expect(navigation).toHaveAttribute("aria-current", "page");

    const opener = page
      .getByRole("button", { name: /abrir teclado|expandir teclado|^teclado$/i })
      .first();
    await expect(opener, `${name}: apertura global`).toBeVisible();
    await opener.click();

    const keyboard = page.getByRole("dialog", { name: "Teclado matemático" });
    await expect(keyboard, `${name}: panel global`).toBeVisible();
    await page.keyboard.press("Escape");
    await expect(keyboard, `${name}: cierre por Escape`).toBeHidden();
  }
});
