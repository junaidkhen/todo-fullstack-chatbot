# Feature Specification: Conversation Persistence Logic (Chunk 7)

**Feature Branch**: `008-conversation-persistence`
**Created**: 2026-01-16
**Status**: Draft
**Input**: Define DB operations for creating/fetching/storing conversation history in stateless way.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Get or Create Conversation (Priority: P1)

As a chat endpoint handler, I need to retrieve an existing conversation or create a new one so that user messages are always associated with a valid conversation context.

**Why this priority**: This is the entry point for all conversation operations. Without the ability to get or create conversations, no messages can be stored or retrieved.

**Independent Test**: Can be fully tested by calling `get_or_create_conversation` with a user_id and no conversation_id, verifying a new conversation is created, then calling again with the returned conversation_id to verify the existing conversation is retrieved.

**Acceptance Scenarios**:

1. **Given** a user_id and no existing conversation_id, **When** `get_or_create_conversation(user_id, None)` is called, **Then** a new Conversation record is created and returned with the user_id and auto-generated id.
2. **Given** a user_id and a valid conversation_id that belongs to that user, **When** `get_or_create_conversation(user_id, conversation_id)` is called, **Then** the existing Conversation record is retrieved and returned.
3. **Given** a user_id and a conversation_id that belongs to a different user, **When** `get_or_create_conversation(user_id, conversation_id)` is called, **Then** a new Conversation is created (user isolation enforced; cannot hijack another user's conversation).
4. **Given** a user_id and a non-existent conversation_id, **When** `get_or_create_conversation(user_id, conversation_id)` is called, **Then** a new Conversation is created (graceful handling of invalid ids).

---

### User Story 2 - Fetch Conversation History (Priority: P1)

As a Gemini agent runner, I need to fetch recent messages from a conversation so that the AI model has context for generating responses.

**Why this priority**: Context retrieval is essential for AI-powered conversations. Without history, the AI cannot maintain coherent multi-turn conversations.

**Independent Test**: Can be fully tested by creating a conversation with 40 messages, calling `fetch_history(conversation_id, limit=30)`, and verifying exactly 30 messages are returned in chronological order (oldest to newest).

**Acceptance Scenarios**:

1. **Given** a conversation with 10 messages, **When** `fetch_history(conversation_id, limit=30)` is called, **Then** all 10 messages are returned in chronological order (oldest first).
2. **Given** a conversation with 50 messages, **When** `fetch_history(conversation_id, limit=30)` is called, **Then** the 30 most recent messages are returned in chronological order.
3. **Given** a conversation with no messages, **When** `fetch_history(conversation_id)` is called, **Then** an empty list is returned.
4. **Given** a valid conversation_id, **When** `fetch_history(conversation_id)` is called, **Then** messages are returned as dictionaries with keys: role, content, created_at (Gemini-compatible format).

---

### User Story 3 - Store User Message (Priority: P1)

As a chat endpoint handler, I need to persist user messages so that conversation history is maintained across requests and server restarts.

**Why this priority**: Storing user messages is fundamental to stateless architecture. Without persistence, conversation context is lost on every request.

**Independent Test**: Can be fully tested by calling `store_user_message(conversation_id, "Hello")`, then fetching history and verifying the message exists with role="user" and content="Hello".

**Acceptance Scenarios**:

1. **Given** a valid conversation_id and message content, **When** `store_user_message(conversation_id, content)` is called, **Then** a Message record is created with role="user", the provided content, and auto-generated created_at.
2. **Given** a message stored via `store_user_message`, **When** fetching history for that conversation, **Then** the message appears in the history with role="user".
3. **Given** an empty content string, **When** `store_user_message(conversation_id, "")` is called, **Then** the message is stored (empty strings are valid for user silence/empty submit scenarios).

---

### User Story 4 - Store Assistant Response (Priority: P1)

As a chat endpoint handler, I need to persist AI assistant responses with optional tool call metadata so that the full conversation is recorded for context and audit.

**Why this priority**: Storing assistant responses completes the conversation loop and enables full context replay for the AI model.

**Independent Test**: Can be fully tested by calling `store_assistant_response(conversation_id, "Here are your tasks", [{"name": "list_tasks", "args": {}}])`, then fetching history and verifying the response exists with role="assistant", content, and tool_calls metadata.

**Acceptance Scenarios**:

1. **Given** a valid conversation_id and response content without tool calls, **When** `store_assistant_response(conversation_id, content, None)` is called, **Then** a Message record is created with role="assistant" and the provided content.
2. **Given** a valid conversation_id, response content, and tool_calls list, **When** `store_assistant_response(conversation_id, content, tool_calls)` is called, **Then** a Message record is created with role="assistant", content, and tool_calls stored as JSON metadata.
3. **Given** a message stored via `store_assistant_response`, **When** fetching history for that conversation, **Then** the message appears with role="assistant" and any tool_calls metadata is accessible.

---

### User Story 5 - User Isolation in All Operations (Priority: P1)

As a security requirement, I need all conversation operations to enforce user isolation so that one user's data is never accessible to another user.

**Why this priority**: User isolation is a constitutional requirement. Security violations are non-negotiable failures.

**Independent Test**: Can be fully tested by creating conversations for user_a and user_b, then attempting cross-user access via all functions and verifying isolation is maintained.

**Acceptance Scenarios**:

1. **Given** user_a's conversation, **When** user_b attempts to fetch history for that conversation_id, **Then** the operation fails or returns empty (no cross-user access).
2. **Given** user_a's conversation, **When** attempting to store a message without user ownership validation, **Then** the system validates ownership before storing.
3. **Given** all conversation persistence functions, **When** auditing the implementation, **Then** every function that accesses data includes user_id validation.

---

### Edge Cases

- What happens when `fetch_history` is called with a non-existent conversation_id? Returns empty list or raises NotFoundError (implementation choice, but graceful handling required).
- How does system handle very long message content (>10KB)? Message is stored; content field uses TEXT type with no practical limit.
- What happens when tool_calls contains non-serializable data? Tool calls must be JSON-serializable; validation at function boundary.
- How does system handle concurrent message stores to same conversation? Database handles concurrency; messages get unique IDs and timestamps.
- What happens when conversation_id is None in fetch_history? Raises validation error (conversation_id is required for fetching history).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST implement `get_or_create_conversation(user_id: str, conversation_id: int | None) -> Conversation` that creates a new conversation if conversation_id is None or doesn't exist for the user, otherwise returns the existing conversation.

- **FR-002**: System MUST implement `fetch_history(conversation_id: int, limit: int = 30) -> list[dict]` that returns the most recent N messages for a conversation in chronological order (oldest to newest within the limit).

- **FR-003**: System MUST implement `store_user_message(conversation_id: int, content: str) -> Message` that creates a Message with role="user" and persists it to the database.

- **FR-004**: System MUST implement `store_assistant_response(conversation_id: int, content: str, tool_calls: list | None) -> Message` that creates a Message with role="assistant", content, and optional tool_calls metadata.

- **FR-005**: System MUST return messages from `fetch_history` as dictionaries with at minimum: role (str), content (str), and created_at (ISO datetime string).

- **FR-006**: System MUST enforce user isolation in `get_or_create_conversation` by validating that the conversation_id belongs to the requesting user_id before returning it.

- **FR-007**: System MUST use async database operations (async/await pattern) for all persistence functions.

- **FR-008**: System MUST handle the case where conversation_id is provided but doesn't exist by creating a new conversation (graceful degradation).

- **FR-009**: System MUST store tool_calls as JSON-serializable data in the Message metadata field when provided to `store_assistant_response`.

- **FR-010**: System MUST order messages returned by `fetch_history` by created_at ascending (chronological order) within the limit window.

- **FR-011**: System MUST apply the limit to `fetch_history` by selecting the N most recent messages, then returning them in chronological order.

- **FR-012**: System MUST accept a user_id parameter in functions that need ownership context (get_or_create_conversation requires user_id; store functions use the conversation's implicit user context).

### Key Entities

- **Conversation**: Represents a chat session. Key attributes: id, user_id, created_at, updated_at. Parent entity for Messages.

- **Message**: Represents a single message in a conversation. Key attributes: id, conversation_id, role (user/assistant), content, tool_calls (optional JSON), created_at. Child entity of Conversation.

- **Function Return Types**:
  - `get_or_create_conversation` returns a Conversation model instance
  - `fetch_history` returns a list of dictionaries (Gemini-compatible format)
  - `store_user_message` and `store_assistant_response` return Message model instances

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All four persistence functions can be called from the chat endpoint without blocking or errors under normal conditions.

- **SC-002**: Conversation creation and retrieval completes within reasonable time for serverless database operations.

- **SC-003**: Fetching 30 messages from a conversation with 100+ messages returns exactly 30 messages in correct chronological order.

- **SC-004**: Messages stored via `store_user_message` and `store_assistant_response` are retrievable via `fetch_history` with correct role attribution.

- **SC-005**: User A cannot access User B's conversations through any of the persistence functions (100% isolation).

- **SC-006**: Server restart does not lose any previously stored conversations or messages (stateless architecture verified).

- **SC-007**: Tool calls stored with assistant responses are retrievable and parseable as JSON from the message metadata.

- **SC-008**: Empty conversation (no messages) returns empty list from `fetch_history` without errors.

## Function Signatures Reference

This section provides the expected function signatures for implementation reference.

### get_or_create_conversation

```python
async def get_or_create_conversation(
    user_id: str,
    conversation_id: int | None
) -> Conversation:
    """
    Get an existing conversation or create a new one.

    Args:
        user_id: The authenticated user's ID
        conversation_id: Optional existing conversation ID

    Returns:
        Conversation model instance (existing or newly created)

    Behavior:
        - If conversation_id is None: create new conversation for user_id
        - If conversation_id exists and belongs to user_id: return it
        - If conversation_id exists but belongs to different user: create new
        - If conversation_id doesn't exist: create new
    """
```

### fetch_history

```python
async def fetch_history(
    conversation_id: int,
    limit: int = 30
) -> list[dict]:
    """
    Fetch recent message history for a conversation.

    Args:
        conversation_id: The conversation to fetch messages from
        limit: Maximum number of messages to return (default 30)

    Returns:
        List of message dictionaries with keys: role, content, created_at
        Messages are ordered chronologically (oldest first within limit)

    Behavior:
        - Select the N most recent messages by created_at
        - Return them in chronological order (ascending created_at)
        - Return empty list if conversation has no messages
        - Return empty list if conversation_id doesn't exist
    """
```

### store_user_message

```python
async def store_user_message(
    conversation_id: int,
    content: str
) -> Message:
    """
    Store a user message in the conversation.

    Args:
        conversation_id: The conversation to add the message to
        content: The user's message content

    Returns:
        The created Message model instance

    Behavior:
        - Create Message with role="user"
        - Set created_at to current timestamp
        - Associate with conversation_id
    """
```

### store_assistant_response

```python
async def store_assistant_response(
    conversation_id: int,
    content: str,
    tool_calls: list | None
) -> Message:
    """
    Store an assistant response in the conversation.

    Args:
        conversation_id: The conversation to add the response to
        content: The assistant's response text
        tool_calls: Optional list of tool calls made (JSON-serializable)

    Returns:
        The created Message model instance

    Behavior:
        - Create Message with role="assistant"
        - Set created_at to current timestamp
        - Store tool_calls as JSON metadata if provided
        - Associate with conversation_id
    """
```

## Database Schema Dependencies

This spec depends on the database models defined in `003-db-models-schema`:

- **Conversation** model with: id, user_id, created_at, updated_at, messages relationship
- **Message** model with: id, conversation_id, role (MessageRole enum), content, created_at
- **MessageRole** enum with values: "user", "assistant"

The Message model may need a `tool_calls` field (JSON/JSONB) to store tool call metadata. If not present in current schema, this requires a schema update.

## Assumptions

- Database session management is handled at the endpoint level (functions receive session or use context)
- The Conversation and Message models from spec 003 are available and implemented
- Async database driver (asyncpg) is configured for Neon PostgreSQL
- user_id validation happens at the API layer before calling these functions
- Tool calls are passed as Python lists/dicts that are JSON-serializable

## Dependencies

- SQLModel ORM (from spec 003)
- Conversation model (from spec 003)
- Message model (from spec 003)
- MessageRole enum (from spec 003)
- Async database session management
- Neon PostgreSQL (serverless)

## Non-Goals

- Authentication/authorization (handled by Better Auth at API layer)
- Rate limiting (handled at API layer)
- Message content validation beyond basic type checking
- Conversation summarization (future enhancement, out of scope)
- Message search/filtering beyond chronological retrieval
- Real-time message streaming (not required for this spec)
