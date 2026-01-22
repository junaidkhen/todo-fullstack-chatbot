# Research: FastAPI Backend Structure & Chat Endpoint (Chunk 4)

**Feature**: 005-fastapi-chat-endpoint
**Date**: 2026-01-17
**Status**: Complete

## Overview

This document captures research findings for implementing the FastAPI chat endpoint. All NEEDS CLARIFICATION items from the plan have been resolved.

---

## Research Topic 1: google-generativeai SDK Compatibility

### Question
Is `google-generativeai` compatible with Python 3.12 and the existing project dependencies?

### Findings

1. **Package**: `google-generativeai>=0.8.0` supports Python 3.9+
2. **Async Support**: Uses `generate_content_async()` for non-blocking calls
3. **Function Calling**: Native support via `Tool` and `FunctionDeclaration` classes
4. **Compatibility**: No conflicts with FastAPI, SQLModel, or existing deps

### Decision
Install `google-generativeai>=0.8.0` via pip

### Rationale
Latest stable version with full function calling and async support. Well-maintained by Google.

### Alternatives Considered
- **Direct REST API**: More boilerplate, no SDK type hints, manual auth handling
- **langchain-google-genai**: Adds unnecessary abstraction layer for our use case

---

## Research Topic 2: FastAPI Path Parameter User Validation

### Question
Best practice for validating user_id in the URL path?

### Findings

1. **Dependency Injection**: FastAPI supports dependencies at router level
2. **Pattern**: Create `get_validated_user(user_id: str, session: AsyncSession)` dependency
3. **Error Handling**: Raise HTTPException with appropriate status codes

### Decision
Use a dependency function that validates user exists in database

### Implementation Pattern

```python
from fastapi import Depends, HTTPException, Path

async def get_validated_user(
    user_id: str = Path(..., description="User ID from auth"),
    session: AsyncSession = Depends(get_session)
) -> str:
    """Validate user_id exists and return it."""
    from src.models.task import User
    from sqlmodel import select

    result = await session.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=401,
            detail={"error": "unauthorized", "message": "User not found"}
        )
    return user_id
```

### Rationale
- Clean separation of concerns
- Reusable across all endpoints needing user validation
- Consistent error responses

### Alternatives Considered
- **Middleware**: Less granular, validates all routes
- **In-endpoint validation**: Code duplication

---

## Research Topic 3: Conversation Persistence Patterns

### Question
How to handle async message persistence with SQLModel?

### Findings

1. **Session Pattern**: Use `async with AsyncSession` for transaction boundaries
2. **Commit Strategy**: Commit user message before Gemini call, commit assistant after
3. **Rollback**: On error, messages are committed but conversation is consistent

### Decision
Persist each message with explicit commit after creation

### Implementation Pattern

```python
async def add_message(
    conversation_id: int,
    user_id: str,
    role: MessageRole,
    content: str,
    session: AsyncSession
) -> Message:
    """Add a message to conversation."""
    message = Message(
        conversation_id=conversation_id,
        user_id=user_id,
        role=role,
        content=content
    )
    session.add(message)
    await session.commit()
    await session.refresh(message)

    # Update conversation updated_at
    from sqlmodel import select
    from src.models.conversation import Conversation

    result = await session.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conversation = result.scalar_one()
    conversation.updated_at = datetime.utcnow()
    session.add(conversation)
    await session.commit()

    return message
```

### Rationale
- Ensures durability: if Gemini call fails, user message is still saved
- Conversation updated_at tracks activity
- Simple recovery pattern

### Alternatives Considered
- **Single transaction**: Long-running, risk of lock contention
- **Background task**: Complicates error handling, may lose messages

---

## Research Topic 4: Error Handling for Gemini API

### Question
How to handle Gemini API errors gracefully?

### Findings

1. **Rate Limit**: `google.api_core.exceptions.ResourceExhausted`
2. **Server Error**: `google.api_core.exceptions.ServiceUnavailable`
3. **Auth Error**: `google.api_core.exceptions.PermissionDenied`
4. **FastAPI Handlers**: Use `@app.exception_handler()` decorator

### Decision
Create custom exception handlers in main.py

### Implementation Pattern

```python
from fastapi import Request
from fastapi.responses import JSONResponse
from google.api_core.exceptions import ResourceExhausted, ServiceUnavailable

@app.exception_handler(ResourceExhausted)
async def gemini_rate_limit_handler(request: Request, exc: ResourceExhausted):
    return JSONResponse(
        status_code=429,
        content={
            "error": "rate_limited",
            "message": "I'm a bit busy right now. Please try again in a moment!"
        }
    )

@app.exception_handler(ServiceUnavailable)
async def gemini_unavailable_handler(request: Request, exc: ServiceUnavailable):
    return JSONResponse(
        status_code=503,
        content={
            "error": "service_unavailable",
            "message": "I'm having trouble connecting. Please try again shortly."
        }
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    # Log the actual error for debugging
    import logging
    logging.exception("Unhandled exception")

    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_error",
            "message": "Something went wrong on my end. Please try again."
        }
    )
```

### Rationale
- User-friendly messages (Phase III constitution principle IV)
- No stack traces exposed
- Consistent error response format

### Alternatives Considered
- **Try/catch in endpoint**: Duplicates error handling logic
- **Middleware**: Less control over response format

---

## Research Topic 5: CORS Configuration

### Question
How to configure CORS for the chat endpoint?

### Findings

1. **Existing Setup**: `main.py` already has CORS middleware
2. **Hardcoded Origin**: Currently `http://localhost:3000`
3. **Need**: Make configurable via environment variable

### Decision
Move origin to environment variable

### Implementation

```python
# src/config.py
import os

FRONTEND_ORIGIN = os.environ.get("FRONTEND_ORIGIN", "http://localhost:3000")

# main.py
from src.config import FRONTEND_ORIGIN

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Rationale
- Production flexibility
- No code changes for deployment

---

## Research Topic 6: Conversation ID Handling

### Question
How to handle invalid or missing conversation_id?

### Findings

1. **Spec Requirement**: Create new conversation if not provided or invalid
2. **Ownership Check**: Must verify conversation belongs to user
3. **Edge Case**: ID provided but doesn't exist → create new

### Decision
Use get_or_create pattern with ownership validation

### Implementation Pattern

```python
async def get_or_create_conversation(
    user_id: str,
    conversation_id: Optional[int],
    session: AsyncSession
) -> Conversation:
    """Get existing conversation or create new one."""
    if conversation_id:
        from sqlmodel import select
        result = await session.execute(
            select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id  # Ownership check
            )
        )
        conversation = result.scalar_one_or_none()

        if conversation:
            return conversation
        # If not found or wrong user, fall through to create

    # Create new conversation
    conversation = Conversation(user_id=user_id)
    session.add(conversation)
    await session.commit()
    await session.refresh(conversation)
    return conversation
```

### Rationale
- Graceful handling of invalid IDs
- Implicit ownership enforcement
- New users automatically get a conversation

---

## Research Topic 7: Request/Response Validation

### Question
Best Pydantic validation patterns for chat schemas?

### Findings

1. **Field Validators**: Use `Field(min_length=1, max_length=10000)`
2. **Optional Fields**: `Optional[int] = None` for conversation_id
3. **Nested Models**: ToolCall as separate model embedded in ChatResponse

### Decision
Use Pydantic v2 patterns with explicit validators

### Implementation

```python
from pydantic import BaseModel, Field
from typing import Optional

class ChatRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="User's natural language message"
    )
    conversation_id: Optional[int] = Field(
        default=None,
        ge=1,
        description="ID of existing conversation to continue"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "Add a task to buy groceries",
                "conversation_id": None
            }
        }
    }
```

### Rationale
- Clear validation rules matching spec
- Good OpenAPI documentation
- Pydantic v2 compatibility

---

## Summary of Decisions

| Topic | Decision | Key Rationale |
|-------|----------|---------------|
| SDK | google-generativeai>=0.8.0 | Async + function calling support |
| User Validation | Dependency injection | Clean, reusable |
| Message Persistence | Per-message commit | Durability |
| Error Handling | Exception handlers | Consistent UX |
| CORS | Environment variable | Production flexibility |
| Conversation ID | Get-or-create pattern | Graceful handling |
| Validation | Pydantic v2 patterns | Type safety + docs |

---

## Dependencies to Add

```text
# requirements.txt additions
google-generativeai>=0.8.0
google-api-core>=2.0.0  # For exception types
```

---

## Next Steps

1. Proceed with data-model.md for API schemas
2. Generate OpenAPI contract in contracts/
3. Implement following the plan sequence
