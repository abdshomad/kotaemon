# Custom web UI (Next.js + Python API)

This directory will hold the **replacement** for the Gradio UI: a **Next.js** frontend and a **Python** HTTP API that wraps existing `libs/ktem` and `libs/kotaemon` logic.

## Intended layout

```
custom-web-ui/
  frontend/          # Next.js (App Router, TypeScript) — Phase 0 scaffold present
  backend/           # FastAPI service (to be added in migration Phase 0)
  nginx/             # Reverse proxy config for Docker Compose
  docker-compose.yml # nginx + frontend + backend; only nginx publishes ports
  README.md          # this file
```

### Frontend (local dev)

From `custom-web-ui/frontend/`: `npm install`, then `npm run dev` (Next.js dev server). `npm run build` / `npm start` for production build. `npm run lint` and `npm run format` / `npm run format:check` for ESLint and Prettier.

## Deployment

**Docker Compose + nginx:** only **nginx** should expose ports to the internet. The **frontend** and **backend** services run on an internal Docker network; nginx routes `/` to Next.js and `/api` to the API.

Authoritative planning details: [../remake-ui-plan/architecture/docker-compose-nginx.md](../remake-ui-plan/architecture/docker-compose-nginx.md).
