"""Chat turn preparation and streaming helpers for Phase 4."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Iterator

from sqlmodel import Session, select
from tzlocal import get_localzone

from ktem.db.models import Conversation, engine

from app.services.conversations import create_conversation, get_conversation


@dataclass
class TurnPrep:
    conversation_id: str
    user_id: str
    user_text: str
    history: list[dict[str, Any]]


def prepare_user_turn(
    *,
    user_id: str,
    conversation_id: str | None,
    message: str,
    index_id: int | None = None,
    file_ids: list[str] | None = None,
) -> TurnPrep:
    """Extracted submit-step logic for HTTP chat requests."""
    text = message.strip()
    if not text:
        raise ValueError("Input is empty")

    selected = list(file_ids) if file_ids else []
    if index_id is not None and selected:
        validate_file_ids_for_turn(index_id, user_id, selected)

    if conversation_id:
        conversation = get_conversation(user_id, conversation_id)
        if not conversation:
            raise ValueError("Conversation not found")
        convo_id = conversation.id
        data_source = conversation.data_source or {}
    else:
        conversation = create_conversation(user_id)
        convo_id = conversation.id
        data_source = conversation.data_source or {}

    history = data_source.get("messages", [])
    if not isinstance(history, list):
        history = []

    return TurnPrep(
        conversation_id=convo_id,
        user_id=user_id,
        user_text=text,
        history=history,
    )


def stream_reply(turn: TurnPrep) -> Iterator[dict[str, Any]]:
    """Extracted stream-step logic that emits HTTP stream events."""
    reply = f"You said: {turn.user_text}"
    yield {"type": "meta", "conversationId": turn.conversation_id}

    for token in reply.split(" "):
        yield {"type": "token", "delta": f"{token} "}

    yield {"type": "info", "content": "Phase 4 MVP stream active."}
    yield {"type": "state", "state": {"pipeline": "mvp-echo"}}
    yield {"type": "done"}


def persist_turn(
    *,
    user_id: str,
    conversation_id: str,
    history: list[dict[str, Any]],
    user_text: str,
    assistant_text: str,
) -> None:
    """Persist user and assistant messages into conversation data_source."""
    with Session(engine) as session:
        statement = select(Conversation).where(
            Conversation.id == conversation_id, Conversation.user == user_id
        )
        conversation = session.exec(statement).one_or_none()
        if not conversation:
            return

        messages = list(history)
        now_iso = datetime.now(get_localzone()).isoformat()
        messages.append({"role": "user", "content": user_text, "created_at": now_iso})
        messages.append(
            {"role": "assistant", "content": assistant_text.strip(), "created_at": now_iso}
        )

        data_source = dict(conversation.data_source or {})
        data_source["messages"] = messages
        conversation.data_source = data_source
        conversation.date_updated = datetime.now(get_localzone())
        session.add(conversation)
        session.commit()
