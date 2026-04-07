# Design system (Next.js)

## Current sources

- Theme: [`libs/ktem/ktem/assets/theme.py`](../../libs/ktem/ktem/assets/theme.py) (`KotaemonTheme` — Gradio `Theme` subclass).
- Global CSS: [`libs/ktem/ktem/assets/css/main.css`](../../libs/ktem/ktem/assets/css/main.css).
- Dark mode toggle: [`libs/ktem/ktem/pages/chat/control.py`](../../libs/ktem/ktem/pages/chat/control.py) (`btn_toggle_dark_mode` toggles `gr.themes.Base` dark/light).

## Migration approach

1. **Extract design tokens** from `main.css` and Gradio theme kwargs: primary/background/border radii, fonts (`IBM Plex Sans`, `IBM Plex Mono` where used).
2. **Define CSS variables** on `:root` and `[data-theme="dark"]` in Next.js `globals.css` (or Tailwind `@theme` if using Tailwind v4).
3. **Mirror dark mode** using `prefers-color-scheme` and/or explicit toggle storing preference in `localStorage` + `document.documentElement.dataset.theme`, matching current UX.
4. **Do not** embed Gradio components; use headless primitives (Radix, Ariakit) or minimal custom components styled with the same tokens.

## Components to restyle explicitly

| Area | Notes |
|------|--------|
| Chat bubbles | Match chatbot height-fill layout classes (`fill-main-area-height` from tabs) |
| Conversation sidebar | Replace Gradio dropdown + buttons with list + context menu |
| Info / citation panel | HTML from `info` channel — sanitize with DOMPurify or equivalent; typography for citations |
| Settings | Accordion sections → `<details>` or collapsible panels |
| File table | `pandas`/`gr.Dataframe` → TanStack Table or simple HTML table with same column semantics |

## Assets

- Favicon: [`libs/ktem/ktem/assets/img/favicon.svg`](../../libs/ktem/ktem/assets/img/favicon.svg) — copy to Next `app/` metadata or `public/`.
- PDF.js: see [chat-and-streaming.md](chat-and-streaming.md).

## Accessibility

Preserve focus behavior (e.g. chat input focus after new chat in [`chat/__init__.py`](../../libs/ktem/ktem/pages/chat/__init__.py) `chat_input_focus_js`) using `useEffect` + ref or Radix focus management.
