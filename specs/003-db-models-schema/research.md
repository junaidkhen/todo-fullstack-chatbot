# Research: Database Models & Schema (Chunk 2)

**Feature**: 003-db-models-schema
**Date**: 2026-01-16
**Status**: Complete

## Overview

This document captures research findings and technology decisions for implementing SQLModel classes for Task, Conversation, and Message with Alembic migrations for Neon PostgreSQL.

---

## Research Task 1: SQLModel with Async PostgreSQL

### Question
How to properly configure SQLModel with asyncpg for Neon PostgreSQL?

### Decision
Use `sqlalchemy.ext.asyncio.create_async_engine` with `postgresql+asyncpg://` connection string.

### Rationale
- SQLModel is built on SQLAlchemy 2.x which has first-class async support
- asyncpg is the recommended async driver for PostgreSQL
- Neon PostgreSQL is standard PostgreSQL and fully compatible

### Alternatives Considered
1. **Synchronous psycopg2**: Rejected - Would block event loop, incompatible with FastAPI async
2. **aiopg**: Rejected - asyncpg has better performance and more active maintenance
3. **Databases library**: Rejected - Adds another abstraction layer; SQLModel handles this well

### Implementation Notes
```python
from sqlalchemy.ext.asyncio import create_async_engine

# Convert connection string
url = os.getenv("DATABASE_URL").replace("postgresql://", "postgresql+asyncpg://")
async_engine = create_async_engine(url, echo=True)
```

---

## Research Task 2: SQLModel Relationships Best Practices

### Question
How to define bidirectional one-to-many relationships in SQLModel between Conversation and Message?

### Decision
Use SQLModel's `Relationship` with `back_populates` and forward references via `TYPE_CHECKING`.

### Rationale
- `TYPE_CHECKING` prevents circular import issues at runtime
- `back_populates` ensures relationship is synchronized in both directions
- SQLModel's Relationship wraps SQLAlchemy's relationship with Pydantic integration

### Alternatives Considered
1. **backref**: Rejected - Deprecated in SQLAlchemy 2.x; back_populates is preferred
2. **Single direction only**: Rejected - Spec requires bidirectional navigation (SC-008)
3. **No TYPE_CHECKING**: Rejected - Causes circular import errors

### Implementation Notes
```python
# In conversation.py
if TYPE_CHECKING:
    from .message import Message

class Conversation(SQLModel, table=True):
    messages: List["Message"] = Relationship(back_populates="conversation")

# In message.py
if TYPE_CHECKING:
    from .conversation import Conversation

class Message(SQLModel, table=True):
    conversation: Optional["Conversation"] = Relationship(back_populates="messages")
```

---

## Research Task 3: Server-Side Timestamps in PostgreSQL

### Question
How to implement auto-populating timestamps using PostgreSQL server_default instead of Python datetime?

### Decision
Use SQLAlchemy's `func.now()` with `sa_column_kwargs={"server_default": func.now()}`.

### Rationale
- Server-side defaults ensure consistency regardless of application server time
- PostgreSQL's `now()` is timezone-aware and consistent
- Reduces risk of clock drift issues in distributed deployments

### Alternatives Considered
1. **Python default_factory**: Rejected - Uses application server time, not database time
2. **text("now()")**: Rejected - func.now() is cleaner and properly typed
3. **CURRENT_TIMESTAMP**: Equivalent to func.now(), either works

### Implementation Notes
```python
from sqlalchemy.sql import func

class Task(SQLModel, table=True):
    created_at: datetime = Field(
        default=None,  # Required for server_default to work
        sa_column_kwargs={"server_default": func.now()}
    )
    updated_at: datetime = Field(
        default=None,
        sa_column_kwargs={
            "server_default": func.now(),
            "onupdate": func.now()
        }
    )
```

**Important**: Set `default=None` when using server_default, otherwise SQLModel tries to set a Python default which conflicts.

---

## Research Task 4: Cascade Delete Configuration

### Question
How to ensure deleting a Conversation automatically deletes all associated Messages?

### Decision
Use SQLAlchemy relationship kwargs with `cascade="all, delete-orphan"`.

### Rationale
- Spec FR-011 requires cascade delete from Conversation to Message
- "delete-orphan" also handles cases where message is disassociated from conversation
- Database-level ON DELETE CASCADE is backup, but ORM-level is more explicit

### Alternatives Considered
1. **Database-only cascade**: Rejected - Less explicit, harder to test
2. **Manual deletion in code**: Rejected - Error-prone, violates spec
3. **Soft deletes**: Rejected - Spec explicitly states no soft deletes needed

### Implementation Notes
```python
class Conversation(SQLModel, table=True):
    messages: List["Message"] = Relationship(
        back_populates="conversation",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
```

Also add to foreign key in migration for database-level enforcement:
```python
sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE')
```

---

## Research Task 5: Alembic Async Configuration

### Question
How to configure Alembic to work with async SQLAlchemy engine?

### Decision
Use `async_engine_from_config` with `asyncio.run()` wrapper in env.py.

### Rationale
- Alembic doesn't natively support async, but SQLAlchemy 2.x provides helpers
- `run_sync` method allows running sync migrations on async connection
- Same pattern used by SQLAlchemy documentation

### Alternatives Considered
1. **Separate sync engine for migrations**: Rejected - Requires maintaining two configurations
2. **alembic-async-sqlalchemy package**: Rejected - Adds dependency; built-in approach works
3. **Sync driver just for migrations**: Rejected - Inconsistent with production setup

### Implementation Notes
See Step 9 in plan.md for complete env.py implementation.

---

## Research Task 6: Composite Index Definition in SQLModel

### Question
How to define composite indexes on multiple columns in SQLModel?

### Decision
Use SQLAlchemy's `Index` in `__table_args__` tuple.

### Rationale
- SQLModel's `Field(index=True)` only creates single-column indexes
- Composite indexes require SQLAlchemy's Index class directly
- `__table_args__` is the standard SQLAlchemy approach for table-level constraints

### Alternatives Considered
1. **Separate CREATE INDEX migration**: Rejected - Better to define in model
2. **Raw SQL in migration**: Rejected - Not captured in model metadata
3. **Multiple single-column indexes**: Rejected - Less efficient for multi-column queries

### Implementation Notes
```python
from sqlalchemy import Index

class Task(SQLModel, table=True):
    __table_args__ = (
        Index("ix_tasks_user_id_completed", "user_id", "completed"),
    )

class Message(SQLModel, table=True):
    __table_args__ = (
        Index("ix_messages_conversation_id_created_at", "conversation_id", "created_at"),
    )
```

---

## Research Task 7: Enum Handling with Pydantic/SQLModel

### Question
How to properly handle MessageRole enum for database storage and API validation?

### Decision
Use Python Enum inheriting from both `str` and `Enum` for automatic serialization.

### Rationale
- `str, Enum` base classes allow automatic JSON serialization
- PostgreSQL stores as VARCHAR, not native ENUM type (simpler migrations)
- Pydantic validates enum values automatically on model instantiation

### Alternatives Considered
1. **PostgreSQL ENUM type**: Rejected - Harder to migrate, adds complexity
2. **Plain string with validation**: Rejected - Less type-safe, requires manual validation
3. **Integer enum**: Rejected - Less readable in database, harder to debug

### Implementation Notes
```python
class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"

# In Message model
role: MessageRole = Field(nullable=False)

# This allows:
# - Database stores "user" or "assistant" as VARCHAR
# - Pydantic validates on instantiation
# - JSON serialization works automatically
```

---

## Research Task 8: Neon PostgreSQL Compatibility

### Question
Are there any Neon-specific considerations for the database schema?

### Decision
No special considerations needed. Neon is fully PostgreSQL-compatible.

### Rationale
- Neon PostgreSQL supports all standard PostgreSQL features
- Foreign keys, indexes, constraints work identically
- Serverless architecture is transparent to the application

### Considerations
1. **Connection pooling**: Neon has built-in pooling; additional pooling optional
2. **Cold starts**: First connection may be slower; use `pool_pre_ping=True` for resilience
3. **SSL**: Neon requires SSL; asyncpg handles this with `sslmode=require` in URL

### Implementation Notes
No code changes needed. Environment variable `DATABASE_URL` from Neon dashboard works directly.

---

## Summary of Decisions

| Area | Decision | Rationale |
|------|----------|-----------|
| Async Driver | asyncpg | Best performance, first-class SQLAlchemy support |
| Relationships | back_populates + TYPE_CHECKING | Bidirectional, no circular imports |
| Timestamps | func.now() server_default | Database-consistent time |
| Cascade Delete | ORM + DB level | Explicit and enforced |
| Alembic Async | asyncio.run wrapper | Works with existing async engine |
| Indexes | __table_args__ with Index | Standard SQLAlchemy approach |
| Enum Storage | str, Enum as VARCHAR | Simple, portable, auto-serialized |
| Neon | Standard PostgreSQL | No special handling needed |

---

## References

- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [SQLAlchemy 2.0 Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Alembic Documentation](https://alembic.sqlalchemy.org/en/latest/)
- [asyncpg Documentation](https://magicstack.github.io/asyncpg/)
- [Neon PostgreSQL](https://neon.tech/docs)
