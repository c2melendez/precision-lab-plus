import { readFileSync } from "node:fs";
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


test("EN-SG-28 browser cancels real evaluation and recovers", async ({ page }) => {
  await page.goto("/");
  const field = page.locator("math-field").first();
  const enter = (value: string) => field.evaluate((el, v) => {
    (el as HTMLElement & { setValue: (value: string) => void }).setValue(v);
    el.dispatchEvent(new InputEvent("input", { bubbles: true, data: v }));
  }, value);
  await enter("2+3");
  const sent = page.waitForRequest(req => req.url().endsWith("/api/v1/evaluate"));
  await page.getByRole("button", { name: "Evaluar", exact: true }).click();
  await sent;
  await page.getByRole("button", { name: "Detener cálculo" }).click();
  await expect(page.getByRole("button", { name: "Detener cálculo" })).toHaveCount(0);
  await enter("4+5");
  const reply = page.waitForResponse(resp => resp.url().endsWith("/api/v1/evaluate"));
  await page.getByRole("button", { name: "Evaluar", exact: true }).click();
  expect((await (await reply).json()).result_approx).toBe(9);
});


test("EN-SG-28 browser Stop reaps the same live isolated worker PID", async ({ page }) => {
  const eventsPath = process.env.SG28_CI_EVENT_FILE;
  // In Linux CI missing instrumentation must FAIL, never silently SKIP the certification gate.
  test.skip(process.platform !== "linux" || (!process.env.CI && !eventsPath), "Linux process evidence required");
  if (process.env.CI) expect(eventsPath, "SG28_CI_EVENT_FILE must be configured in CI").toBeTruthy();
  type Event = { event: string; pid: number; time: number };
  const events = (): Event[] => {
    try {
      return readFileSync(eventsPath!, "utf8").trim().split("\n")
        .filter(Boolean).map((line) => JSON.parse(line) as Event);
    } catch {
      return [];
    }
  };

  await page.goto("/");
  const field = page.locator("math-field").first();
  await field.waitFor({ state: "visible" });
  await field.evaluate(el => {
    (el as HTMLElement & { setValue: (v: string) => void }).setValue("7+11");
    el.dispatchEvent(new InputEvent("input", { bubbles: true, data: "7+11" }));
  });
  const baseline = events().length;
  const sent = page.waitForRequest(req =>
    req.url().endsWith("/api/v1/evaluate") && req.postData()?.includes("7+11") === true
  );
  await page.getByRole("button", { name: "Evaluar", exact: true }).click();
  await sent;
  let pid = 0;
  await expect.poll(() => {
    const started = events().slice(baseline).find(e => e.event === "start");
    pid = started?.pid ?? 0;
    return pid > 0;
  }, { timeout: 7000, message: "Isolated child never became observable" }).toBe(true);

  expect(() => process.kill(pid, 0)).not.toThrow();
  await page.getByRole("button", { name: "Detener cálculo" }).click();
  await expect.poll(() => events().some(e => e.event === "finish" && e.pid === pid),
    { timeout: 5500, message: "Browser Stop did not reap the observed child" }).toBe(true);
  expect(() => process.kill(pid, 0)).toThrow();
  const lifecycle = events();
  const startedAt = lifecycle.find(e => e.event === "start" && e.pid === pid)!.time;
  const finishedAt = lifecycle.find(e => e.event === "finish" && e.pid === pid)!.time;
  expect(finishedAt - startedAt).toBeLessThan(3.8);

  await field.evaluate(el => {
    (el as HTMLElement & { setValue: (v: string) => void }).setValue("4+5");
    el.dispatchEvent(new InputEvent("input", { bubbles: true, data: "4+5" }));
  });
  const reply = page.waitForResponse(resp =>
    resp.url().endsWith("/api/v1/evaluate") && resp.request().postData()?.includes("4+5") === true
  );
  await page.getByRole("button", { name: "Evaluar", exact: true }).click();
  expect((await (await reply).json()).result_approx).toBe(9);
});


test("EN-SG-28 navigating away reaps pending worker and permits fresh evaluation", async ({ page }) => {
  const eventsPath = process.env.SG28_CI_EVENT_FILE;
  test.skip(process.platform !== "linux" || (!process.env.CI && !eventsPath), "Linux process evidence required");
  if (process.env.CI) expect(eventsPath, "SG28_CI_EVENT_FILE must be configured in CI").toBeTruthy();
  const events = (): Array<{ event: string; pid: number; time: number }> => {
    try {
      return readFileSync(eventsPath!, "utf8").trim().split("\n")
        .filter(Boolean).map((line) => JSON.parse(line));
    } catch { return []; }
  };
  await page.goto("/");
  const field = page.locator("math-field").first();
  await field.waitFor({ state: "visible" });
  await field.evaluate(el => {
    (el as HTMLElement & { setValue: (v: string) => void }).setValue("7+11");
    el.dispatchEvent(new InputEvent("input", { bubbles: true, data: "7+11" }));
  });
  const baseline = events().length;
  const sent = page.waitForRequest(req =>
    req.url().endsWith("/api/v1/evaluate") && req.postData()?.includes("7+11") === true
  );
  await page.getByRole("button", { name: "Evaluar", exact: true }).click();
  await sent;
  let pid = 0;
  await expect.poll(() => {
    pid = events().slice(baseline).find(e => e.event === "start")?.pid ?? 0;
    return pid > 0;
  }, { timeout: 7000 }).toBe(true);
  expect(() => process.kill(pid, 0)).not.toThrow();
  await page.getByRole("navigation", { name: "Modos de la calculadora" })
    .getByRole("button", { name: "Gráficas" }).click();
  await expect.poll(() => events().some(e => e.event === "finish" && e.pid === pid),
    { timeout: 5500, message: "Mode switch did not reap active isolated PID" }).toBe(true);
  expect(() => process.kill(pid, 0)).toThrow();

  await page.getByRole("navigation", { name: "Modos de la calculadora" })
    .getByRole("button", { name: "Científica" }).click();
  const recoveredField = page.locator("math-field").first();
  await recoveredField.waitFor({ state: "visible" });
  await recoveredField.evaluate(el => {
    (el as HTMLElement & { setValue: (v: string) => void }).setValue("4+5");
    el.dispatchEvent(new InputEvent("input", { bubbles: true, data: "4+5" }));
  });
  const reply = page.waitForResponse(resp =>
    resp.url().endsWith("/api/v1/evaluate") && resp.request().postData()?.includes("4+5") === true
  );
  await page.getByRole("button", { name: "Evaluar", exact: true }).click();
  expect((await (await reply).json()).result_approx).toBe(9);
  await expect(page.locator("body")).not.toContainText("999999");
});


test("EN-SG-28 closing browser tab reaps active isolated worker and recovers", async ({ page, context }) => {
  const eventsPath = process.env.SG28_CI_EVENT_FILE;
  test.skip(process.platform !== "linux" || (!process.env.CI && !eventsPath), "Linux process evidence required");
  if (process.env.CI) expect(eventsPath, "SG28_CI_EVENT_FILE must be configured in CI").toBeTruthy();
  const events = (): Array<{ event: string; pid: number; time: number }> => {
    try {
      return readFileSync(eventsPath!, "utf8").trim().split("\n")
        .filter(Boolean).map((line) => JSON.parse(line));
    } catch { return []; }
  };
  await page.goto("/");
  const field = page.locator("math-field").first();
  await field.waitFor({ state: "visible" });
  await field.evaluate(el => {
    (el as HTMLElement & { setValue: (v: string) => void }).setValue("7+11");
    el.dispatchEvent(new InputEvent("input", { bubbles: true, data: "7+11" }));
  });
  const baseline = events().length;
  const sent = page.waitForRequest(req =>
    req.url().endsWith("/api/v1/evaluate") && req.postData()?.includes("7+11") === true
  );
  await page.getByRole("button", { name: "Evaluar", exact: true }).click();
  await sent;
  let pid = 0;
  await expect.poll(() => {
    pid = events().slice(baseline).find(e => e.event === "start")?.pid ?? 0;
    return pid > 0;
  }, { timeout: 7000 }).toBe(true);
  expect(() => process.kill(pid, 0)).not.toThrow();

  // A real page close, not a simulated click or mocked HTTP request.
  await page.close();
  await expect.poll(() => events().some(e => e.event === "finish" && e.pid === pid),
    { timeout: 5500, message: "Closing browser tab left isolated PID running" }).toBe(true);
  expect(() => process.kill(pid, 0)).toThrow();

  const reopened = await context.newPage();
  await reopened.goto("/");
  const newField = reopened.locator("math-field").first();
  await newField.waitFor({ state: "visible" });
  await newField.evaluate(el => {
    (el as HTMLElement & { setValue: (v: string) => void }).setValue("4+5");
    el.dispatchEvent(new InputEvent("input", { bubbles: true, data: "4+5" }));
  });
  const reply = reopened.waitForResponse(resp =>
    resp.url().endsWith("/api/v1/evaluate") && resp.request().postData()?.includes("4+5") === true
  );
  await reopened.getByRole("button", { name: "Evaluar", exact: true }).click();
  expect((await (await reply).json()).result_approx).toBe(9);
});
