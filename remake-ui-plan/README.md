# Next.js UI remake — documentation index

This folder contains **planning documentation only** for replacing the Gradio-based UI (`app.py` → `ktem.main.App`) with a **Next.js** frontend while keeping **Python/kotaemon** as the implementation of indexing, LLMs, reasoning pipelines, and persistence.

## Migration progress (task status)

Statuses: **Complete**, **In progress**, **Not yet**.

| Phase | Status |
|-------|--------|
| [Phase 0 — Repository and contracts](migration-phases/phases.md) | **In progress** — Next.js frontend scaffold **Complete**; backend skeleton, Docker Compose + nginx, and `custom-web-ui/README.md` env/run documentation **Not yet** |
| Phase 1 — Auth stub + session | **Not yet** |
| Phase 2 — Settings read-only | **Not yet** |
| Phase 3 — Conversations CRUD | **Not yet** |
| Phase 4 — Chat stream (MVP) | **Not yet** |
| Phase 5 — File index + chat integration | **Not yet** |
| Phase 6 — Settings write + LLM/embeddings/rerank CRUD | **Not yet** |
| Phase 7 — Full auth + Resources + Help | **Not yet** |
| Phase 8 — Hardening and Gradio retirement | **Not yet** |

Per-task detail: [migration-phases/phases.md](migration-phases/phases.md).

## Goals

- **UI**: App Router (TypeScript), routes that mirror current tabs and workflows.
- **Backend**: New HTTP layer (FastAPI or Starlette recommended) exposing REST + **SSE** (or WebSocket) for streaming chat; **no** reimplementation of ML/indexing in Node.
- **Parity**: Ship by vertical slices (chat end-to-end before deep settings polish).

## Constraints

- Business logic stays in Python modules under `libs/ktem` and `libs/kotaemon` where possible; Gradio-specific return values (`gr.update`, generator yields to Gradio components) are replaced with plain data and stream events.
- Existing deploy modes (`launch.sh`, SSO, demo) inform auth and routing but the first implementation can target the default non-SSO path.

## Repository layout: `custom-web-ui/`

All new UI and HTTP API code for this remake lives under **`custom-web-ui/`** at the repository root:

- **`custom-web-ui/frontend/`** — Next.js app (own `package.json`, App Router, TypeScript).
- **`custom-web-ui/backend/`** — Python FastAPI (or Starlette) service that wraps existing `libs/ktem` / `libs/kotaemon` logic.

**Run in production-style mode** with **Docker Compose + nginx**: only the **nginx** service publishes ports to the internet; the frontend and backend run as internal services, and nginx routes `/` to the Next app and `/api` to the Python API. See [Docker Compose + nginx](architecture/docker-compose-nginx.md).

Share configuration with the rest of the repo via `.env`, `flowsettings.py`, and `RUNME.md` conventions (backend container typically mounts or receives the same env as the current Gradio app).

## Sub-plans

### Architecture

- [System boundaries](architecture/system-boundaries.md) — what lives in Next vs Python; sessions and env vars.
- [Docker Compose + nginx](architecture/docker-compose-nginx.md) — `custom-web-ui/` layout, internal services, single public entrypoint.
- [Gradio → HTTP mapping](architecture/gradio-to-http-mapping.md) — `gr.State`, events, and handlers mapped to API concepts.

### Frontend (Next.js)

- [Routing and layout](frontend/routing-and-layout.md) — tab → route mapping and nested layouts.
- [Design system](frontend/design-system.md) — theme/CSS parity with `KotaemonTheme` and dark mode.
- [Chat and streaming](frontend/chat-and-streaming.md) — messages, citations, PDF viewing.

### Backend API (Python)

- [Endpoints outline](backend-api/endpoints-outline.md) — REST/SSE resource sketch.
- [Extraction strategy](backend-api/extraction-strategy.md) — pulling logic out of Gradio into callable services.

### Features (parity tracking)

- [Chat](features/chat.md)
- [Files and indexing](features/files-and-indexing.md)
- [Settings and LLM](features/settings-and-llm.md)
- [Auth and users](features/auth-and-users.md)

### Migration

- [Phases](migration-phases/phases.md) — ordered rollout with dependencies.

## Reading order

1. `architecture/system-boundaries.md` + `architecture/docker-compose-nginx.md` (when deploying with Compose)
2. `backend-api/extraction-strategy.md` + `architecture/gradio-to-http-mapping.md`
3. `backend-api/endpoints-outline.md` + `frontend/routing-and-layout.md`
4. Feature docs as you implement each epic
5. `migration-phases/phases.md` for sequencing

## Out of scope (this documentation)

- One-shot rewrite of all Gradio UI code.
- Moving embeddings, retrieval, or graph indexing to JavaScript.
