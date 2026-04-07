"""Chat streaming API endpoints (Phase 4 MVP)."""

from __future__ import annotations

import json
from collections.abc import Iterator

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.auth import SESSION_USER_KEY
from app.services.chat import persist_turn, prepare_user_turn, stream_reply

router = APIRouter(prefix="/api/chat", tags=["chat"])


class ChatStreamBody(BaseModel):
    conversation_id: str | None = None
    message: str
    index_id: int | None = None
    file_ids: list[str] | None = None


def _require_user_id(request: Request) -> str:
    user = request.session.get(SESSION_USER_KEY)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user_id = user.get("id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return str(user_id)


def _to_sse(event: dict) -> str:
    event_type = str(event.get("type", "message"))
    payload = json.dumps(event, ensure_ascii=True)
    return f"event: {event_type}\ndata: {payload}\n\n"


@router.post("/stream")
def api_chat_stream(request: Request, body: ChatStreamBody) -> StreamingResponse:
    user_id = _require_user_id(request)
    try:
        turn = prepare_user_turn(
            user_id=user_id,
            conversation_id=body.conversation_id,
            message=body.message,
        )
    except ValueError as exc:
        text = str(exc)
        code = 404 if text == "Conversation not found" else 400
        raise HTTPException(status_code=code, detail=text) from exc

    def event_iter() -> Iterator[str]:
        assistant_text = ""
        for event in stream_reply(turn):
            if event.get("type") == "token":
                assistant_text += str(event.get("delta", ""))
            yield _to_sse(event)
        persist_turn(
            user_id=user_id,
            conversation_id=turn.conversation_id,
            history=turn.history,
            user_text=turn.user_text,
            assistant_text=assistant_text,
        )

    return StreamingResponse(
        event_iter(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
