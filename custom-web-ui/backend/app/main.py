from pathlib import Path
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware


def _ensure_repo_libs_on_path() -> Path:
    """Add monorepo libs to sys.path for local and container runs."""
    repo_root = Path(__file__).resolve().parents[3]
    libs_dir = repo_root / "libs"
    if str(libs_dir) not in sys.path:
        sys.path.insert(0, str(libs_dir))
    return repo_root


REPO_ROOT = _ensure_repo_libs_on_path()

from app.auth import router as auth_router
from app.chat import router as chat_router
from app.config import get_cors_origins, get_session_secret
from app.conversations import router as conversations_router
from app.settings import router as settings_router

app = FastAPI(title="Kotaemon custom web API", version="0.1.0")

app.add_middleware(
    SessionMiddleware,
    secret_key=get_session_secret(),
    session_cookie="kh_session",
    same_site="lax",
    https_only=False,
    max_age=14 * 24 * 60 * 60,
)

_origins = get_cors_origins()
if _origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(auth_router)
app.include_router(settings_router)
app.include_router(conversations_router)
app.include_router(chat_router)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "custom-web-ui-backend",
        "repo_root": str(REPO_ROOT),
    }
