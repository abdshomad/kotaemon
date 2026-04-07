# System boundaries

## What stays in Python

| Area | Location (indicative) | Notes |
|------|------------------------|--------|
| Database access | `libs/ktem/ktem/db/`, `ktem/db/models.py` | SQLModel/SQLAlchemy |
| Index lifecycle | `ktem/index/manager.py`, `ktem/index/file/` | File index, graph indices, pipelines |
| LLM / embeddings / reranking managers | `ktem/llms/`, `ktem/embeddings/`, `ktem/rerankings/` | Configuration from settings |
| Reasoning pipelines | `ktem/reasoning/`, `ktem/components.py` | Selected by user in chat |
| Chat orchestration | `ktem/pages/chat/__init__.py` (`chat_fn`, `create_pipeline`, `submit_msg`) | Refactor to services, not rewrite |
| MCP | `ktem/mcp/` | If enabled |
| Rate limiting | `ktem/utils/rate_limit.py` | Demo / per-request limits |

## What moves to Next.js

| Area | Responsibility |
|------|----------------|
| Routing and layouts | Replace `gr.Tabs` with file-based routes and shared shell layout |
| Forms and interactive widgets | Conversation list, settings forms, file tables, modals |
| Client streaming UI | Consume SSE/WebSocket; render markdown, citations, plots |
| Theme | CSS variables / Tailwind (or similar) replacing `KotaemonTheme` + bundled CSS |
| Auth UX | Login page, redirects; tokens or cookies as agreed with API |

## New component: HTTP API (Python)

A dedicated layer implemented under **`custom-web-ui/backend/`** (importing `libs/ktem` and `libs/kotaemon` from the repo root), or as a package (e.g. `ktem_api/`) colocated there:

- Validates requests (Pydantic models).
- Maps authenticated user to `user_id` (same semantics as `gr.State` today).
- Calls **service functions** extracted from current Gradio handlers.
- Returns JSON or **SSE** streams for chat.

Gradio must not be required for API operation once parity is reached (optional: keep Gradio for transition behind a feature flag).

## Session and identity

Current patterns:

- **Default**: `user_id` in `gr.State` — often `"default"` when user management is off (`KH_FEATURE_USER_MANAGEMENT`).
- **User management**: `LoginPage` + `User` model; `onSignIn` / `onSignOut` toggle tab visibility.
- **SSO / demo**: separate entrypoints (`sso_app.py`, `sso_app_demo.py`, `KH_SSO_ENABLED`, `KH_DEMO_MODE`).

Next.js + API should agree on one mechanism:

- **Session cookie** issued by API after login (HttpOnly), or
- **JWT** in Authorization header for SPA,

with the API resolving to the same `user_id` string (or integer id) the rest of ktem expects.

## Environment variables

Reuse existing knobs where possible (see `flowsettings.py`, `.env`, `RUNME.md`):

- `KH_APP_DATA_DIR`, model paths, feature flags (`KH_DEMO_MODE`, `KH_WEB_SEARCH_BACKEND`, etc.).
- New vars as needed: `NEXT_PUBLIC_API_BASE_URL` — use **empty or same origin** when the browser talks to nginx only; `API_CORS_ORIGINS` mainly for local dev without nginx; optional `API_SESSION_SECRET`.

## Deployment

- **Development (no Docker)**: Next dev server (e.g. `:3000`) + Uvicorn API (e.g. `:8000`) with CORS; optional local nginx mirroring production routes.
- **Docker Compose + nginx (recommended for integrated deploy)**: See [docker-compose-nginx.md](docker-compose-nginx.md). Only **nginx** binds host ports `80`/`443`; **`custom-web-ui/frontend`** and **`custom-web-ui/backend`** are internal services. Nginx proxies `/` → frontend and `/api` → backend so the public internet never connects directly to Next or FastAPI.

Document image build contexts (repo root vs `custom-web-ui/`) in `custom-web-ui/README.md` when implemented.
