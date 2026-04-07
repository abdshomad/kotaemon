# Custom web UI (Next.js + Python API)

This directory will hold the **replacement** for the Gradio UI: a **Next.js** frontend and a **Python** HTTP API that wraps existing `libs/ktem` and `libs/kotaemon` logic.

## Intended layout

```
custom-web-ui/
  frontend/          # Next.js (App Router, TypeScript)
  backend/           # FastAPI API skeleton with /api/health
  nginx/             # Reverse proxy config for Docker Compose
  docker-compose.yml # nginx + frontend + backend; only nginx publishes ports
  README.md          # this file
```

### Frontend (local dev)

From `custom-web-ui/frontend/`: `npm install`, then `npm run dev` (Next.js dev server). `npm run build` / `npm start` for production build. `npm run lint` and `npm run format` / `npm run format:check` for ESLint and Prettier.

### Backend (local dev)

From `custom-web-ui/backend/`: create a virtualenv, install `requirements.txt`, then run:

`uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`

Health check endpoint: `GET /api/health`.

The backend skeleton is structured for monorepo imports and adds `libs/` to `sys.path` so it can evolve to call `ktem`/`kotaemon` services directly.

## Environment variables

- `WEB_PORT` (default `8080`) for nginx host port in compose.
- `KH_APP_DATA_DIR` (default `/app/ktem_app_data`) passed into backend container.
- `API_CORS_ORIGINS` (optional) for backend CORS allowlist when needed.
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
