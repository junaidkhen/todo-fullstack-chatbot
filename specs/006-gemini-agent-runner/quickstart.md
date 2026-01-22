# Quickstart: Gemini Agent Integration & Runner

**Feature**: 006-gemini-agent-runner | **Date**: 2026-01-17

## Overview

This guide provides step-by-step instructions for implementing the Gemini agent module. Follow these steps in order - each builds on the previous.

## Prerequisites

- [ ] Python 3.11+ installed
- [ ] `google-genai` package installed (`pip install google-genai`)
- [ ] `GEMINI_API_KEY` environment variable set
- [ ] Chunk 3/4 tool declarations implemented (or implement inline)
- [ ] Existing database.py with AsyncSession support

## Implementation Steps

### Step 1: Create Agent Module Structure

Create the new services directory and agent module:

```bash
mkdir -p backend/src/services
touch backend/src/services/__init__.py
touch backend/src/services/agent.py
```

### Step 2: Define Constants and Config

In `backend/src/services/agent.py`:

```python
"""
Gemini Agent Integration & Runner

Stateless agent that processes user messages through Gemini API
with function calling for task management operations.
"""

import os
import logging
from dataclasses import dataclass
from typing import Any, Optional

from google import genai
from google.genai import types
from google.api_core.exceptions import (
    ResourceExhausted,
    ServiceUnavailable,
    DeadlineExceeded
)

logger = logging.getLogger(__name__)

# System prompt establishing TaskBot persona
SYSTEM_PROMPT = """You are a helpful and friendly Todo manager assistant. Your name is TaskBot.

You help users manage their tasks through natural conversation. You can:
- Add new tasks
- List existing tasks (all, pending, or completed)
- Mark tasks as complete
- Delete tasks
- Update task titles or descriptions

Guidelines:
1. Always confirm actions after completing them (e.g., "Done! I've added 'Buy groceries' to your list.")
2. Be conversational and friendly. Mixed English/Urdu responses are welcome.
3. When a user refers to a task ambiguously (like "delete that one"), first list their tasks to clarify.
4. If something goes wrong, explain it simply (e.g., "Task nahi mila bhai" for not found).
5. Only use tools when the user wants to perform a task operation. For general chat, just respond naturally.
6. Keep responses concise but helpful.

The user_id will be provided automatically for all operations - you don't need to ask for it."""
```

### Step 3: Define Data Classes

Add to `backend/src/services/agent.py`:

```python
@dataclass
class ToolCallRecord:
    """Record of a tool invocation during agent processing."""
    name: str
    arguments: dict[str, Any]
    result: dict[str, Any]


@dataclass
class AgentResponse:
    """Response from the agent runner."""
    text: str
    tool_calls: list[ToolCallRecord]
    conversation_id: Optional[int] = None


@dataclass
class AgentConfig:
    """Agent configuration loaded from environment."""
    api_key: str
    model: str = "gemini-1.5-flash"
    max_iterations: int = 5
    max_history_messages: int = 20
    max_tokens: int = 90000

    @classmethod
    def from_env(cls) -> "AgentConfig":
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

### Step 4: Initialize Gemini Client

Add to `backend/src/services/agent.py`:

```python
# Module-level client (initialized on first use)
_client: Optional[genai.Client] = None
_config: Optional[AgentConfig] = None


def get_gemini_client() -> genai.Client:
    """Get or create the Gemini client singleton."""
    global _client, _config
    if _client is None:
        _config = AgentConfig.from_env()
        _client = genai.Client(api_key=_config.api_key)
        logger.info(f"Initialized Gemini client with model: {_config.model}")
    return _client


def get_config() -> AgentConfig:
    """Get the agent configuration."""
    global _config
    if _config is None:
        get_gemini_client()  # This initializes config
    return _config
```

### Step 5: Import Tool Declarations

Either import from Chunk 3/4 implementation or define inline:

```python
# Option A: Import from tools module (preferred)
from src.gemini.tools import get_task_tools, execute_tool

# Option B: Define inline (if tools not yet implemented)
def get_task_tools() -> types.Tool:
    """Return the tool declarations for task management."""
    # See specs/004-gemini-function-tools for full definitions
    function_declarations = [
        types.FunctionDeclaration(
            name="add_task",
            description="Create a new todo task for the user.",
            parameters_json_schema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string"},
                    "title": {"type": "string"},
                    "description": {"type": "string"}
                },
                "required": ["user_id", "title"]
            }
        ),
        # ... other declarations
    ]
    return types.Tool(function_declarations=function_declarations)
```

### Step 6: History Building Function

Add to `backend/src/services/agent.py`:

```python
def build_contents_from_history(
    history: list[dict],
    max_messages: int = 20
) -> list[types.Content]:
    """
    Convert conversation history to Gemini contents format.

    Args:
        history: List of {"role": "user"|"assistant", "content": "..."}
        max_messages: Maximum messages to include (oldest pruned)

    Returns:
        Gemini-compatible contents array
    """
    # Truncate to most recent messages
    recent = history[-max_messages:] if len(history) > max_messages else history

    contents = []
    for msg in recent:
        # Map assistant role to model role for Gemini
        role = "model" if msg["role"] == "assistant" else "user"
        contents.append(types.Content(
            role=role,
            parts=[types.Part(text=msg["content"])]
        ))

    return contents


def estimate_tokens(text: str) -> int:
    """Rough token estimation (4 chars per token average)."""
    return len(text) // 4
```

### Step 7: Main Agent Runner

Add to `backend/src/services/agent.py`:

```python
async def run_gemini_agent(
    user_id: str,
    history: list[dict],
    new_message: str,
    db_session  # AsyncSession
) -> AgentResponse:
    """
    Process a user message through the Gemini agent.

    Args:
        user_id: Authenticated user's ID for tool execution
        history: Previous conversation messages
        new_message: Current user message
        db_session: Database session for tool execution

    Returns:
        AgentResponse with final text and executed tool calls
    """
    client = get_gemini_client()
    config = get_config()

    # Validate input
    if not new_message.strip():
        return AgentResponse(
            text="I didn't catch that. Could you say something?",
            tool_calls=[]
        )

    logger.info(f"Agent request started user_id={user_id} message={new_message[:50]}...")

    # Build contents from history
    contents = build_contents_from_history(history, config.max_history_messages)
    contents.append(types.Content(
        role="user",
        parts=[types.Part(text=new_message)]
    ))

    # Prepare configuration
    gen_config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        tools=[get_task_tools()],
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
    )

    # Tool execution loop
    tool_calls_executed = []

    for iteration in range(config.max_iterations):
        logger.debug(f"Gemini call iteration={iteration}")

        # Call Gemini
        response = await client.aio.models.generate_content(
            model=config.model,
            contents=contents,
            config=gen_config
        )

        # Check for function calls
        if not response.function_calls:
            # No function calls - return final text
            final_text = response.text or "I'm not sure how to respond to that."
            logger.info(f"Response generated text_length={len(final_text)} tool_count={len(tool_calls_executed)}")
            return AgentResponse(
                text=final_text,
                tool_calls=tool_calls_executed
            )

        # Execute function calls
        function_parts = []
        for fc in response.function_calls:
            fn_name = fc.name
            fn_args = dict(fc.args)

            # Security: Inject user_id
            fn_args["user_id"] = user_id

            logger.info(f"Function call detected tool={fn_name} args={fn_args}")

            # Execute tool
            result = await execute_tool(fn_name, fn_args, db_session)

            logger.info(f"Tool execution result tool={fn_name} status={result.get('status')}")

            # Track execution
            tool_calls_executed.append(ToolCallRecord(
                name=fn_name,
                arguments=fn_args,
                result=result
            ))

            # Prepare function response
            function_parts.append(types.Part(
                function_response=types.FunctionResponse(
                    name=fn_name,
                    response=result
                )
            ))

        # Append model response and function results to contents
        contents.append(response.candidates[0].content)
        contents.append(types.Content(role="function", parts=function_parts))

    # Max iterations reached
    logger.warning("Max tool iterations reached")
    return AgentResponse(
        text="I've been working on that but need to pause. Could you try again?",
        tool_calls=tool_calls_executed
    )
```

### Step 8: Error Handling Wrapper

Add to `backend/src/services/agent.py`:

```python
async def run_gemini_agent_safe(
    user_id: str,
    history: list[dict],
    new_message: str,
    db_session
) -> AgentResponse:
    """
    Safe wrapper for run_gemini_agent with error handling.

    This is the primary interface for the chat endpoint.
    """
    try:
        return await run_gemini_agent(user_id, history, new_message, db_session)

    except ResourceExhausted:
        logger.warning("Gemini rate limit hit")
        return AgentResponse(
            text="I'm a bit busy right now. Please try again in a moment!",
            tool_calls=[]
        )

    except ServiceUnavailable:
        logger.error("Gemini service unavailable")
        return AgentResponse(
            text="I'm having trouble connecting. Please try again shortly.",
            tool_calls=[]
        )

    except DeadlineExceeded:
        logger.error("Gemini request timeout")
        return AgentResponse(
            text="That took too long. Could you try a simpler request?",
            tool_calls=[]
        )

    except ValueError as e:
        # Configuration errors (missing API key)
        logger.error(f"Configuration error: {e}")
        return AgentResponse(
            text="Something's not configured correctly. Please contact support.",
            tool_calls=[]
        )

    except Exception as e:
        logger.exception("Unexpected error in agent")
        return AgentResponse(
            text="Something went wrong on my end. Please try again.",
            tool_calls=[]
        )
```

### Step 9: Module Exports

Add at the end of `backend/src/services/agent.py`:

```python
__all__ = [
    "SYSTEM_PROMPT",
    "ToolCallRecord",
    "AgentResponse",
    "AgentConfig",
    "run_gemini_agent_safe",
    "run_gemini_agent",
    "build_contents_from_history",
]
```

## Verification Steps

### 1. Unit Test for History Building

```python
# tests/test_agent.py
import pytest
from src.services.agent import build_contents_from_history

def test_build_contents_empty_history():
    result = build_contents_from_history([])
    assert result == []

def test_build_contents_role_mapping():
    history = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"},
    ]
    result = build_contents_from_history(history)
    assert result[0].role == "user"
    assert result[1].role == "model"  # assistant -> model

def test_build_contents_truncation():
    history = [{"role": "user", "content": f"msg{i}"} for i in range(30)]
    result = build_contents_from_history(history, max_messages=20)
    assert len(result) == 20
```

### 2. Integration Test with Mock

```python
# tests/test_agent_integration.py
import pytest
from unittest.mock import AsyncMock, patch
from src.services.agent import run_gemini_agent_safe

@pytest.mark.asyncio
async def test_conversational_response():
    """Test that non-task messages get text-only responses."""
    with patch('src.services.agent.get_gemini_client') as mock_client:
        # Setup mock response with no function calls
        mock_response = AsyncMock()
        mock_response.function_calls = []
        mock_response.text = "Hello! How can I help you today?"

        mock_client.return_value.aio.models.generate_content = AsyncMock(
            return_value=mock_response
        )

        result = await run_gemini_agent_safe(
            user_id="test-user",
            history=[],
            new_message="Hello!",
            db_session=AsyncMock()
        )

        assert result.text == "Hello! How can I help you today?"
        assert result.tool_calls == []
```

### 3. Manual Test

```python
# scripts/test_agent_manual.py
import asyncio
import os
from src.services.agent import run_gemini_agent_safe

async def main():
    os.environ["GEMINI_API_KEY"] = "your-key-here"

    result = await run_gemini_agent_safe(
        user_id="test-user",
        history=[],
        new_message="Hello, what can you help me with?",
        db_session=None  # Won't be used for conversational response
    )

    print(f"Response: {result.text}")
    print(f"Tool calls: {result.tool_calls}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Integration with Chat Endpoint

The chat endpoint (Chunk 4) calls the agent like this:

```python
# backend/src/api/chat.py
from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database import get_session
from src.services.agent import run_gemini_agent_safe

router = APIRouter()

@router.post("/api/{user_id}/chat")
async def chat(
    user_id: str,
    request: ChatRequest,
    session: AsyncSession = Depends(get_session)
):
    # 1. Fetch conversation history from database
    history = await get_conversation_history(user_id, session)

    # 2. Call the agent
    response = await run_gemini_agent_safe(
        user_id=user_id,
        history=history,
        new_message=request.message,
        db_session=session
    )

    # 3. Save messages to database
    await save_message(user_id, "user", request.message, session)
    await save_message(user_id, "assistant", response.text, session)

    # 4. Return response
    return {"text": response.text, "tool_calls": [...]}
```

## Checklist

- [ ] Created `backend/src/services/agent.py`
- [ ] Defined SYSTEM_PROMPT constant
- [ ] Implemented ToolCallRecord, AgentResponse, AgentConfig dataclasses
- [ ] Implemented get_gemini_client() initialization
- [ ] Implemented build_contents_from_history()
- [ ] Implemented run_gemini_agent() with tool execution loop
- [ ] Implemented run_gemini_agent_safe() error wrapper
- [ ] Added comprehensive logging
- [ ] Created unit tests for history building
- [ ] Created integration tests with mocks
- [ ] Verified with manual test script
- [ ] Integrated with chat endpoint (Chunk 4)
