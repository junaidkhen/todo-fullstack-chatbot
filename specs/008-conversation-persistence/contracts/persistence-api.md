# API Contract: Conversation Persistence Functions

**Feature Branch**: `008-conversation-persistence`
**Date**: 2026-01-17
**Status**: Complete

## Overview

This document defines the internal Python API contracts for conversation persistence functions. These are not HTTP endpoints but Python async functions that will be called by the chat endpoint handler and agent runner.

---

## Module Location

```
backend/src/persistence.py
```

---

## Function: get_or_create_conversation

### Signature

```python
async def get_or_create_conversation(
    session: AsyncSession,
    user_id: str,
    conversation_id: int | None
) -> Conversation
```

### Description

Retrieves an existing conversation or creates a new one. Enforces user isolation by validating ownership.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `session` | `AsyncSession` | Yes | Active database session |
| `user_id` | `str` | Yes | Authenticated user's ID |
| `conversation_id` | `int \| None` | Yes | Existing conversation ID or None |

### Return Value

| Type | Description |
|------|-------------|
| `Conversation` | Conversation model instance (existing or newly created) |

### Behavior Matrix

| conversation_id | Exists? | Owner Match? | Result |
|-----------------|---------|--------------|--------|
| `None` | N/A | N/A | Create new conversation |
| Valid ID | Yes | Yes | Return existing conversation |
| Valid ID | Yes | No | Create new conversation |
| Invalid ID | No | N/A | Create new conversation |

### Example Usage

```python
from sqlmodel.ext.asyncio.session import AsyncSession
from src.persistence import get_or_create_conversation

async def handle_chat(session: AsyncSession, user_id: str, conv_id: int | None):
    conversation = await get_or_create_conversation(session, user_id, conv_id)
    # conversation.id is now guaranteed to be valid for this user
```

### Error Handling

- No exceptions raised for normal operations
- Database errors propagate to caller
- Empty `user_id` behavior: Creates conversation (validation at API layer)

---

## Function: fetch_history

### Signature

```python
async def fetch_history(
    session: AsyncSession,
    conversation_id: int,
    user_id: str,
    limit: int = 30
) -> list[dict]
```

### Description

Fetches recent message history for a conversation. Returns the N most recent messages in chronological order (oldest to newest).

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `session` | `AsyncSession` | Yes | - | Active database session |
| `conversation_id` | `int` | Yes | - | Conversation to fetch from |
| `user_id` | `str` | Yes | - | User ID for isolation validation |
| `limit` | `int` | No | 30 | Maximum messages to return |

### Return Value

| Type | Description |
|------|-------------|
| `list[dict]` | List of message dictionaries, chronologically ordered |

### Message Dictionary Schema

```python
{
    "role": str,        # "user" or "assistant"
    "content": str,     # Message content
    "created_at": str,  # ISO 8601 datetime string
    "tool_calls": list | None  # Deserialized tool calls (assistant only)
}
```

### Behavior Matrix

| Condition | Result |
|-----------|--------|
| Valid conversation, has messages | Return up to `limit` messages |
| Valid conversation, no messages | Return `[]` |
| Invalid conversation_id | Return `[]` |
| Wrong user_id | Return `[]` |

### Example Usage

```python
from src.persistence import fetch_history

async def get_context(session: AsyncSession, conv_id: int, user_id: str):
    history = await fetch_history(session, conv_id, user_id, limit=30)
    # history is list of dicts ready for Gemini prompt
    for msg in history:
        print(f"{msg['role']}: {msg['content']}")
```

### Query Pattern

```sql
-- Logical SQL (not actual implementation)
SELECT * FROM (
    SELECT * FROM messages
    WHERE conversation_id = :conv_id
      AND user_id = :user_id
    ORDER BY created_at DESC
    LIMIT :limit
) sub
ORDER BY created_at ASC
```

---

## Function: store_user_message

### Signature

```python
async def store_user_message(
    session: AsyncSession,
    conversation_id: int,
    user_id: str,
    content: str
) -> Message
```

### Description

Stores a user message in the conversation. Validates conversation ownership before storing.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `session` | `AsyncSession` | Yes | Active database session |
| `conversation_id` | `int` | Yes | Target conversation |
| `user_id` | `str` | Yes | User ID for isolation validation |
| `content` | `str` | Yes | User's message content |

### Return Value

| Type | Description |
|------|-------------|
| `Message` | Created Message model instance |

### Message Fields Set

| Field | Value |
|-------|-------|
| `conversation_id` | From parameter |
| `user_id` | From parameter |
| `role` | `MessageRole.USER` |
| `content` | From parameter |
| `tool_calls` | `None` |
| `created_at` | Server timestamp |

### Example Usage

```python
from src.persistence import store_user_message

async def save_user_input(session: AsyncSession, conv_id: int, user_id: str, text: str):
    message = await store_user_message(session, conv_id, user_id, text)
    print(f"Stored message {message.id}")
```

### Error Handling

| Condition | Behavior |
|-----------|----------|
| Invalid conversation_id | Raises `ValueError("Invalid conversation")` |
| Wrong user_id | Raises `ValueError("Invalid conversation")` |
| Empty content | Allowed (valid for empty submit) |

---

## Function: store_assistant_response

### Signature

```python
async def store_assistant_response(
    session: AsyncSession,
    conversation_id: int,
    user_id: str,
    content: str,
    tool_calls: list | None
) -> Message
```

### Description

Stores an assistant response with optional tool call metadata. Validates conversation ownership before storing.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `session` | `AsyncSession` | Yes | Active database session |
| `conversation_id` | `int` | Yes | Target conversation |
| `user_id` | `str` | Yes | User ID for isolation validation |
| `content` | `str` | Yes | Assistant's response text |
| `tool_calls` | `list \| None` | Yes | Tool calls made (JSON-serializable) |

### Return Value

| Type | Description |
|------|-------------|
| `Message` | Created Message model instance |

### Message Fields Set

| Field | Value |
|-------|-------|
| `conversation_id` | From parameter |
| `user_id` | From parameter |
| `role` | `MessageRole.ASSISTANT` |
| `content` | From parameter |
| `tool_calls` | JSON-serialized if provided |
| `created_at` | Server timestamp |

### Tool Calls Schema

```python
# Expected tool_calls format
[
    {
        "name": "list_tasks",
        "args": {"status": "pending"}
    },
    {
        "name": "add_task",
        "args": {"title": "Buy milk", "description": None}
    }
]
```

### Example Usage

```python
from src.persistence import store_assistant_response

async def save_ai_response(session, conv_id, user_id, response_text, tools_used):
    message = await store_assistant_response(
        session, conv_id, user_id, response_text, tools_used
    )
    print(f"Stored assistant response {message.id}")
```

### Error Handling

| Condition | Behavior |
|-----------|----------|
| Invalid conversation_id | Raises `ValueError("Invalid conversation")` |
| Wrong user_id | Raises `ValueError("Invalid conversation")` |
| Non-serializable tool_calls | Raises `TypeError` from json.dumps |

---

## Type Definitions

### Import Statement

```python
from sqlmodel.ext.asyncio.session import AsyncSession
from src.models.conversation import Conversation, Message, MessageRole
```

### Type Hints Summary

```python
# Function signatures with full type hints
async def get_or_create_conversation(
    session: AsyncSession,
    user_id: str,
    conversation_id: int | None
) -> Conversation: ...

async def fetch_history(
    session: AsyncSession,
    conversation_id: int,
    user_id: str,
    limit: int = 30
) -> list[dict]: ...

async def store_user_message(
    session: AsyncSession,
    conversation_id: int,
    user_id: str,
    content: str
) -> Message: ...

async def store_assistant_response(
    session: AsyncSession,
    conversation_id: int,
    user_id: str,
    content: str,
    tool_calls: list | None
) -> Message: ...
```

---

## Transaction Handling

### Caller Responsibility

The persistence functions do NOT commit transactions. The caller (endpoint handler) is responsible for:

1. Beginning the transaction (automatic with AsyncSession)
2. Calling persistence functions
3. Committing on success: `await session.commit()`
4. Rolling back on error: `await session.rollback()`

### Example: Full Chat Flow

```python
async def chat_handler(session: AsyncSession, user_id: str, conv_id: int | None, user_msg: str):
    try:
        # Get or create conversation
        conversation = await get_or_create_conversation(session, user_id, conv_id)

        # Store user message
        await store_user_message(session, conversation.id, user_id, user_msg)

        # Fetch history for AI context
        history = await fetch_history(session, conversation.id, user_id)

        # ... call Gemini, get response ...
        ai_response = "Your tasks are..."
        tool_calls = [{"name": "list_tasks", "args": {}}]

        # Store assistant response
        await store_assistant_response(
            session, conversation.id, user_id, ai_response, tool_calls
        )

        # Commit all changes
        await session.commit()

        return {"response": ai_response, "conversation_id": conversation.id}

    except Exception as e:
        await session.rollback()
        raise
```

---

## Security Contract

### User Isolation Guarantee

All functions that access user data MUST include user_id validation:

```python
# Every query includes user_id filter
.where(Conversation.user_id == user_id)
.where(Message.user_id == user_id)
```

### Ownership Validation

Before any write operation:

```python
# Validate conversation ownership
conversation = await session.get(Conversation, conversation_id)
if not conversation or conversation.user_id != user_id:
    raise ValueError("Invalid conversation")
```

---

## References

- Feature Spec: `/specs/008-conversation-persistence/spec.md`
- Data Model: `/specs/008-conversation-persistence/data-model.md`
- Research: `/specs/008-conversation-persistence/research.md`
