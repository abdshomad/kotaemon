# Gradio → HTTP mapping

This document ties **Gradio concepts** in ktem to **HTTP API** concepts for the Next.js client.

## App-level state

| Gradio | Role | HTTP equivalent |
|--------|------|-----------------|
| `gr.State` / `settings_state` | Flattened settings from `SettingGroup` | `GET /api/settings` → JSON blob; `PATCH /api/settings` for updates; optionally ETag per session |
| `user_id` in `gr.State` | Current user key for DB and pipelines | Resolved from session/JWT on each request; never trust client-sent user id unless internal service |
| `Conversation` list / selection | `conversation_id`, dropdown, rename | `GET /api/conversations`, `POST /api/conversations`, `PATCH /api/conversations/:id` |

## Chat pipeline (critical path)

Two-step Gradio chain (see `ChatPage.on_register_events` in [`chat/__init__.py`](../../libs/ktem/ktem/pages/chat/__init__.py)):

1. **`submit_msg`** — parses multimodal input, URLs, `@file` references, `WEB_SEARCH_COMMAND`, creates conversation if needed, updates file selector state.
2. **`chat_fn`** — builds pipeline via `create_pipeline`, streams `Document` chunks on channels `chat`, `info`, `plot`.

| Step | Inputs (conceptual) | Outputs (conceptual) | HTTP shape |
|------|---------------------|----------------------|------------|
| Submit | `chat_input` (text + files), `chat_history`, `user_id`, `settings`, `conv_id`, `conv_name`, selector choices | Cleared input, appended user message, new `conv_id`, conversation list, selectors, `command_state` | **Option A**: `POST /api/chat/turn` returns JSON with new `conversationId`, user message row, selector snapshot. **Option B**: same request starts SSE stream and first events include metadata. |
| Stream | Same as `chat_fn` inputs including `reasoning_type`, `model_type`, mindmap, citation, language, `state_chat`, `command_state`, index selections | Incremental assistant text, info panel HTML, plot JSON, updated `chat_state` | **`GET` or `POST` stream** with SSE events (see [chat-and-streaming.md](../frontend/chat-and-streaming.md)) |

### SSE event types (suggested)

Map yields from `chat_fn` to a small union of event types:

- `meta` — `conversationId`, `messageId` (if persisted incrementally).
- `token` — delta for assistant message (channel `chat`).
- `info` — retrieval panel fragment (channel `info`).
- `plot` — Plotly JSON (channel `plot`).
- `state` — reasoning pipeline slice for persistence (`chat_state`).
- `done` — final markers; optional `suggest_name`, follow-up questions (today: `check_and_suggest_name_conv`, `suggest_chat_conv`).
- `error` — user-safe message + optional code.

## Secondary chat handlers (post-stream)

| Gradio handler | Role | HTTP |
|----------------|------|------|
| `persist_data_source` | Saves retrieval/plot history to state/DB | `POST` at end of stream or debounced persist inside API |
| `check_and_suggest_name_conv` + `rename_conv` | Auto-title conversation | `PATCH /api/conversations/:id` with suggested name or dedicated `POST .../suggest-name` |
| `suggest_chat_conv` | Follow-up question chips | `POST /api/chat/followups` after `done` |
| PDF preview JS (`pdfview_js`) | Client-side citation links | Next.js: same behavior in React (scroll/highlight); no API unless preloading PDFs |

## File index UI

| Gradio | HTTP |
|--------|------|
| `upload_button.click` → processing | `POST /api/files/upload` (multipart) or presigned URL flow |
| `filter.submit`, group buttons | `GET /api/files?query=&group=` |
| `chat_button` from file row | Could navigate to `/chat` with `file_ids` query or `POST /api/chat/turn` with context |

## Settings / LLM / reranking / MCP

Gradio sub-pages per manager: each “Save” / “Test” is a handler → **`PATCH` or `POST` per resource** under `/api/settings/...`, `/api/llms/...`, etc. (see [endpoints-outline.md](../backend-api/endpoints-outline.md)).

## Auth

| Gradio | HTTP |
|--------|------|
| `LoginPage.login` + `onSignIn` | `POST /api/auth/login` → Set-Cookie; `POST /api/auth/logout` |
| `toggle_login_visibility` on tabs | Client-side redirect after login; server enforces on API |

## Priority handlers for extraction

1. **`submit_msg`** + **`chat_fn`** + **`create_pipeline`** — core product.
2. **`ConversationControl.new_conv`**, **`select_conv`**, **`reload_conv`** — conversation CRUD.
3. **File index `File` page** — upload pipeline and listing (large surface in [`index/file/ui.py`](../../libs/ktem/ktem/index/file/ui.py)).
4. Settings save handlers — after chat is stable.

See [extraction-strategy.md](../backend-api/extraction-strategy.md) for function boundaries.
