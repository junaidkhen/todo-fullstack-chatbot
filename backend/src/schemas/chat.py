"""Pydantic schemas for chat API endpoint.

Defines request and response models for the chat endpoint:
- ChatRequest: Incoming message with optional conversation_id
- ChatResponse: AI response with conversation_id and tool_calls
- ToolCall: Record of a tool invocation
- ErrorResponse: Standardized error format
"""

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
