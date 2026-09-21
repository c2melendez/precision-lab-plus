import { expect, test } from "@playwright/test";

const api = "http://127.0.0.1:8000/api/v1";

test("health y evaluación básica del backend", async ({ request }) => {
  const health = await request.get(`${api}/health`);
  expect(health.ok()).toBeTruthy();

  const response = await request.post(`${api}/evaluate`, {
    data: { expression: "2+2" },
  });
  expect(response.ok()).toBeTruthy();
  const body = await response.json();
  expect(body.success).toBe(true);
  expect(body.result_approx).toBe(4);
});

test("contrato log base 10 y ln natural", async ({ request }) => {
  const logResponse = await request.post(`${api}/evaluate`, {
    data: { expression: "log(100)" },
  });
  const logBody = await logResponse.json();
  expect(logBody.success).toBe(true);
  expect(logBody.result_approx).toBeCloseTo(2, 12);

  const lnResponse = await request.post(`${api}/evaluate`, {
    data: { expression: "ln(e)" },
  });
  const lnBody = await lnResponse.json();
  expect(lnBody.success).toBe(true);
  expect(lnBody.result_approx).toBeCloseTo(1, 12);
});
