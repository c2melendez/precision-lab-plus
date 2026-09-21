import { defineConfig, devices } from "@playwright/test";

const frontendPort = 4174;
const backendPort = 8000;
const baseURL = `http://127.0.0.1:${frontendPort}/`;
const frontendOrigin = `http://127.0.0.1:${frontendPort}`;

export default defineConfig({
  testDir: "./e2e",
  timeout: 35_000,
  expect: { timeout: 7_500 },
  fullyParallel: true,
  forbidOnly: Boolean(process.env.CI),
  retries: process.env.CI ? 1 : 0,
  workers: process.env.CI ? 2 : undefined,
  reporter: [["list"], ["html", { open: "never" }]],
  use: {
    baseURL,
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
    video: "retain-on-failure",
  },
  projects: [
    { name: "desktop-chromium", use: { ...devices["Desktop Chrome"], browserName: "chromium", viewport: { width: 1440, height: 900 } } },
    { name: "tablet-chromium", use: { browserName: "chromium", viewport: { width: 1024, height: 768 }, hasTouch: true } },
    { name: "mobile-chromium", use: { ...devices["Pixel 7"], browserName: "chromium" } },
  ],
  webServer: [
    {
      command: `python -m uvicorn app.main:app --host 127.0.0.1 --port ${backendPort}`,
      cwd: "../backend",
      url: `http://127.0.0.1:${backendPort}/api/v1/health`,
      reuseExistingServer: !process.env.CI,
      timeout: 120_000,
      // QA-only: el frontend E2E vive en otro puerto/origen.
      env: { CORS_ORIGINS: frontendOrigin },
    },
    {
      command: `npm run dev -- --host 127.0.0.1 --port ${frontendPort}`,
      cwd: ".",
      url: baseURL,
      reuseExistingServer: !process.env.CI,
      timeout: 120_000,
      env: { VITE_API_BASE_URL: `http://127.0.0.1:${backendPort}` },
    },
  ],
});
