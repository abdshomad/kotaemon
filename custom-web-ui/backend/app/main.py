from pathlib import Path
import sys

from fastapi import FastAPI


def _ensure_repo_libs_on_path() -> Path:
    """Add monorepo libs to sys.path for local and container runs."""
    repo_root = Path(__file__).resolve().parents[3]
    libs_dir = repo_root / "libs"
    if str(libs_dir) not in sys.path:
        sys.path.insert(0, str(libs_dir))
    return repo_root


REPO_ROOT = _ensure_repo_libs_on_path()

app = FastAPI(title="Kotaemon custom web API", version="0.1.0")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "custom-web-ui-backend",
        "repo_root": str(REPO_ROOT),
    }
