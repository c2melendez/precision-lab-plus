import { expect, test } from "@playwright/test";

test("EN-SG-28 Plus Basic cancels a pending request and recovers", async ({ page }) => {
  await page.route("**/api/v1/evaluate", async (route) => {
    const body = route.request().postDataJSON() as { expression?: string };
    if (body.expression === "2+3") {
      // Keep an actual browser fetch pending without consuming backend resources.
      await new Promise<void>((resolve) => {
        route.request().response().then(() => resolve()).catch(() => resolve());
        setTimeout(resolve, 1800);
      });
      try {
        await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({
          success: true, operation: "evaluate", request_id: "sg28-old",
          result_text: "999999", result_latex: "999999",
          steps: [], has_detailed_steps: false, warnings: [], duration_ms: 1,
        }) });
      } catch { /* browser cancelled its pending request */ }
      return;
    }
    await route.continue();
  });

  await page.goto("/");
  const field = page.locator("math-field").first();
  await field.waitFor({ state: "visible" });
  const setInput = async (value: string) => {
    await field.evaluate((el, v) => {
      const mf = el as HTMLElement & { setValue: (s: string) => void };
      mf.setValue(v);
      el.dispatchEvent(new InputEvent("input", { bubbles: true, inputType: "insertText", data: v }));
    }, value);
  };

  await setInput("2+3");
  await page.getByRole("button", { name: "Evaluar", exact: true }).click();
  const cancel = page.getByRole("button", { name: "Detener cálculo" });
  await expect(cancel).toBeVisible();
  await cancel.click();
  await expect(cancel).toHaveCount(0);
  await setInput("4+5");
  await page.getByRole("button", { name: "Evaluar", exact: true }).click();
  await expect(page.locator("body")).not.toContainText("999999");
  await expect(page.locator('[aria-live="polite"]').last()).toContainText("9", { timeout: 15000 });
});



test("EN-SG-28 Plus browser evaluates against the real isolated backend", async ({ page }) => {
  // No page.route interception: production API, Pydantic MathResponse and
  // actual spawned evaluation worker are exercised together in CI.
  await page.goto("/");
  const field = page.locator("math-field").first();
  await field.waitFor({ state: "visible" });
  await field.evaluate((el) => {
    const mf = el as HTMLElement & { setValue: (value: string) => void };
    mf.setValue("2+3");
    el.dispatchEvent(new InputEvent("input", {
      bubbles: true, inputType: "insertText", data: "2+3",
    }));
  });
  const responsePromise = page.waitForResponse(
    (response) => response.url().endsWith("/api/v1/evaluate")
      && response.request().method() === "POST",
  );
  await page.getByRole("button", { name: "Evaluar", exact: true }).click();
  const response = await responsePromise;
  expect(response.status()).toBe(200);
  const body = await response.json();
  expect(body.success).toBe(true);
  expect(body.operation).toBe("evaluate");
  expect(body.result_approx).toBe(5);
  expect(body.request_id).toBeTruthy();
  await expect(page.locator('[aria-live="polite"]').last()).toContainText("5");
});



test("EN-SG-28 Plus browser preserves real isolated backend parse errors and recovers", async ({ page }) => {
  // This path is never mocked; the flag is enabled only in the SG28 UI CI job.
  await page.goto("/");
  const field = page.locator("math-field").first();
  await field.waitFor({ state: "visible" });
  const enter = async (value: string) => {
    await field.evaluate((el, v) => {
      const mf = el as HTMLElement & { setValue: (value: string) => void };
      mf.setValue(v);
      el.dispatchEvent(new InputEvent("input", {
        bubbles: true, inputType: "insertText", data: v,
      }));
    }, value);
  };

  await enter("x+(");
  const failed = page.waitForResponse((response) =>
    response.url().endsWith("/api/v1/evaluate") &&
    response.request().method() === "POST"
  );
  await page.getByRole("button", { name: "Evaluar", exact: true }).click();
  const invalidResponse = await failed;
  expect(invalidResponse.status()).toBe(200);
  const invalidBody = await invalidResponse.json();
  expect(invalidBody.success).toBe(false);
  expect(invalidBody.error_code).toBe("PARSE_ERROR");
  expect(invalidBody.request_id).toBeTruthy();

  await enter("4+5");
  const recovered = page.waitForResponse((response) =>
    response.url().endsWith("/api/v1/evaluate") &&
    response.request().method() === "POST"
  );
  await page.getByRole("button", { name: "Evaluar", exact: true }).click();
  const validResponse = await recovered;
  expect(validResponse.status()).toBe(200);
  const validBody = await validResponse.json();
  expect(validBody.success).toBe(true);
  expect(validBody.result_approx).toBe(9);
  await expect(page.locator('[aria-live="polite"]').last()).toContainText("9");
});
