# Scripts (`custom-web-ui/scripts`)

## `pick_ports.py`

Finds the first free TCP port on a host from configurable starting points (defaults: frontend `3000`, backend `8000`).

```bash
python3 scripts/pick_ports.py --json
python3 scripts/pick_ports.py   # KEY=value lines for shells
```

## `apply-local-ports.sh`

Runs `pick_ports.py` and writes:

| File | Purpose |
|------|---------|
| `../.ports.env` | `source` in your shell — exports `CUSTOM_WEB_UI_FRONTEND_PORT`, `CUSTOM_WEB_UI_BACKEND_PORT`, `API_PROXY_TARGET`, `INTERNAL_API_URL`, `PLAYWRIGHT_BASE_URL` |
| `../frontend/.env.local` | Next.js rewrites + middleware (`API_PROXY_TARGET`, `INTERNAL_API_URL` only) |

From `frontend/`: `npm run ports:apply`

Environment overrides:

| Variable | Effect |
|----------|--------|
| `CUSTOM_WEB_UI_HOST` | Bind probe host (default `127.0.0.1`) |
| `PREFERRED_FRONTEND_PORT` | First candidate for Next (default `3000`) |
| `PREFERRED_BACKEND_PORT` | First candidate for API (default `8000`) |
| `CUSTOM_WEB_UI_PORTS_ENV` | Output path for `.ports.env` |
| `CUSTOM_WEB_UI_ENV_LOCAL` | Output path for `frontend/.env.local` |

Backend still needs the same **Python** setup as the main app (repo `PYTHONPATH`, `flowsettings` / `KH_APP_DATA_DIR`, `.venv` from the repository root). The script only picks ports and URLs; it does not start uvicorn.
