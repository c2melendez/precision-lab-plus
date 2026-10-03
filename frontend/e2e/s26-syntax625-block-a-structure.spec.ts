import { expect, test, type Page } from "@playwright/test";

type StructuralCase = {
  id: string;
  input: string;
  mustContain: string[];
  mustNotContain?: string[];
  mustNotMatchEcho?: RegExp[];
};

const CASES: StructuralCase[] = [
  { id: "EN-FR-07", input: "\\frac{x+1}{x-1}", mustContain: ["x+1", "x-1"] },
  { id: "EN-FR-08", input: "(x+1)/(x-1)", mustContain: ["x+1", "x-1"] },
  { id: "EN-FR-09", input: "x+1\\over x-1", mustContain: ["x+1", "x-1"] },
  { id: "EN-FR-11", input: "\\frac1x", mustContain: ["1/x"] },
  { id: "EN-FR-16", input: "\\frac{1}{\\frac{1}{x}+\\frac{1}{y}}", mustContain: ["x", "y"] },
  { id: "EN-FR-19", input: "\\frac{a}{b}\\frac{c}{d}", mustContain: ["a", "b", "c", "d"] },

  { id: "EN-FR-17", input: "\\frac{1}{2}x", mustContain: ["1/2", "x"], mustNotMatchEcho: [/\\frac\{1\}\{2\s*x\}/] },
  { id: "EN-FR-18", input: "\\frac{1}{2x}", mustContain: ["2x"] },
  { id: "EN-FR-20", input: "x+1/x-1", mustContain: ["x", "1/x"] },
  { id: "EN-DL-01", input: "\\left(x+1\\right)^{2}", mustContain: ["(x+1)", "^2"] },
  { id: "EN-DL-02", input: "\\left[x+1\\right]^{2}", mustContain: ["x+1", "^2"] },
  { id: "EN-DL-04", input: "\\bigl(x+1\\bigr)^{2}", mustContain: ["(x+1)", "^2"] },
  { id: "EN-DL-06", input: "\\mleft(x+1\\mright)^{2}", mustContain: ["(x+1)", "^2"] },
  { id: "EN-DL-11", input: "\\|x-1\\|", mustContain: ["|x-1|"] },
  { id: "EN-DL-12", input: "\\left\\| x-1 \\right\\|", mustContain: ["|x-1|"] },
  { id: "EN-DL-13", input: "\\|\\|x\\|-1\\|", mustContain: ["x", "1"] },
  { id: "EN-DL-14", input: "\\lvert\\lvert x\\rvert-1\\rvert", mustContain: ["x", "1"] },
  { id: "EN-DL-15", input: "\\lvert x\\rvert\\lvert y\\rvert", mustContain: ["x", "y"] },
  { id: "EN-DL-07", input: "((x))", mustContain: ["x"] },
  { id: "EN-DL-10", input: "\\lvert x-1\\rvert", mustContain: ["|x-1|"] },
  { id: "EN-OP-08", input: "2\\cdot x\\cdot y", mustContain: ["2", "x", "y"] },
  { id: "EN-RD-05", input: "\\sqrt{x}y", mustContain: ["sqrt", "x", "y"] },
  { id: "EN-RD-10", input: "\\sqrt[n]{x}", mustContain: ["x", "n"] },
];

async function setExpression(page: Page, value: string) {
  await page.evaluate(() => customElements.whenDefined("math-field"));
  const field = page.locator("math-field").first();
  await expect(field).toBeVisible();
  await field.evaluate((node, v) => {
    const el = node as HTMLElement & { value: string };
    el.value = v as string;
    el.dispatchEvent(new Event("input", { bubbles: true }));
  }, value);
}

type EvaluateBody = {
  success: boolean;
  result_views?: Array<{ key: string; label: string; latex: string }>;
  error_code?: string | null;
  error_message?: string | null;
};

async function originalLatex(page: Page, caseId?: string): Promise<string> {
  const calculate = page.getByRole("button", { name: /calcular|evaluar/i }).first();
  const responsePromise = page.waitForResponse(
    (r) => r.url().includes("/api/v1/evaluate") && r.request().method() === "POST",
  );
  await calculate.click();
  const response = await responsePromise;
  const body = (await response.json()) as EvaluateBody;
  let assertionContext = JSON.stringify(body);
  if (caseId && ["EN-DL-11", "EN-DL-12", "EN-DL-13"].includes(caseId)) {
    const field = page.locator("math-field").first();
    assertionContext = JSON.stringify({
      caseId,
      canonical: await field.inputValue(),
      requestBody: response.request().postDataJSON?.() ?? null,
      body,
    });
  }
  expect(body.success, assertionContext).toBe(true);

  const originalView = body.result_views?.find((view) => view.key === "original");
  expect(originalView, JSON.stringify(body)).toBeDefined();

  const original = page.getByRole("button", { name: "Original", exact: true }).first();
  await expect(original).toBeVisible({ timeout: 12000 });
  await original.click();
  await expect(original).toHaveAttribute("aria-pressed", "true");

  return String(originalView?.latex ?? "")
    .replace(/\\left|\\right/g, "")
    .replace(/\s+/g, "");
}

test.describe("S26 Sintaxis 625 — Bloque A eco estructural", () => {
  for (const tc of CASES) {
    test(tc.id, async ({ page }) => {
      await page.goto("./");
      await setExpression(page, tc.input);
      const echo = await originalLatex(page, tc.id);
      const plain = echo
        .replace(/\\frac\{([^{}]+)\}\{([^{}]+)\}/g, "$1/$2")
        .replace(/\\sqrt\{([^{}]+)\}/g, "sqrt($1)")
        .replace(/[{}]/g, "");
      for (const fragment of tc.mustContain) expect(plain, `${tc.id}: ${echo}`).toContain(fragment);
      for (const fragment of tc.mustNotContain ?? []) expect(plain, `${tc.id}: ${echo}`).not.toContain(fragment);
      for (const pattern of tc.mustNotMatchEcho ?? []) expect(echo, `${tc.id}: ${echo}`).not.toMatch(pattern);
    });
  }
});
