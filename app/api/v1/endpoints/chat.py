import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.chat import (
    ConversationCreate,
    ConversationRead,
    MessageCreate,
    ChatAssistantResponse,
)
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["Chat & Research Assistant"])


@router.post(
    "/conversations", response_model=ConversationRead, status_code=status.HTTP_201_CREATED
)
async def create_conversation(
    data: ConversationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ChatService(db)
    conv = await service.create_conversation(current_user, data)
    return await service.get_conversation(conv.id, current_user)


@router.get("/conversations", response_model=List[ConversationRead])
async def list_conversations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ChatService(db)
    return await service.list_conversations(current_user)


@router.get("/conversations/{id}", response_model=ConversationRead)
async def get_conversation(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ChatService(db)
    return await service.get_conversation(id, current_user)


@router.delete("/conversations/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ChatService(db)
    await service.delete_conversation(id, current_user)


@router.post("/conversations/{id}/messages", response_model=ChatAssistantResponse)
async def post_message(
    id: uuid.UUID,
    data: MessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ChatService(db)
    return await service.post_message(id, current_user, data)


@router.post("/conversations/{id}/messages/stream")
async def stream_message(
    id: uuid.UUID,
    data: MessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Streams assistant responses using Server-Sent Events (SSE).
    Emits events: message_start, token, source, message_complete, error.
    """
    service = ChatService(db)
    generator = service.stream_message(id, current_user, data)

    return StreamingResponse(
        generator,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
