# Feature Specification: Database Models & Schema (Chunk 2)

**Feature Branch**: `003-db-models-schema`
**Created**: 2026-01-16
**Status**: Draft
**Input**: Define SQLModel classes for Task, Conversation, and Message with relationships, indexes, and Alembic migration strategy for Neon PostgreSQL.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Task Data Persistence (Priority: P1)

As a system component, I need to persist task data reliably so that users' todo items survive server restarts and are isolated per user.

**Why this priority**: Task persistence is the core value of the application. Without reliable task storage, the entire todo functionality fails.

**Independent Test**: Can be fully tested by creating a task via direct database insert, restarting the database connection, and verifying the task is retrievable with all fields intact.

**Acceptance Scenarios**:

1. **Given** a Task model with all required fields, **When** a task is created with user_id, title, and description, **Then** the task is persisted with auto-generated id, created_at, and updated_at timestamps.
2. **Given** an existing task in the database, **When** the database connection is closed and reopened, **Then** the task data is fully retrievable.
3. **Given** multiple users with tasks, **When** querying tasks for user_id "user_a", **Then** only tasks belonging to "user_a" are returned (user isolation enforced).

---

### User Story 2 - Conversation History Storage (Priority: P1)

As an AI chatbot system, I need to store conversation history so that the AI agent can maintain context across multiple messages within a session.

**Why this priority**: Conversation history enables context-aware AI responses, which is fundamental to the chatbot experience.

**Independent Test**: Can be fully tested by creating a conversation with multiple messages, querying the conversation, and verifying all messages are returned in creation order.

**Acceptance Scenarios**:

1. **Given** a user initiates a chat session, **When** a new conversation is started, **Then** a Conversation record is created with user_id, auto-generated id, and timestamps.
2. **Given** an active conversation, **When** messages are added, **Then** each Message is associated with the conversation via conversation_id foreign key.
3. **Given** a conversation with 10 messages, **When** fetching messages for that conversation, **Then** messages are returned in chronological order (by created_at).

---

### User Story 3 - Message Role Differentiation (Priority: P2)

As a conversation system, I need to distinguish between user messages and assistant messages so that the AI prompt can be constructed with proper role attribution.

**Why this priority**: Role differentiation is essential for proper AI prompt construction but builds on top of the basic conversation functionality.

**Independent Test**: Can be fully tested by creating messages with "user" and "assistant" roles, then filtering by role to verify correct categorization.

**Acceptance Scenarios**:

1. **Given** a message being stored, **When** the role is "user", **Then** the message is persisted with role="user".
2. **Given** a message being stored, **When** the role is "assistant", **Then** the message is persisted with role="assistant".
3. **Given** a message creation attempt with invalid role "system", **Then** the operation is rejected with a validation error.

---

### User Story 4 - Efficient Query Performance (Priority: P2)

As a backend system, I need optimized indexes so that common queries (tasks by user/status, messages by conversation) execute efficiently.

**Why this priority**: Performance optimization is important but secondary to core functionality.

**Independent Test**: Can be tested by verifying index existence in database schema and running EXPLAIN ANALYZE on representative queries.

**Acceptance Scenarios**:

1. **Given** the Task table with composite index on (user_id, completed), **When** querying pending tasks for a user, **Then** the query uses the index (verified via EXPLAIN).
2. **Given** the Message table with index on (conversation_id, created_at), **When** fetching recent messages for a conversation, **Then** the query uses the index efficiently.
3. **Given** the Conversation table with index on user_id, **When** listing all conversations for a user, **Then** the query uses the index.

---

### User Story 5 - Schema Migration Support (Priority: P3)

As a developer, I need database migrations managed by Alembic so that schema changes can be applied consistently across environments.

**Why this priority**: Migration tooling is operational infrastructure, lower priority than core data models.

**Independent Test**: Can be tested by generating a migration, applying it to a fresh database, and verifying schema matches model definitions.

**Acceptance Scenarios**:

1. **Given** a fresh database, **When** running alembic upgrade head, **Then** all tables (Task, Conversation, Message) are created with correct structure.
2. **Given** a schema change to models, **When** running alembic revision --autogenerate, **Then** a migration script is generated capturing the changes.
3. **Given** an existing database with data, **When** applying a non-destructive migration, **Then** existing data is preserved.

---

### Edge Cases

- What happens when attempting to create a Message with a non-existent conversation_id? Foreign key constraint violation.
- How does system handle nullable fields (description on Task)? Null values are permitted and stored correctly.
- What happens when user_id is empty string? Validation rejects empty user_id at model level.
- How does system handle concurrent task creation for same user? Database handles concurrency; no duplicate id conflicts due to auto-increment.
- What happens when updated_at is not explicitly set on update? onupdate trigger auto-updates the timestamp.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST define a Task model with fields: id (integer, primary key, auto-increment), user_id (string, indexed, required), title (string, required), description (string or null), completed (boolean, default false), created_at (datetime with server default), updated_at (datetime with server default and auto-update).

- **FR-002**: System MUST define a Conversation model with fields: id (integer, primary key, auto-increment), user_id (string, indexed, required), created_at (datetime with server default), updated_at (datetime with server default and auto-update).

- **FR-003**: System MUST define a Message model with fields: id (integer, primary key, auto-increment), user_id (string, required), conversation_id (integer, foreign key to Conversation.id, required), role (string enum: "user" or "assistant", required), content (text, required), created_at (datetime with server default).

- **FR-004**: System MUST implement a one-to-many relationship between Conversation and Message using SQLModel's Relationship with back_populates.

- **FR-005**: System MUST create a composite index on Task table for columns (user_id, completed) to optimize filtered task queries.

- **FR-006**: System MUST create a composite index on Message table for columns (conversation_id, created_at) to optimize conversation history retrieval.

- **FR-007**: System MUST create a single-column index on Conversation.user_id to optimize user conversation lookups.

- **FR-008**: System MUST use SQLModel's Field and sa_column_kwargs to configure PostgreSQL-compatible server_default=func.now() for created_at fields.

- **FR-009**: System MUST use SQLModel's Field and sa_column_kwargs to configure onupdate=func.now() for updated_at fields.

- **FR-010**: System MUST define a MessageRole enum with values "user" and "assistant" for type-safe role validation.

- **FR-011**: System MUST enforce foreign key constraint from Message.conversation_id to Conversation.id with cascade delete.

- **FR-012**: System MUST support Alembic for schema migrations with autogenerate capability from SQLModel models.

### Key Entities

- **Task**: Represents an individual todo item belonging to a user. Key attributes: ownership (user_id), completion status, title/description, audit timestamps. No relationship to conversations (tasks are user-level resources independent of chat sessions).

- **Conversation**: Represents a chat session for a user. Key attributes: ownership (user_id), audit timestamps. One conversation has many messages (parent in one-to-many).

- **Message**: Represents a single message in a conversation. Key attributes: conversation association (foreign key), sender role (user vs assistant), content, timestamp. Child in one-to-many with Conversation.

- **MessageRole**: Enum type constraining message roles to "user" or "assistant" values. Used for type-safe role validation.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All three models (Task, Conversation, Message) can be instantiated and persisted to Neon PostgreSQL without errors.

- **SC-002**: Foreign key constraint on Message.conversation_id correctly prevents orphaned messages (inserting message with invalid conversation_id fails).

- **SC-003**: Timestamp fields (created_at, updated_at) are automatically populated by the database without explicit values in application code.

- **SC-004**: updated_at field automatically changes when a record is modified (verified by updating a task title and checking timestamp).

- **SC-005**: User isolation is enforced by user_id field presence on all user-facing models (Task, Conversation, Message).

- **SC-006**: Indexes are created and utilized by the database query planner (verified via EXPLAIN ANALYZE on representative queries).

- **SC-007**: Alembic can generate migrations from model changes and apply them to a fresh database successfully.

- **SC-008**: Relationship navigation works bidirectionally: conversation.messages returns all associated messages, message.conversation returns the parent conversation.

## Model Structure Reference

This section provides the expected model structure for implementation reference. These are skeleton structures showing field definitions and relationships.

### MessageRole Enum

```python
from enum import Enum

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
```

### Task Model

```python
from sqlmodel import SQLModel, Field
from sqlalchemy import func, Index
from datetime import datetime
from typing import Optional

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    title: str = Field(nullable=False)
    description: Optional[str] = Field(default=None)
    completed: bool = Field(default=False)
    created_at: datetime = Field(
        sa_column_kwargs={"server_default": func.now()}
    )
    updated_at: datetime = Field(
        sa_column_kwargs={
            "server_default": func.now(),
            "onupdate": func.now()
        }
    )

    __table_args__ = (
        Index("ix_tasks_user_id_completed", "user_id", "completed"),
    )
```

### Conversation Model

```python
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import func
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .message import Message

class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    created_at: datetime = Field(
        sa_column_kwargs={"server_default": func.now()}
    )
    updated_at: datetime = Field(
        sa_column_kwargs={
            "server_default": func.now(),
            "onupdate": func.now()
        }
    )

    # Relationship to messages
    messages: List["Message"] = Relationship(back_populates="conversation")
```

### Message Model

```python
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import func, Index, Text
from datetime import datetime
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .conversation import Conversation

class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(nullable=False)
    conversation_id: int = Field(
        foreign_key="conversations.id",
        nullable=False
    )
    role: MessageRole = Field(nullable=False)
    content: str = Field(sa_column=Column(Text, nullable=False))
    created_at: datetime = Field(
        sa_column_kwargs={"server_default": func.now()}
    )

    # Relationship to conversation
    conversation: Optional["Conversation"] = Relationship(back_populates="messages")

    __table_args__ = (
        Index("ix_messages_conversation_id_created_at", "conversation_id", "created_at"),
    )
```

## Migration Strategy (Alembic)

### Initial Setup Steps

1. Install dependencies: `pip install alembic asyncpg`
2. Initialize Alembic: `alembic init alembic`
3. Configure `alembic.ini` with async PostgreSQL driver
4. Configure `alembic/env.py` to import SQLModel metadata
5. Generate initial migration: `alembic revision --autogenerate -m "initial_schema"`
6. Apply migration: `alembic upgrade head`

### env.py Configuration Notes

- Import all models before accessing metadata
- Use async engine configuration for Neon PostgreSQL
- Set `target_metadata = SQLModel.metadata`

### Migration Best Practices

- Always review autogenerated migrations before applying
- Use descriptive migration message names
- Test migrations on development database before production
- Keep migrations atomic (one logical change per migration)

## Assumptions

- User authentication is handled by Better Auth, which manages the users table separately
- user_id values come from Better Auth and are string type (UUIDs or similar)
- Neon PostgreSQL supports standard PostgreSQL features including indexes and foreign keys
- The application uses async database operations (asyncpg driver)
- No soft deletes required; cascade delete on conversation removes associated messages

## Dependencies

- SQLModel library for ORM functionality
- SQLAlchemy (underlying engine for SQLModel)
- asyncpg for async PostgreSQL connectivity
- Alembic for migrations
- Neon PostgreSQL as the database service
- Better Auth manages user authentication (separate concern)

## Non-Goals

- User authentication and users table management (handled by Better Auth)
- API endpoint implementation (separate spec)
- Gemini integration (separate spec)
- Chat UI implementation (separate spec)
- Database connection pooling configuration (infrastructure concern)
