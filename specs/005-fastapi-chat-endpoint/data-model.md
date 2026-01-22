# Data Model: FastAPI Chat Endpoint Schemas (Chunk 4)

**Feature**: 005-fastapi-chat-endpoint
**Date**: 2026-01-17
**Status**: Complete

## Overview

This document defines the Pydantic schemas for the chat endpoint's request and response models. These are API-layer models, separate from the database models (defined in Chunk 2).

---

## Schema Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        API Layer Schemas                         │
└─────────────────────────────────────────────────────────────────┘

Request Flow:
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  ChatRequest    │────►│  Processing     │────►│  ChatResponse   │
│                 │     │                 │     │                 │
│ - message       │     │ - Validate user │     │ - conversation_id│
│ - conversation_id│    │ - Store message │     │ - response      │
└─────────────────┘     │ - Call agent    │     │ - tool_calls    │
                        │ - Store response│     └────────┬────────┘
                        └─────────────────┘              │
                                                         │
                                            ┌────────────▼────────────┐
                                            │      ToolCall           │
                                            │ - name                  │
                                            │ - arguments             │
                                            │ - result                │
                                            └─────────────────────────┘

Error Flow:
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Invalid Request│────►│  Validation     │────►│  ErrorResponse  │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     │ - error         │
                                                │ - message       │
                                                │ - details       │
                                                └─────────────────┘
```

---

## Schema: ChatRequest

**Purpose**: Incoming request body for chat endpoint
**Location**: `backend/src/schemas/chat.py`

### Fields

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| message | string | Yes | min_length=1, max_length=10000 | User's natural language message |
| conversation_id | integer/null | No | ge=1 if provided | ID of existing conversation |

### Validation Rules

1. **message**: Must not be empty or whitespace-only
2. **message**: Maximum 10,000 characters
3. **conversation_id**: If provided, must be positive integer

### Pydantic Model

```python
from pydantic import BaseModel, Field, field_validator
from typing import Optional

class ChatRequest(BaseModel):
    """Request body for chat endpoint."""
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

    @field_validator('message')
    @classmethod
    def message_not_whitespace(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Message cannot be empty or whitespace')
        return v.strip()

    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "Add a task to buy groceries",
                "conversation_id": None
            }
        }
    }
```

---

## Schema: ToolCall

**Purpose**: Record of a single tool execution
**Location**: `backend/src/schemas/chat.py`

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | Yes | Tool function name (e.g., "add_task") |
| arguments | object | Yes | Arguments passed to the tool |
| result | object | Yes | Result returned from tool execution |

### Pydantic Model

```python
from pydantic import BaseModel
from typing import Any

class ToolCall(BaseModel):
    """Record of a tool invocation during chat processing."""
    name: str = Field(
        ...,
        description="Name of the tool executed"
    )
    arguments: dict[str, Any] = Field(
        ...,
        description="Arguments passed to the tool"
    )
    result: dict[str, Any] = Field(
        ...,
        description="Result returned from tool execution"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "add_task",
                "arguments": {"user_id": "user-123", "title": "Buy groceries"},
                "result": {"status": "created", "task_id": 5, "title": "Buy groceries"}
            }
        }
    }
```

---

## Schema: ChatResponse

**Purpose**: Response body for successful chat processing
**Location**: `backend/src/schemas/chat.py`

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| conversation_id | integer | Yes | ID of the conversation (new or existing) |
| response | string | Yes | AI's natural language response |
| tool_calls | array/null | No | List of tools executed, or null if none |

### Pydantic Model

```python
from pydantic import BaseModel, Field
from typing import Optional

class ChatResponse(BaseModel):
    """Response body for chat endpoint."""
    conversation_id: int = Field(
        ...,
        description="ID of the conversation (new or existing)"
    )
    response: str = Field(
        ...,
        description="AI's natural language response"
    )
    tool_calls: Optional[list[ToolCall]] = Field(
        default=None,
        description="List of tools executed during processing"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "conversation_id": 42,
                "response": "Done! I've added 'Buy groceries' to your task list.",
                "tool_calls": [
                    {
                        "name": "add_task",
                        "arguments": {"user_id": "user-123", "title": "Buy groceries"},
                        "result": {"status": "created", "task_id": 5, "title": "Buy groceries"}
                    }
                ]
            }
        }
    }
```

---

## Schema: ErrorResponse

**Purpose**: Standardized error response format
**Location**: `backend/src/schemas/chat.py`

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| error | string | Yes | Error type/code |
| message | string | Yes | Human-readable error description |
| details | object/null | No | Optional additional context |

### Pydantic Model

```python
from pydantic import BaseModel, Field
from typing import Optional, Any

class ErrorResponse(BaseModel):
    """Standardized error response."""
    error: str = Field(
        ...,
        description="Error type/code"
    )
    message: str = Field(
        ...,
        description="Human-readable error description"
    )
    details: Optional[dict[str, Any]] = Field(
        default=None,
        description="Optional additional error context"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "error": "validation_error",
                "message": "Message cannot be empty",
                "details": {"field": "message"}
            }
        }
    }
```

---

## Error Response Mapping

| HTTP Status | Error Code | Message Template | When Used |
|-------------|------------|------------------|-----------|
| 400 | bad_request | "Invalid request: {details}" | Malformed request |
| 400 | validation_error | "{field validation message}" | Pydantic validation failure |
| 401 | unauthorized | "User not found" | user_id doesn't exist |
| 403 | forbidden | "Access denied to this resource" | Wrong user's conversation |
| 422 | unprocessable_entity | "Request body validation failed" | FastAPI validation |
| 429 | rate_limited | "I'm a bit busy right now..." | Gemini rate limit |
| 500 | internal_error | "Something went wrong..." | Unhandled exceptions |
| 503 | service_unavailable | "I'm having trouble connecting..." | Gemini unavailable |

---

## Internal Types (Not API Exposed)

### HistoryMessage

**Purpose**: Format for conversation history passed to Gemini
**Location**: `backend/src/services/conversation.py`

```python
from typing import TypedDict, Literal

class HistoryMessage(TypedDict):
    """Message format for agent history context."""
    role: Literal["user", "assistant"]
    content: str
```

### AgentResponse

**Purpose**: Return type from Gemini agent runner
**Location**: `backend/src/services/agent.py`

```python
from dataclasses import dataclass

@dataclass
class ToolCallRecord:
    """Internal record of tool execution."""
    name: str
    arguments: dict
    result: dict

@dataclass
class AgentResponse:
    """Response from Gemini agent runner."""
    text: str
    tool_calls: list[ToolCallRecord]
```

---

## Conversion Functions

### ToolCallRecord to ToolCall

```python
def tool_record_to_schema(record: ToolCallRecord) -> ToolCall:
    """Convert internal record to API schema."""
    return ToolCall(
        name=record.name,
        arguments=record.arguments,
        result=record.result
    )
```

### AgentResponse to ChatResponse

```python
def agent_to_chat_response(
    conversation_id: int,
    agent_response: AgentResponse
) -> ChatResponse:
    """Convert agent response to API response."""
    tool_calls = None
    if agent_response.tool_calls:
        tool_calls = [
            tool_record_to_schema(tc)
            for tc in agent_response.tool_calls
        ]

    return ChatResponse(
        conversation_id=conversation_id,
        response=agent_response.text,
        tool_calls=tool_calls
    )
```

---

## Schema Module Structure

```python
# backend/src/schemas/chat.py

from pydantic import BaseModel, Field, field_validator
from typing import Optional, Any

__all__ = [
    "ChatRequest",
    "ChatResponse",
    "ToolCall",
    "ErrorResponse",
]

class ToolCall(BaseModel):
    """Record of a tool invocation during chat processing."""
    ...

class ChatRequest(BaseModel):
    """Request body for chat endpoint."""
    ...

class ChatResponse(BaseModel):
    """Response body for chat endpoint."""
    ...

class ErrorResponse(BaseModel):
    """Standardized error response."""
    ...
```

---

## Validation Test Cases

### ChatRequest Validation

| Input | Expected | Reason |
|-------|----------|--------|
| `{"message": "Hello"}` | Valid | Basic valid request |
| `{"message": "Hello", "conversation_id": 5}` | Valid | With conversation |
| `{"message": ""}` | Invalid | Empty message |
| `{"message": "   "}` | Invalid | Whitespace only |
| `{"message": "x" * 10001}` | Invalid | Exceeds max length |
| `{"conversation_id": 5}` | Invalid | Missing message |
| `{"message": "Hi", "conversation_id": 0}` | Invalid | Invalid ID (< 1) |
| `{"message": "Hi", "conversation_id": -1}` | Invalid | Negative ID |

### ChatResponse Validation

| Input | Expected | Reason |
|-------|----------|--------|
| `{"conversation_id": 1, "response": "Done!"}` | Valid | No tool calls |
| `{"conversation_id": 1, "response": "Done!", "tool_calls": []}` | Valid | Empty tool calls |
| `{"conversation_id": 1, "response": "Done!", "tool_calls": null}` | Valid | Null tool calls |
| Full response with tool_calls | Valid | Complete response |

---

## Appendix: Complete Module Code

```python
# backend/src/schemas/chat.py
"""Pydantic schemas for chat API endpoint."""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, Any

__all__ = [
    "ChatRequest",
    "ChatResponse",
    "ToolCall",
    "ErrorResponse",
]


class ToolCall(BaseModel):
    """Record of a tool invocation during chat processing."""

    name: str = Field(..., description="Name of the tool executed")
    arguments: dict[str, Any] = Field(
        ..., description="Arguments passed to the tool"
    )
    result: dict[str, Any] = Field(
        ..., description="Result returned from tool execution"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "add_task",
                "arguments": {"user_id": "user-123", "title": "Buy groceries"},
                "result": {
                    "status": "created",
                    "task_id": 5,
                    "title": "Buy groceries",
                },
            }
        }
    }


class ChatRequest(BaseModel):
    """Request body for chat endpoint."""

    message: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="User's natural language message",
    )
    conversation_id: Optional[int] = Field(
        default=None, ge=1, description="ID of existing conversation to continue"
    )

    @field_validator("message")
    @classmethod
    def message_not_whitespace(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Message cannot be empty or whitespace")
        return v.strip()

    model_config = {
        "json_schema_extra": {
            "example": {"message": "Add a task to buy groceries", "conversation_id": None}
        }
    }


class ChatResponse(BaseModel):
    """Response body for chat endpoint."""

    conversation_id: int = Field(
        ..., description="ID of the conversation (new or existing)"
    )
    response: str = Field(..., description="AI's natural language response")
    tool_calls: Optional[list[ToolCall]] = Field(
        default=None, description="List of tools executed during processing"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "conversation_id": 42,
                "response": "Done! I've added 'Buy groceries' to your task list.",
                "tool_calls": [
                    {
                        "name": "add_task",
                        "arguments": {"user_id": "user-123", "title": "Buy groceries"},
                        "result": {
                            "status": "created",
                            "task_id": 5,
                            "title": "Buy groceries",
                        },
                    }
                ],
            }
        }
    }


class ErrorResponse(BaseModel):
    """Standardized error response."""

    error: str = Field(..., description="Error type/code")
    message: str = Field(..., description="Human-readable error description")
    details: Optional[dict[str, Any]] = Field(
        default=None, description="Optional additional error context"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "error": "validation_error",
                "message": "Message cannot be empty",
                "details": {"field": "message"},
            }
        }
    }
```
