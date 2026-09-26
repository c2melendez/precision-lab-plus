import { expect, test } from "@playwright/test";

test("Historial: Reusar vuelve al módulo de origen y muestra matrices, fecha y hora", async ({ page }) => {
  await page.addInitScript(() => {
    const timestamp = new Date(2026, 8, 25, 20, 16, 21).getTime();
    localStorage.setItem("calculadora-cientifica-history", JSON.stringify({
      schemaVersion: 1,
      entries: [{
        id: "matrix-history",
        sourceModule: "Matrices",
        operation: "matrix_operation",
        endpointUrl: "/matrix/operations",
        requestPayload: {
          operation: "multiply",
          matrix_a: [[1, 2], [3, 4]],
          matrix_b: [[5, 6], [7, 8]],
        },
        label: "A × B",
        resultText: "[[19,22],[43,50]]",
        hasDetailedSteps: false,
        warnings: [],
        timestamp,
      }],
    }));
  });

  await page.goto("./");
  await page.getByRole("button", { name: "Historial", exact: true }).click();

  const panel = page.locator("#history-panel");
  await expect(panel).toBeVisible();
  await expect(panel.getByText("Matrices", { exact: true })).toBeVisible();
  await expect(panel.getByText("Operación de matrices", { exact: true })).toBeVisible();
  await expect(panel.getByText("A =", { exact: true })).toBeVisible();
  await expect(panel.getByText("B =", { exact: true })).toBeVisible();
  await expect(panel.getByText("Resultado =", { exact: true })).toBeVisible();
  await expect(panel.locator("time")).toContainText(/\d{2}\/\d{2}\/\d{4}/);
  await expect(panel.locator("time")).toContainText(/\d{2}:\d{2}/);

  await panel.getByRole("button", { name: /Reusar entrada/ }).click();
  await expect(panel).toHaveCount(0);
  await expect(page.getByRole("heading", { name: "Matrices", exact: true }).first()).toBeVisible();
  await expect(page.getByLabel("Matriz A celda fila 1 columna 1")).toHaveValue("1");
  await expect(page.getByLabel("Matriz A celda fila 1 columna 2")).toHaveValue("2");
  await expect(page.getByLabel("Matriz A celda fila 2 columna 1")).toHaveValue("3");
  await expect(page.getByLabel("Matriz A celda fila 2 columna 2")).toHaveValue("4");
  await expect(page.getByLabel("Matriz B celda fila 1 columna 1")).toHaveValue("5");
  await expect(page.getByLabel("Matriz B celda fila 2 columna 2")).toHaveValue("8");
});


test("Historial: Reusar reconstruye una integral completa en Científica", async ({ page }) => {
  await page.addInitScript(() => {
    localStorage.setItem("calculadora-cientifica-history", JSON.stringify({
      schemaVersion: 1,
      entries: [{
        id: "integral-history",
        sourceModule: "Científica",
        operation: "integral",
        endpointUrl: "/integral",
        requestPayload: {
          expression: "x**2/4",
          variable: "x"
        },
        inputText: "∫ x**2/4",
        label: "∫ x**2/4",
        resultLatex: "\\frac{x^{3}}{12}+C",
        resultText: "x**3/12 + C",
        hasDetailedSteps: false,
        warnings: [],
        timestamp: Date.now(),
      }],
    }));
  });

  await page.goto("./");
  await page.getByRole("button", { name: "Historial", exact: true }).click();
  const panel = page.locator("#history-panel");
  await expect(panel).toBeVisible();

  await panel.getByRole("button", { name: /Reusar entrada/ }).click();
  await expect(panel).toHaveCount(0);
  await expect(page.getByRole("button", { name: "Científica", exact: true })).toHaveAttribute("aria-current", "page");

  const field = page.locator('math-field[aria-label="Expresión matemática"]').first();
  await expect(field).toBeVisible();
  const latex = await field.evaluate((node) => (node as unknown as { getValue: (format?: string) => string }).getValue("latex-unstyled"));
  expect(latex).toContain("\\int");
  expect(latex).toContain("x");
  expect(latex).toMatch(/d\s*x|dx/);
  expect(latex).not.toBe("x^{2}/4");
});
