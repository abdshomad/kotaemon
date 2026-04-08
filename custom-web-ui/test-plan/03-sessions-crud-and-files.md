# Test plan 03 — Sessions, conversations CRUD, and files page

**Goal:** Cover **stateful** behavior beyond the minimal path: multiple conversations, renaming, file list filtering, deleting an indexed file, and logout.

**Depends on:** Core flow in [01-e2e-login-upload-index-chat.md](01-e2e-login-upload-index-chat.md) passing.

## Prerequisites

- Logged-in session (browser or cookie jar).
- At least one indexed file (from plan 01) or willingness to upload one.

## A. Conversations

1. On **Chat** (`/`), create **New** twice so you have at least two conversations.
2. **Expect:** Sidebar lists both; switching updates messages area (or empty state).
3. Rename one conversation if the UI exposes rename, or call `PATCH /api/conversations/{id}` with `{"name":"Renamed"}`.
4. **Expect:** Name updates in sidebar after refresh or optimistic UI.

## B. Files page filters

1. Open **`/files`**.
2. Type a substring into the filter box that matches your PDF name.
3. **Expect:** List narrows; clearing filter shows all files again.

## C. Delete indexed file

1. On **`/files`**, delete one file using the UI control (if present) or `DELETE /api/index/{index_id}/files/{file_id}`.
2. Refresh list.
3. **Expect:** File no longer listed; subsequent chat turns must not reference removed `file_id` (API should reject invalid ids with `400` when `file_ids` are sent).

## D. Logout

1. If the UI has logout, use it; else `POST /api/auth/logout` with cookies.
2. Open `/` or `/files`.
3. **Expect:** Redirect to login or `401` on API without session.

## Pass criteria

- CRUD operations complete without 500 errors.
- Deleted files disappear from index list and cannot be used as valid `file_ids` in chat.

## Related

- API curl flow: [02-api-happy-path.md](02-api-happy-path.md)
- Docker: [04-docker-nginx-stack.md](04-docker-nginx-stack.md)
