"""Conversation persistence functions for stateless chat history management.

This module provides async database operations for creating, fetching, and storing
conversation history. All functions enforce user isolation and use the caller's
database session (no transaction commits within functions).

Functions:
    get_or_create_conversation: Retrieve or create a conversation for a user
    fetch_history: Fetch recent messages from a conversation
    store_user_message: Store a user message in a conversation
    store_assistant_response: Store an assistant response with optional tool calls
"""
import json
from typing import Optional

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.models.conversation import Conversation
from src.models.message import Message, MessageRole


__all__ = [
    "get_or_create_conversation",
    "fetch_history",
    "store_user_message",
    "store_assistant_response",
]


async def _validate_conversation_ownership(
    session: AsyncSession,
    conversation_id: int,
    user_id: str
) -> Optional[Conversation]:
    """Validate that a conversation exists and belongs to the specified user.

    Args:
        session: Active database session
        conversation_id: Conversation ID to validate
        user_id: User ID for ownership check

    Returns:
        Conversation if valid and owned by user, None otherwise
    """
    conversation = await session.get(Conversation, conversation_id)
    if conversation and conversation.user_id == user_id:
        return conversation
    return None


async def get_or_create_conversation(
    session: AsyncSession,
    user_id: str,
    conversation_id: int | None
) -> Conversation:
    """Retrieve an existing conversation or create a new one.

    Enforces user isolation by validating ownership. If the provided
    conversation_id doesn't exist or belongs to a different user,
    a new conversation is created.

    Args:
        session: Active database session
        user_id: Authenticated user's ID
        conversation_id: Existing conversation ID or None for new

    Returns:
        Conversation model instance (existing or newly created)

    Behavior:
        - conversation_id=None: Create new conversation
        - conversation_id exists and owned by user: Return existing
        - conversation_id exists but different owner: Create new (isolation)
        - conversation_id doesn't exist: Create new (graceful handling)
    """
    # Try to get existing conversation if ID provided
    if conversation_id is not None:
        conversation = await _validate_conversation_ownership(
            session, conversation_id, user_id
        )
        if conversation:
            return conversation

    # Create new conversation for user
    conversation = Conversation(user_id=user_id)
    session.add(conversation)
    await session.flush()  # Get the ID without committing
    return conversation


async def fetch_history(
    session: AsyncSession,
    conversation_id: int,
    user_id: str,
    limit: int = 30
) -> list[dict]:
    """Fetch recent message history for a conversation.

    Returns the N most recent messages in chronological order (oldest to newest).
    Enforces user isolation by validating ownership.

    Args:
        session: Active database session
        conversation_id: Conversation to fetch from
        user_id: User ID for isolation validation
        limit: Maximum messages to return (default 30)

    Returns:
        List of message dictionaries in chronological order, each containing:
        - role: "user" or "assistant"
        - content: Message content
        - created_at: ISO 8601 datetime string
        - tool_calls: Deserialized tool calls list or None

    Note:
        Returns empty list for invalid/unauthorized conversation_id
    """
    # First verify conversation ownership (security check)
    conversation = await _validate_conversation_ownership(
        session, conversation_id, user_id
    )
    if not conversation:
        return []

    # Query N most recent messages (DESC), then reverse for chronological order
    statement = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .where(Message.user_id == user_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    result = await session.exec(statement)
    messages = result.all()

    # Reverse to chronological order (oldest first)
    messages = list(reversed(messages))

    # Convert to dict format for Gemini API compatibility
    return [_message_to_dict(msg) for msg in messages]


def _message_to_dict(message: Message) -> dict:
    """Convert Message model to Gemini-compatible dictionary.

    Args:
        message: Message model instance

    Returns:
        Dictionary with role, content, created_at, and tool_calls
    """
    return {
        "role": message.role.value,  # "user" or "assistant"
        "content": message.content,
        "created_at": message.created_at.isoformat() if message.created_at else None,
        "tool_calls": json.loads(message.tool_calls) if message.tool_calls else None
    }


async def store_user_message(
    session: AsyncSession,
    conversation_id: int,
    user_id: str,
    content: str
) -> Message:
    """Store a user message in the conversation.

    Validates conversation ownership before storing.

    Args:
        session: Active database session
        conversation_id: Target conversation
        user_id: User ID for isolation validation
        content: User's message content (empty string allowed)

    Returns:
        Created Message model instance

    Raises:
        ValueError: If conversation_id is invalid or belongs to different user
    """
    # Validate conversation ownership
    conversation = await _validate_conversation_ownership(
        session, conversation_id, user_id
    )
    if not conversation:
        raise ValueError("Invalid conversation")

    # Create and store message
    message = Message(
        conversation_id=conversation_id,
        user_id=user_id,
        role=MessageRole.USER,
        content=content,
        tool_calls=None
    )
    session.add(message)
    await session.flush()  # Get the ID without committing
    return message


async def store_assistant_response(
    session: AsyncSession,
    conversation_id: int,
    user_id: str,
    content: str,
    tool_calls: list | None
) -> Message:
    """Store an assistant response with optional tool call metadata.

    Validates conversation ownership before storing. Tool calls are
    serialized to JSON string for storage.

    Args:
        session: Active database session
        conversation_id: Target conversation
        user_id: User ID for isolation validation
        content: Assistant's response text
        tool_calls: Tool calls made (JSON-serializable list) or None

    Returns:
        Created Message model instance

    Raises:
        ValueError: If conversation_id is invalid or belongs to different user
        TypeError: If tool_calls is not JSON-serializable
    """
    # Validate conversation ownership
    conversation = await _validate_conversation_ownership(
        session, conversation_id, user_id
    )
    if not conversation:
        raise ValueError("Invalid conversation")

    # Serialize tool_calls to JSON string
    tool_calls_json = json.dumps(tool_calls) if tool_calls else None

    # Create and store message
    message = Message(
        conversation_id=conversation_id,
        user_id=user_id,
        role=MessageRole.ASSISTANT,
        content=content,
        tool_calls=tool_calls_json
    )
    session.add(message)
    await session.flush()  # Get the ID without committing
    return message
