# Test plan 04 — Docker Compose + nginx (full stack)

**Goal:** Validate **production-like** topology: only **nginx** publishes a host port; Next.js and FastAPI are internal; routing sends `/` to the frontend and `/api` to the backend.

**Audience:** Release verification or infra changes.

## Prerequisites

- Docker and Docker Compose available.
- Repository root context as documented in [`../docker-compose.yml`](../docker-compose.yml).

## Steps

1. From `custom-web-ui/`:

   ```bash
   docker compose up --build
   ```

2. Open `http://localhost:${WEB_PORT:-8080}` (default **8080**).

3. Run **plan 01** (login → upload PDF → chat) through the **browser** at this origin (not port 3000).

4. **Expect:**
   - Single entry URL (nginx only).
   - Static assets and Next routes load from `/`.
   - API calls from the browser go to **same origin** `/api/...` and reach FastAPI (check Network tab: no CORS errors for same-origin).

5. **Negative:** Direct access to `frontend:3000` or `backend:8000` from the host should **not** be required; if compose does not publish those ports, they must not be reachable from outside (per design).

## Pass criteria

- Plan 01 completes behind nginx.
- No accidental exposure of internal service ports on production-like configs.

## Related

- Architecture: [`../../remake-ui-plan/architecture/docker-compose-nginx.md`](../../remake-ui-plan/architecture/docker-compose-nginx.md)
- Smoke E2E: [01-e2e-login-upload-index-chat.md](01-e2e-login-upload-index-chat.md)
