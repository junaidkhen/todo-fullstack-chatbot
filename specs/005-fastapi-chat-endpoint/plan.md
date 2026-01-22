# Implementation Plan: FastAPI Backend Structure & Chat Endpoint (Chunk 4)

**Branch**: `005-fastapi-chat-endpoint` | **Date**: 2026-01-17 | **Spec**: [specs/005-fastapi-chat-endpoint/spec.md](./spec.md)
**Input**: Feature specification for "Chunk 4: FastAPI Backend Structure & Chat Endpoint"

## Summary

Implement a single stateless chat endpoint (`POST /api/{user_id}/chat`) that receives user messages, orchestrates AI processing via the Gemini agent (Chunk 5), executes tool calls (Chunk 3/4), persists conversation history, and returns natural language responses with transparency on executed tools. The architecture follows Phase III constitution's stateless design with all context persisted in the database.

## Technical Context

**Language/Version**: Python 3.12
**Primary Dependencies**: FastAPI 0.115.0, SQLModel 0.0.22, Pydantic 2.9.2, google-generativeai (to add)
**Storage**: Neon PostgreSQL / SQLite (dev), using existing async engine from `backend/src/database.py`
**Testing**: pytest + pytest-asyncio (existing)
**Target Platform**: Linux server / Docker
**Project Type**: Web application (backend only for this chunk)
**Performance Goals**: <3 seconds response (excluding Gemini API latency)
**Constraints**: Gemini free tier (5-15 RPM), stateless backend, user isolation
**Scale/Scope**: Single endpoint, multi-user via user_id path parameter

## Constitution Check

*GATE: Pass - Phase III constitution verified*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Spec-Driven Development | ✅ Pass | Following spec.md → plan.md → tasks.md workflow |
| II. Stateless Backend Architecture | ✅ Pass | No in-memory state; all from DB |
| III. Gemini API Free Tier Compliance | ✅ Pass | Using gemini-1.5-flash, rate-aware design |
| IV. Friendly Conversational Interface | ✅ Pass | Delegated to Chunk 6/7 (Agent Behavior) |
| V. Security Through User Isolation | ✅ Pass | user_id in path, ownership validation on all ops |
| VI. Type Safety and Validation | ✅ Pass | Pydantic schemas, Python type hints |
| VII. Persistent Storage | ✅ Pass | Conversations table from Chunk 2 |

## Project Structure

### Documentation (this feature)

```text
specs/005-fastapi-chat-endpoint/
├── spec.md              # Feature specification (exists)
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── chat-api.yaml    # OpenAPI spec for chat endpoint
└── tasks.md             # Phase 2 output (/sp.tasks)
```

### Source Code (repository root)

```text
backend/
├── main.py                  # Application entry point (modify: add chat router)
├── src/
│   ├── __init__.py
│   ├── database.py          # Async engine + session (exists)
│   ├── models/
│   │   ├── task.py          # Task, User models (exists)
│   │   └── conversation.py  # Conversation, Message models (NEW - from Chunk 2)
│   ├── api/
│   │   ├── tasks.py         # REST CRUD endpoints (exists)
│   │   ├── health.py        # Health check (exists)
│   │   ├── auth.py          # Auth endpoints (exists)
│   │   └── chat.py          # Chat endpoint (NEW)
│   ├── schemas/
│   │   └── chat.py          # ChatRequest, ChatResponse, ToolCall (NEW)
│   ├── services/
│   │   ├── agent.py         # Gemini agent runner (Chunk 5 - stub for now)
│   │   └── conversation.py  # Conversation CRUD operations (NEW)
│   ├── tools/
│   │   └── task_tools.py    # 5 task tools + declarations (Chunk 3 - stub for now)
│   ├── dependencies.py      # User validation dependency (NEW)
│   └── config.py            # Environment configuration (NEW)
└── tests/
    ├── unit/
    │   └── test_chat_schemas.py     # (NEW)
    └── integration/
        └── test_chat_endpoint.py    # (NEW)
```

**Structure Decision**: Web application pattern. Backend extensions add new modules under `src/` following existing layout. No changes to frontend in this chunk.

## Complexity Tracking

No constitution violations requiring justification.

---

## Phase 0: Research

### Research Tasks

1. **google-generativeai SDK installation**: Verify package compatibility with Python 3.12 and existing requirements
2. **FastAPI path parameter validation**: Best practices for user_id validation in path
3. **Conversation persistence patterns**: Async SQLModel patterns for message insertion/retrieval
4. **Error handling middleware**: FastAPI exception handlers for Gemini API errors

### Research Findings

*(Detailed in `research.md`)*

**Decision 1**: Use `google-generativeai>=0.8.0` (latest stable with function calling support)
**Rationale**: Supports async, function calling, Gemini 1.5/2.5 models
**Alternatives**: Direct REST API calls (rejected: more boilerplate, no SDK benefits)

**Decision 2**: Use path parameter dependency for user_id validation
**Rationale**: FastAPI dependency injection allows clean separation of auth validation
**Alternatives**: Middleware (rejected: less granular control per endpoint)

**Decision 3**: Async session with explicit commit per message
**Rationale**: Ensures message persistence before Gemini call, enabling recovery
**Alternatives**: Transaction wrapping entire flow (rejected: long transaction risk)

---

## Phase 1: Design & Contracts

### Key Entities (API Layer)

| Entity | Purpose | Module |
|--------|---------|--------|
| ChatRequest | Incoming request body | src/schemas/chat.py |
| ChatResponse | Outgoing response | src/schemas/chat.py |
| ToolCall | Tool execution record | src/schemas/chat.py |
| ErrorResponse | Standardized error | src/schemas/chat.py |

### Dependencies (New)

| Dependency | Module | Purpose |
|------------|--------|---------|
| get_validated_user | src/dependencies.py | Validates user_id exists |
| get_session | src/database.py | Existing async session provider |

### API Contract Summary

**Endpoint**: `POST /api/{user_id}/chat`

**Request**:
```json
{
  "message": "string (required, 1-10000 chars)",
  "conversation_id": "integer or null (optional)"
}
```

**Response (200)**:
```json
{
  "conversation_id": "integer",
  "response": "string",
  "tool_calls": [
    {
      "name": "string",
      "arguments": {},
      "result": {}
    }
  ] // or null
}
```

**Error Responses**:
- 400: Invalid user_id or request body
- 401: User not found
- 403: Conversation belongs to different user
- 422: Validation error
- 429: Gemini rate limit
- 500: Internal error (user-friendly message)

### Processing Flow

```
1. Validate user_id (dependency)
2. Parse ChatRequest body
3. Resolve conversation (create if needed)
4. Store user message
5. Load conversation history (last 20 messages)
6. Call Gemini agent (Chunk 5 interface)
7. Agent returns: text + tool_calls
8. Store assistant message
9. Return ChatResponse
```

### Integration Points

| Component | Interface | Status |
|-----------|-----------|--------|
| Gemini Agent | `run_gemini_agent_safe(user_id, history, message, session)` | Chunk 5 (stub) |
| Tool Declarations | `TOOL_DECLARATIONS` | Chunk 3/4 (stub) |
| Conversation Models | `Conversation`, `Message` | Chunk 2 (exists) |
| User Validation | Check users table | Phase II (exists) |

---

## Implementation Sequence

### Step 1: Dependencies & Configuration

1. Add `google-generativeai` to requirements.txt
2. Create `src/config.py` with environment variables:
   - GEMINI_API_KEY
   - GEMINI_MODEL (default: gemini-1.5-flash)
   - FRONTEND_ORIGIN (for CORS)
   - MAX_TOOL_ITERATIONS (default: 5)
   - HISTORY_MESSAGE_LIMIT (default: 20)

### Step 2: Models (if not from Chunk 2)

1. Verify `Conversation` and `Message` models exist in `src/models/`
2. Add to database init imports

### Step 3: Schemas

1. Create `src/schemas/chat.py`:
   - ChatRequest (Pydantic BaseModel)
   - ChatResponse
   - ToolCall
   - ErrorResponse

### Step 4: Dependencies

1. Create `src/dependencies.py`:
   - `get_validated_user(user_id: str, session: AsyncSession)` → str or HTTPException

### Step 5: Conversation Service

1. Create `src/services/conversation.py`:
   - `get_or_create_conversation(user_id, conversation_id, session)` → Conversation
   - `add_message(conversation_id, user_id, role, content, session)` → Message
   - `get_conversation_history(conversation_id, limit, session)` → List[dict]

### Step 6: Chat Router

1. Create `src/api/chat.py`:
   - `POST /chat` endpoint
   - Calls agent (stub returns dummy response for now)
   - Handles all error cases

### Step 7: Main App Integration

1. Modify `main.py`:
   - Add CORS origin from config
   - Include chat router at `/api/{user_id}`

### Step 8: Error Handlers

1. Add exception handlers in `main.py`:
   - Gemini rate limit → 429
   - Generic errors → 500 with friendly message

### Step 9: Tests

1. Unit tests for schemas
2. Integration tests for endpoint with mocked agent

---

## Stub Interfaces (For Dependencies)

### Agent Stub (until Chunk 5)

```python
# src/services/agent.py (stub)
from dataclasses import dataclass
from typing import Optional

@dataclass
class ToolCallRecord:
    name: str
    arguments: dict
    result: dict

@dataclass
class AgentResponse:
    text: str
    tool_calls: list[ToolCallRecord]

async def run_gemini_agent_safe(
    user_id: str,
    history: list[dict],
    new_message: str,
    db_session
) -> AgentResponse:
    """Stub: Returns dummy response until Chunk 5 implementation."""
    return AgentResponse(
        text=f"Echo: {new_message}",
        tool_calls=[]
    )
```

### Tool Declarations Stub (until Chunk 3)

```python
# src/tools/task_tools.py (stub)
TOOL_DECLARATIONS = []  # Populated by Chunk 3/4

async def execute_tool(tool_name: str, args: dict, session) -> dict:
    """Stub: Returns error until Chunk 3/4 implementation."""
    return {"status": "error", "message": "Tools not implemented"}
```

---

## Success Criteria Verification

| Criterion | Verification Method |
|-----------|---------------------|
| SC-001: <3s response | Manual test with stub agent |
| SC-002: Error responses | Integration tests |
| SC-003: Message persistence | Integration tests |
| SC-004: Statelessness | Server restart test |
| SC-005: Auth blocking | Integration tests with invalid user |
| SC-006: CORS | Browser test or curl |
| SC-007: Tool transparency | Response schema validation |
| SC-008: No stack traces | Error handler tests |

---

## Risks & Mitigations

1. **Risk**: Chunk 2 models not implemented
   **Mitigation**: Create models in this chunk if missing

2. **Risk**: Agent stub insufficient for integration testing
   **Mitigation**: Stub returns predictable responses for test assertions

3. **Risk**: CORS issues with frontend
   **Mitigation**: Make origin configurable, test with actual frontend

---

## Next Steps

1. Run `/sp.tasks` to generate implementation tasks
2. Implement in sequence: config → models → schemas → dependencies → service → router
3. After Chunk 5 implementation, replace agent stub with real integration
