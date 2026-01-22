# Implementation Plan: Database Models & Schema (Chunk 2)

**Branch**: `003-db-models-schema` | **Date**: 2026-01-16 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-db-models-schema/spec.md`

## Summary

Define SQLModel classes for Task, Conversation, and Message with relationships, indexes, and Alembic migration strategy for Neon PostgreSQL. This chunk extends the existing Phase II Task model and adds new Conversation/Message models for Phase III AI chatbot conversation history.

## Technical Context

**Language/Version**: Python 3.12
**Primary Dependencies**: SQLModel 0.0.22, SQLAlchemy 2.0.35, asyncpg 0.30.0, Alembic (to be added)
**Storage**: Neon PostgreSQL (async via asyncpg)
**Testing**: pytest 8.3.4, pytest-asyncio 0.24.0
**Target Platform**: Linux server (FastAPI backend)
**Project Type**: Web application (frontend + backend)
**Performance Goals**: Sub-100ms database queries for common operations
**Constraints**: Async-only database operations, Neon PostgreSQL compatibility
**Scale/Scope**: Multi-user todo application with conversation history

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Spec-Driven Development Only | ✅ PASS | Following spec → plan → tasks workflow |
| II. Stateless Backend Architecture | ✅ PASS | All state persisted in database |
| III. Gemini API Free Tier Compliance | N/A | Not applicable to database layer |
| IV. Friendly Conversational Interface | N/A | Not applicable to database layer |
| V. Security Through User Isolation | ✅ PASS | user_id on all models enforces isolation |
| VI. Type Safety and Validation | ✅ PASS | SQLModel + Pydantic provides full typing |
| VII. Persistent Storage with Conversation History | ✅ PASS | Conversation + Message tables defined |

## Project Structure

### Documentation (this feature)

```text
specs/003-db-models-schema/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (N/A for database models)
└── tasks.md             # Phase 2 output (created by /sp.tasks)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   ├── __init__.py          # Model exports
│   │   ├── task.py              # Existing Task model (to be updated)
│   │   ├── conversation.py      # NEW: Conversation model
│   │   └── message.py           # NEW: Message model + MessageRole enum
│   ├── database.py              # Existing async engine config
│   └── init_db.py               # Database initialization
├── alembic/                     # NEW: Alembic migrations
│   ├── versions/                # Migration scripts
│   ├── env.py                   # Alembic environment config
│   └── script.py.mako           # Migration template
├── alembic.ini                  # NEW: Alembic config
└── tests/
    └── unit/
        └── test_models.py       # Model unit tests
```

**Structure Decision**: Web application structure with backend/ containing SQLModel models. Alembic migrations added at backend/ level for database schema management.

## Complexity Tracking

No violations. Implementation follows constitutional principles with minimal complexity.

---

# Chunk 2 Implementation Plan

## Step 1: Install Dependencies

Add Alembic for database migrations to requirements.txt.

**File**: `backend/requirements.txt`

**Additions**:
```
alembic==1.13.1
```

**Verification**: Run `pip install -r requirements.txt` and verify `alembic --version` outputs version info.

---

## Step 2: Create MessageRole Enum and Message Model

Create the MessageRole enum and Message model in a new file.

**File**: `backend/src/models/message.py`

**Implementation**:
```python
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, Text, Index
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .conversation import Conversation


class MessageRole(str, Enum):
    """Enum for message roles in conversation."""
    USER = "user"
    ASSISTANT = "assistant"


class Message(SQLModel, table=True):
    """Message entity representing a single message in a conversation."""
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
        default=None,
        sa_column_kwargs={"server_default": func.now()}
    )

    # Relationship to conversation
    conversation: Optional["Conversation"] = Relationship(back_populates="messages")

    __table_args__ = (
        Index("ix_messages_conversation_id_created_at", "conversation_id", "created_at"),
    )
```

**Verification**: Import the module without errors: `python -c "from src.models.message import Message, MessageRole"`

---

## Step 3: Create Conversation Model

Create the Conversation model with relationship to messages.

**File**: `backend/src/models/conversation.py`

**Implementation**:
```python
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .message import Message


class Conversation(SQLModel, table=True):
    """Conversation entity representing a chat session for a user."""
    __tablename__ = "conversations"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    created_at: datetime = Field(
        default=None,
        sa_column_kwargs={"server_default": func.now()}
    )
    updated_at: datetime = Field(
        default=None,
        sa_column_kwargs={
            "server_default": func.now(),
            "onupdate": func.now()
        }
    )

    # Relationship to messages (cascade delete when conversation deleted)
    messages: List["Message"] = Relationship(
        back_populates="conversation",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
```

**Verification**: Import the module without errors: `python -c "from src.models.conversation import Conversation"`

---

## Step 4: Update Task Model

Update the existing Task model to add the composite index and fix timestamp handling for PostgreSQL server_default.

**File**: `backend/src/models/task.py`

**Changes**:
1. Add composite index on (user_id, completed)
2. Update created_at/updated_at to use server_default with func.now()
3. Remove priority, category, due_date fields (not in Phase III spec)

**Verification**: Import the module without errors and verify index definition exists.

---

## Step 5: Update Models __init__.py

Export all models from a single location.

**File**: `backend/src/models/__init__.py`

**Implementation**:
```python
from .task import Task, TaskCreate, TaskUpdate, TaskResponse, User
from .conversation import Conversation
from .message import Message, MessageRole

__all__ = [
    "Task",
    "TaskCreate",
    "TaskUpdate",
    "TaskResponse",
    "User",
    "Conversation",
    "Message",
    "MessageRole",
]
```

**Verification**: `python -c "from src.models import Task, Conversation, Message, MessageRole"`

---

## Step 6: Update database.py

Update database.py to import all models for SQLModel metadata.

**File**: `backend/src/database.py`

**Changes**:
- Import Conversation and Message models in init_db()
- Ensure all models are registered with SQLModel.metadata

**Verification**: Run `python -c "from src.database import init_db; import asyncio; asyncio.run(init_db())"` (creates tables in dev DB).

---

## Step 7: Initialize Alembic

Initialize Alembic for database migrations.

**Commands** (from backend/ directory):
```bash
cd backend
alembic init alembic
```

**Verification**: `alembic/` directory created with env.py, script.py.mako, and versions/.

---

## Step 8: Configure alembic.ini

Update alembic.ini with database connection string template.

**File**: `backend/alembic.ini`

**Changes**:
- Set `sqlalchemy.url` to use environment variable: `driver://user:pass@localhost/dbname`
- Comment out default value; actual URL comes from env.py

**Verification**: File updated, no syntax errors.

---

## Step 9: Configure alembic/env.py

Configure env.py to use SQLModel metadata and async engine.

**File**: `backend/alembic/env.py`

**Implementation**:
```python
import os
import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context
from sqlmodel import SQLModel

# Import all models to register with metadata
from src.models import Task, User, Conversation, Message  # noqa: F401

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata to SQLModel's metadata
target_metadata = SQLModel.metadata

# Get database URL from environment
def get_url():
    url = os.getenv("DATABASE_URL", "sqlite:///./todo_dev.db")
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif url.startswith("sqlite:///"):
        path = url.split("sqlite:///")[1]
        url = f"sqlite+aiosqlite:///{path}"
    return url


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in 'online' mode with async engine."""
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()
    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

**Verification**: `alembic check` runs without errors.

---

## Step 10: Generate Initial Migration

Generate the initial migration with autogenerate.

**Command**:
```bash
cd backend
alembic revision --autogenerate -m "add_conversation_and_message_tables"
```

**Verification**: New migration file created in `alembic/versions/` with create_table for conversations and messages.

---

## Step 11: Review and Apply Migration

Review the autogenerated migration and apply to database.

**Commands**:
```bash
# Review the generated migration file manually
# Then apply:
alembic upgrade head
```

**Verification**:
- `alembic current` shows the migration is applied
- Database has conversations and messages tables
- Indexes exist (verify with `\d messages` in psql or equivalent)

---

## Step 12: Write Test Script for Model Validation

Create/update test file to verify models, relationships, and indexes.

**File**: `backend/tests/unit/test_models.py`

**Test Cases**:
1. Task model instantiation with all fields
2. Conversation model instantiation with timestamps
3. Message model instantiation with role enum
4. MessageRole enum validation (reject invalid roles)
5. Conversation-Message relationship (bidirectional navigation)
6. Cascade delete (deleting conversation deletes messages)
7. Foreign key constraint (message with invalid conversation_id fails)
8. Timestamp auto-population (server_default works)
9. updated_at auto-update on modification

**Verification**: `pytest tests/unit/test_models.py -v` passes all tests.

---

## Step 13: Integration Test with Neon PostgreSQL

Test against actual Neon PostgreSQL database.

**Prerequisites**: Set `DATABASE_URL` environment variable to Neon connection string.

**Test Cases**:
1. Create conversation, add messages, verify persistence
2. Query messages by conversation_id with ordering
3. Verify index usage via EXPLAIN ANALYZE
4. Test user isolation (query with different user_id)

**Verification**: All integration tests pass against Neon PostgreSQL.

---

## Debugging / Common Issues

### Issue 1: Connection String Format
**Problem**: asyncpg requires `postgresql+asyncpg://` prefix.
**Solution**: database.py and env.py both convert `postgresql://` to `postgresql+asyncpg://`.

### Issue 2: SQLModel Relationship Circular Import
**Problem**: Conversation and Message import each other.
**Solution**: Use `TYPE_CHECKING` guard and string forward references.

### Issue 3: func.now() Not Working in SQLite
**Problem**: SQLite doesn't support server_default with func.now().
**Solution**: Use aiosqlite driver and ensure DateTime column type. For dev, consider using default_factory as fallback.

### Issue 4: Alembic Can't Find Models
**Problem**: Autogenerate produces empty migration.
**Solution**: Import all models in env.py BEFORE accessing SQLModel.metadata.

### Issue 5: Enum Not Persisted Correctly
**Problem**: MessageRole enum saves as string but doesn't validate on load.
**Solution**: Use `str, Enum` base class and SQLModel handles serialization. Validation occurs at Pydantic layer.

### Issue 6: Cascade Delete Not Working
**Problem**: Deleting conversation doesn't delete messages.
**Solution**: Add `sa_relationship_kwargs={"cascade": "all, delete-orphan"}` to Relationship.

### Issue 7: Neon Connection Timeout
**Problem**: Neon serverless may have cold start delays.
**Solution**: Use connection pooling or handle timeout gracefully. For Alembic, use `pool_pre_ping=True`.

---

## Success Criteria Checklist

- [ ] SC-001: All three models persist to Neon PostgreSQL without errors
- [ ] SC-002: FK constraint prevents orphaned messages
- [ ] SC-003: Timestamps auto-populated by database
- [ ] SC-004: updated_at changes on record modification
- [ ] SC-005: user_id present on Task, Conversation, Message
- [ ] SC-006: Indexes created and used by query planner
- [ ] SC-007: Alembic generates and applies migrations
- [ ] SC-008: Bidirectional relationship navigation works

---

## Next Steps

After completing this plan:
1. Run `/sp.tasks` to generate tasks.md with actionable items
2. Implement each step sequentially
3. Run tests at each verification point
4. Create PHR documenting the implementation
