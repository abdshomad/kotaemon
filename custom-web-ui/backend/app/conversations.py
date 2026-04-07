"""Conversation API endpoints (Phase 3 scaffold)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException, Request, Response, status
from pydantic import BaseModel

from app.auth import SESSION_USER_KEY
from app.services.conversations import (
    create_conversation,
    delete_conversation,
    get_conversation,
    get_last_messages,
    list_conversations,
    update_conversation,
    validate_conversation_name,
)

router = APIRouter(prefix="/api/conversations", tags=["conversations"])


class ConversationOut(BaseModel):
    id: str
    name: str
    is_public: bool
    date_created: datetime
    date_updated: datetime


class ConversationDetailOut(ConversationOut):
    data_source: dict[str, Any]
    last_messages: list[Any]


class CreateConversationBody(BaseModel):
    name: str | None = None


class UpdateConversationBody(BaseModel):
    name: str | None = None
    is_public: bool | None = None


def _require_user_id(request: Request) -> str:
    user = request.session.get(SESSION_USER_KEY)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user_id = user.get("id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return str(user_id)


def _to_out(conversation: Any) -> ConversationOut:
    return ConversationOut(
        id=conversation.id,
        name=conversation.name,
        is_public=conversation.is_public,
        date_created=conversation.date_created,
        date_updated=conversation.date_updated,
    )


@router.get("", response_model=list[ConversationOut])
def api_list_conversations(request: Request) -> list[ConversationOut]:
    user_id = _require_user_id(request)
    conversations = list_conversations(user_id)
    return [_to_out(item) for item in conversations]


@router.post("", response_model=ConversationOut, status_code=status.HTTP_201_CREATED)
def api_create_conversation(
    request: Request, body: CreateConversationBody | None = None
) -> ConversationOut:
    user_id = _require_user_id(request)
    body = body or CreateConversationBody()
    if body.name is not None:
        error = validate_conversation_name(body.name)
        if error:
            raise HTTPException(status_code=400, detail=error)
    created = create_conversation(user_id, body.name)
    return _to_out(created)


@router.get("/{conversation_id}", response_model=ConversationDetailOut)
def api_get_conversation(conversation_id: str, request: Request) -> ConversationDetailOut:
    user_id = _require_user_id(request)
    conversation = get_conversation(user_id, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return ConversationDetailOut(
        **_to_out(conversation).model_dump(),
        data_source=conversation.data_source,
        last_messages=get_last_messages(conversation.data_source),
    )


@router.patch("/{conversation_id}", response_model=ConversationOut)
def api_patch_conversation(
    conversation_id: str, request: Request, body: UpdateConversationBody
) -> ConversationOut:
    user_id = _require_user_id(request)
    if body.name is None and body.is_public is None:
        raise HTTPException(status_code=400, detail="No fields to update")
    if body.name is not None:
        error = validate_conversation_name(body.name)
        if error:
            raise HTTPException(status_code=400, detail=error)
    conversation = update_conversation(
        user_id, conversation_id, name=body.name, is_public=body.is_public
    )
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return _to_out(conversation)


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def api_delete_conversation(conversation_id: str, request: Request) -> Response:
    user_id = _require_user_id(request)
    removed = delete_conversation(user_id, conversation_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
