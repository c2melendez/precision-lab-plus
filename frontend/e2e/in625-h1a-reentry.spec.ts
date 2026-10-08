import { expect, test } from "@playwright/test";

type Page = import("@playwright/test").Page;

const cases = [
  ["EN-RE-01", "\\frac{1}{2}+\\frac{1}{3}"],
  ["EN-RE-02", "2^{10}"],
  ["EN-RE-03", "\\sqrt{8}"],
  ["EN-RE-04", "\\sin^{2}x+\\cos^{2}x"],
  ["EN-RE-05", "\\arcsin\\left(\\frac{1}{2}\\right)"],
  ["EN-RE-06", "\\frac{d}{dx}\\left(x\\ln x-x\\right)"],
  ["EN-RE-07", "e^{x}"],
  ["EN-RE-08", "\\sqrt{-4}"],
] as const;

async function setInput(page: Page, value: string) {
  const field = page.locator("math-field").first();
  await field.waitFor({ state: "visible" });
  await field.evaluate((el, v) => {
    const mf = el as HTMLElement & { setValue?: (value: string) => void; value?: string };
    if (typeof mf.setValue === "function") mf.setValue(String(v));
    else mf.value = String(v);
    el.dispatchEvent(new InputEvent("input", { bubbles: true, inputType: "insertText", data: String(v) }));
  }, value);
  await page.waitForTimeout(120);
}

async function calculate(page: Page): Promise<string> {
  await page.evaluate(() => window.mathVirtualKeyboard?.hide());
  const responsePromise = page.waitForResponse(
    (r) => r.url().includes("/api/v1/evaluate") && r.request().method() === "POST",
    { timeout: 15000 },
  );
  await page.getByRole("button", { name: "Evaluar", exact: true }).click();
  const response = await responsePromise;
  const body = await response.json();
  expect(body.success, JSON.stringify(body)).toBe(true);
  const output = String(body.result_latex ?? body.result_text ?? body.result_approx ?? "");
  expect(output.trim()).not.toBe("");
  return output;
}

function canonical(text: string) {
  return text
    .replace(/\\left|\\right/g, "")
    .replace(/\\,/g, "")
    .replace(/\\cdot/g, "")
    .replace(/\s+/g, "");
}

test.describe("IN625 H1a reentrada básica Plus", () => {
  for (const [id, input] of cases) {
    test(id + " salida vuelve a entrar como punto fijo", async ({ page }) => {
      await page.goto("./");
      await setInput(page, input);
      const s1 = await calculate(page);

      await setInput(page, s1);
      const reinjected = await page.locator("math-field").first().evaluate((el) =>
        String((el as HTMLElement & { value?: string }).value ?? "")
      );
      const s2 = await calculate(page).catch((err) => {
        throw new Error(id + " S1=" + s1 + " REINJECTED=" + reinjected + " ERROR=" + String(err));
      });
      expect(canonical(s2), id + " S1=" + s1 + " REINJECTED=" + reinjected + " S2=" + s2).toBe(canonical(s1));
    });
  }
});
