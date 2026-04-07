# Extraction strategy: Gradio → services

Goal: **thin HTTP adapters** that call **pure-ish Python functions** returning dicts, lists, or async generators—**not** `gr.update` or Gradio-specific types.

## Principles

1. **Keep DB and pipeline code untouched** in the first pass; only wrap the outer layer.
2. **Split “compute” from “map to UI”**: today `submit_msg` mixes parsing, side effects, and `gr.update` — extract `parse_chat_input(...) -> ParsedTurn` then `apply_turn_to_conversation(...)`.
3. **Streaming**: `chat_fn` already yields tuples for Gradio; replace with `AsyncIterator[StreamEvent]` for SSE.

## Priority 1 — Chat send path

| Current | Location | Proposed service |
|---------|----------|------------------|
| `submit_msg` | [`ChatPage.submit_msg`](../../libs/ktem/ktem/pages/chat/__init__.py) | `services/chat/turn.py`: `prepare_user_turn(parsed, user_id, settings, conv_id, ...) -> TurnPrep` (new conv id, user message text, file ids, command) |
| URL ingestion via `first_indexing_url_fn` | Called inside `submit_msg` | Keep callable; return structured `IngestResult` instead of mutating selector in-place |
| `chat_fn` | Same file | `services/chat/stream.py`: `stream_reply(turn_ctx, pipeline_inputs) -> AsyncIterator[StreamEvent]` |
| `create_pipeline` | Same file | Move unchanged to `services/chat/pipeline_factory.py` (import from current module to avoid duplication) |
| `persist_data_source` | Same file | `services/chat/persist.py`: called after stream completes |

**Handler boundaries:**

- **`prepare_user_turn`**: Everything from line ~885 to ~977 except return formatting — returns a dataclass instead of tuple ending in `used_command`.
- **`stream_reply`**: Body of `chat_fn` (from `create_pipeline` through final yield) — emit `StreamEvent` instead of `(chat_history, refs, plot_gr, plot, chat_state)`.

## Priority 2 — Conversation control

| Current | Location | Proposed service |
|---------|----------|------------------|
| `new_conv`, `select_conv`, `reload_conv`, `rename_conv` | [`chat/control.py`](../../libs/ktem/ktem/pages/chat/control.py) | `services/conversations.py`: CRUD using same `Session(engine)` patterns |

## Priority 3 — File index

| Current | Location | Proposed service |
|---------|----------|------------------|
| Upload / delete / filter / group actions | [`index/file/ui.py`](../../libs/ktem/ktem/index/file/ui.py) | `services/files/index_ops.py`: one function per Gradio `.click`/`.submit` group, returning DTOs for tables |

Start with **upload + list**; add group/batch later.

## Priority 4 — Settings

| Current | [`pages/settings.py`](../../libs/ktem/ktem/pages/settings.py), `llms/ui.py`, etc. | `services/settings.py`: load/save flattened dict with validation hooks already on `SettingGroup` |

## Testing strategy

- **Unit tests** on new service functions using fake DB or transactions.
- **Golden tests** for `prepare_user_turn` with sample inputs (URLs, `@file`, web search command).
- **Integration tests** hitting FastAPI `TestClient` with SSE consumer for one short stream.

## Anti-patterns

- Importing `gradio` inside service modules (keep adapters in `api/gradio_legacy.py` only if temporary).
- Returning HTML strings for API responses where JSON is clearer — map `info` channel to structured citations when possible (optional second phase).
