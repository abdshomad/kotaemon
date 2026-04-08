# Test plan 02 — API happy path (curl): login → upload PDF → index → chat

**Goal:** Run the same logical sequence as [01-e2e-login-upload-index-chat.md](01-e2e-login-upload-index-chat.md) **without a browser**, using a cookie jar so session cookies persist.

**Audience:** Developers debugging proxies, CORS, or preparing shell-based CI checks.

## Prerequisites

- Backend reachable at `BASE` (example: `http://127.0.0.1:8000`).
- `curl` installed.
- A path to a small PDF: `SAMPLE.pdf`.

## Variables

```bash
export BASE=http://127.0.0.1:8000
export COOKIE_JAR=/tmp/kh_cookies.txt
export SAMPLE=/path/to/sample.pdf
```

## Steps

### 1. Health

```bash
curl -sS "$BASE/api/health"
```

**Expect:** JSON with `"status":"ok"`.

### 2. Login (session cookie)

```bash
curl -sS -c "$COOKIE_JAR" -b "$COOKIE_JAR" \
  -X POST "$BASE/api/auth/login" \
  -H 'Content-Type: application/json' \
  -d '{"username":"default","password":"x"}'
```

**Expect:** `200` and JSON user payload; cookie jar contains `kh_session` (or equivalent).

### 3. List indices

```bash
curl -sS -b "$COOKIE_JAR" "$BASE/api/index"
```

**Expect:** `200` and a non-empty JSON array; record **`id`** of the file index to use as `INDEX_ID` (often `1`).

```bash
export INDEX_ID=1   # set from response
```

### 4. Upload PDF (multipart)

```bash
curl -sS -b "$COOKIE_JAR" \
  -X POST "$BASE/api/index/$INDEX_ID/upload" \
  -F "file=@$SAMPLE;type=application/pdf"
```

**Expect:** `200`, JSON with `"ok":true`, `"file_id":"..."`. Export:

```bash
export FILE_ID='<uuid-from-response>'
```

### 5. List files (sanity)

```bash
curl -sS -b "$COOKIE_JAR" "$BASE/api/index/$INDEX_ID/files"
```

**Expect:** `200`; uploaded file appears with matching `id` and `name`.

### 6. Chat stream with index context

```bash
curl -sS -b "$COOKIE_JAR" \
  -X POST "$BASE/api/chat/stream" \
  -H 'Content-Type: application/json' \
  -d "{\"conversation_id\":null,\"message\":\"Hello from API test\",\"index_id\":$INDEX_ID,\"file_ids\":[\"$FILE_ID\"]}"
```

**Expect:** `200`, `Content-Type: text/event-stream`; body contains SSE lines `event: ...` and `data: {...}` with at least `meta`, `token`, `done`.

**MVP note:** Assistant tokens may still reflect the echo pipeline; assert **connectivity** and **info/state** carrying `indexId` / `fileIds` when present.

### 7. Optional: me

```bash
curl -sS -b "$COOKIE_JAR" "$BASE/api/auth/me"
```

**Expect:** `200` with current user.

## Pass / fail

| Step | Pass |
|------|------|
| Login | `200` + cookie stored |
| Upload | `ok: true` + `file_id` |
| Stream | `200` + SSE events |

## Related

- Browser plan: [01-e2e-login-upload-index-chat.md](01-e2e-login-upload-index-chat.md)
- Failures: [05-negative-and-edge-cases.md](05-negative-and-edge-cases.md)
