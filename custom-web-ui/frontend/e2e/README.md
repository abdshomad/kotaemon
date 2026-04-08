# Playwright E2E (`custom-web-ui/frontend/e2e`)

## What runs here

- **`01-login-upload-chat.spec.ts`** — automates [../../test-plan/01-e2e-login-upload-index-chat.md](../../test-plan/01-e2e-login-upload-index-chat.md): login → upload PDF → chat with `@` mention.

## Default PDF (no configuration)

Tests use **`e2e/fixtures/sample.pdf`** by default, resolved as  
`path.join(process.cwd(), "e2e", "fixtures", "sample.pdf")`.

Run **`npm run test:e2e` from `custom-web-ui/frontend`** so the default path matches  
`.../frontend/e2e/fixtures/sample.pdf`.

Override only if needed:

```bash
E2E_SAMPLE_PDF=/other/path/doc.pdf npm run test:e2e
```

## Prerequisites

1. **Backend** (from repo, with `libs` + app data):

   ```bash
   cd custom-web-ui/backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **`frontend/.env.local`** so Next can reach the API (rewrites + middleware). If default ports are busy, generate matching URLs:

   ```bash
   cd custom-web-ui/frontend && npm run ports:apply
   source ../.ports.env   # sets PLAYWRIGHT_BASE_URL, etc.
   ```

   Or set manually:

   ```bash
   API_PROXY_TARGET=http://127.0.0.1:8000
   INTERNAL_API_URL=http://127.0.0.1:8000
   ```

3. **Next.js**: Playwright starts **`npm run dev`** automatically via `webServer` (same shell as tests). If you already run the dev server, set **`PLAYWRIGHT_SKIP_WEBSERVER=1`** to avoid a second instance.

4. **Install browser** (once):

   ```bash
   cd custom-web-ui/frontend
   npx playwright install chromium
   ```

## Commands

| Command                                                      | Meaning                                        |
| ------------------------------------------------------------ | ---------------------------------------------- |
| `npm run test:e2e`                                           | Run tests; PDF = `e2e/fixtures/sample.pdf`     |
| `npm run test:e2e:ui`                                        | Playwright UI mode                             |
| `PLAYWRIGHT_BASE_URL=http://localhost:3000 npm run test:e2e` | Override base URL                              |

## Environment variables

| Variable              | Default                 | Purpose            |
| --------------------- | ----------------------- | ------------------ |
| `PLAYWRIGHT_BASE_URL` | `http://127.0.0.1:3000` | Next.js origin (use `source ../.ports.env` after `npm run ports:apply` if ports shifted) |
| `E2E_SAMPLE_PDF`      | *(see Default PDF)*   | Alternate PDF path |

## Timeouts

Indexing a PDF can take **minutes** on first run (embeddings, chunking). The spec uses long timeouts; if the machine is slow, increase them in `playwright.config.ts` or the spec file.
