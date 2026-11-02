import uuid
from typing import AsyncGenerator, Dict, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.chat import ChatConversation, ConversationMode
from app.models.chat_message import ChatMessage, MessageRole
from app.models.user import User
from app.schemas.chat import ConversationCreate, MessageCreate, ChatAssistantResponse
from app.ai.assistant.assistant_engine import AssistantEngine
from app.core.exceptions import EntityNotFoundException, PermissionDeniedException


class ChatService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_conversation(
        self, user: User, data: ConversationCreate
    ) -> ChatConversation:
        conversation = ChatConversation(
            user_id=user.id,
            title=data.title,
            mode=data.mode,
        )
        self.db.add(conversation)
        await self.db.flush()
        return conversation

    async def list_conversations(self, user: User) -> List[ChatConversation]:
        query = (
            select(ChatConversation)
            .where(ChatConversation.user_id == user.id)
            .order_by(ChatConversation.updated_at.desc())
        )
        res = await self.db.execute(query)
        return list(res.scalars().all())

    async def get_conversation(
        self, conversation_id: uuid.UUID, user: User
    ) -> ChatConversation:
        query = (
            select(ChatConversation)
            .options(selectinload(ChatConversation.messages))
            .where(ChatConversation.id == conversation_id)
        )
        res = await self.db.execute(query)
        conversation = res.scalar_one_or_none()
        if not conversation:
            raise EntityNotFoundException("ChatConversation", conversation_id)
        if conversation.user_id != user.id and user.role.value != "ADMIN":
            raise PermissionDeniedException("You do not have access to this conversation.")
        return conversation

    async def delete_conversation(self, conversation_id: uuid.UUID, user: User) -> bool:
        conversation = await self.get_conversation(conversation_id, user)
        await self.db.delete(conversation)
        await self.db.flush()
        return True

    async def post_message(
        self, conversation_id: uuid.UUID, user: User, data: MessageCreate
    ) -> ChatAssistantResponse:
        conversation = await self.get_conversation(conversation_id, user)

        # 1. Save user message
        user_msg = ChatMessage(
            conversation_id=conversation.id,
            role=MessageRole.USER,
            content=data.content,
            metadata_={"filters": data.filters.model_dump() if data.filters else {}},
        )
        self.db.add(user_msg)
        await self.db.flush()

        # Build history for context
        history = [
            {"role": m.role.value, "content": m.content}
            for m in conversation.messages[-6:]
        ]

        # 2. Process query via AssistantEngine
        rag_output = await AssistantEngine.process_research_query(
            query=data.content,
            db=self.db,
            filters=data.filters,
            chat_history=history,
        )

        # 3. Save assistant message with citation metadata
        assistant_msg = ChatMessage(
            conversation_id=conversation.id,
            role=MessageRole.ASSISTANT,
            content=rag_output["answer"],
            metadata_={
                "sources": rag_output.get("sources", []),
                "provider": rag_output.get("provider", "unknown"),
            },
        )
        self.db.add(assistant_msg)
        await self.db.flush()

        return ChatAssistantResponse(
            message_id=str(assistant_msg.id),
            conversation_id=str(conversation.id),
            role=MessageRole.ASSISTANT,
            content=assistant_msg.content,
            sources=rag_output.get("sources", []),
        )

    async def stream_message(
        self, conversation_id: uuid.UUID, user: User, data: MessageCreate
    ) -> AsyncGenerator[str, None]:
        conversation = await self.get_conversation(conversation_id, user)

        user_msg = ChatMessage(
            conversation_id=conversation.id,
            role=MessageRole.USER,
            content=data.content,
            metadata_={},
        )
        self.db.add(user_msg)
        await self.db.flush()

        history = [
            {"role": m.role.value, "content": m.content}
            for m in conversation.messages[-6:]
        ]

        async for event in AssistantEngine.stream_research_query(
            query=data.content,
            db=self.db,
            filters=data.filters,
            chat_history=history,
        ):
            yield event
