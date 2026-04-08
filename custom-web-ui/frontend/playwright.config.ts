import { defineConfig, devices } from "@playwright/test";

const baseURL = process.env.PLAYWRIGHT_BASE_URL ?? "http://127.0.0.1:3000";

/**
 * E2E tests drive the **browser** against a running Next app + API.
 *
 * - **Next.js** is started automatically via `webServer` unless you set `PLAYWRIGHT_SKIP_WEBSERVER=1`
 *   (e.g. you already run `npm run dev`).
 * - **Backend** must still be running (e.g. uvicorn on port 8000) with `API_PROXY_TARGET` in
 *   `.env.local` so `/api/*` rewrites work for `page.request.post('/api/auth/login', ...)`.
 *
 * PDF path: `E2E_SAMPLE_PDF` or bundled `e2e/fixtures/sample.pdf`
 */
export default defineConfig({
  testDir: "./e2e",
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  workers: 1,
  timeout: 300_000,
  expect: { timeout: 60_000 },
  reporter: [["list"], ["html", { open: "never" }]],
  use: {
    baseURL,
    trace: "on-first-retry",
    screenshot: "only-on-failure",
    video: "retain-on-failure",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  ...(process.env.PLAYWRIGHT_SKIP_WEBSERVER
    ? {}
    : {
        webServer: {
          command: "npm run dev",
          url: baseURL,
          reuseExistingServer: !process.env.CI,
          timeout: 180_000,
          stdout: "pipe",
          stderr: "pipe",
        },
      }),
});
