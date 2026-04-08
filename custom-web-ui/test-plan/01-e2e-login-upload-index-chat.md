# Test plan 01 — E2E: login, upload PDF, index, chat (simplest)

**Goal:** Validate the minimum happy path in the **browser** with the smallest number of steps: authenticate, put a PDF into the primary file index, then send a chat turn that references that file.

**Audience:** QA or developers doing a quick smoke test.

## Prerequisites

- Backend running with monorepo `libs/` available (see [`../README.md`](../README.md)).
- `KH_APP_DATA_DIR` (or default app data) writable so the file index and DB can be created.
- A small **PDF** file on disk (any short PDF; content can be a single page).

## Environment

| Mode | Base URL | Notes |
|------|----------|--------|
| Next dev + API proxy | `http://localhost:3000` | Set `API_PROXY_TARGET` and optionally `INTERNAL_API_URL` on the frontend so `/api/*` and middleware work. |
| API only | `http://127.0.0.1:8000` | Use plan [02-api-happy-path.md](02-api-happy-path.md) instead. |

## Steps

### 1. Login

1. Open `/login`.
2. Submit the form (stub auth accepts any password; username can be default).
3. **Expect:** Redirect to the main app (e.g. `/` or chat home), no infinite redirect loop.

### 2. Upload a PDF and index it

1. Open **`/files`** (Files page).
2. **Expect:** At least one file index appears (first index selected by default).
3. Use **Choose file** / upload control and select your PDF.
4. Wait until upload finishes (loading state clears).
5. **Expect:**
   - Success path: the file appears in the list with a **name**, **size**, and **id** (implicit in row actions).
   - If upload fails, note the error message and HTTP status (see [05-negative-and-edge-cases.md](05-negative-and-edge-cases.md)).

**Backend behavior:** `POST /api/index/{index_id}/upload` runs the ktem indexing pipeline for the saved file.

### 3. Note `index_id` and `file_id`

For the chat step you need:

- **`index_id`:** Shown as the selected index on `/files`, or from `GET /api/index` (first index is usually `1` in default configs).
- **`file_id`:** From the file row after upload (the API returns `file_id` on upload success; the list endpoint returns each file’s `id`).

### 4. Chat with the indexed file

1. Open **`/`** (chat).
2. Ensure a conversation exists (create **New** if needed).
3. Attach file context **as implemented by the UI** (e.g. `@` mention and pick the file, or multi-select chips — follow current chat page behavior).
4. Send a short question that only makes sense if the PDF is in context (e.g. “Summarize the document”).

**Pass criteria (current MVP):**

- Stream starts (`POST /api/chat/stream` returns `200`, `text/event-stream`).
- SSE includes `meta` with `conversationId`, then `token` events, then `done`.
- **Info panel** or stream payload reflects **index context** when files are selected (e.g. info mentioning selected file count / index id).
- **Note:** Until full RAG is wired to `libs/ktem` retrievers, the assistant text may still be an **echo-style MVP** while proving **session + index + chat payload** end-to-end. Treat “indexed PDF + successful stream + context in info/state” as pass for this plan.

## Failure triage (quick)

| Symptom | Check |
|---------|--------|
| Redirect loop on `/` | `INTERNAL_API_URL` / `kh_session` / `GET /api/auth/me` |
| 401 on `/api/index/*` | Login cookie not sent; `credentials: "include"` in frontend |
| Upload 4xx/5xx | `python-multipart` installed; PDF allowed by index `supported_file_types`; backend logs |
| Chat ignores files | Request body includes `index_id` + `file_ids`; see Network tab |

## Automated run (Playwright)

The same flow is implemented as a browser test:

- Spec: [`../frontend/e2e/01-login-upload-chat.spec.ts`](../frontend/e2e/01-login-upload-chat.spec.ts)
- How-to: [`../frontend/e2e/README.md`](../frontend/e2e/README.md)

**Quick start:** start backend (`uvicorn`) and frontend (`npm run dev`) with `API_PROXY_TARGET` / `INTERNAL_API_URL`, then from `custom-web-ui/frontend`:

```bash
npx playwright install chromium   # once
npm run test:e2e
```

**Default PDF:** `frontend/e2e/fixtures/sample.pdf` (no prompts). Override: `E2E_SAMPLE_PDF=/absolute/path/doc.pdf npm run test:e2e`

## Related

- API-only version: [02-api-happy-path.md](02-api-happy-path.md)
- Broader UI flows: [03-sessions-crud-and-files.md](03-sessions-crud-and-files.md)
