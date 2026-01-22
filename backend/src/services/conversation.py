"""Conversation persistence service for chat endpoint.

Provides async functions for managing conversations and messages:
- get_or_create_conversation: Get existing or create new conversation
- fetch_history: Retrieve recent messages for Gemini context
- store_user_message: Save user's message
- store_assistant_response: Save assistant's response

All functions enforce user isolation per Phase III constitution.
"""

import logging
from typing import Optional
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from fastapi import HTTPException, status

from src.models.conversation import Conversation
from src.models.message import Message, MessageRole

logger = logging.getLogger(__name__)


async def get_or_create_conversation(
    user_id: str,
    conversation_id: Optional[int],
    session: AsyncSession
) -> Conversation:
    """
    Get an existing conversation or create a new one.

    Args:
        user_id: The authenticated user's ID
        conversation_id: Optional existing conversation ID
        session: Database session

    Returns:
        Conversation instance (existing or new)

    Raises:
        HTTPException 403: If conversation belongs to another user
    """
    if conversation_id is not None:
        # Try to load existing conversation
        query = select(Conversation).where(Conversation.id == conversation_id)
        result = await session.execute(query)
        conversation = result.scalar_one_or_none()

        if conversation:
            # T022: Ownership validation
            if conversation.user_id != user_id:
                logger.warning(
                    f"User {user_id} attempted to access conversation {conversation_id} "
                    f"owned by {conversation.user_id}"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "error": "forbidden",
                        "message": "Access denied to this resource",
                        "details": {"resource": "conversation", "id": conversation_id}
                    }
                )
            return conversation
        else:
            # T034: Conversation not found - create new one (graceful fallback)
            logger.info(
                f"Conversation {conversation_id} not found for user {user_id}, creating new"
            )

    # Create new conversation
    conversation = Conversation(user_id=user_id)
    session.add(conversation)
    await session.commit()
    # Re-fetch to get the generated ID without relationship lazy-loading issues
    result = await session.execute(
        select(Conversation).where(Conversation.user_id == user_id).order_by(Conversation.id.desc()).limit(1)
    )
    conversation = result.scalar_one()
    logger.info(f"Created conversation {conversation.id} for user {user_id}")
    return conversation


async def fetch_history(
    conversation_id: int,
    user_id: str,
    limit: int = 20,
    session: AsyncSession = None
) -> list[dict]:
    """
    Fetch recent conversation history for Gemini context.

    Args:
        conversation_id: The conversation to fetch history for
        user_id: The user ID (for validation)
        limit: Maximum number of messages to return
        session: Database session

    Returns:
        List of message dicts: [{"role": "user"|"assistant", "content": "..."}]
    """
    # Query messages ordered by creation time, limited
    query = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .where(Message.user_id == user_id)
        .order_by(Message.created_at.asc())
        .limit(limit)
    )
    result = await session.execute(query)
    messages = result.scalars().all()

    # Convert to Gemini history format
    history = []
    for msg in messages:
        history.append({
            "role": msg.role.value,  # "user" or "assistant"
            "content": msg.content
        })

    logger.debug(f"Fetched {len(history)} messages for conversation {conversation_id}")
    return history


async def store_user_message(
    conversation_id: int,
    user_id: str,
    content: str,
    session: AsyncSession
) -> Message:
    """
    Store a user's message in the conversation.

    Args:
        conversation_id: The conversation ID
        user_id: The user's ID
        content: The message content
        session: Database session

    Returns:
        The created Message instance
    """
    message = Message(
        conversation_id=conversation_id,
        user_id=user_id,
        role=MessageRole.USER,
        content=content
    )
    session.add(message)
    await session.commit()
    # Skip refresh to avoid lazy-loading relationship issues with async session
    logger.debug(f"Stored user message in conversation {conversation_id}")
    return message


async def store_assistant_response(
    conversation_id: int,
    user_id: str,
    content: str,
    session: AsyncSession
) -> Message:
    """
    Store the assistant's response in the conversation.

    Args:
        conversation_id: The conversation ID
        user_id: The user's ID
        content: The response content
        session: Database session

    Returns:
        The created Message instance
    """
    message = Message(
        conversation_id=conversation_id,
        user_id=user_id,
        role=MessageRole.ASSISTANT,
        content=content
    )
    session.add(message)
    await session.commit()
    # Skip refresh to avoid lazy-loading relationship issues with async session
    logger.debug(f"Stored assistant message in conversation {conversation_id}")
    return message
