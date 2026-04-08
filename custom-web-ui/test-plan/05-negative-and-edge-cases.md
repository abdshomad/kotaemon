# Test plan 05 — Negative and edge cases

**Goal:** Exercise **failures** and **boundaries** after happy paths work. Use after changes to auth, validation, or error handling.

**Audience:** Hardening passes; not required for first-time smoke tests.

## Auth

| Case | Action | Expect |
|------|--------|--------|
| Unauthenticated API | `GET /api/settings` or `GET /api/index` **without** cookie | `401` |
| Invalid session | Call API with tampered or expired `kh_session` | `401` on protected routes |
| Login | `POST /api/auth/login` with empty body | `200` (stub) with default user — document actual behavior |

## Index / files

| Case | Action | Expect |
|------|--------|--------|
| Unknown index | `GET /api/index/99999/files` with valid session | `404` |
| Bad upload | Upload empty file or disallowed type per index config | `4xx` / `ok:false` with clear `error` |
| Delete missing | `DELETE /api/index/{id}/files/nonexistent-id` | `404` |
| Private index | If `private` is true, verify another user cannot list/delete (when multi-user exists) | `403` or empty list — match product rules |

## Chat

| Case | Action | Expect |
|------|--------|--------|
| Empty message | `POST /api/chat/stream` with `"message":""` | `400` |
| `file_ids` without `index_id` | Body with `file_ids` only | `400` with validation message |
| Invalid `file_id` | `file_ids` containing deleted or wrong id | `400` |
| Wrong conversation | `conversation_id` not owned by user | `404` |

## Frontend / middleware

| Case | Action | Expect |
|------|--------|--------|
| Deep link without login | Open `/files` in private window | Redirect to `/login` (when middleware enabled) |
| Next without `INTERNAL_API_URL` | Middleware cookie-only mode | Documented stub behavior per [`../README.md`](../README.md) |

## Related

- Happy path API: [02-api-happy-path.md](02-api-happy-path.md)
- CRUD flows: [03-sessions-crud-and-files.md](03-sessions-crud-and-files.md)
