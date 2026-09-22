import { expect, test } from "@playwright/test";

async function openComplex(page: import("@playwright/test").Page) {
  await page.goto("./");
  const opener = page.getByRole("button", { name: /abrir teclado|expandir teclado/i }).first();
  await expect(opener).toBeVisible();
  await opener.click();
  await page.getByRole("tab", { name: "Complejos", exact: true }).click();
}

async function setExpression(page: import("@playwright/test").Page, value: string) {
  const field = page.locator("math-field").first();
  await field.evaluate((node, v) => {
    const el = node as HTMLElement & { value: string };
    el.value = v as string;
    el.dispatchEvent(new Event("input", { bubbles: true }));
  }, value);
}

test("suite original módulo 5: inventario complejo compartido está activo", async ({ page }) => {
  await openComplex(page);
  for (const name of [
    "parte real",
    "parte imaginaria",
    "argumento",
    "conjugado",
    "módulo",
    "convertir a forma polar",
    "logaritmo complejo (rama principal)",
    "potencia compleja",
    "raíz n-ésima compleja (rama principal)",
    "graficar en el plano de Argand",
  ]) {
    const key = page.getByRole("button", { name, exact: true }).first();
    await expect(key).toBeVisible();
    expect(await key.isDisabled()).toBe(false);
  }
});

test("suite original módulo 5: Argand 3+4i usa ejes Re e Im", async ({ page }) => {
  await openComplex(page);
  await setExpression(page, "3+4i");
  // BasicMode usa el estado React `latex` para construir la petición.
  // "Graficar" se habilita solo cuando React ya consumió el evento input.
  await expect(page.getByRole("button", { name: "Graficar", exact: true }).first()).toBeVisible();

  // El contenido del teclado se registra en un store mediante useEffect.
  // Cerrarlo y reabrirlo después de la actualización de `latex` garantiza
  // que la acción Argand use el callback más reciente y evita probar una
  // closure anterior creada antes de inyectar 3+4i.
  await page.keyboard.press("Escape");
  const field = page.locator("math-field").first();
  await field.focus();
  const dialog = page.getByRole("dialog", { name: "Teclado matemático" });
  await expect(dialog).toBeVisible();
  await dialog.getByRole("tab", { name: "Complejos", exact: true }).click();

  const responsePromise = page.waitForResponse(
    (r) => r.url().includes("/api/v1/graph/complex_point") && r.request().method() === "POST",
  );
  const graph = dialog.getByRole("button", { name: "graficar en el plano de Argand", exact: true }).first();
  await graph.click();
  const response = await responsePromise;
  const body = await response.json();
  expect(body.success, JSON.stringify(body)).toBe(true);
  expect(body.graph_data?.x_axis_label).toBe("Re");
  expect(body.graph_data?.y_axis_label).toBe("Im");

  await expect(page.getByText("Re", { exact: true }).first()).toBeVisible({ timeout: 12000 });
  await expect(page.getByText("Im", { exact: true }).first()).toBeVisible({ timeout: 12000 });
});
