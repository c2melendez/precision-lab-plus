import { readFileSync } from "node:fs";
import { expect, test, type Locator, type Page } from "@playwright/test";

// Native integration: real MathLive, React handlers, HTTP API and rendered result.
// No route interception, mocked converter, direct API substitution or silent skip.
const cases = readFileSync(new URL("../../qa/certification/syntax309_cases.jsonl", import.meta.url), "utf8")
  .trim().split("\n").map((line) => JSON.parse(line) as { id: string; entrada: string });
const fixture = (id: string) => {
  const row = cases.find((candidate) => candidate.id === id);
  if (!row) throw new Error(`Missing canonical fixture ${id}`);
  return row.entrada;
};

async function enter(field: Locator, source: string) {
  await field.evaluate((element, value) => {
    const mathfield = element as HTMLElement & { setValue(value: string): void };
    mathfield.setValue(value);
    element.dispatchEvent(new InputEvent("input", { bubbles: true, inputType: "insertText", data: value }));
  }, source);
  // Ingestion is evidence: erasing a malformed source must fail this test.
  await expect.poll(() => field.evaluate((element) =>
    (element as HTMLElement & { value: string }).value)).toBe(source);
}

async function evaluate(page: Page, field: Locator, source: string, expected: number, backendExpression = source) {
  await enter(field, source);
  const responsePromise = page.waitForResponse((response) =>
    response.url().endsWith("/api/v1/evaluate") && response.request().method() === "POST");
  await page.getByRole("button", { name: "Evaluar", exact: true }).click();
  const response = await responsePromise;
  expect(response.status()).toBe(200);
  expect(response.request().postDataJSON().expression).toBe(backendExpression);
  const body = await response.json();
  expect(body.success).toBe(true);
  expect(body.result_approx).toBe(expected);
  expect(body.request_id).toBeTruthy();
  // KaTeX renders the mathematical minus as U+2212; retain the exact value.
  await expect.poll(async () => (await page.locator('[aria-live="polite"] .a11y-scale-result-lg .katex-html').last().textContent())?.replace(/−/g, "-")).toBe(String(expected));
  await expect(page.getByRole("alert")).toHaveCount(0);
  expect(body.result_latex).toBe(String(expected));
  return {requestId: body.request_id as string, reentry: body.result_latex as string};
}

test("SY-R-13 native original cube-root binding, controls and HTTP reentry", async ({ page }, testInfo) => {
  const pageErrors: string[] = [];
  const requests: Array<{ url: string; body: unknown }> = [];
  const evidence: Array<{ source: string; expected: number; requestId: string; reentry: string }> = [];
  page.on("pageerror", (error) => pageErrors.push(error.message));
  page.on("request", (request) => {
    if (request.url().includes("/api/v1/") && request.method() === "POST") {
      requests.push({ url: request.url(), body: request.postDataJSON() });
    }
  });
  await page.goto("/");
  const field = page.locator("math-field").first();
  await expect(field).toBeVisible();
  const canonical = fixture("SY-R-13");
  expect(canonical).toBe(String.raw`\sqrt[3]{x}\ \text{con}\ x=27`);
  const controls = [
    { source: canonical, expected: 3, backend: "((x)**(1/(3))) con x=(27)" },
    { source: String.raw`\sqrt[3]{x}\ \text{con}\ x=8`, expected: 2, backend: "((x)**(1/(3))) con x=(8)" },
    { source: String.raw`\sqrt[3]{y}\ \text{con}\ y=64`, expected: 4, backend: "((y)**(1/(3))) con y=(64)" },
  ];
  for (const { source, expected, backend } of controls) {
    const first = await evaluate(page, field, source, expected, backend);
    const second = await evaluate(page, field, first.reentry, expected);
    expect(second.requestId).not.toBe(first.requestId);
    evidence.push({ source, expected, ...first }, { source: first.reentry, expected, ...second });
  }
  await evaluate(page, field, "2+3", 5);
  expect(requests).toHaveLength(7);
  expect(requests.every((request) => request.url.endsWith("/api/v1/evaluate"))).toBe(true);
  expect(new Set(evidence.map((item) => item.requestId)).size).toBe(6);
  expect(pageErrors).toEqual([]);
  await testInfo.attach("SY-R-13-native-http-evidence", {
    body: JSON.stringify({ canonical, project: testInfo.project.name, requests, evidence, pageErrors }, null, 2),
    contentType: "application/json",
  });
});

test("SY-R-14 native original absolute value, signed controls and HTTP reentry", async ({ page }, testInfo) => {
  const pageErrors: string[] = [];
  const requests: Array<{ url: string; body: unknown }> = [];
  const evidence: Array<{ source: string; expected: number; requestId: string; reentry: string }> = [];
  page.on("pageerror", (error) => pageErrors.push(error.message));
  page.on("request", (request) => {
    if (request.url().includes("/api/v1/") && request.method() === "POST") {
      requests.push({ url: request.url(), body: request.postDataJSON() });
    }
  });
  await page.goto("/");
  const field = page.locator("math-field").first();
  await expect(field).toBeVisible();
  const canonical = fixture("SY-R-14");
  expect(canonical).toBe(String.raw`\left\lvert x\right\rvert\ \text{con}\ x=-4`);
  const controls = [
    // The existing typed-bars UI resolves the declared scalar, retaining abs
    // for real backend evaluation. The input itself remains the full fixture.
    { source: canonical, expected: 4, backend: "abs(-4)" },
    { source: String.raw`\left\lvert x\right\rvert+x\ \text{con}\ x=-4`, expected: 0, backend: "(abs(x)+x) con x=(-4)" },
    { source: String.raw`\left\lvert x\right\rvert+x\ \text{con}\ x=4`, expected: 8, backend: "(abs(x)+x) con x=(4)" },
    { source: String.raw`\left\lvert y\right\rvert\ \text{con}\ y=-7`, expected: 7, backend: "abs(-7)" },
  ];
  for (const { source, expected, backend } of controls) {
    const first = await evaluate(page, field, source, expected, backend);
    const second = await evaluate(page, field, first.reentry, expected);
    expect(second.requestId).not.toBe(first.requestId);
    evidence.push({ source, expected, ...first }, { source: first.reentry, expected, ...second });
  }
  await evaluate(page, field, "2+3", 5);
  expect(requests).toHaveLength(9);
  expect(requests.every((request) => request.url.endsWith("/api/v1/evaluate"))).toBe(true);
  expect(new Set(evidence.map((item) => item.requestId)).size).toBe(8);
  expect(pageErrors).toEqual([]);
  await testInfo.attach("SY-R-14-native-http-evidence", {
    body: JSON.stringify({ canonical, project: testInfo.project.name, requests, evidence, pageErrors }, null, 2),
    contentType: "application/json",
  });
});

test("SY-X-05 native30 grouping levels, scalar controls and HTTP reentry", async ({ page }, testInfo) => {
  const errors: string[] = [];
  const sources: Array<{ source: string; requestId: string; reentry: string }> = [];
  page.on("pageerror", (error) => errors.push(error.message));
  await page.goto("/");
  const field = page.locator("math-field").first();
  await expect(field).toBeVisible();
  const canonical = fixture("SY-X-05");
  expect(canonical).toBe(String.raw`\underbrace{(\cdots((1))\cdots)}_{30\text{ niveles}}`);
  for (const [inner, expected] of [["1", 1], ["7", 7], ["2+3", 5]] as const) {
    const source = "(".repeat(30) + inner + ")".repeat(30);
    expect(source.length).toBe(60 + inner.length);
    expect(source.match(/\(/g)).toHaveLength(30);
    expect(source.match(/\)/g)).toHaveLength(30);
    // evaluate verifies exact ingestion AND the unflattened HTTP request.
    const first = await evaluate(page, field, source, expected);
    const second = await evaluate(page, field, first.reentry, expected);
    expect(second.requestId).not.toBe(first.requestId);
    sources.push({ source, ...first }, { source: first.reentry, ...second });
  }
  await evaluate(page, field, "2+3", 5);
  expect(new Set(sources.map((item) => item.requestId)).size).toBe(6);
  expect(errors).toEqual([]);
  await testInfo.attach("SY-X-05-native-http-evidence", {
    body: JSON.stringify({ canonical, project: testInfo.project.name, sources, errors }, null, 2),
    contentType: "application/json",
  });
});

test("SY-X-06 native10000-character source, readable HTTP length rejection and recovery", async ({ page }, testInfo) => {
  testInfo.setTimeout(90000);
  const errors: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  await page.goto("/");
  const field = page.locator("math-field").first();
  await expect(field).toBeVisible();
  const canonical = fixture("SY-X-06");
  expect(canonical).toBe(String.raw`\text{(entrada de 10 000 caracteres)}`);
  const source = "1+".repeat(4999) + "11";
  expect(source).toHaveLength(10000);
  await enter(field, source);
  const responsePromise = page.waitForResponse((response) => response.url().endsWith("/api/v1/evaluate") && response.request().method() === "POST");
  await page.getByRole("button", { name: "Evaluar", exact: true }).click();
  const response = await responsePromise;
  expect(response.request().postDataJSON().expression).toBe(source);
  expect(response.status()).toBe(422);
  const rejected = await response.json();
  expect(rejected.success).toBe(false);
  expect(rejected.error_code).toBe("VALIDATION_ERROR");
  expect(rejected.result_latex).toBeNull();
  const resultAlert = page.locator('form[aria-labelledby="basic-mode-heading"]').getByRole("alert");
  await expect(resultAlert).toContainText("VALIDATION_ERROR");
  await expect(resultAlert).toContainText("Entrada demasiado larga: el máximo permitido es de 500 caracteres.");
  const recovered = await evaluate(page, field, "2+3", 5);
  const reentered = await evaluate(page, field, recovered.reentry, 5);
  expect(new Set([rejected.request_id, recovered.requestId, reentered.requestId]).size).toBe(3);
  expect(errors).toEqual([]);
  await testInfo.attach("SY-X-06-native-length-evidence", {
    body: JSON.stringify({ canonical, project: testInfo.project.name, sourceLength: source.length,
      source, rejected, recovered, reentered, errors }, null, 2),
    contentType: "application/json",
  });
});

test("SY-X-08 native principal complex root, HTTP reentry and finite recovery", async ({ page }, testInfo) => {
  const errors: string[] = [];
  const evidence: unknown[] = [];
  const ids: string[] = [];
  page.on("pageerror", error => errors.push(error.message));
  await page.goto("/");
  const field = page.locator("math-field").first();
  await expect(field).toBeVisible();
  const canonical = fixture("SY-X-08");
  expect(canonical).toBe(String.raw`\sqrt{-1}`);
  async function complex(source: string, backend: string) {
    await enter(field, source);
    const pending = page.waitForResponse(response => response.url().endsWith("/api/v1/evaluate") && response.request().method() === "POST");
    await page.getByRole("button", {name:"Evaluar", exact:true}).click();
    const response = await pending;
    expect(response.status()).toBe(200);
    expect(response.request().postDataJSON().expression).toBe(backend);
    const body = await response.json();
    expect(body.success).toBe(true);
    expect(body.result_type).toBe("scalar");
    expect(body.result_text).toBe("I");
    expect(body.result_latex).toBe("i");
    expect(body.result_approx).toBeNull();
    expect(body.error_code).toBeNull();
    expect(body.request_id).toBeTruthy();
    await expect(page.locator('[aria-live="polite"] .a11y-scale-result-lg .katex-html').last()).toHaveText("i");
    await expect(page.getByRole("alert")).toHaveCount(0);
    ids.push(body.request_id);
    evidence.push({source, backend, body});
    return body.result_latex as string;
  }
  await complex(await complex(canonical, "sqrt(-1)"), "i");
  ids.push((await evaluate(page, field, "i^2", -1)).requestId);
  const recovery = await evaluate(page, field, "2+3", 5);
  const again = await evaluate(page, field, recovery.reentry, 5);
  ids.push(recovery.requestId, again.requestId);
  expect(new Set(ids).size).toBe(5);
  expect(errors).toEqual([]);
  await testInfo.attach("SY-X-08-native-http-evidence", {body:JSON.stringify({domain:"existing principal complex branch", canonical, project:testInfo.project.name, evidence, ids, errors},null,2),contentType:"application/json"});
});

const rejectionMessages: Record<string, string> = {
  "SY-X-01": "La expresión no puede estar vacía.",
  "SY-X-02": "La expresión no puede estar vacía.",
  "SY-X-03": "Sintaxis incompleta",
  "SY-R-12": "Entrada no matemática: escribe una expresión válida.",
  "SY-X-07": "Forma indeterminada: infinito menos infinito no está definido.",
};

for (const id of Object.keys(rejectionMessages)) {
  test(`${id} native source, readable local rejection and two real HTTP recoveries`, async ({ page }, testInfo) => {
    const pageErrors: string[] = [];
    const sent: Array<{ url: string; body: unknown }> = [];
    page.on("pageerror", (error) => pageErrors.push(error.message));
    page.on("request", (request) => {
      if (request.url().includes("/api/v1/") && request.method() === "POST") {
        sent.push({ url: request.url(), body: request.postDataJSON() });
      }
    });
    await page.goto("/");
    const field = page.locator("math-field").first();
    await expect(field).toBeVisible();
    const canonical = fixture(id);
    if (id === "SY-X-01") expect(canonical).toBe("*(vacía)*");
    if (id === "SY-R-12") expect(canonical).toBe(String.raw`\text{no existe}`);
    if (id === "SY-X-07") expect(canonical).toBe(String.raw`\infty-\infty`);
    const source = id === "SY-X-01" ? "" : canonical;
    for (let cycle = 0; cycle < 2; cycle += 1) {
      const before = sent.length;
      await enter(field, source);
      await page.getByRole("button", { name: "Evaluar", exact: true }).click();
      const alert = page.getByRole("alert");
      await expect(alert).toContainText(rejectionMessages[id]);
      if (id === "SY-X-03" || id === "SY-R-12") await expect(alert).not.toContainText("vacía");
      expect(sent).toHaveLength(before); // local validation must not fabricate backend evidence
      const expected = id === "SY-X-07" ? (cycle === 0 ? 0 : 5) : cycle === 0 ? 5 : 9;
      const recovery = id === "SY-X-07" ? (cycle === 0 ? "3-3" : "2+3") : cycle === 0 ? "2+3" : "4+5";
      const first = await evaluate(page, field, recovery, expected);
      const second = await evaluate(page, field, first.reentry, expected);
      expect(second.requestId).not.toBe(first.requestId);
      expect(sent).toHaveLength(before + 2);
      expect(pageErrors).toEqual([]);
    }
    await testInfo.attach(`${id}-native-http-evidence`, {
      body: JSON.stringify({ id, project: testInfo.project.name, canonical, source, sent, pageErrors }, null, 2),
      contentType: "application/json",
    });
  });
}


test("SY-X-09 native extreme power bounded HTTP rejection and finite reentry", async ({ page }, testInfo) => {
  const errors: string[] = [];
  page.on("pageerror", error => errors.push(error.message));
  await page.goto("/");
  const field = page.locator("math-field").first();
  await expect(field).toBeVisible();
  const source = fixture("SY-X-09");
  expect(source).toBe("99999999999^{99999999999}");
  await enter(field, source);
  const responsePromise = page.waitForResponse(response =>
    response.url().endsWith("/api/v1/evaluate") && response.request().method() === "POST");
  await page.getByRole("button", { name: "Evaluar", exact: true }).click();
  const response = await responsePromise;
  expect(response.status()).toBe(200);
  expect(response.request().postDataJSON().expression).toBe("99999999999^(99999999999)");
  const rejected = await response.json();
  expect(rejected.success).toBe(false);
  expect(rejected.error_code).toBe("COMPLEXITY_LIMIT");
  expect(rejected.result_latex).toBeNull();
  expect(rejected.result_text).toBeNull();
  await expect(page.getByRole("alert").filter({ hasText: "COMPLEXITY_LIMIT" })).toContainText("COMPLEXITY_LIMIT");
  const recovery = await evaluate(page, field, "2+3", 5);
  const reentry = await evaluate(page, field, recovery.reentry, 5);
  expect(new Set([rejected.request_id, recovery.requestId, reentry.requestId]).size).toBe(3);
  expect(errors).toEqual([]);
  await testInfo.attach("SY-X-09-native-http-evidence", {
    body: JSON.stringify({ source, project:testInfo.project.name, rejected, recovery, reentry, errors }, null, 2),
    contentType:"application/json",
  });
});


test("SY-X-10 native astronomical nested power rejects before expansion and recovers", async ({page}, testInfo) => {
  const errors: string[] = [];
  page.on("pageerror", error => errors.push(error.message));
  await page.goto("/");
  const field = page.locator("math-field").first();
  await expect(field).toBeVisible();
  const source = fixture("SY-X-10");
  expect(source).toBe("10^{10^{10}}");
  await enter(field, source);
  const pending = page.waitForResponse(response =>
    response.url().endsWith("/api/v1/evaluate") && response.request().method() === "POST");
  await page.getByRole("button", {name:"Evaluar",exact:true}).click();
  const response = await pending;
  expect(response.status()).toBe(200);
  expect(response.request().postDataJSON().expression.replace(/[()]/g,"")).toBe("10^10^10");
  const rejected = await response.json();
  expect(rejected.success).toBe(false);
  expect(rejected.error_code).toBe("COMPLEXITY_LIMIT");
  expect(rejected.result_text).toBeNull();
  expect(rejected.result_latex).toBeNull();
  await expect(page.getByRole("alert").filter({hasText:"COMPLEXITY_LIMIT"})).toContainText("COMPLEXITY_LIMIT");
  const recovered = await evaluate(page,field,"2+3",5);
  const reentered = await evaluate(page,field,recovered.reentry,5);
  expect(new Set([rejected.request_id,recovered.requestId,reentered.requestId]).size).toBe(3);
  expect(errors).toEqual([]);
  await testInfo.attach("SY-X-10-native-http-evidence",{
    body:JSON.stringify({source,project:testInfo.project.name,rejected,recovered,reentered,errors},null,2),
    contentType:"application/json"
  });
});
test("SY-X-11 native astronomical nested power rejects before expansion and recovers", async ({page}, testInfo) => {
  const errors: string[] = [];
  page.on("pageerror", error => errors.push(error.message));
  await page.goto("/");
  const field = page.locator("math-field").first();
  await expect(field).toBeVisible();
  const source = fixture("SY-X-11");
  expect(source).toBe("9^{9^{9}}");
  await enter(field, source);
  const pending = page.waitForResponse(response =>
    response.url().endsWith("/api/v1/evaluate") && response.request().method() === "POST");
  await page.getByRole("button", {name:"Evaluar",exact:true}).click();
  const response = await pending;
  expect(response.status()).toBe(200);
  expect(response.request().postDataJSON().expression.replace(/[()]/g,"")).toBe("9^9^9");
  const rejected = await response.json();
  expect(rejected.success).toBe(false);
  expect(rejected.error_code).toBe("COMPLEXITY_LIMIT");
  expect(rejected.result_text).toBeNull();
  expect(rejected.result_latex).toBeNull();
  await expect(page.getByRole("alert").filter({hasText:"COMPLEXITY_LIMIT"})).toContainText("COMPLEXITY_LIMIT");
  const recovered = await evaluate(page,field,"2+3",5);
  const reentered = await evaluate(page,field,recovered.reentry,5);
  expect(new Set([rejected.request_id,recovered.requestId,reentered.requestId]).size).toBe(3);
  expect(errors).toEqual([]);
  await testInfo.attach("SY-X-11-native-http-evidence",{
    body:JSON.stringify({source,project:testInfo.project.name,rejected,recovered,reentered,errors},null,2),
    contentType:"application/json"
  });
});

test("SY-X-12 native non-elementary integral notice, finite integral recovery and reentry", async ({page}, testInfo) => {
  test.setTimeout(60_000);
  const errors: string[] = [];
  page.on("pageerror", error => errors.push(error.message));
  await page.goto("/");
  const field = page.locator("math-field").first();
  await expect(field).toBeVisible();
  const source = fixture("SY-X-12");
  expect(source).toBe(String.raw`\int\sin\left(x^{x}\right)dx`);
  await enter(field, source);
  const pending = page.waitForResponse(response =>
    response.url().endsWith("/api/v1/integral") && response.request().method() === "POST");
  await page.getByRole("button", {name:"Evaluar", exact:true}).click();
  const response = await pending;
  expect(response.status()).toBe(200);
  const payload = response.request().postDataJSON() as {expression: string; variable: string; lower_bound?: string; upper_bound?: string};
  expect(payload.variable).toBe("x");
  expect(payload.lower_bound).toBeUndefined();
  expect(payload.upper_bound).toBeUndefined();
  const integrand = payload.expression.replace(/\s/g, "");
  expect(integrand).toMatch(/sin/i);
  expect(integrand).not.toMatch(/integral/i);
  const rejected = await response.json();
  expect(rejected.success).toBe(false);
  expect(rejected.error_code).toBe("UNSUPPORTED_OPERATION");
  expect(rejected.result_text).toBeNull();
  expect(rejected.result_latex).toBeNull();
  expect(String(rejected.error_message)).toContain("Sin forma elemental");
  const alert = page.getByRole("alert").filter({hasText:"UNSUPPORTED_OPERATION"});
  await expect(alert).toContainText("Sin forma elemental");
  await expect(page.locator(".a11y-scale-result-lg")).toHaveCount(0);

  await enter(field, String.raw`\int x\,dx`);
  const finitePending = page.waitForResponse(http =>
    http.url().endsWith("/api/v1/integral") && http.request().method() === "POST");
  await page.getByRole("button", {name:"Evaluar", exact:true}).click();
  const finiteResponse = await finitePending;
  expect(finiteResponse.status()).toBe(200);
  expect(String(finiteResponse.request().postDataJSON().expression).replace(/\s/g, "")).toBe("x");
  const finite = await finiteResponse.json();
  expect(finite.success).toBe(true);
  expect(String(finite.result_text)).toMatch(/x\*\*2\/2/);
  expect(String(finite.result_text)).toContain("+ C");
  expect(String(finite.result_text)).not.toMatch(/Integral/);
  expect(finite.request_id).toBeTruthy();
  expect(finite.request_id).not.toBe(rejected.request_id);
  await expect(page.getByRole("alert")).toHaveCount(0);

  const recovered = await evaluate(page, field, "2+3", 5);
  const reentered = await evaluate(page, field, recovered.reentry, 5);
  expect(new Set([rejected.request_id, finite.request_id, recovered.requestId, reentered.requestId]).size).toBe(4);
  expect(errors).toEqual([]);
  await testInfo.attach("SY-X-12-native-http-evidence", {
    body: JSON.stringify({
      source, project: testInfo.project.name, integrand, rejected, finite, recovered, reentered, errors,
    }, null, 2),
    contentType: "application/json",
  });
});
