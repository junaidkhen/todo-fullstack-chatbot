# Data Model: Conversation Persistence (Chunk 7)

**Feature Branch**: `008-conversation-persistence`
**Date**: 2026-01-17
**Status**: Complete

## Overview

This document defines the data models for conversation persistence, including the Conversation and Message entities, their relationships, and validation rules. These models extend the existing database schema from Chunk 2.

---

## Entity: MessageRole (Enum)

### Definition

String enumeration for type-safe message role validation.

```python
from enum import Enum

class MessageRole(str, Enum):
    """Message sender role for conversation history."""
    USER = "user"
    ASSISTANT = "assistant"
```

### Values

| Value | Description |
|-------|-------------|
| `user` | Message sent by the human user |
| `assistant` | Message sent by the AI assistant |

### Usage Notes

- Used as the `role` field type in Message model
- String enum for JSON serialization compatibility
- Matches Gemini API message format

---

## Entity: Conversation

### Definition

Represents a chat session for a user. Parent entity in the one-to-many relationship with Messages.

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | `int` | Primary Key, Auto-increment | Unique conversation identifier |
| `user_id` | `str` | Required, Indexed, NOT NULL | Owner's user ID (from Better Auth) |
| `created_at` | `datetime` | Server Default, NOT NULL | Conversation creation timestamp |
| `updated_at` | `datetime` | Server Default, Auto-update, NOT NULL | Last modification timestamp |

### Relationships

| Relationship | Target | Cardinality | Description |
|--------------|--------|-------------|-------------|
| `messages` | `Message` | One-to-Many | All messages in this conversation |

### Indexes

| Index Name | Columns | Purpose |
|------------|---------|---------|
| `ix_conversations_user_id` | `user_id` | Optimize user conversation lookups |

### SQLModel Implementation

```python
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import func
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .conversation import Message

class Conversation(SQLModel, table=True):
    """Represents a chat session for a user."""
    __tablename__ = "conversations"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    created_at: datetime = Field(
        default=None,
        sa_column_kwargs={"server_default": func.now(), "nullable": False}
    )
    updated_at: datetime = Field(
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
```

### Validation Rules

1. `user_id` MUST NOT be empty string
2. `created_at` is automatically set by database
3. `updated_at` is automatically updated on any change

---

## Entity: Message

### Definition

Represents a single message in a conversation. Child entity in the one-to-many relationship with Conversation.

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | `int` | Primary Key, Auto-increment | Unique message identifier |
| `conversation_id` | `int` | Foreign Key, Required, NOT NULL | Parent conversation |
| `user_id` | `str` | Required, NOT NULL | Owner's user ID (denormalized for isolation) |
| `role` | `MessageRole` | Required, NOT NULL | Sender role (user/assistant) |
| `content` | `str` | TEXT, Required, NOT NULL | Message content |
| `tool_calls` | `str` | Optional, JSON string | Serialized tool call metadata |
| `created_at` | `datetime` | Server Default, NOT NULL | Message creation timestamp |

### Relationships

| Relationship | Target | Cardinality | Description |
|--------------|--------|-------------|-------------|
| `conversation` | `Conversation` | Many-to-One | Parent conversation |

### Foreign Keys

| Column | References | On Delete |
|--------|------------|-----------|
| `conversation_id` | `conversations.id` | CASCADE |

### Indexes

| Index Name | Columns | Purpose |
|------------|---------|---------|
| `ix_messages_conversation_created` | `conversation_id, created_at` | Optimize chronological message retrieval |

### SQLModel Implementation

```python
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import func, Text, Index
from sqlalchemy import Column
from datetime import datetime
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .conversation import Conversation

class Message(SQLModel, table=True):
    """Represents a single message in a conversation."""
    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id", nullable=False)
    user_id: str = Field(nullable=False)
    role: MessageRole = Field(nullable=False)
    content: str = Field(sa_column=Column(Text, nullable=False))
    tool_calls: Optional[str] = Field(default=None)  # JSON-serialized tool calls
    created_at: datetime = Field(
        default=None,
        sa_column_kwargs={"server_default": func.now(), "nullable": False}
    )

    # Relationship to conversation
    conversation: Optional["Conversation"] = Relationship(back_populates="messages")

    __table_args__ = (
        Index("ix_messages_conversation_created", "conversation_id", "created_at"),
    )
```

### Validation Rules

1. `conversation_id` MUST reference valid Conversation
2. `user_id` MUST match conversation's user_id (enforced at persistence layer)
3. `role` MUST be valid MessageRole enum value
4. `content` MAY be empty string (valid for empty submit scenarios)
5. `tool_calls` MUST be valid JSON string if provided

---

## Entity Relationship Diagram

```
┌─────────────────────────────────────┐
│           Conversation              │
├─────────────────────────────────────┤
│ id: int (PK)                        │
│ user_id: str (IX, NOT NULL)         │
│ created_at: datetime (NOT NULL)     │
│ updated_at: datetime (NOT NULL)     │
├─────────────────────────────────────┤
│ messages: List[Message] ────────────┼─┐
└─────────────────────────────────────┘ │
                                        │ 1:N
┌─────────────────────────────────────┐ │
│             Message                 │ │
├─────────────────────────────────────┤ │
│ id: int (PK)                        │ │
│ conversation_id: int (FK, IX) ──────┼─┘
│ user_id: str (NOT NULL)             │
│ role: MessageRole (NOT NULL)        │
│ content: text (NOT NULL)            │
│ tool_calls: str (NULL)              │
│ created_at: datetime (NOT NULL)     │
├─────────────────────────────────────┤
│ conversation: Conversation          │
└─────────────────────────────────────┘
```

---

## State Transitions

### Conversation States

Conversations are stateless records - no explicit state machine. Lifecycle:

1. **Created**: New conversation with no messages
2. **Active**: Conversation with messages being added
3. **Deleted**: Cascade deletes all messages (no soft delete)

### Message States

Messages are immutable once created. No state transitions.

---

## Data Serialization

### Message to Dict (for fetch_history)

```python
def message_to_dict(message: Message) -> dict:
    """Convert Message to Gemini-compatible dictionary."""
    return {
        "role": message.role.value,  # "user" or "assistant"
        "content": message.content,
        "created_at": message.created_at.isoformat(),
        "tool_calls": json.loads(message.tool_calls) if message.tool_calls else None
    }
```

### Tool Calls Serialization

```python
# Storing tool calls
tool_calls_json = json.dumps(tool_calls) if tool_calls else None

# Retrieving tool calls
tool_calls = json.loads(message.tool_calls) if message.tool_calls else None
```

---

## Migration Notes

### New Tables

1. `conversations` - Parent table for chat sessions
2. `messages` - Child table for conversation messages

### Required Migration Steps

1. Create `conversations` table with indexes
2. Create `messages` table with foreign key and indexes
3. No data migration needed (new tables)

### Rollback Plan

```sql
-- Rollback: Drop in reverse dependency order
DROP TABLE IF EXISTS messages;
DROP TABLE IF EXISTS conversations;
```

---

## User Isolation Requirements

### Design Decision: Denormalized user_id

The `user_id` is stored on both Conversation and Message models:
- **Conversation.user_id**: Primary ownership indicator
- **Message.user_id**: Denormalized for query efficiency and defense-in-depth

### Query Patterns

All queries MUST include user_id filter:

```python
# Correct: Includes user isolation
messages = await session.exec(
    select(Message)
    .where(Message.conversation_id == conversation_id)
    .where(Message.user_id == user_id)
)

# WRONG: Missing user isolation
messages = await session.exec(
    select(Message)
    .where(Message.conversation_id == conversation_id)
)
```

---

## File Location

Models will be implemented in:
```
backend/src/models/conversation.py
```

Contents:
- MessageRole enum
- Conversation model
- Message model

---

## References

- Feature Spec: `/specs/008-conversation-persistence/spec.md`
- DB Schema Spec: `/specs/003-db-models-schema/spec.md`
- Research: `/specs/008-conversation-persistence/research.md`
- Constitution: `/specs/phase3/constitution.md`
