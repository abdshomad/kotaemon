# API endpoints outline (draft)

Prefix: `/api` (version later: `/api/v1`).

All authenticated routes resolve `user_id` from session/JWT the same way `gr.State` does today.

## Health

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/health` | Liveness |
| GET | `/api/ready` | DB + optional model warm-up check |

## Auth

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/auth/login` | Body: username/password if user management enabled |
| POST | `/api/auth/logout` | Clear session |
| GET | `/api/auth/me` | Current user profile or 401 |

## Settings

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/settings` | Flattened settings (mirror `settings_state` initial value) |
| PATCH | `/api/settings` | Partial updates; validate per `SettingGroup` |

## Conversations

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/conversations` | List for sidebar (filter by user) |
| POST | `/api/conversations` | Create empty conversation (`new_conv`) |
| GET | `/api/conversations/:id` | Metadata + optional last messages |
| PATCH | `/api/conversations/:id` | Rename, `is_public` |
| DELETE | `/api/conversations/:id` | Delete with cascade rules matching current behavior |

## Chat

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/chat/turn` | Body: `conversationId?`, `message` (multimodal JSON), `settingsSnapshot`, `reasoningType`, `modelType`, `language`, `citation`, `mindmap`, `indexSelections`, `command` — returns `202` + stream URL **or** opens SSE directly |
| GET or POST | `/api/chat/stream` | SSE: `conversationId`, message payload as query/body per security choice |

Follow-up and naming:

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/conversations/:id/suggest-name` | `check_and_suggest_name_conv` |
| POST | `/api/chat/followups` | `suggest_chat_conv` inputs |

## Files / index

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/index/:indexId/files` | List/filter (parity with file index UI) |
| POST | `/api/index/:indexId/upload` | Multipart upload |
| POST | `/api/index/:indexId/url` | Ingest URL(s) |
| GET | `/api/index/:indexId/files/:fileId` | Metadata |
| GET | `/api/index/:indexId/files/:fileId/content` | Download or PDF stream |
| DELETE | `/api/index/:indexId/files/:fileId` | Delete |
| … | Groups, batch ops | Mirror `group_*` handlers in `index/file/ui.py` |

## Admin / resources

| Method | Path | Purpose |
|--------|------|---------|
| GET/POST | `/api/resources/users` | If `ResourcesTab` user CRUD remains; **admin-only** |

## LLM / embeddings / reranking / MCP (if exposed separately)

Often folded under `PATCH /api/settings`; optional explicit test endpoints:

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/llms/:id/test` | Connection test |
| POST | `/api/embeddings/:id/test` | Connection test |

## Errors

Use JSON: `{ "error": { "code": "...", "message": "..." } }` with appropriate HTTP status (400, 401, 403, 429, 500).

Rate limiting: align with [`check_rate_limit`](../../libs/ktem/ktem/utils/rate_limit.py) for demo mode.
