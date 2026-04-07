# Routing and layout (Gradio tabs → Next.js)

Source of truth for tab structure: [`libs/ktem/ktem/main.py`](../../libs/ktem/ktem/main.py) (`App.ui`).

## Route table

Assumed **App Router** base path `/`. Adjust if the app is mounted under a subpath (e.g. SSO `GR_FILE_ROOT_PATH`).

| Gradio tab / area | `elem_id` / notes | Next.js route | Layout notes |
|-------------------|-------------------|---------------|--------------|
| Welcome (login) | `login-tab`, only if `KH_FEATURE_USER_MANAGEMENT` | `/login` | Full-width or minimal shell; no main nav until authenticated |
| Chat | `chat-tab` | `/` or `/chat` | Default landing after login; primary layout with sidebar (conversations) |
| File index (single index) | Tab title = index name, `indices-tab` | `/files` or `/index/:indexId` | If one index, `/files` is enough |
| Files (multiple indices) | Parent tab "Files", nested tabs per index | `/files` with nested `[indexId]` | `app/files/layout.tsx` + `app/files/[indexId]/page.tsx` |
| Resources | `resources-tab`, hidden if `KH_SSO_ENABLED` or demo | `/resources` | Admin-only visibility should mirror Python: non-admin users may not see this route |
| Settings | `settings-tab`, hidden in `KH_DEMO_MODE` | `/settings` | Long scrolling form sections; sub-routes optional (`/settings/llm`, etc.) |
| Help | `help-tab` | `/help` | Static or MDX content |
| First setup | `SetupPage` overlay when `KH_ENABLE_FIRST_SETUP` | `/setup` or modal on first visit | Gate main app until complete; match `toggle_first_setup_visibility` behavior |

## Nested layout proposal

```
app/
  layout.tsx          # root: providers, theme, optional auth check
  (main)/             # route group for authenticated shell
    layout.tsx        # sidebar + top bar (chat / files / settings / help)
    page.tsx          # chat home → redirect or render Chat
    chat/page.tsx     # optional alias
    files/[[...slug]]/page.tsx
    settings/page.tsx
    resources/page.tsx
    help/page.tsx
  login/page.tsx
  setup/page.tsx
```

- **(main) group**: Shared chrome (conversation list, nav links matching former tabs).
- **Login**: Outside `(main)` to avoid loading chat data providers.

## Visibility flags → middleware / loader

| Flag | Behavior |
|------|----------|
| `KH_DEMO_MODE` | Simplify nav (hide Files/Settings per `main.py`); demo hints |
| `KH_SSO_ENABLED` | Resources tab omitted; SSO may replace `/login` flow |
| `KH_FEATURE_USER_MANAGEMENT` | Protect `(main)` routes; redirect to `/login` if no session |
| `KH_ENABLE_FIRST_SETUP` | Redirect to `/setup` until complete |

Implement with Next.js **middleware** (cookie/JWT check) and/or server layout loaders that call a small **session** API.

## Deep links

- Conversation: `/chat?c=<conversation_id>` or `/chat/[conversationId]` for shareable state (match existing `Conversation.id` usage).
- File index filters: query params mirroring Gradio state where useful (`?group=`, `?q=`).

## Related files

- Chat composition: [`libs/ktem/ktem/pages/chat/__init__.py`](../../libs/ktem/ktem/pages/chat/__init__.py)
- Index UI: [`libs/ktem/ktem/index/file/ui.py`](../../libs/ktem/ktem/index/file/ui.py)
