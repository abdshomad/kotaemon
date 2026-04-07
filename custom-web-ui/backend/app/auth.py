"""Auth stub: session cookie + default user when full user management is not wired yet."""

from typing import Any

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

router = APIRouter(prefix="/api/auth", tags=["auth"])

SESSION_USER_KEY = "user"


class LoginBody(BaseModel):
    username: str | None = None
    password: str | None = None


class UserOut(BaseModel):
    id: str
    username: str
    is_admin: bool


def _default_user(payload: LoginBody | None) -> dict[str, Any]:
    name = (payload.username if payload else None) or "default"
    return {
        "id": "default",
        "username": name,
        "is_admin": True,
    }


@router.post("/login", response_model=UserOut)
def login(request: Request, body: LoginBody | None = None) -> UserOut:
    """Establish a signed session (stub: no password check until Phase 7)."""
    body = body or LoginBody()
    user = _default_user(body)
    request.session[SESSION_USER_KEY] = user
    return UserOut(**user)


@router.get("/me", response_model=UserOut)
def me(request: Request) -> UserOut:
    user = request.session.get(SESSION_USER_KEY)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return UserOut(**user)


@router.post("/logout")
def logout(request: Request) -> dict[str, str]:
    request.session.clear()
    return {"status": "ok"}
