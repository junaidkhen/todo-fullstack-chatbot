# Research: Conversation Persistence Logic (Chunk 7)

**Feature Branch**: `008-conversation-persistence`
**Date**: 2026-01-17
**Status**: Complete

## Research Overview

This document captures the research findings for implementing conversation persistence logic in the Phase III AI chatbot. All findings are based on analysis of the existing codebase and the Chunk 2 (DB Models & Schema) and Chunk 7 (Conversation Persistence) specifications.

---

## Decision 1: Database Models Availability

### Context
The spec requires Conversation and Message models with relationships. Need to verify if these models exist or need to be created.

### Finding
**Current State**: The `backend/src/models/task.py` file contains only `Task` and `User` models. The Conversation and Message models defined in Chunk 2 spec are NOT yet implemented.

**Decision**: Implement Conversation and Message models in a new file `backend/src/models/conversation.py` before implementing persistence functions.

**Rationale**:
- Separation of concerns: Task models vs Conversation models
- Follows existing pattern of model organization
- Models must exist before persistence layer can be built

**Alternatives Considered**:
- Adding to task.py: Rejected - file would become too large and mix unrelated concerns

---

## Decision 2: Persistence Module Location

### Context
Need to determine where to place the persistence functions (get_or_create_conversation, fetch_history, store_user_message, store_assistant_response).

### Finding
**Current State**: The project has:
- `backend/src/database.py` - Database engine and session management
- `backend/src/api/tasks.py` - Task CRUD API routes (inline database operations)

**Decision**: Create `backend/src/persistence.py` as a dedicated module for conversation persistence functions.

**Rationale**:
- Clean separation: API routes stay thin, persistence logic is reusable
- Consistent with spec requirement for testable, standalone functions
- Can be easily imported by chat endpoint handler and agent runner
- Matches the function signature patterns defined in the spec

**Alternatives Considered**:
- Inline in API endpoint: Rejected - functions need to be shared between chat endpoint and agent runner
- In database.py: Rejected - database.py should only handle connection/session management

---

## Decision 3: Async Session Management Pattern

### Context
The spec requires async database operations. Need to determine how persistence functions receive database sessions.

### Finding
**Current State**: `database.py` provides an async generator `get_session()` that yields `AsyncSession`. This is designed as a FastAPI dependency.

**Decision**: Persistence functions accept `AsyncSession` as a parameter. Caller (endpoint handler) is responsible for session lifecycle.

**Rationale**:
- Follows dependency injection pattern
- Functions become pure and testable
- Transaction boundaries controlled by caller
- Matches existing pattern in the codebase

**Function Signature Pattern**:
```python
async def get_or_create_conversation(
    session: AsyncSession,
    user_id: str,
    conversation_id: int | None
) -> Conversation
```

**Alternatives Considered**:
- Context manager within functions: Rejected - each function would create its own session, breaking transaction boundaries
- Global session: Rejected - not compatible with async patterns

---

## Decision 4: tool_calls Field Storage

### Context
The Message model in Chunk 2 spec does NOT include a `tool_calls` field, but Chunk 7 spec requires storing tool call metadata with assistant responses.

### Finding
**Schema Gap**: The Message model reference in Chunk 2 needs extension to include tool_calls field.

**Decision**: Add `tool_calls: Optional[str] = Field(default=None)` to Message model, storing JSON-serialized tool calls.

**Rationale**:
- JSON string is simple and PostgreSQL-compatible
- No need for JSONB operations (we only store and retrieve, no queries on content)
- Avoids adding complex JSON column type dependencies
- Tool calls are serialized to JSON on store, deserialized on fetch

**Data Format**:
```python
# Store
tool_calls_json = json.dumps(tool_calls) if tool_calls else None

# Fetch (in dict output)
"tool_calls": json.loads(message.tool_calls) if message.tool_calls else None
```

**Alternatives Considered**:
- PostgreSQL JSONB: Rejected - overkill for store/retrieve pattern, adds complexity
- Separate ToolCall table: Rejected - over-engineering for current requirements

---

## Decision 5: User Isolation Enforcement Strategy

### Context
Constitution requires user isolation at all layers. Need to determine how fetch_history and store functions enforce isolation.

### Finding
**Security Requirement**: Every function accessing conversation data must validate user ownership.

**Decision**:
- `get_or_create_conversation`: Takes user_id, validates conversation belongs to user
- `fetch_history`: Accepts both conversation_id AND user_id for validation
- `store_user_message` / `store_assistant_response`: Accept both conversation_id AND user_id for validation

**Rationale**:
- Defense in depth: Even if caller is compromised, persistence layer enforces isolation
- Matches constitutional requirement: "every function that accesses data includes user_id validation"
- Small API surface change but significant security improvement

**Updated Function Signatures**:
```python
async def fetch_history(
    session: AsyncSession,
    conversation_id: int,
    user_id: str,  # Added for isolation
    limit: int = 30
) -> list[dict]

async def store_user_message(
    session: AsyncSession,
    conversation_id: int,
    user_id: str,  # Added for isolation
    content: str
) -> Message

async def store_assistant_response(
    session: AsyncSession,
    conversation_id: int,
    user_id: str,  # Added for isolation
    content: str,
    tool_calls: list | None
) -> Message
```

**Alternatives Considered**:
- Trust caller to validate: Rejected - violates constitutional security principle
- Only validate in get_or_create: Rejected - store functions could still write to wrong conversation

---

## Decision 6: fetch_history Ordering Strategy

### Context
Spec requires: "Select the N most recent messages by created_at, then return them in chronological order."

### Finding
**Query Pattern**: Need to select recent messages (descending), then reverse for chronological output.

**Decision**: Use subquery pattern with ORDER BY twice.

**SQL Logic**:
```sql
SELECT * FROM (
    SELECT * FROM messages
    WHERE conversation_id = :id AND user_id = :user_id
    ORDER BY created_at DESC
    LIMIT :limit
) sub
ORDER BY created_at ASC
```

**SQLModel Implementation**:
```python
from sqlalchemy import select

subq = (
    select(Message)
    .where(Message.conversation_id == conversation_id)
    .where(Message.user_id == user_id)
    .order_by(Message.created_at.desc())
    .limit(limit)
).subquery()

messages = await session.exec(
    select(Message)
    .from_statement(
        select(subq).order_by(subq.c.created_at.asc())
    )
)
```

**Rationale**:
- Single database round-trip
- Efficient use of limit
- Correct chronological ordering in output

**Alternatives Considered**:
- Python-side reversal: Acceptable fallback if subquery is complex
- Window functions: Over-engineering for this use case

---

## Decision 7: Error Handling Approach

### Context
Need to determine how functions handle edge cases like non-existent conversations.

### Finding
**Spec Requirements**:
- `get_or_create_conversation`: Create new if not found or wrong user
- `fetch_history`: Return empty list if conversation doesn't exist
- Store functions: Should validate conversation ownership before storing

**Decision**: Follow graceful degradation pattern specified in spec.

**Behavior**:
```python
# get_or_create_conversation
if conversation_id is None or not exists or wrong_user:
    return create_new_conversation(user_id)

# fetch_history
if not exists or wrong_user:
    return []  # Empty list, no error

# store_user_message / store_assistant_response
if not exists or wrong_user:
    raise ValueError("Invalid conversation")  # Fail loudly on writes
```

**Rationale**:
- Reads are forgiving (empty results)
- Writes are strict (fail on invalid state)
- Matches user expectations: can't store to non-existent conversation

---

## Decision 8: Timestamp Handling

### Context
Models use `datetime.utcnow` but database should use server timestamps for consistency.

### Finding
**Current Implementation**: Task model uses `default_factory=datetime.utcnow` which sets timestamps at Python model instantiation, not database insert time.

**Decision**: For Conversation and Message models, use SQLAlchemy's `server_default=func.now()` pattern.

**Rationale**:
- Database-level consistency
- Works correctly with async and concurrent operations
- Matches Chunk 2 spec recommendations

**Implementation**:
```python
from sqlalchemy import func
from sqlmodel import Field

created_at: datetime = Field(
    default=None,
    sa_column_kwargs={"server_default": func.now(), "nullable": False}
)
```

---

## Decision 9: Message Role Enum

### Context
Need to implement MessageRole enum for type-safe role validation.

### Finding
**Spec Requirement**: MessageRole enum with values "user" and "assistant".

**Decision**: Use Python string enum matching the spec.

**Implementation**:
```python
from enum import Enum

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
```

**Rationale**:
- String enum for JSON serialization compatibility
- Matches Gemini message format
- Type-safe role validation

---

## Dependencies Confirmed

| Dependency | Status | Notes |
|------------|--------|-------|
| SQLModel | ✅ Available | Already in use |
| AsyncSession | ✅ Available | database.py provides get_session() |
| SQLAlchemy func | ✅ Available | For server_default timestamps |
| asyncpg | ✅ Configured | PostgreSQL async driver |
| json module | ✅ Standard library | For tool_calls serialization |

---

## Implementation Order

Based on dependencies:

1. **Create Models** (prerequisite)
   - `backend/src/models/conversation.py`
   - MessageRole enum
   - Conversation model
   - Message model (with tool_calls field)

2. **Update database.py**
   - Import new models in init_db()

3. **Create Persistence Module**
   - `backend/src/persistence.py`
   - get_or_create_conversation()
   - fetch_history()
   - store_user_message()
   - store_assistant_response()

4. **Integration Ready**
   - Functions ready for import by chat endpoint (Chunk 4)
   - Functions ready for import by agent runner (Chunk 6)

---

## Open Questions Resolved

| Question | Resolution |
|----------|------------|
| Where are Conversation/Message models? | Need to be created in new file |
| How to pass session to functions? | Dependency injection via parameter |
| How to store tool_calls? | JSON string field |
| How to enforce user isolation? | Add user_id parameter to all functions |
| What to return on missing conversation? | Empty list for reads, error for writes |

---

## References

- Feature Spec: `/specs/008-conversation-persistence/spec.md`
- DB Schema Spec: `/specs/003-db-models-schema/spec.md`
- Constitution: `/specs/phase3/constitution.md`
- Existing Models: `/backend/src/models/task.py`
- Database Module: `/backend/src/database.py`
