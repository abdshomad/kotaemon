import path from "node:path";

import { expect, test } from "@playwright/test";
import type { APIRequestContext } from "@playwright/test";

/** Idempotent runs: remove prior test upload so POST /upload succeeds (no "already indexed"). */
async function removeSamplePdfIfPresent(request: APIRequestContext) {
  const idxRes = await request.get("/api/index");
  if (!idxRes.ok()) return;
  const indices = (await idxRes.json()) as { id: number }[];
  const indexId = indices[0]?.id;
  if (indexId == null) return;
  const filesRes = await request.get(`/api/index/${indexId}/files`);
  if (!filesRes.ok()) return;
  const files = (await filesRes.json()) as { id: string; name: string }[];
  for (const f of files) {
    if (f.name === "sample.pdf") {
      await request.delete(
        `/api/index/${indexId}/files/${encodeURIComponent(f.id)}`
      );
    }
  }
}

/**
 * Default PDF when `E2E_SAMPLE_PDF` is unset: `frontend/e2e/fixtures/sample.pdf`
 * (run `npm run test:e2e` from `custom-web-ui/frontend` so `process.cwd()` is correct.)
 */
function resolveSamplePdf(): string {
  const envPath = process.env.E2E_SAMPLE_PDF;
  if (envPath) {
    return path.resolve(envPath);
  }
  return path.join(process.cwd(), "e2e", "fixtures", "sample.pdf");
}

/**
 * Mirrors custom-web-ui/test-plan/01-e2e-login-upload-index-chat.md
 *
 * Session is created via the same `/api/auth/login` route the UI uses (through Next rewrites).
 * Requires: Next (webServer or manual `npm run dev`) + backend + `API_PROXY_TARGET` in `.env.local`.
 */
test.describe("01 — login, upload PDF, index, chat with @ mention", () => {
  test("full path", async ({ page }) => {
    const samplePdf = resolveSamplePdf();

    await test.step("login (session via /api/auth/login)", async () => {
      const res = await page.request.post("/api/auth/login", {
        data: { username: "default", password: "e2e" },
        headers: { "Content-Type": "application/json" },
      });
      const body = await res.text();
      if (!res.ok()) {
        throw new Error(
          `Login API failed (${res.status()}). Is the backend up and API_PROXY_TARGET set? Body: ${body.slice(0, 500)}`
        );
      }
      await removeSamplePdfIfPresent(page.request);
    });

    await test.step("upload PDF and wait for index row", async () => {
      await page.goto("/files");
      await expect(page.getByTestId("files-page")).toBeVisible();
      // Wait until primary index + file list are loaded; "No file index" is absent
      // during "Loading…" too, so that alone is not enough (avoids uploading with indexId null).
      await page.waitForResponse(
        (r) =>
          /\/api\/index\/\d+\/files(\?|$)/.test(r.url()) &&
          r.request().method() === "GET" &&
          r.ok(),
        { timeout: 120_000 }
      );
      await expect(
        page.getByText("No file index configured.")
      ).not.toBeVisible();
      await expect(page.getByTestId("files-upload-input")).toBeEnabled({
        timeout: 30_000,
      });

      const uploadDone = page.waitForResponse(
        (r) =>
          r.url().includes("/upload") &&
          r.request().method() === "POST" &&
          r.ok(),
        { timeout: 300_000 }
      );
      // Associate with the visible "Upload file" label so the file input receives the change event.
      await page
        .locator("label")
        .filter({ hasText: "Upload file" })
        .locator('input[type="file"]')
        .setInputFiles(samplePdf);
      await uploadDone;

      await expect(
        page.locator('[data-testid="files-row"]').first()
      ).toBeVisible({
        timeout: 240_000,
      });
      await expect(
        page.locator('[data-testid="files-page"] p[role="alert"]')
      ).not.toBeVisible();
    });

    await test.step("chat with @ file mention and stream", async () => {
      const filesReady = page.waitForResponse(
        (r) => /\/api\/index\/\d+\/files(\?|$)/.test(r.url()) && r.ok(),
        { timeout: 120_000 }
      );
      await page.getByTestId("nav-chat").click();
      await expect(page.getByTestId("chat-input")).toBeVisible();
      await filesReady;

      const chat = page.getByTestId("chat-input");
      await chat.fill("@");
      await expect(page.getByTestId("chat-mention-option").first()).toBeVisible(
        {
          timeout: 30_000,
        }
      );
      await page.getByTestId("chat-mention-option").first().click();

      await chat.fill("Summarize the document");
      await page.getByTestId("chat-send").click();

      await expect(page.getByTestId("chat-info-panel")).not.toHaveText(
        "No retrieval info yet.",
        { timeout: 120_000 }
      );
      await expect(page.getByTestId("chat-info-panel")).toContainText(
        /Phase 5|file|MVP/i
      );
    });
  });
});
