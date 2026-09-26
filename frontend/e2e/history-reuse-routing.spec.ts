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
  await expect(panel.locator("time")).toContainText(/\d{2}\/\d{2}\/\d{4}/);
  await expect(panel.locator("time")).toContainText(/\d{2}:\d{2}/);

  await panel.getByRole("button", { name: /Reusar entrada/ }).click();
  await expect(panel).toHaveCount(0);
  await expect(page.getByRole("heading", { name: "Matrices", exact: true }).first()).toBeVisible();
});
