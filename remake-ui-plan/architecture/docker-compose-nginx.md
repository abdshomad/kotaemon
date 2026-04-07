# Docker Compose + nginx (production-style topology)

All new UI and API code for the Next.js remake lives under **`custom-web-ui/`** at the repository root. Frontend and backend are **separate** subprojects inside that folder so they can be built as distinct images and wired together by **nginx**.

## Directory layout

```
custom-web-ui/
  frontend/                 # Next.js (App Router, TypeScript)
    package.json
    Dockerfile              # multi-stage: build + node runner or static export + serve
  backend/                  # Python FastAPI (or Starlette) API layer
    pyproject.toml / requirements.txt
    Dockerfile              # installs deps; COPY ktem/kotaemon from build context
  nginx/
    nginx.conf              # reverse proxy only (or templates for envsubst)
  docker-compose.yml        # orchestrates nginx + frontend + backend (+ optional volumes)
  .env.example              # compose-time variables (not secrets in git)
```

The **Python API** implementation should import existing packages from the parent repo (`libs/ktem`, `libs/kotaemon`). Typical Docker build context is the **repository root** so Dockerfiles can `COPY libs/ ...` and `COPY custom-web-ui/backend/ ...`, or use a monorepo-friendly pattern with `context: ..` and `dockerfile: custom-web-ui/backend/Dockerfile`.

## Services (conceptual)

| Service | Role | Published to host |
|---------|------|-------------------|
| **nginx** | TLS termination (optional), routes `/` to frontend and `/api` (and `/api/*`) to backend | **Yes** — only `80` / `443` (or a single chosen port) |
| **frontend** | Next.js standalone server or static files served by nginx | **No** — internal Docker network only |
| **backend** | Uvicorn/Gunicorn FastAPI | **No** — reachable only as `http://backend:8000` from nginx |

Internet clients never connect directly to the frontend or backend containers; they only hit **nginx**.

## nginx routing

- **`/`** → `proxy_pass` to the frontend upstream (e.g. `http://frontend:3000` for Next standalone, or serve static files from a volume if exported).
- **`/api/`** → `proxy_pass` to the backend (e.g. `http://backend:8000/api/`). Keep path prefixes consistent with FastAPI’s `root_path` / router prefix if used.

### SSE (chat streaming)

For `text/event-stream` responses, nginx must not buffer the stream indefinitely:

- `proxy_buffering off;` (or appropriate `proxy_read_timeout`) on the `/api/` location that handles SSE.
- Optionally `chunked_transfer_encoding on;` where relevant.

### WebSockets (if used later)

- `proxy_http_version 1.1;`, `Upgrade` and `Connection` headers for the upgrade path.

## Browser → API base URL

With this topology, the browser uses a **single origin** (nginx). Configure Next.js so client fetches use **relative URLs** (e.g. `fetch('/api/...')`) or `NEXT_PUBLIC_API_BASE_URL=""` / same origin. Avoid exposing a separate public URL for the backend.

Cookies for session auth should be set with `Path=/` and `SameSite` appropriate for your domain; the API remains behind `/api` on the same host.

## docker-compose outline

```yaml
# Illustrative only — adjust image names, build contexts, and env files when implementing.
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      # - "443:443"  # when TLS is configured
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - frontend
      - backend
    networks: [internal]

  frontend:
    build:
      context: ../..   # repo root if Dockerfile needs full tree
      dockerfile: custom-web-ui/frontend/Dockerfile
    expose:
      - "3000"
    networks: [internal]
    # environment: NODE_ENV, etc.

  backend:
    build:
      context: ../..
      dockerfile: custom-web-ui/backend/Dockerfile
    expose:
      - "8000"
    networks: [internal]
    env_file:
      - ../.env   # or custom-web-ui/.env — align with flowsettings / KH_*
    volumes:
      # optional: mount KH_APP_DATA_DIR, model cache, or sqlite DB path

networks:
  internal:
    driver: bridge
```

**Port publishing:** only **`nginx`** declares `ports:`. `frontend` and `backend` use **`expose`** (or no host ports) so they stay on the internal network.

## Development vs production

- **Local dev** without Docker: run `frontend` and `backend` on localhost with different ports and CORS, as in [system-boundaries.md](system-boundaries.md).
- **Docker Compose**: use the nginx topology above for integration tests and production-like demos.
- **TLS**: terminate at nginx with certificates (Let’s Encrypt or mounted secrets); do not expose backend to apply TLS separately.

## Related

- [system-boundaries.md](system-boundaries.md) — env vars and session model.
- [phases.md](../migration-phases/phases.md) — Phase 0 includes compose + nginx scaffolding.
