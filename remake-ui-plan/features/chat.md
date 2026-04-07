# Feature parity: Chat

Source: [`libs/ktem/ktem/pages/chat/__init__.py`](../../libs/ktem/ktem/pages/chat/__init__.py), [`chat_panel.py`](../../libs/ktem/ktem/pages/chat/chat_panel.py), [`control.py`](../../libs/ktem/ktem/pages/chat/control.py).

## Core

- [ ] Multiline chat input with submit (Enter) — `chat_panel.text_input.submit` → `submit_msg`
- [ ] Chat history display (user/assistant alternating)
- [ ] Streaming assistant response with placeholder text (`KH_CHAT_MSG_PLACEHOLDER`, empty message placeholder)
- [ ] Reasoning type selector (`_reasoning_type`) — limit count in demo (`REASONING_LIMITS`)
- [ ] LLM / model type (`model_type`)
- [ ] Language selector + `DEFAULT_SETTING` sentinel
- [ ] Citation toggle (`citation`)
- [ ] Mind map toggle (`use_mindmap`) — export template `MINDMAP_HTML_EXPORT_TEMPLATE` if exposed in UI

## Conversation management

- [ ] New conversation (`btn_new` → `new_conv` / `select_conv`)
- [ ] Delete conversation with confirm/cancel
- [ ] Rename conversation (inline + `SuggestConvNamePipeline` on first message)
- [ ] Conversation dropdown / list binding to `user_id`
- [ ] Public/private toggle (`on_set_public_conversation`, `cb_is_public`) when enabled

## Indices in chat

- [ ] Per-index file selectors (`_indices_input`) — when multiple indices, map selectors to `selecteds` in `create_pipeline`
- [ ] URL ingestion from message text (`get_urls`, `first_indexing_url_fn`)
- [ ] `@filename` resolution via `get_file_names_regex` and `first_selector_choices`

## Commands

- [ ] Web search path when `WEB_SEARCH_COMMAND` in input and `KH_WEB_SEARCH_BACKEND` set — `WebSearch` retriever

## Post-answer UX

- [ ] Info / retrieval panel (`info_panel`) + expand/collapse (`btn_info_expand`, `INFO_PANEL_SCALES`)
- [ ] Plot panel (`plot_panel`, Plotly)
- [ ] Follow-up questions (`ChatSuggestion`, `suggest_chat_conv`)
- [ ] PDF/citation preview JS parity — see [chat-and-streaming.md](../frontend/chat-and-streaming.md)

## Demo mode (`KH_DEMO_MODE`)

- [ ] Rate limit via `check_rate_limit` on chat
- [ ] Paper list, quick URLs, demo logout — trim UI per product decision

## SSO

- [ ] Reload conversations on sign-in (`reload_conv` on `onSignIn`)

## Report / misc

- [ ] Report issue flow ([`report.py`](../../libs/ktem/ktem/pages/chat/report.py))
