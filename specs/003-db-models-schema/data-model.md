# Data Model: Database Models & Schema (Chunk 2)

**Feature**: 003-db-models-schema
**Date**: 2026-01-16
**Status**: Complete

## Overview

This document defines the entity models, relationships, and validation rules for the Phase III AI Chatbot database schema.

---

## Entity Relationship Diagram

```
┌─────────────────┐
│      User       │
│  (Better Auth)  │
├─────────────────┤
│ id: string (PK) │
│ email: string   │
│ password_hash   │
│ created_at      │
└────────┬────────┘
         │
         │ 1:N
         ▼
┌─────────────────┐       ┌─────────────────────┐
│      Task       │       │    Conversation     │
├─────────────────┤       ├─────────────────────┤
│ id: int (PK)    │       │ id: int (PK)        │
│ user_id: string │◄──────│ user_id: string     │
│ title: string   │   1:N │ created_at: datetime│
│ description     │       │ updated_at: datetime│
│ completed: bool │       └──────────┬──────────┘
│ created_at      │                  │
│ updated_at      │                  │ 1:N (cascade delete)
└─────────────────┘                  ▼
                          ┌─────────────────────┐
                          │      Message        │
                          ├─────────────────────┤
                          │ id: int (PK)        │
                          │ user_id: string     │
                          │ conversation_id: int│
                          │ role: MessageRole   │
                          │ content: text       │
                          │ created_at: datetime│
                          └─────────────────────┘
```

---

## Entity: User

**Table Name**: `users`
**Managed By**: Better Auth (external)

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | string | PK | UUID from Better Auth |
| email | string | UNIQUE, NOT NULL | User email address |
| password_hash | string | NOT NULL | Hashed password |
| created_at | datetime | NOT NULL | Account creation time |

**Notes**: This entity is managed by Better Auth and exists for referential integrity. Application code should not modify this table directly.

---

## Entity: Task

**Table Name**: `tasks`
**Purpose**: Stores individual todo items per user

### Fields

| Field | Type | Constraints | Default | Description |
|-------|------|-------------|---------|-------------|
| id | integer | PK, AUTO_INCREMENT | - | Unique task identifier |
| user_id | string | FK → users.id, NOT NULL, INDEX | - | Owner of the task |
| title | string(200) | NOT NULL | - | Task title (1-200 chars) |
| description | text | NULLABLE | NULL | Optional task description |
| completed | boolean | NOT NULL | false | Completion status |
| created_at | datetime | NOT NULL | server now() | Creation timestamp |
| updated_at | datetime | NOT NULL | server now(), auto-update | Last modification timestamp |

### Indexes

| Name | Columns | Purpose |
|------|---------|---------|
| ix_tasks_user_id | user_id | Fast user task lookup |
| ix_tasks_user_id_completed | user_id, completed | Optimized filtered queries |

### Validation Rules

1. **title**: Must be non-empty string, max 200 characters
2. **user_id**: Must be non-empty string (from auth system)
3. **completed**: Boolean only, no null
4. **description**: Max 5000 characters if provided

### State Transitions

```
[Created] ──completed=true──► [Completed]
    ▲                              │
    │                              │
    └───────completed=false────────┘
```

---

## Entity: Conversation

**Table Name**: `conversations`
**Purpose**: Represents a chat session for a user

### Fields

| Field | Type | Constraints | Default | Description |
|-------|------|-------------|---------|-------------|
| id | integer | PK, AUTO_INCREMENT | - | Unique conversation identifier |
| user_id | string | NOT NULL, INDEX | - | Owner of the conversation |
| created_at | datetime | NOT NULL | server now() | Session start time |
| updated_at | datetime | NOT NULL | server now(), auto-update | Last activity time |

### Indexes

| Name | Columns | Purpose |
|------|---------|---------|
| ix_conversations_user_id | user_id | Fast user conversation lookup |

### Validation Rules

1. **user_id**: Must be non-empty string (from auth system)

### Relationships

| Relationship | Type | Target | Cascade |
|--------------|------|--------|---------|
| messages | One-to-Many | Message | DELETE (delete messages when conversation deleted) |

---

## Entity: Message

**Table Name**: `messages`
**Purpose**: Stores individual messages within a conversation

### Fields

| Field | Type | Constraints | Default | Description |
|-------|------|-------------|---------|-------------|
| id | integer | PK, AUTO_INCREMENT | - | Unique message identifier |
| user_id | string | NOT NULL | - | Owner (for user isolation) |
| conversation_id | integer | FK → conversations.id, NOT NULL | - | Parent conversation |
| role | MessageRole | NOT NULL | - | Sender role (user/assistant) |
| content | text | NOT NULL | - | Message content |
| created_at | datetime | NOT NULL | server now() | Message timestamp |

### Indexes

| Name | Columns | Purpose |
|------|---------|---------|
| ix_messages_conversation_id_created_at | conversation_id, created_at | Chronological message retrieval |

### Validation Rules

1. **user_id**: Must be non-empty string
2. **conversation_id**: Must reference existing conversation
3. **role**: Must be valid MessageRole enum value
4. **content**: Must be non-empty string

### Foreign Key Constraints

| Column | References | On Delete |
|--------|------------|-----------|
| conversation_id | conversations.id | CASCADE |

---

## Enum: MessageRole

**Purpose**: Type-safe role identification for messages

| Value | Description |
|-------|-------------|
| USER | Message from the user |
| ASSISTANT | Message from the AI assistant |

**Storage**: VARCHAR (PostgreSQL), stores literal enum value ("user", "assistant")

**Validation**: Invalid values rejected at Pydantic validation layer before database insert.

---

## Query Patterns

### Pattern 1: Get User's Pending Tasks

```sql
SELECT * FROM tasks
WHERE user_id = :user_id AND completed = false
ORDER BY created_at DESC;
```
**Uses Index**: ix_tasks_user_id_completed

### Pattern 2: Get Conversation Messages

```sql
SELECT * FROM messages
WHERE conversation_id = :conversation_id
ORDER BY created_at ASC;
```
**Uses Index**: ix_messages_conversation_id_created_at

### Pattern 3: Get User's Conversations

```sql
SELECT * FROM conversations
WHERE user_id = :user_id
ORDER BY updated_at DESC;
```
**Uses Index**: ix_conversations_user_id

### Pattern 4: Get Recent Conversation with Messages

```sql
SELECT c.*, m.*
FROM conversations c
LEFT JOIN messages m ON m.conversation_id = c.id
WHERE c.user_id = :user_id
ORDER BY c.updated_at DESC, m.created_at ASC
LIMIT 1;
```

---

## Data Integrity Rules

### Rule 1: User Isolation
All queries MUST include user_id filter. No query should return data for users other than the authenticated user.

### Rule 2: Referential Integrity
- Task.user_id → User.id (not enforced at DB level, validated at app level)
- Conversation.user_id → User.id (not enforced at DB level, validated at app level)
- Message.conversation_id → Conversation.id (FK constraint enforced)

### Rule 3: Cascade Delete
Deleting a Conversation MUST delete all associated Messages (CASCADE).

### Rule 4: Timestamp Consistency
- created_at: Set once at creation, never modified
- updated_at: Auto-updated on every modification

---

## Migration Sequence

### Migration 1: Initial Schema (Phase II)
- Creates `users` table
- Creates `tasks` table with basic indexes

### Migration 2: Add Conversation Tables (Phase III - This Chunk)
- Creates `conversations` table
- Creates `messages` table
- Adds composite index on tasks
- Adds composite index on messages
- Sets up foreign key with cascade delete

---

## Sample Data for Testing

### Task Samples
```json
[
  {
    "user_id": "user-001",
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "completed": false
  },
  {
    "user_id": "user-001",
    "title": "Call dentist",
    "description": null,
    "completed": true
  }
]
```

### Conversation Samples
```json
[
  {
    "id": 1,
    "user_id": "user-001",
    "messages": [
      {"role": "user", "content": "Add a task to buy milk"},
      {"role": "assistant", "content": "I've added 'buy milk' to your tasks!"},
      {"role": "user", "content": "Show my tasks"},
      {"role": "assistant", "content": "You have 2 pending tasks: 1. Buy groceries 2. Buy milk"}
    ]
  }
]
```

---

## Appendix: SQLModel Class Summary

```python
# MessageRole Enum
class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"

# Task Model
class Task(SQLModel, table=True):
    id: Optional[int]          # PK
    user_id: str               # Indexed
    title: str                 # Required
    description: Optional[str] # Nullable
    completed: bool            # Default false
    created_at: datetime       # Server default
    updated_at: datetime       # Server default + onupdate

# Conversation Model
class Conversation(SQLModel, table=True):
    id: Optional[int]          # PK
    user_id: str               # Indexed
    created_at: datetime       # Server default
    updated_at: datetime       # Server default + onupdate
    messages: List["Message"]  # Relationship

# Message Model
class Message(SQLModel, table=True):
    id: Optional[int]          # PK
    user_id: str               # Required
    conversation_id: int       # FK to Conversation
    role: MessageRole          # Enum
    content: str               # Text
    created_at: datetime       # Server default
    conversation: Optional["Conversation"]  # Relationship
```
