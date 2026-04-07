"""Conversation CRUD service extracted from chat control behavior."""

from __future__ import annotations

from typing import Any

from sqlmodel import Session, select

from ktem.db.models import Conversation, engine


def validate_conversation_name(name: str) -> str:
    if len(name) == 0:
        return "Name cannot be empty"
    if len(name) > 40:
        return "Name cannot be longer than 40 characters"
    return ""


def list_conversations(user_id: str) -> list[Conversation]:
    with Session(engine) as session:
        statement = (
            select(Conversation)
            .where(Conversation.user == user_id)
            .order_by(Conversation.date_created.desc())  # type: ignore[arg-type]
        )
        return list(session.exec(statement).all())


def create_conversation(user_id: str, name: str | None = None) -> Conversation:
    new_conversation = Conversation(user=user_id)
    if name:
        new_conversation.name = name
    with Session(engine) as session:
        session.add(new_conversation)
        session.commit()
        session.refresh(new_conversation)
        return new_conversation


def get_conversation(user_id: str, conversation_id: str) -> Conversation | None:
    with Session(engine) as session:
        statement = select(Conversation).where(
            Conversation.id == conversation_id, Conversation.user == user_id
        )
        return session.exec(statement).one_or_none()


def update_conversation(
    user_id: str,
    conversation_id: str,
    *,
    name: str | None = None,
    is_public: bool | None = None,
) -> Conversation | None:
    with Session(engine) as session:
        statement = select(Conversation).where(
            Conversation.id == conversation_id, Conversation.user == user_id
        )
        conversation = session.exec(statement).one_or_none()
        if not conversation:
            return None
        if name is not None:
            conversation.name = name
        if is_public is not None:
            conversation.is_public = is_public
        session.add(conversation)
        session.commit()
        session.refresh(conversation)
        return conversation


def delete_conversation(user_id: str, conversation_id: str) -> bool:
    with Session(engine) as session:
        statement = select(Conversation).where(
            Conversation.id == conversation_id, Conversation.user == user_id
        )
        conversation = session.exec(statement).one_or_none()
        if not conversation:
            return False
        session.delete(conversation)
        session.commit()
        return True


def get_last_messages(data_source: dict[str, Any], limit: int = 10) -> list[Any]:
    messages = data_source.get("messages", [])
    if not isinstance(messages, list):
        return []
    return messages[-limit:]
