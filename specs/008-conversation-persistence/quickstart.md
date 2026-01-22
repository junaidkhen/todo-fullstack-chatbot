# Quickstart: Conversation Persistence Implementation

**Feature Branch**: `008-conversation-persistence`
**Date**: 2026-01-17
**Estimated Tasks**: 4 implementation components

## Prerequisites

Before starting implementation, ensure:

- [ ] Backend environment is set up (`cd backend && pip install -r requirements.txt`)
- [ ] Database connection works (`DATABASE_URL` environment variable set)
- [ ] Existing models work (`backend/src/models/task.py` imports successfully)

## Implementation Steps

### Step 1: Create Conversation Models

**File**: `backend/src/models/conversation.py`

```python
"""Conversation and Message models for chat history persistence."""

from enum import Enum
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
import json

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import func, Text, Index, Column

if TYPE_CHECKING:
    pass  # Forward references resolved at runtime


class MessageRole(str, Enum):
    """Message sender role for conversation history."""
    USER = "user"
    ASSISTANT = "assistant"


class Conversation(SQLModel, table=True):
    """Represents a chat session for a user."""
    __tablename__ = "conversations"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column_kwargs={"server_default": func.now(), "nullable": False}
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column_kwargs={
            "server_default": func.now(),
            "onupdate": func.now(),
            "nullable": False
        }
    )

    # Relationship to messages
    messages: List["Message"] = Relationship(
        back_populates="conversation",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


class Message(SQLModel, table=True):
    """Represents a single message in a conversation."""
    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id", nullable=False)
    user_id: str = Field(nullable=False)
    role: MessageRole = Field(nullable=False)
    content: str = Field(sa_column=Column(Text, nullable=False))
    tool_calls: Optional[str] = Field(default=None)  # JSON-serialized
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column_kwargs={"server_default": func.now(), "nullable": False}
    )

    # Relationship to conversation
    conversation: Optional["Conversation"] = Relationship(back_populates="messages")

    __table_args__ = (
        Index("ix_messages_conversation_created", "conversation_id", "created_at"),
    )
```

**Verification**:
```bash
cd backend
python -c "from src.models.conversation import Conversation, Message, MessageRole; print('Models OK')"
```

### Step 2: Update database.py

**File**: `backend/src/database.py`

Add import in `init_db()` function:

```python
async def init_db():
    """Initialize the database by creating all tables."""
    from sqlmodel import SQLModel
    # Import all models so SQLModel knows about them
    from src.models.task import Task, User  # noqa: F401
    from src.models.conversation import Conversation, Message  # noqa: F401  # ADD THIS
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
```

**Verification**:
```bash
cd backend
python -c "import asyncio; from src.database import init_db; asyncio.run(init_db()); print('Tables created')"
```

### Step 3: Create Persistence Module

**File**: `backend/src/persistence.py`

```python
"""Conversation persistence functions for stateless chat operations."""

import json
from datetime import datetime
from typing import Optional

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.models.conversation import Conversation, Message, MessageRole


async def get_or_create_conversation(
    session: AsyncSession,
    user_id: str,
    conversation_id: int | None
) -> Conversation:
    """
    Get an existing conversation or create a new one.

    Args:
        session: Active database session
        user_id: The authenticated user's ID
        conversation_id: Optional existing conversation ID

    Returns:
        Conversation model instance (existing or newly created)
    """
    if conversation_id is not None:
        # Try to get existing conversation
        result = await session.exec(
            select(Conversation)
            .where(Conversation.id == conversation_id)
            .where(Conversation.user_id == user_id)
        )
        conversation = result.first()
        if conversation:
            return conversation

    # Create new conversation
    conversation = Conversation(user_id=user_id)
    session.add(conversation)
    await session.flush()  # Get ID without committing
    await session.refresh(conversation)
    return conversation


async def fetch_history(
    session: AsyncSession,
    conversation_id: int,
    user_id: str,
    limit: int = 30
) -> list[dict]:
    """
    Fetch recent message history for a conversation.

    Args:
        session: Active database session
        conversation_id: The conversation to fetch messages from
        user_id: User ID for isolation validation
        limit: Maximum number of messages to return (default 30)

    Returns:
        List of message dictionaries with keys: role, content, created_at, tool_calls
        Messages are ordered chronologically (oldest first within limit)
    """
    # Verify conversation belongs to user
    conv_result = await session.exec(
        select(Conversation)
        .where(Conversation.id == conversation_id)
        .where(Conversation.user_id == user_id)
    )
    conversation = conv_result.first()
    if not conversation:
        return []

    # Get N most recent messages, ordered by created_at desc
    result = await session.exec(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .where(Message.user_id == user_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    messages = result.all()

    # Reverse to get chronological order (oldest first)
    messages = list(reversed(messages))

    # Convert to dictionaries
    return [
        {
            "role": msg.role.value,
            "content": msg.content,
            "created_at": msg.created_at.isoformat() if msg.created_at else None,
            "tool_calls": json.loads(msg.tool_calls) if msg.tool_calls else None
        }
        for msg in messages
    ]


async def store_user_message(
    session: AsyncSession,
    conversation_id: int,
    user_id: str,
    content: str
) -> Message:
    """
    Store a user message in the conversation.

    Args:
        session: Active database session
        conversation_id: The conversation to add the message to
        user_id: User ID for isolation validation
        content: The user's message content

    Returns:
        The created Message model instance

    Raises:
        ValueError: If conversation doesn't exist or doesn't belong to user
    """
    # Verify conversation ownership
    conv_result = await session.exec(
        select(Conversation)
        .where(Conversation.id == conversation_id)
        .where(Conversation.user_id == user_id)
    )
    conversation = conv_result.first()
    if not conversation:
        raise ValueError("Invalid conversation")

    # Create and store message
    message = Message(
        conversation_id=conversation_id,
        user_id=user_id,
        role=MessageRole.USER,
        content=content
    )
    session.add(message)
    await session.flush()
    await session.refresh(message)
    return message


async def store_assistant_response(
    session: AsyncSession,
    conversation_id: int,
    user_id: str,
    content: str,
    tool_calls: list | None
) -> Message:
    """
    Store an assistant response in the conversation.

    Args:
        session: Active database session
        conversation_id: The conversation to add the response to
        user_id: User ID for isolation validation
        content: The assistant's response text
        tool_calls: Optional list of tool calls made (JSON-serializable)

    Returns:
        The created Message model instance

    Raises:
        ValueError: If conversation doesn't exist or doesn't belong to user
    """
    # Verify conversation ownership
    conv_result = await session.exec(
        select(Conversation)
        .where(Conversation.id == conversation_id)
        .where(Conversation.user_id == user_id)
    )
    conversation = conv_result.first()
    if not conversation:
        raise ValueError("Invalid conversation")

    # Serialize tool_calls to JSON
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
    await session.flush()
    await session.refresh(message)
    return message
```

**Verification**:
```bash
cd backend
python -c "from src.persistence import get_or_create_conversation, fetch_history, store_user_message, store_assistant_response; print('Persistence OK')"
```

### Step 4: Create Tests

**File**: `backend/tests/test_persistence.py`

```python
"""Tests for conversation persistence functions."""

import pytest
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.models.conversation import Conversation, Message, MessageRole
from src.persistence import (
    get_or_create_conversation,
    fetch_history,
    store_user_message,
    store_assistant_response,
)


@pytest.mark.asyncio
async def test_get_or_create_conversation_creates_new(session: AsyncSession):
    """Given no conversation_id, creates new conversation."""
    conversation = await get_or_create_conversation(session, "user_1", None)
    await session.commit()

    assert conversation.id is not None
    assert conversation.user_id == "user_1"


@pytest.mark.asyncio
async def test_get_or_create_conversation_returns_existing(session: AsyncSession):
    """Given valid conversation_id, returns existing conversation."""
    # Create conversation
    conv = await get_or_create_conversation(session, "user_1", None)
    await session.commit()

    # Get same conversation
    same_conv = await get_or_create_conversation(session, "user_1", conv.id)
    assert same_conv.id == conv.id


@pytest.mark.asyncio
async def test_get_or_create_conversation_user_isolation(session: AsyncSession):
    """Given other user's conversation_id, creates new conversation."""
    # Create conversation for user_1
    conv1 = await get_or_create_conversation(session, "user_1", None)
    await session.commit()

    # User_2 tries to access user_1's conversation
    conv2 = await get_or_create_conversation(session, "user_2", conv1.id)
    await session.commit()

    # Should be different conversation
    assert conv2.id != conv1.id
    assert conv2.user_id == "user_2"


@pytest.mark.asyncio
async def test_fetch_history_returns_chronological(session: AsyncSession):
    """Messages are returned in chronological order."""
    conv = await get_or_create_conversation(session, "user_1", None)
    await session.commit()

    # Store messages
    await store_user_message(session, conv.id, "user_1", "First")
    await store_assistant_response(session, conv.id, "user_1", "Second", None)
    await store_user_message(session, conv.id, "user_1", "Third")
    await session.commit()

    history = await fetch_history(session, conv.id, "user_1")

    assert len(history) == 3
    assert history[0]["content"] == "First"
    assert history[1]["content"] == "Second"
    assert history[2]["content"] == "Third"


@pytest.mark.asyncio
async def test_fetch_history_respects_limit(session: AsyncSession):
    """Limit returns most recent N messages."""
    conv = await get_or_create_conversation(session, "user_1", None)
    await session.commit()

    # Store 5 messages
    for i in range(5):
        await store_user_message(session, conv.id, "user_1", f"Message {i}")
    await session.commit()

    history = await fetch_history(session, conv.id, "user_1", limit=3)

    assert len(history) == 3
    # Should be the 3 most recent, in chronological order
    assert history[0]["content"] == "Message 2"
    assert history[1]["content"] == "Message 3"
    assert history[2]["content"] == "Message 4"


@pytest.mark.asyncio
async def test_fetch_history_user_isolation(session: AsyncSession):
    """Cannot fetch another user's conversation history."""
    conv = await get_or_create_conversation(session, "user_1", None)
    await store_user_message(session, conv.id, "user_1", "Secret message")
    await session.commit()

    # User_2 tries to fetch user_1's history
    history = await fetch_history(session, conv.id, "user_2")

    assert history == []


@pytest.mark.asyncio
async def test_store_user_message_success(session: AsyncSession):
    """Stores user message with correct role."""
    conv = await get_or_create_conversation(session, "user_1", None)
    await session.commit()

    msg = await store_user_message(session, conv.id, "user_1", "Hello")
    await session.commit()

    assert msg.role == MessageRole.USER
    assert msg.content == "Hello"
    assert msg.conversation_id == conv.id


@pytest.mark.asyncio
async def test_store_user_message_invalid_conversation(session: AsyncSession):
    """Raises ValueError for invalid conversation."""
    with pytest.raises(ValueError, match="Invalid conversation"):
        await store_user_message(session, 99999, "user_1", "Hello")


@pytest.mark.asyncio
async def test_store_assistant_response_with_tool_calls(session: AsyncSession):
    """Stores assistant response with serialized tool calls."""
    conv = await get_or_create_conversation(session, "user_1", None)
    await session.commit()

    tool_calls = [{"name": "list_tasks", "args": {"status": "pending"}}]
    msg = await store_assistant_response(
        session, conv.id, "user_1", "Here are your tasks", tool_calls
    )
    await session.commit()

    assert msg.role == MessageRole.ASSISTANT
    assert msg.content == "Here are your tasks"

    # Verify tool_calls are retrievable
    history = await fetch_history(session, conv.id, "user_1")
    assert history[0]["tool_calls"] == tool_calls


@pytest.mark.asyncio
async def test_empty_conversation_returns_empty_history(session: AsyncSession):
    """Empty conversation returns empty list."""
    conv = await get_or_create_conversation(session, "user_1", None)
    await session.commit()

    history = await fetch_history(session, conv.id, "user_1")

    assert history == []
```

**Test Fixture** (add to `conftest.py`):
```python
import pytest
import asyncio
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

@pytest.fixture(scope="function")
async def session():
    """Create a test database session."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        yield session
```

**Run Tests**:
```bash
cd backend
pytest tests/test_persistence.py -v
```

## Verification Checklist

After implementation, verify:

- [ ] `python -c "from src.models.conversation import Conversation, Message"` works
- [ ] `python -c "from src.persistence import get_or_create_conversation"` works
- [ ] Database tables created: `conversations`, `messages`
- [ ] All tests pass: `pytest tests/test_persistence.py -v`
- [ ] User isolation works (test with different user_ids)

## Integration Points

After this chunk is complete, the following chunks can proceed:

1. **Chunk 4 (Chat Endpoint)**: Import and use persistence functions
   ```python
   from src.persistence import get_or_create_conversation, fetch_history, store_user_message, store_assistant_response
   ```

2. **Chunk 6 (Agent Runner)**: Use fetch_history for context
   ```python
   history = await fetch_history(session, conversation_id, user_id)
   # history is ready for Gemini prompt
   ```

## Troubleshooting

### Issue: Circular import error
**Solution**: Use `TYPE_CHECKING` for forward references in models.

### Issue: "Table already exists" error
**Solution**: Drop tables and recreate: `await conn.run_sync(SQLModel.metadata.drop_all)`

### Issue: Timestamps are None
**Solution**: Ensure `server_default=func.now()` is set in Field kwargs, not as default value.

### Issue: Tool calls serialization fails
**Solution**: Ensure tool_calls contain only JSON-serializable data (no datetime, no custom objects).
