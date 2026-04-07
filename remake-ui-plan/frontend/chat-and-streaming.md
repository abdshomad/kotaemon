# Chat UI and streaming

## Message model

- **User message**: Plain text; may include `@file` references and URLs (parsed server-side in `submit_msg`).
- **Assistant message**: Streaming markdown; may be empty then filled (placeholder: `KH_CHAT_MSG_PLACEHOLDER` / `KH_CHAT_EMPTY_MSG_PLACEHOLDER` from flowsettings).
- **Info panel**: HTML string from retrieval (`channel == "info"`).
- **Plot**: Plotly figure JSON (`channel == "plot"`) — today passed through `plotly.io.from_json` in Gradio.

Next.js should:

1. Render assistant text with a markdown renderer (e.g. `react-markdown`) with **streaming** updates (append-only chunks).
2. Render `info` in a side panel or tab; sanitize HTML.
3. Render Plotly via `react-plotly.js` or load JSON into a client-only chart component.

## Streaming transport

- Prefer **SSE** from FastAPI (`EventSourceResponse`) for simplicity with HTTP/2 proxies.
- Alternative: **WebSocket** if bidirectional keepalive is required.

Client: `EventSource` or `fetch` with `ReadableStream` if using POST for SSE.

When using **Docker Compose + nginx** ([docker-compose-nginx.md](../architecture/docker-compose-nginx.md)), call the API with **same-origin** URLs such as `/api/chat/stream` so traffic goes through nginx to the backend. Configure nginx to disable buffering for SSE (`proxy_buffering off`) on the streaming location.

## Citations and PDF preview

Current behavior uses [`libs/ktem/ktem/assets/js/pdf_viewer.js`](../../libs/ktem/ktem/assets/js/pdf_viewer.js) and Gradio `pdfview_js` after each chat completion.

Options for Next:

- **Iframe + PDF.js** (same as today): host static PDF.js from `public/`; pass blob URLs or file IDs resolved via `GET /api/files/:id/pdf`.
- **react-pdf**: simpler for in-app viewing; watch bundle size.

## Commands and mentions

- **Web search**: `WEB_SEARCH_COMMAND` from [`ktem/utils/commands.py`](../../libs/ktem/ktem/utils/commands.py) — UI should offer the same trigger (e.g. `@web_search` or dedicated tag) and send `command_state` to API.
- **Tribute.js**-style `@` mentions for files: reimplement with a React mention autocomplete fed by `GET /api/files/choices` (selector choices analogous to `first_selector_choices`).

## Concurrency

Gradio uses `concurrency_limit=20` on chat events. API should document rate limits and optionally mirror with a server-side semaphore.

## Related

- [gradio-to-http-mapping.md](../architecture/gradio-to-http-mapping.md) — SSE event schema.
- [features/chat.md](../features/chat.md) — full feature list.
