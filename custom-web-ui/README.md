# Custom web UI (Next.js + Python API)

This directory will hold the **replacement** for the Gradio UI: a **Next.js** frontend and a **Python** HTTP API that wraps existing `libs/ktem` and `libs/kotaemon` logic.

## Intended layout

```
custom-web-ui/
  frontend/          # Next.js (App Router, TypeScript)
  backend/           # FastAPI: /api/health, /api/auth/*, /api/settings, /api/index*, /api/conversations*, /api/chat/stream
  nginx/             # Reverse proxy config for Docker Compose
  docker-compose.yml # nginx + frontend + backend; only nginx publishes ports
  README.md          # this file
```

### Frontend (local dev)

From `custom-web-ui/frontend/`: `npm install`, then `npm run dev` (Next.js dev server). `npm run build` / `npm start` for production build. `npm run lint` and `npm run format` / `npm run format:check` for ESLint and Prettier.

#### Ports already in use

If `3000` / `8000` are taken, allocate free ports and refresh env files:

```bash
cd custom-web-ui/frontend && npm run ports:apply
# or: bash custom-web-ui/scripts/apply-local-ports.sh
```

This writes:

- `custom-web-ui/.ports.env` — `source` this in your shell for `PLAYWRIGHT_BASE_URL`, `CUSTOM_WEB_UI_*_PORT`, etc.
- `frontend/.env.local` — `API_PROXY_TARGET` and `INTERNAL_API_URL` pointing at the chosen backend URL.

Optional: `PREFERRED_FRONTEND_PORT=3100 PREFERRED_BACKEND_PORT=8100 npm run ports:apply` to start searching from other bases.

When the API runs on a different origin (e.g. `http://127.0.0.1:8000`), create `frontend/.env.local` with (or use `ports:apply` above):

- `API_PROXY_TARGET=http://127.0.0.1:8000` — rewrites `/api/*` in Next to the backend so login and cookies stay same-origin to the dev server.
- `INTERNAL_API_URL=http://127.0.0.1:8000` — used by **middleware** to call `GET /api/auth/me` with forwarded cookies (stronger than cookie presence alone).

If `INTERNAL_API_URL` is unset, middleware only checks for the `kh_session` cookie (stub behavior).

### Backend (local dev)

From `custom-web-ui/backend/`: create a virtualenv, install `requirements.txt`, then run:

`uvicorn app.main:app --reload --host 0.0.0.0 --port 8000` (or the port printed by `npm run ports:apply`; set `PYTHONPATH` / `KH_APP_DATA_DIR` / repo root per your environment — see [`scripts/README.md`](scripts/README.md))

Health check endpoint: `GET /api/health`.

Auth (Phase 1): signed cookie `kh_session` via Starlette sessions — `POST /api/auth/login` (optional JSON body), `GET /api/auth/me`, `POST /api/auth/logout`. Stub accepts any credentials until full user management (Phase 7).

Settings (Phase 2): authenticated `GET /api/settings` returns a flattened settings snapshot compatible with the chat pipeline.

Frontend debug page: authenticated `/settings` fetches and renders `/api/settings` JSON.

Conversations (Phase 3): authenticated CRUD scaffold at `GET/POST /api/conversations`, `GET/PATCH/DELETE /api/conversations/{id}`.

Frontend chat shell now includes a sidebar list with conversation selection and a "New" action.

Chat stream (Phase 4 MVP): authenticated `POST /api/chat/stream` emits SSE events (`meta`, `token`, `info`, `state`, `done`) and persists message history into the selected conversation.

File index (Phase 5): authenticated `GET /api/index`, `GET /api/index/{id}/files`, `POST /api/index/{id}/upload` (multipart), `DELETE /api/index/{id}/files/{fileId}` using ktem `FileIndex` pipelines. The chat stream accepts optional `index_id` and `file_ids` and stores them on user messages. Next.js `/files` lists and manages uploads; the chat composer supports `@` mentions against indexed files.

The backend skeleton is structured for monorepo imports and adds `libs/` to `sys.path` so it can evolve to call `ktem`/`kotaemon` services directly.

## Environment variables

- `WEB_PORT` (default `8080`) for nginx host port in compose.
- `KH_APP_DATA_DIR` (default `/app/ktem_app_data`) passed into backend container.
- `API_CORS_ORIGINS` (optional) for backend CORS allowlist when needed.
- `SESSION_SECRET` for signing the `kh_session` cookie (defaults in compose for dev only; set in production).
- `INTERNAL_API_URL` (frontend) — base URL for middleware to validate sessions (`http://backend:8000` in Compose).
- `API_PROXY_TARGET` (frontend local dev) — Next.js rewrite target so `/api` hits the Python server.
- `NEXT_PUBLIC_API_BASE_URL` for frontend local dev; use same-origin/relative `/api` in nginx topology.

## Build contexts and run instructions

`custom-web-ui/docker-compose.yml` uses repository-root build context (`context: ..`) so backend images can import/copy shared code from `libs/`.

From `custom-web-ui/`:

- Start stack: `docker compose up --build`
- Stop stack: `docker compose down`

Access app at `http://localhost:${WEB_PORT:-8080}`. Only nginx publishes a host port; frontend/backend remain internal-only.

## Deployment

**Docker Compose + nginx:** only **nginx** should expose ports to the internet. The **frontend** and **backend** services run on an internal Docker network; nginx routes `/` to Next.js and `/api` to the API.

Authoritative planning details:

- [../remake-ui-plan/architecture/docker-compose-nginx.md](../remake-ui-plan/architecture/docker-compose-nginx.md)
- [../remake-ui-plan/architecture/system-boundaries.md](../remake-ui-plan/architecture/system-boundaries.md)
