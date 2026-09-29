import { expect, test } from "@playwright/test";

const VIEWPORTS = [
  { id: "desktop-1440", width: 1440, height: 900 },
  { id: "laptop-1280", width: 1280, height: 800 },
  { id: "tablet-768", width: 768, height: 1024 },
  { id: "mobile-390", width: 390, height: 844 },
] as const;

const LAYOUTS = ["fused", "split", "focus", "separated"] as const;

async function openScientific(page: import("@playwright/test").Page, layout = "fused") {
  await page.goto("./");
  await page.evaluate((value) => localStorage.setItem("precision-lab-layout-mode", value), layout);
  await page.reload();
  const scientific = page.locator("nav").getByRole("button", { name: "Científica", exact: true });
  await scientific.click();
  await expect(scientific).toHaveAttribute("aria-current", "page");
}

async function setExpression(page: import("@playwright/test").Page, value: string) {
  await page.evaluate(() => customElements.whenDefined("math-field"));
  const field = page.locator("math-field").first();
  await expect(field).toBeVisible();
  await field.evaluate((node, v) => {
    const el = node as HTMLElement & { value: string };
    el.value = v as string;
    el.dispatchEvent(new Event("input", { bubbles: true }));
  }, value);
}

async function expectFourSurfaces(page: import("@playwright/test").Page) {
  await expect(page.getByRole("region", { name: "Entrada", exact: true })).toBeVisible();
  await expect(page.getByRole("region", { name: "Resultado", exact: true })).toBeVisible();
  await expect(page.getByRole("region", { name: "Entradas previas", exact: true })).toBeVisible();
  await expect(page.getByTestId("scientific-graph")).toBeVisible();
}

async function expectNoHorizontalOverflow(page: import("@playwright/test").Page) {
  const metrics = await page.evaluate(() => ({
    viewport: document.documentElement.clientWidth,
    scrollWidth: document.documentElement.scrollWidth,
  }));
  expect(metrics.scrollWidth).toBeLessThanOrEqual(metrics.viewport + 2);
}

test.describe("S26 B7 — Científica Plus", () => {
  for (const viewport of VIEWPORTS) {
    test(`cuatro superficies sin overflow (${viewport.id})`, async ({ page }) => {
      await page.setViewportSize({ width: viewport.width, height: viewport.height });
      await openScientific(page);
      await expectFourSurfaces(page);
      await expectNoHorizontalOverflow(page);
    });
  }

  for (const layout of LAYOUTS) {
    test(`preset ${layout} conserva las cuatro superficies`, async ({ page }) => {
      await page.setViewportSize({ width: 1440, height: 900 });
      await openScientific(page, layout);
      await expectFourSurfaces(page);
      await expectNoHorizontalOverflow(page);
    });
  }

  test("Balanceada coloca Gráfica a la derecha del bloque de cálculo", async ({ page }) => {
    await page.setViewportSize({ width: 1440, height: 900 });
    await openScientific(page, "fused");

    const input = page.getByRole("region", { name: "Entrada", exact: true });
    const graph = page.getByTestId("scientific-graph");
    const previous = page.getByRole("region", { name: "Entradas previas", exact: true });
    const [inputBox, graphBox, previousBox] = await Promise.all([
      input.boundingBox(),
      graph.boundingBox(),
      previous.boundingBox(),
    ]);
    expect(inputBox).not.toBeNull();
    expect(graphBox).not.toBeNull();
    expect(previousBox).not.toBeNull();
    if (inputBox && graphBox && previousBox) {
      expect(graphBox.x).toBeGreaterThan(inputBox.x + inputBox.width - 2);
      expect(graphBox.y).toBeLessThanOrEqual(inputBox.y + 2);
      expect(graphBox.y + graphBox.height).toBeGreaterThanOrEqual(previousBox.y + previousBox.height - 2);
    }
  });

  test("Plus no conserva Ejemplos ni Sustituciones en Científica", async ({ page }) => {
    await page.setViewportSize({ width: 1440, height: 900 });
    await openScientific(page);
    await expect(page.getByTestId("scientific-examples")).toHaveCount(0);
    await expect(page.getByTestId("scientific-advanced-options")).toHaveCount(0);
  });

  test("resultado y entrada previa real permanecen utilizables", async ({ page }) => {
    await page.setViewportSize({ width: 1440, height: 900 });
    await openScientific(page);
    await setExpression(page, "2+2");

    const calculate = page.getByRole("region", { name: "Entrada", exact: true })
      .getByRole("button", { name: /calcular|evaluar/i }).first();
    await expect(calculate).toBeEnabled();
    await calculate.click();

    await expect(page.getByRole("region", { name: "Resultado", exact: true })).toContainText("4");
    const previous = page.getByRole("region", { name: "Entradas previas", exact: true });
    await expect(previous.getByRole("button", { name: /Reusar entrada/i }).first()).toBeVisible();
    await expectNoHorizontalOverflow(page);
  });

  test("función directa transfiere entrada y variable a Gráficas", async ({ page }) => {
    await openScientific(page);
    await setExpression(page, "y^2+1");
    const evaluation = page.waitForResponse((response) =>
      response.url().includes("/api/v1/evaluate") && response.request().method() === "POST",
    );
    await page.getByRole("region", { name: "Entrada", exact: true })
      .getByRole("button", { name: /calcular|evaluar/i }).first().click();
    expect((await evaluation).ok()).toBeTruthy();
    await expect(page.getByTestId("scientific-graph")).toContainText("con resultado conservado");
    await expect(page.getByTestId("scientific-preview-plot")).toBeVisible();
    await expect(page.getByTestId("scientific-preview-plot").locator("path")).toHaveCount(1);

    const graphResponse = page.waitForResponse((response) =>
      response.url().includes("/api/v1/graph/2d") && response.request().method() === "POST",
    );
    await page.getByTestId("scientific-graph").getByRole("button", { name: "Abrir en Gráficas" }).click();
    const response = await graphResponse;
    const payload = response.request().postDataJSON();
    expect(payload.variable).toBe("y");
    expect(payload.expressions).toHaveLength(1);
    expect(payload.expressions[0]).toContain("y");
    expect(response.ok()).toBeTruthy();
    await expect(page.getByRole("region", { name: "Gráficas", exact: true })).toBeVisible();
    await expect(page.getByTestId("scientific-graph-context")).toContainText("función de y · resultado conservado");
    await expect.poll(() => page.locator('math-field[aria-label="Expresión 1"]').evaluate(
      (field) => (field as HTMLElement & { value: string }).value,
    )).toContain("y");
  });

  test("derivada muestra dos curvas y transfiere ambas a Gráficas", async ({ page }) => {
    await openScientific(page);
    await setExpression(page, "\\frac{d}{dx}\\left(x^2+1\\right)");
    const derivative = page.waitForResponse((response) =>
      response.url().includes("/api/v1/derivative") && response.request().method() === "POST",
    );
    await page.getByRole("region", { name: "Entrada", exact: true })
      .getByRole("button", { name: /calcular|evaluar/i }).first().click();
    expect((await derivative).ok()).toBeTruthy();

    const preview = page.getByTestId("scientific-graph");
    await expect(preview).toContainText("Función original y derivada de orden 1");
    await expect(preview.getByTestId("scientific-preview-plot").locator("path")).toHaveCount(2);
    const graphResponse = page.waitForResponse((response) =>
      response.url().includes("/api/v1/graph/2d") && response.request().method() === "POST",
    );
    await preview.getByRole("button", { name: "Abrir en Gráficas" }).click();
    const response = await graphResponse;
    expect(response.ok()).toBeTruthy();
    expect(response.request().postDataJSON().expressions).toHaveLength(2);
    await expect(page.getByTestId("scientific-graph-context")).toContainText("derivada de x");
    await expect(page.locator('math-field[aria-label^="Expresión "]')).toHaveCount(2);
  });

  test("integral indefinida conserva +C y grafica la antiderivada con C=0", async ({ page }) => {
    await openScientific(page);
    await setExpression(page, "\\int x^2\\,dx");
    const integral = page.waitForResponse((response) =>
      response.url().includes("/api/v1/integral") && response.request().method() === "POST",
    );
    await page.getByRole("region", { name: "Entrada", exact: true })
      .getByRole("button", { name: /calcular|evaluar/i }).first().click();
    const integralResponse = await integral;
    expect(integralResponse.ok()).toBeTruthy();
    expect((await integralResponse.json()).result_text).toBe("x**3/3 + C");
    const preview = page.getByTestId("scientific-graph");
    await expect(preview).toContainText("C=0 solo en la gráfica");
    await expect(preview.getByTestId("scientific-preview-plot").locator("path")).toHaveCount(2);
    const graphResponse = page.waitForResponse((response) =>
      response.url().includes("/api/v1/graph/2d") && response.request().method() === "POST",
    );
    await preview.getByRole("button", { name: "Abrir en Gráficas" }).click();
    const graph = await graphResponse;
    expect(graph.ok()).toBeTruthy();
    const expressions = graph.request().postDataJSON().expressions;
    expect(expressions).toHaveLength(2);
    expect(expressions[0]).toContain("x");
    expect(expressions[1]).toBe("x**3/3");
    await expect(page.getByTestId("scientific-graph-context")).toContainText("integral de x");
    await expect(page.locator('math-field[aria-label^="Expresión "]')).toHaveCount(2);
  });

  test("integral definida muestra región firmada y conserva límites invertidos en Gráficas", async ({ page }) => {
    await openScientific(page);
    await setExpression(page, "\\int_{2}^{0} x^2\\,dx");
    const integral = page.waitForResponse((response) =>
      response.url().includes("/api/v1/integral") && response.request().method() === "POST",
    );
    await page.getByRole("region", { name: "Entrada", exact: true })
      .getByRole("button", { name: /calcular|evaluar/i }).first().click();
    const response = await integral;
    expect(response.ok()).toBeTruthy();
    expect(response.request().postDataJSON()).toMatchObject({ lower_bound: "2", upper_bound: "0" });
    expect((await response.json()).result_text).toBe("-8/3");
    const preview = page.getByTestId("scientific-graph");
    await expect(preview).toContainText("Región con signo de 2 a 0");
    await expect(preview).toContainText("Valor exacto: -8/3");
    await expect(preview.getByTestId("integral-negative-region")).toBeVisible();
    const graphResponse = page.waitForResponse((next) =>
      next.url().includes("/api/v1/graph/2d") && next.request().method() === "POST",
    );
    await preview.getByRole("button", { name: "Abrir en Gráficas" }).click();
    const graph = await graphResponse;
    expect(graph.ok()).toBeTruthy();
    expect(graph.request().postDataJSON()).toMatchObject({ expressions: ["x^2"], x_min: -1, x_max: 3 });
    await expect(page.getByTestId("scientific-graph-context")).toContainText("límites 2 → 0 · valor firmado -8/3");
    await expect(page.getByLabel("x mínimo (opcional)")).toHaveValue("-1");
    await expect(page.getByLabel("x máximo (opcional)")).toHaveValue("3");
    await expect(page.getByRole("img", { name: "Gráfica de las expresiones ingresadas" })).toBeVisible();
    await expect(page.locator(".legendtext").filter({ hasText: "Aporte negativo" })).toBeVisible();
  });

  test("límite bilateral inexistente muestra ambos lados y transfiere punto y resultado", async ({ page }) => {
    await openScientific(page);
    await setExpression(page, "\\lim_{x\\to0}\\frac{1}{x}");
    const limit = page.waitForResponse((response) =>
      response.url().includes("/api/v1/limit") && response.request().method() === "POST",
    );
    await page.getByRole("region", { name: "Entrada", exact: true })
      .getByRole("button", { name: /calcular|evaluar/i }).first().click();
    const result = await limit;
    expect(result.ok()).toBeTruthy();
    expect((await result.json()).result_text).toBe("DNE");
    const preview = page.getByTestId("scientific-graph");
    await expect(preview).toContainText("Aproximación por ambos lados a 0; los límites laterales difieren");
    await expect(preview.getByTestId("limit-left-approach")).toBeVisible();
    await expect(preview.getByTestId("limit-right-approach")).toBeVisible();
    const graphResponse = page.waitForResponse((response) =>
      response.url().includes("/api/v1/graph/2d") && response.request().method() === "POST",
    );
    await preview.getByRole("button", { name: "Abrir en Gráficas" }).click();
    const graph = await graphResponse;
    expect(graph.ok()).toBeTruthy();
    expect(graph.request().postDataJSON()).toMatchObject({ variable: "x", x_min: -2, x_max: 2 });
    await expect(page.getByTestId("scientific-graph-context")).toContainText("ambos lados → 0 · resultado DNE");
    await expect(page.locator(".legendtext").filter({ hasText: "Aproximación izquierda" })).toBeVisible();
    await expect(page.locator(".legendtext").filter({ hasText: "Aproximación derecha" })).toBeVisible();
  });

  test("límite lateral derecho enfatiza solo x→0+", async ({ page }) => {
    await openScientific(page);
    await setExpression(page, "\\lim_{x\\to0^{+}}\\frac{1}{x}");
    const limit = page.waitForResponse((response) =>
      response.url().includes("/api/v1/limit") && response.request().method() === "POST",
    );
    await page.getByRole("region", { name: "Entrada", exact: true })
      .getByRole("button", { name: /calcular|evaluar/i }).first().click();
    expect((await limit).request().postDataJSON().direction).toBe("right");
    const preview = page.getByTestId("scientific-graph");
    await expect(preview).toContainText("Aproximación por la derecha a 0");
    await expect(preview.getByTestId("limit-right-approach")).toBeVisible();
    await expect(preview.getByTestId("limit-left-approach")).toHaveCount(0);
  });

  test("límite al infinito enfoca el comportamiento lejano", async ({ page }) => {
    await openScientific(page);
    await setExpression(page, "\\lim_{x\\to\\infty}\\frac{1}{x}");
    const limit = page.waitForResponse((response) =>
      response.url().includes("/api/v1/limit") && response.request().method() === "POST",
    );
    await page.getByRole("region", { name: "Entrada", exact: true })
      .getByRole("button", { name: /calcular|evaluar/i }).first().click();
    const response = await limit;
    expect(response.request().postDataJSON().point).toBe("oo");
    expect((await response.json()).result_text).toBe("0");
    const preview = page.getByTestId("scientific-graph");
    await expect(preview).toContainText("Comportamiento hacia +∞");
    await expect(preview.getByTestId("limit-right-approach")).toBeVisible();
    await expect(preview.getByTestId("limit-left-approach")).toHaveCount(0);
    const graphResponse = page.waitForResponse((next) =>
      next.url().includes("/api/v1/graph/2d") && next.request().method() === "POST",
    );
    await preview.getByRole("button", { name: "Abrir en Gráficas" }).click();
    expect((await graphResponse).request().postDataJSON()).toMatchObject({ x_min: 4, x_max: 20 });
    await expect(page.getByTestId("scientific-graph-context")).toContainText("hacia +∞ · resultado 0");
  });

  test("error controlado conserva la Científica utilizable", async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await openScientific(page);
    await setExpression(page, "(");

    const calculate = page.getByRole("region", { name: "Entrada", exact: true })
      .getByRole("button", { name: /calcular|evaluar/i }).first();
    await expect(calculate).toBeEnabled();
    await calculate.click();

    await expect(page.locator('[role="alert"][aria-live="assertive"]').first()).toBeVisible({ timeout: 15000 });
    await expectFourSurfaces(page);
    await expectNoHorizontalOverflow(page);
  });
});
