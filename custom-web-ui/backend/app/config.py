"""Runtime configuration for the API."""

import os


def get_session_secret() -> str:
    """Secret for signed session cookies (Starlette SessionMiddleware)."""
    return os.environ.get("SESSION_SECRET", "dev-insecure-change-me")


def get_cors_origins() -> list[str]:
    raw = os.environ.get("API_CORS_ORIGINS", "")
    return [o.strip() for o in raw.split(",") if o.strip()]
