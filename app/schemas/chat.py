import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from app.models.chat import ConversationMode
from app.models.chat_message import MessageRole
from app.ai.retrieval.context_builder import SourceCitation
from app.ai.retrieval.hybrid_search import SearchFilter


class ConversationCreate(BaseModel):
    title: str = "گفتگوی جدید"
    mode: ConversationMode = ConversationMode.RESEARCH


class MessageCreate(BaseModel):
    content: str
    filters: Optional[SearchFilter] = None
    stream: bool = False


class MessageRead(BaseModel):
    id: uuid.UUID
    conversation_id: uuid.UUID
    role: MessageRole
    content: str
    metadata_: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    mode: ConversationMode
    created_at: datetime
    updated_at: datetime
    messages: List[MessageRead] = []

    class Config:
        from_attributes = True


class ChatAssistantResponse(BaseModel):
    message_id: str
    conversation_id: str
    role: MessageRole = MessageRole.ASSISTANT
    content: str
    sources: List[SourceCitation] = []
