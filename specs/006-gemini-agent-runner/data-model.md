# Data Model: Gemini Agent Integration & Runner

**Feature**: 006-gemini-agent-runner | **Date**: 2026-01-17

## Overview

This document defines the data structures used by the Gemini agent module. These are runtime structures, not database models - they represent the agent's input/output contracts and internal state tracking.

## Entities

### 1. ToolCallRecord

Tracks a single tool invocation during agent processing.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | str | Yes | Name of the tool executed (e.g., "add_task") |
| arguments | dict[str, Any] | Yes | Arguments passed to the tool (includes injected user_id) |
| result | dict[str, Any] | Yes | JSON result returned by the tool execution |

**Python Definition**:
```python
from dataclasses import dataclass
from typing import Any

@dataclass
class ToolCallRecord:
    name: str
    arguments: dict[str, Any]
    result: dict[str, Any]
```

**Example Instance**:
```python
ToolCallRecord(
    name="add_task",
    arguments={"user_id": "user-123", "title": "Buy groceries"},
    result={"status": "created", "task_id": 5, "title": "Buy groceries"}
)
```

### 2. AgentResponse

The final output of the agent runner, returned to the chat endpoint.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| text | str | Yes | Natural language response from Gemini |
| tool_calls | list[ToolCallRecord] | Yes | All tools executed during this request (may be empty) |
| conversation_id | int \| None | No | Optional conversation ID for persistence tracking |

**Python Definition**:
```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class AgentResponse:
    text: str
    tool_calls: list[ToolCallRecord]
    conversation_id: Optional[int] = None
```

**Example Instance (No Tools)**:
```python
AgentResponse(
    text="Hello! I'm TaskBot, your friendly todo manager. How can I help you today?",
    tool_calls=[],
    conversation_id=42
)
```

**Example Instance (With Tools)**:
```python
AgentResponse(
    text="Done! I've added 'Buy groceries' to your task list.",
    tool_calls=[
        ToolCallRecord(
            name="add_task",
            arguments={"user_id": "user-123", "title": "Buy groceries"},
            result={"status": "created", "task_id": 5, "title": "Buy groceries"}
        )
    ],
    conversation_id=42
)
```

### 3. ConversationMessage

Represents a single message in conversation history (input to agent).

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| role | Literal["user", "assistant"] | Yes | Message author role |
| content | str | Yes | Message text content |

**Python Definition**:
```python
from typing import Literal, TypedDict

class ConversationMessage(TypedDict):
    role: Literal["user", "assistant"]
    content: str
```

**Example**:
```python
[
    {"role": "user", "content": "Add a task to buy milk"},
    {"role": "assistant", "content": "Done! I've added 'Buy milk' to your list."},
    {"role": "user", "content": "Show my tasks"}
]
```

### 4. AgentConfig

Configuration for agent initialization (derived from environment).

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| api_key | str | Yes | - | GEMINI_API_KEY from environment |
| model | str | No | "gemini-1.5-flash" | GEMINI_MODEL from environment |
| max_iterations | int | No | 5 | MAX_TOOL_ITERATIONS from environment |
| max_history_messages | int | No | 20 | MAX_HISTORY_MESSAGES from environment |
| max_tokens | int | No | 90000 | Token budget for context (10k buffer below 100k) |

**Python Definition**:
```python
from dataclasses import dataclass, field

@dataclass
class AgentConfig:
    api_key: str
    model: str = "gemini-1.5-flash"
    max_iterations: int = 5
    max_history_messages: int = 20
    max_tokens: int = 90000

    @classmethod
    def from_env(cls) -> "AgentConfig":
        """Load configuration from environment variables."""
        import os
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        return cls(
            api_key=api_key,
            model=os.environ.get("GEMINI_MODEL", "gemini-1.5-flash"),
            max_iterations=int(os.environ.get("MAX_TOOL_ITERATIONS", "5")),
            max_history_messages=int(os.environ.get("MAX_HISTORY_MESSAGES", "20"))
        )
```

## Relationships

```
┌──────────────────────┐
│    Chat Endpoint     │
│  (API Layer - Chunk 4)│
└──────────┬───────────┘
           │ Calls
           ▼
┌──────────────────────┐
│   run_gemini_agent   │
│   (Agent Runner)     │
│                      │
│ Input:               │
│ - user_id: str       │
│ - history: list[     │
│     ConversationMsg] │
│ - new_message: str   │
│ - db_session         │
│                      │
│ Output:              │
│ - AgentResponse      │
└──────────┬───────────┘
           │ Uses
           ▼
┌──────────────────────┐
│    Tool Handlers     │
│  (From Chunk 3/4)    │
│                      │
│ Returns:             │
│ - dict (JSON result) │
└──────────────────────┘
```

## Validation Rules

### ToolCallRecord
- `name` must be one of: "add_task", "list_tasks", "complete_task", "delete_task", "update_task"
- `arguments` must always contain "user_id" key
- `result` must contain "status" key

### AgentResponse
- `text` must not be empty (even error cases have a message)
- `tool_calls` can be empty list (for conversational responses)
- `conversation_id` is set when conversation persistence is enabled

### ConversationMessage
- `role` must be exactly "user" or "assistant" (not "model")
- `content` must be non-empty string

### AgentConfig
- `api_key` is required and non-empty
- `model` should be "gemini-1.5-flash" or "gemini-2.5-flash"
- `max_iterations` must be positive integer (1-10 range recommended)
- `max_history_messages` must be positive integer (10-50 range recommended)

## State Transitions

The agent is stateless per-request, but tool execution follows a state machine:

```
┌─────────────┐
│   START     │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│                    TOOL EXECUTION LOOP                       │
│                                                              │
│  ┌─────────────┐    ┌──────────────┐    ┌───────────────┐   │
│  │ Call Gemini │───►│ Has Function │───►│ Execute Tools │   │
│  └─────────────┘    │   Calls?     │Yes └───────┬───────┘   │
│        ▲            └──────┬───────┘            │           │
│        │                   │No                  │           │
│        │                   ▼                    │           │
│        │            ┌─────────────┐             │           │
│        │            │ Return Text │             │           │
│        │            │  Response   │             │           │
│        │            └─────────────┘             │           │
│        │                                        │           │
│        └──────────────Feed Back─────────────────┘           │
│                                                              │
│  (Max 5 iterations, then force exit with pause message)     │
└─────────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────┐
│    END      │
│ AgentResponse│
└─────────────┘
```

## Serialization

### AgentResponse to JSON (for API response)

```python
def agent_response_to_dict(response: AgentResponse) -> dict:
    return {
        "text": response.text,
        "tool_calls": [
            {
                "name": tc.name,
                "arguments": tc.arguments,
                "result": tc.result
            }
            for tc in response.tool_calls
        ],
        "conversation_id": response.conversation_id
    }
```

### ConversationMessage from JSON (from API request or DB)

```python
def parse_history(history_json: list[dict]) -> list[ConversationMessage]:
    return [
        {"role": msg["role"], "content": msg["content"]}
        for msg in history_json
    ]
```
