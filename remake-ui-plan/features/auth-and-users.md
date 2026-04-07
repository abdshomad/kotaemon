# Feature parity: Auth and users

## Local user management

When `KH_FEATURE_USER_MANAGEMENT` is true:

- [ ] Login page parity: [`libs/ktem/ktem/pages/login.py`](../../libs/ktem/ktem/pages/login.py) — username/password, `User` model, `login()` verification
- [ ] Session persistence: today uses JS `getStorage` / `setStorage` for credentials on load — replace with **secure** HTTP-only cookies or token storage per security review
- [ ] Sign-out clears session and resets chat/index state (`onSignOut` chain in `ChatPage.on_subscribe_public_events`)
- [ ] Tab visibility: non-admin hides Resources (`resources-tab` in [`main.py`](../../libs/ktem/ktem/main.py)); enforce same rules in API (`GET /api/resources` → 403)

## First setup

When `KH_ENABLE_FIRST_SETUP` and missing app data:

- [ ] Setup wizard: [`pages/setup.py`](../../libs/ktem/ktem/pages/setup.py)
- [ ] `onFirstSetupComplete` toggles visibility — Next: gate routes until setup API returns complete

## SSO

When `KH_SSO_ENABLED`:

- [ ] Gradio path mounts under `sso_app.py` — Next app should use same backend auth middleware (OIDC headers, cookies, or tokens) as Uvicorn stack
- [ ] Resources tab may be hidden; login tab may differ — align with [`launch.sh`](../../launch.sh) branches

## Demo mode

- [ ] `KH_DEMO_MODE`: simplified tabs; demo login/logout buttons in [`control.py`](../../libs/ktem/ktem/pages/chat/control.py)

## API contract

- [ ] `POST /api/auth/login` returns user id + role flags (`admin`) for UI
- [ ] Middleware rejects unauthorized access to `/api/*` and Next server actions mirror redirects
