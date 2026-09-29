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

async function runAlgebraKeyboardAction(page: import("@playwright/test").Page, name: string) {
  await page.getByRole("button", { name: /abrir teclado|expandir teclado/i }).first().click();
  const dialog = page.getByRole("dialog", { name: "Teclado matemático" });
  await dialog.getByRole("tab", { name: "Álgebra", exact: true }).click();
  await dialog.getByLabel("Subcategorías de Álgebra").getByRole("button", { name: "Ecuaciones", exact: true }).click();
  await dialog.getByRole("button", { name, exact: true }).first().click();
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

  test("Científica usa márgenes laterales de Lite en escritorio", async ({ page }) => {
    await page.setViewportSize({ width: 1920, height: 1080 });
    await openScientific(page, "fused");

    const sidebar = page.getByRole("complementary", { name: "Navegación principal" });
    const input = page.getByRole("region", { name: "Entrada", exact: true });
    const graph = page.getByTestId("scientific-graph");
    const [sidebarBox, inputBox, graphBox] = await Promise.all([
      sidebar.boundingBox(), input.boundingBox(), graph.boundingBox(),
    ]);
    expect(sidebarBox && inputBox && graphBox).toBeTruthy();
    if (sidebarBox && inputBox && graphBox) {
      expect(inputBox.x - (sidebarBox.x + sidebarBox.width)).toBeCloseTo(40, 0);
      expect(1920 - (graphBox.x + graphBox.width)).toBeCloseTo(40, 0);
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

  test("factorización polinómica conserva forma transformada y una curva de dominio completo", async ({ page }) => {
    await openScientific(page);
    await setExpression(page, "x^2-4");
    const factor = page.waitForResponse((response) =>
      response.url().includes("/api/v1/factor") && response.request().method() === "POST",
    );
    await runAlgebraKeyboardAction(page, "Factorizar expresión");
    const response = await factor;
    expect(response.ok()).toBeTruthy();
    expect((await response.json()).graph_polynomial_comparison).toBe(true);
    const preview = page.getByTestId("scientific-graph");
    await expect(preview).toContainText("Ambas formas son polinomios con dominio real completo");
    await expect(preview.getByTestId("scientific-preview-plot").locator("path")).toHaveCount(1);
    const graphResponse = page.waitForResponse((next) =>
      next.url().includes("/api/v1/graph/2d") && next.request().method() === "POST",
    );
    await preview.getByRole("button", { name: "Abrir en Gráficas" }).click();
    expect((await graphResponse).request().postDataJSON().expressions).toHaveLength(1);
    await expect(page.getByTestId("scientific-graph-context")).toContainText("factorización de x · resultado conservado");
    await expect(page.getByTestId("scientific-graph-context")).toContainText("dominio real completo");
  });

  test("simplificar x/x no afirma equivalencia gráfica en el punto excluido", async ({ page }) => {
    await openScientific(page);
    await setExpression(page, "\\frac{x}{x}");
    const simplify = page.waitForResponse((response) =>
      response.url().includes("/api/v1/simplify") && response.request().method() === "POST",
    );
    await runAlgebraKeyboardAction(page, "Simplificar expresión");
    const response = await simplify;
    expect(response.ok()).toBeTruthy();
    expect((await response.json()).graph_polynomial_comparison).toBe(false);
    const preview = page.getByTestId("scientific-graph");
    await expect(preview).toContainText("restricciones de dominio");
    await expect(preview.getByRole("button", { name: "Abrir en Gráficas" })).toHaveCount(0);
  });

  test("EDO particular grafica la solución explícita y conserva la ecuación", async ({ page }) => {
    await openScientific(page);
    await setExpression(page, "y'=y, y(0)=1");
    const ode = page.waitForResponse((response) =>
      response.url().includes("/api/v1/ode") && response.request().method() === "POST",
    );
    await page.getByRole("region", { name: "Entrada", exact: true })
      .getByRole("button", { name: /calcular|evaluar/i }).first().click();
    const response = await ode;
    expect(response.ok()).toBeTruthy();
    expect((await response.json()).ode_solution_expression).toBe("exp(x)");
    const preview = page.getByTestId("scientific-graph");
    await expect(preview).toContainText("Solución particular y(x)");
    await expect(preview.getByTestId("scientific-preview-plot").locator("path")).toHaveCount(1);
    const graphResponse = page.waitForResponse((next) =>
      next.url().includes("/api/v1/graph/2d") && next.request().method() === "POST",
    );
    await preview.getByRole("button", { name: "Abrir en Gráficas" }).click();
    expect((await graphResponse).request().postDataJSON().expressions).toEqual(["exp(x)"]);
    await expect(page.getByTestId("scientific-graph-context")).toContainText("solución EDO de x · resultado conservado · solución particular");
  });

  test("EDO general muestra tres representantes sin perder C₁", async ({ page }) => {
    await openScientific(page);
    await setExpression(page, "y'=y");
    const ode = page.waitForResponse((response) =>
      response.url().includes("/api/v1/ode") && response.request().method() === "POST",
    );
    await page.getByRole("region", { name: "Entrada", exact: true })
      .getByRole("button", { name: /calcular|evaluar/i }).first().click();
    const response = await ode;
    expect(response.ok()).toBeTruthy();
    expect((await response.json()).ode_representative_expressions).toEqual(["-exp(x)", "0", "exp(x)"]);
    const preview = page.getByTestId("scientific-graph");
    await expect(preview).toContainText("C₁=−1, 0, 1");
    await expect(preview.getByTestId("scientific-preview-plot").locator("path")).toHaveCount(3);
    const graphResponse = page.waitForResponse((next) =>
      next.url().includes("/api/v1/graph/2d") && next.request().method() === "POST",
    );
    await preview.getByRole("button", { name: "Abrir en Gráficas" }).click();
    expect((await graphResponse).request().postDataJSON().expressions).toEqual(["-exp(x)", "0", "exp(x)"]);
    await expect(page.getByTestId("scientific-graph-context")).toContainText("familia representativa C₁=−1, 0, 1");
  });

  test("sistema lineal muestra dos curvas y su intersección calculada", async ({ page }) => {
    await openScientific(page);
    await setExpression(page, "\\begin{cases}x+y=3\\\\x-y=1\\end{cases}");
    const solve = page.waitForResponse((response) =>
      response.url().includes("/api/v1/solve/system") && response.request().method() === "POST");
    await page.getByRole("region", { name: "Entrada", exact: true })
      .getByRole("button", { name: /calcular|evaluar/i }).first().click();
    expect((await (await solve).json()).system_graph_intersections).toEqual([[2, 1]]);
    const preview = page.getByTestId("scientific-graph");
    await expect(preview.getByTestId("scientific-preview-plot").locator("path")).toHaveCount(2);
    await expect(preview.getByTestId("system-intersection")).toHaveCount(1);
    const graphResponse = page.waitForResponse((response) =>
      response.url().includes("/api/v1/graph/2d") && response.request().method() === "POST");
    await preview.getByRole("button", { name: "Abrir en Gráficas" }).click();
    expect((await graphResponse).request().postDataJSON().expressions).toEqual(["3 - x", "x - 1"]);
    await expect(page.getByTestId("scientific-graph-context")).toContainText("1 intersección común");
  });

  test("rectas paralelas no inventan intersección", async ({ page }) => {
    await openScientific(page);
    await setExpression(page, "\\begin{cases}x+y=3\\\\x+y=4\\end{cases}");
    const solve = page.waitForResponse((response) =>
      response.url().includes("/api/v1/solve/system") && response.request().method() === "POST");
    await page.getByRole("region", { name: "Entrada", exact: true })
      .getByRole("button", { name: /calcular|evaluar/i }).first().click();
    expect((await (await solve).json()).system_graph_intersections).toEqual([]);
    const preview = page.getByTestId("scientific-graph");
    await expect(preview).toContainText("no tiene solución");
    await expect(preview.getByTestId("system-intersection")).toHaveCount(0);
  });

  test("recta vertical y horizontal conservan su cruce al abrir Gráficas", async ({ page }) => {
    await openScientific(page);
    await setExpression(page, "\\begin{cases}x=1\\\\y=2\\end{cases}");
    const solve = page.waitForResponse((response) =>
      response.url().includes("/api/v1/solve/system") && response.request().method() === "POST");
    await page.getByRole("region", { name: "Entrada", exact: true })
      .getByRole("button", { name: /calcular|evaluar/i }).first().click();
    const result = await (await solve).json();
    expect(result.system_graph_intersections).toEqual([[1, 2]]);
    expect(result.graph_data.traces.map((trace: { type: string }) => trace.type)).toEqual(["line", "line", "point"]);
    const preview = page.getByTestId("scientific-graph");
    await expect(preview.getByTestId("scientific-preview-plot").locator("path")).toHaveCount(2);
    await expect(preview.getByTestId("system-intersection")).toHaveCount(1);
    const bridge = page.waitForResponse((response) =>
      response.url().includes("/api/v1/solve/system") && response.request().method() === "POST");
    await preview.getByRole("button", { name: "Abrir en Gráficas" }).click();
    expect((await bridge).request().postDataJSON().equations).toEqual(["x=1", "y=2"]);
    await expect(page.getByTestId("scientific-graph-context")).toContainText("1 intersección común");
  });

  test("círculo y recta muestran dos cruces simbólicos, con ramas agrupadas", async ({ page }) => {
    await openScientific(page);
    await setExpression(page, "\\begin{cases}x^2+y^2=1\\\\y=x\\end{cases}");
    const solve = page.waitForResponse((response) =>
      response.url().includes("/api/v1/solve/system") && response.request().method() === "POST");
    await page.getByRole("region", { name: "Entrada", exact: true })
      .getByRole("button", { name: /calcular|evaluar/i }).first().click();
    const result = await (await solve).json();
    expect(result.system_graph_component_indices).toEqual([0, 0, 1]);
    expect(result.system_graph_intersections).toHaveLength(2);
    const preview = page.getByTestId("scientific-graph");
    await expect(preview.getByTestId("scientific-preview-plot").locator("path")).toHaveCount(3);
    await expect(preview.getByTestId("system-intersection")).toHaveCount(2);
    const graphResponse = page.waitForResponse((response) =>
      response.url().includes("/api/v1/graph/2d") && response.request().method() === "POST");
    await preview.getByRole("button", { name: "Abrir en Gráficas" }).click();
    expect((await graphResponse).request().postDataJSON().expressions).toHaveLength(3);
    await expect(page.getByTestId("scientific-graph-context")).toContainText("2 intersecciones comunes");
  });

  test("círculo con recta vertical muestra sus dos cruces comunes", async ({ page }) => {
    await openScientific(page);
    await setExpression(page, "\\begin{cases}x=0\\\\x^2+y^2=1\\end{cases}");
    const solve = page.waitForResponse((response) =>
      response.url().includes("/api/v1/solve/system") && response.request().method() === "POST");
    await page.getByRole("region", { name: "Entrada", exact: true })
      .getByRole("button", { name: /calcular|evaluar/i }).first().click();
    const result = await (await solve).json();
    expect(result.system_graph_intersections).toEqual([[0, -1], [0, 1]]);
    expect(result.graph_data.traces.map((trace: { type: string }) => trace.type)).toEqual(["line", "line", "line", "point"]);
    const preview = page.getByTestId("scientific-graph");
    await expect(preview.getByTestId("system-intersection")).toHaveCount(2);
    await preview.getByRole("button", { name: "Abrir en Gráficas" }).click();
    await expect(page.getByTestId("scientific-graph-context")).toContainText("2 intersecciones comunes");
  });

  test("círculo y vertical disjuntos conservan soluciones complejas sin marcador real", async ({ page }) => {
    await openScientific(page);
    await setExpression(page, "\\begin{cases}x^2+y^2=1\\\\x=2\\end{cases}");
    const solve = page.waitForResponse((response) =>
      response.url().includes("/api/v1/solve/system") && response.request().method() === "POST");
    await page.getByRole("region", { name: "Entrada", exact: true })
      .getByRole("button", { name: /calcular|evaluar/i }).first().click();
    const result = await (await solve).json();
    expect(result.system_graph_intersections).toEqual([]);
    expect(result.result_data).toHaveLength(2);
    const preview = page.getByTestId("scientific-graph");
    await expect(preview).toContainText("soluciones complejas");
    await expect(preview.getByTestId("system-intersection")).toHaveCount(0);
  });

  test("inecuación estricta muestra extremo hueco y conserva el conjunto en Gráficas", async ({ page }) => {
    await openScientific(page);
    await setExpression(page, "x>0");
    const solve = page.waitForResponse((response) =>
      response.url().includes("/api/v1/inequality") && response.request().method() === "POST");
    await page.getByRole("region", { name: "Entrada", exact: true })
      .getByRole("button", { name: /calcular|evaluar/i }).first().click();
    const result = await (await solve).json();
    expect(result.inequality_intervals[0].lower_included).toBe(false);
    const preview = page.getByTestId("scientific-graph");
    await expect(preview.getByTestId("inequality-endpoint")).toHaveAttribute("fill", "white");
    await preview.getByRole("button", { name: "Abrir en Gráficas" }).click();
    await expect(page.getByRole("region", { name: "Análisis de inecuación" })).toContainText("Interval.open(0, oo)");
    await expect(page.getByRole("region", { name: "Análisis de inecuación" }).getByTestId("inequality-endpoint"))
      .toHaveAttribute("fill", "white");
  });

  test("inecuación 2D directa dibuja el semiplano y su frontera estricta", async ({ page }) => {
    await openScientific(page);
    await setExpression(page, "x+y>0");
    const solve = page.waitForResponse((response) =>
      response.url().includes("/api/v1/inequality") && response.request().method() === "POST");
    await page.getByRole("region", { name: "Entrada", exact: true })
      .getByRole("button", { name: /calcular|evaluar/i }).first().click();
    const result = await (await solve).json();
    expect(result.inequality_region_kind).toBe("unbounded");
    expect(result.inequality_constraints[0].operator).toBe(">");
    const preview = page.getByTestId("scientific-graph");
    await expect(preview.getByTestId("feasible-region")).toBeVisible();
    await expect(preview.getByTestId("inequality-boundary")).toHaveAttribute("stroke-dasharray", "6 5");
    await preview.getByRole("button", { name: "Abrir en Gráficas" }).click();
    await expect(page.getByRole("region", { name: "Análisis de región de inecuaciones" }))
      .toContainText("x+y>0");
  });

  test("inecuación circular conserva interior abierto y contexto en Gráficas", async ({ page }) => {
    await openScientific(page);
    await setExpression(page, "x^2+y^2<1");
    const solve = page.waitForResponse((response) =>
      response.url().includes("/api/v1/inequality") && response.request().method() === "POST");
    await page.getByRole("region", { name: "Entrada", exact: true })
      .getByRole("button", { name: /calcular|evaluar/i }).first().click();
    const result = await (await solve).json();
    expect(result.inequality_circle.inside).toBe(true);
    expect(result.inequality_circle.boundary_included).toBe(false);
    const preview = page.getByTestId("scientific-graph");
    await expect(preview.getByTestId("circle-interior-region")).toBeAttached();
    await expect(preview.getByTestId("circle-boundary")).toHaveAttribute("stroke-dasharray", "6 5");
    await preview.getByRole("button", { name: "Abrir en Gráficas" }).click();
    const graph = page.getByRole("region", { name: "Análisis de inecuación circular" });
    await expect(graph).toContainText("x^2+y^2<1");
    await expect(graph.getByTestId("circle-interior-region")).toBeAttached();
  });

  test("inecuación elíptica conserva exterior y frontera inclusiva en Gráficas", async ({ page }) => {
    await openScientific(page);
    await setExpression(page, "x^2+2y^2>=1");
    const solve = page.waitForResponse((response) =>
      response.url().includes("/api/v1/inequality") && response.request().method() === "POST");
    await page.getByRole("region", { name: "Entrada", exact: true })
      .getByRole("button", { name: /calcular|evaluar/i }).first().click();
    const result = await (await solve).json();
    expect(result.inequality_ellipse.inside).toBe(false);
    expect(result.inequality_ellipse.boundary_included).toBe(true);
    expect(result.result_latex).toContain("\\mathbb{R}^{2}");
    const preview = page.getByTestId("scientific-graph");
    await expect(preview.getByTestId("ellipse-exterior-region")).toBeAttached();
    await expect(preview.getByTestId("ellipse-boundary")).not.toHaveAttribute("stroke-dasharray");
    await preview.getByRole("button", { name: "Abrir en Gráficas" }).click();
    const graph = page.getByRole("region", { name: "Análisis de inecuación elíptica" });
    await expect(graph).toContainText("x^2+2y^2>=1");
    await expect(graph.getByTestId("ellipse-exterior-region")).toBeAttached();
  });

  test("inecuación inclusiva y conjunto vacío respetan su semántica", async ({ page }) => {
    await openScientific(page);
    await setExpression(page, "x>=0");
    const inclusive = page.waitForResponse((response) =>
      response.url().includes("/api/v1/inequality") && response.request().method() === "POST");
    await page.getByRole("region", { name: "Entrada", exact: true })
      .getByRole("button", { name: /calcular|evaluar/i }).first().click();
    expect((await (await inclusive).json()).inequality_intervals[0].lower_included).toBe(true);
    await expect(page.getByTestId("scientific-graph").getByTestId("inequality-endpoint"))
      .toHaveAttribute("fill", "#2862b8");

    await setExpression(page, "x^2<0");
    const empty = page.waitForResponse((response) =>
      response.url().includes("/api/v1/inequality") && response.request().method() === "POST");
    await page.getByRole("region", { name: "Entrada", exact: true })
      .getByRole("button", { name: /calcular|evaluar/i }).first().click();
    expect((await (await empty).json()).inequality_intervals).toEqual([]);
    await expect(page.getByTestId("scientific-graph")).toContainText("Conjunto solución vacío");
  });

  test("sistema de inecuaciones dibuja solo la región común y fronteras estrictas", async ({ page }) => {
    await openScientific(page);
    await setExpression(page, "\\begin{cases}x>0\\\\y\\ge 0\\\\x+y<4\\end{cases}");
    const solve = page.waitForResponse((response) =>
      response.url().includes("/api/v1/inequality/system") && response.request().method() === "POST");
    await page.getByRole("region", { name: "Entrada", exact: true })
      .getByRole("button", { name: /calcular|evaluar/i }).first().click();
    const result = await (await solve).json();
    expect(result.inequality_region_kind).toBe("bounded");
    expect(result.inequality_constraints.map((item: { operator: string }) => item.operator)).toEqual([">", ">=", "<"]);
    const preview = page.getByTestId("scientific-graph");
    await expect(preview.getByTestId("feasible-region")).toBeVisible();
    const boundaries = preview.getByTestId("inequality-boundary");
    await expect(boundaries).toHaveCount(3);
    await expect(boundaries.nth(0)).toHaveAttribute("stroke-dasharray", "6 5");
    await expect(boundaries.nth(1)).not.toHaveAttribute("stroke-dasharray");
    await preview.getByRole("button", { name: "Abrir en Gráficas" }).click();
    await expect(page.getByRole("region", { name: "Análisis de región de inecuaciones" }))
      .toContainText("x>0 ; y>=0 ; x+y<4");
  });

  test("sistema estrictamente imposible muestra región vacía", async ({ page }) => {
    await openScientific(page);
    await setExpression(page, "\\begin{cases}x>0\\\\x<0\\end{cases}");
    const solve = page.waitForResponse((response) =>
      response.url().includes("/api/v1/inequality/system") && response.request().method() === "POST");
    await page.getByRole("region", { name: "Entrada", exact: true })
      .getByRole("button", { name: /calcular|evaluar/i }).first().click();
    expect((await (await solve).json()).inequality_region_kind).toBe("empty");
    const preview = page.getByTestId("scientific-graph");
    await expect(preview).toContainText("Región factible vacía");
    await expect(preview.getByTestId("feasible-region")).toHaveCount(0);
  });

  test("intersección sobre un rayo dibuja trazo factible y origen excluido", async ({ page }) => {
    await openScientific(page);
    await setExpression(page, "\\begin{cases}x\\ge 0\\\\x\\le 0\\\\y>0\\end{cases}");
    const solve = page.waitForResponse((response) =>
      response.url().includes("/api/v1/inequality/system") && response.request().method() === "POST");
    await page.getByRole("region", { name: "Entrada", exact: true })
      .getByRole("button", { name: /calcular|evaluar/i }).first().click();
    expect((await (await solve).json()).inequality_region_dimension).toBe(1);
    const preview = page.getByTestId("scientific-graph");
    await expect(preview.getByTestId("inequality-region")).toBeVisible();
    await expect(preview.getByTestId("feasible-line")).toHaveAttribute("stroke-width", "5");
    await expect(preview.getByTestId("feasible-region")).toHaveCount(0);
    await expect(preview.getByTestId("feasible-endpoint")).toHaveAttribute("fill", "white");
    await preview.getByRole("button", { name: "Abrir en Gráficas" }).click();
    await expect(page.getByRole("region", { name: "Análisis de región de inecuaciones" })
      .getByTestId("feasible-line")).toHaveAttribute("stroke-width", "5");
  });

  test("complejo aislado conserva sus coordenadas en Argand y Gráficas", async ({ page }) => {
    await openScientific(page);
    await setExpression(page, "3+4i");
    const evaluate = page.waitForResponse((response) =>
      response.url().includes("/api/v1/evaluate") && response.request().method() === "POST");
    await page.getByRole("region", { name: "Entrada", exact: true })
      .getByRole("button", { name: /calcular|evaluar/i }).first().click();
    expect((await (await evaluate).json()).complex_graph_points).toEqual([{ re: 3, im: 4, label: "3 + 4*I" }]);
    const preview = page.getByTestId("scientific-graph");
    await expect(preview.getByTestId("complex-argand")).toBeVisible();
    await expect(preview.getByTestId("complex-point")).toHaveCount(1);
    await preview.getByRole("button", { name: "Abrir en Gráficas" }).click();
    await expect(page.getByRole("region", { name: "Análisis de plano complejo" })).toContainText("3+4i");
  });

  test("raíces complejas se presentan como puntos de Argand", async ({ page }) => {
    await openScientific(page);
    await setExpression(page, "x^2+1=0");
    const solve = page.waitForResponse((response) =>
      response.url().includes("/api/v1/solve") && response.request().method() === "POST");
    await page.getByRole("region", { name: "Entrada", exact: true })
      .getByRole("button", { name: /calcular|evaluar/i }).first().click();
    const points = (await (await solve).json()).complex_graph_points;
    expect(points).toHaveLength(2);
    expect(points.map((point: { im: number }) => point.im).sort()).toEqual([-1, 1]);
    await expect(page.getByTestId("scientific-graph").getByTestId("complex-point")).toHaveCount(2);
  });

  test("función compleja de variable real muestra curvas Re e Im", async ({ page }) => {
    await openScientific(page);
    await setExpression(page, "\\sin(x)+i\\cos(x)");
    const evaluate = page.waitForResponse((response) =>
      response.url().includes("/api/v1/evaluate") && response.request().method() === "POST");
    await page.getByRole("region", { name: "Entrada", exact: true })
      .getByRole("button", { name: /calcular|evaluar/i }).first().click();
    const components = (await (await evaluate).json()).complex_graph_components;
    expect(components).toMatchObject({ variable: "x", re_expression: "sin(x)", im_expression: "cos(x)" });
    const preview = page.getByTestId("scientific-graph");
    await expect(preview.getByTestId("scientific-preview-plot")).toBeVisible();
    await expect(preview).toContainText("Re en azul e Im en naranja");
    await preview.getByRole("button", { name: "Abrir en Gráficas" }).click();
    await expect(page.getByTestId("scientific-graph-context")).toContainText("partes Re e Im");
  });

  test("función f(z) muestra muestras del mapeo complejo sin curva cartesiana", async ({ page }) => {
    await openScientific(page);
    await setExpression(page, "z^2");
    const evaluate = page.waitForResponse((response) =>
      response.url().includes("/api/v1/evaluate") && response.request().method() === "POST");
    await page.getByRole("region", { name: "Entrada", exact: true })
      .getByRole("button", { name: /calcular|evaluar/i }).first().click();
    const result = await (await evaluate).json();
    expect(result.complex_graph_mapping).toHaveLength(4);
    expect(result.complex_graph_components).toBeNull();
    const preview = page.getByTestId("scientific-graph");
    await expect(preview.getByTestId("complex-mapping")).toBeVisible();
    await expect(preview.getByTestId("scientific-preview-plot")).toHaveCount(0);
    await preview.getByRole("button", { name: "Abrir en Gráficas" }).click();
    const analysis = page.getByRole("region", { name: "Análisis de mapeo complejo" });
    await expect(analysis).toContainText("z^2");
    await expect(analysis).toContainText("f(i) = -1 + 0i");
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
