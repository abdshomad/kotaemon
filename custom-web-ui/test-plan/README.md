# Custom web UI — test plans

Manual and semi-automated test plans for `custom-web-ui/`, ordered **from simplest to more involved**. Use them for smoke checks before releases or after refactors.

## How to read these documents

- **Prerequisites** — environment (local dev vs Docker), env vars, and that `libs/ktem` + app data paths are consistent with [`../README.md`](../README.md).
- **Pass criteria** — observable outcomes (HTTP status, UI state, SSE events). Where the stack is still **MVP**, chat may **echo** the user message while still proving **session**, **indexing**, and **payload wiring** (see plan notes).

## Index of plans

| Order | Document | Focus |
|------:|----------|--------|
| 1 | [01-e2e-login-upload-index-chat.md](01-e2e-login-upload-index-chat.md) | Shortest browser path: login → upload PDF → index → chat with file context |
| 2 | [02-api-happy-path.md](02-api-happy-path.md) | Same flow via `curl` / cookie jar (no browser), good for CI hooks later |
| 3 | [03-sessions-crud-and-files.md](03-sessions-crud-and-files.md) | Conversations CRUD, `/files` filters, delete file, logout |
| 4 | [04-docker-nginx-stack.md](04-docker-nginx-stack.md) | Full Compose + nginx: single port, `/` and `/api` routing |
| 5 | [05-negative-and-edge-cases.md](05-negative-and-edge-cases.md) | Auth failures, bad inputs, empty states |

Automated counterpart for plan **01**: see [`../frontend/e2e/README.md`](../frontend/e2e/README.md) and `npm run test:e2e` under `frontend/`.

## Suggested frequency

- **01** — every change that touches auth, index, or chat streaming.
- **02** — when debugging cookies, CORS, or proxy boundaries.
- **03** — after conversation or file-index API changes.
- **04** — before tagging a release that ships Compose.
- **05** — after security or validation hardening.
