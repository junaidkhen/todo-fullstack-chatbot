"""
Gemini Agent Integration & Runner

Stateless agent that processes user messages through Gemini API
with function calling for task management operations.

This module provides:
- ToolCallRecord, AgentResponse, AgentConfig dataclasses
- SYSTEM_PROMPT constant for TaskBot persona
- run_gemini_agent() for processing messages with tool execution loop
- run_gemini_agent_safe() error handling wrapper
- build_contents_from_history() for history conversion

All context is passed per-request; no in-memory state is maintained.
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
from sqlmodel.ext.asyncio.session import AsyncSession

from src.gemini.tools import get_task_tools
from src.services.task_tools import dispatch_tool
from src.services.prompts import SYSTEM_PROMPT

logger = logging.getLogger(__name__)


# =============================================================================
# Data Classes (T006, T007, T008)
# =============================================================================

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
    model: str = "gemini-2.0-flash"
    max_iterations: int = 5
    max_history_messages: int = 20
    max_tokens: int = 90000

    @classmethod
    def from_env(cls) -> "AgentConfig":
        """Load configuration from environment variables."""
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        return cls(
            api_key=api_key,
            model=os.environ.get("GEMINI_MODEL", "gemini-2.0-flash"),
            max_iterations=int(os.environ.get("MAX_TOOL_ITERATIONS", "5")),
            max_history_messages=int(os.environ.get("MAX_HISTORY_MESSAGES", "20"))
        )


# =============================================================================
# Client Singleton (T009, T010)
# =============================================================================

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
    assert _config is not None
    return _config


# =============================================================================
# History Building (T014, T031, T032)
# =============================================================================

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
    # Truncate to most recent messages (T031)
    recent = history[-max_messages:] if len(history) > max_messages else history

    contents = []
    for msg in recent:
        # Map assistant role to model role for Gemini (T032)
        role = "model" if msg["role"] == "assistant" else "user"
        contents.append(types.Content(
            role=role,
            parts=[types.Part(text=msg["content"])]
        ))

    return contents


def estimate_tokens(text: str) -> int:
    """Rough token estimation (4 chars per token average). (T015)"""
    return len(text) // 4


def should_truncate_history(
    history: list[dict],
    new_message: str,
    system_prompt: str,
    max_tokens: int = 90000
) -> bool:
    """Check if history needs truncation based on token estimation. (T033)"""
    total = estimate_tokens(system_prompt) + estimate_tokens(new_message)
    for msg in history:
        total += estimate_tokens(msg.get("content", ""))
    return total > max_tokens


# =============================================================================
# Execute Tool Wrapper (T021)
# =============================================================================

async def execute_tool(
    name: str,
    args: dict[str, Any],
    session: AsyncSession
) -> dict[str, Any]:
    """
    Execute a tool by name with given arguments.

    Wraps dispatch_tool from task_tools module for agent use.

    Args:
        name: Name of the tool to execute
        args: Arguments for the tool (includes user_id)
        session: Database session for operations

    Returns:
        JSON-serializable result dictionary
    """
    return await dispatch_tool(session, name, args)


# =============================================================================
# Main Agent Runner (T016-T030)
# =============================================================================

async def run_gemini_agent(
    user_id: str,
    history: list[dict],
    new_message: str,
    db_session: AsyncSession
) -> AgentResponse:
    """
    Process a user message through the Gemini agent.

    This is the core agent function that:
    1. Builds contents from conversation history
    2. Calls Gemini API with tool declarations
    3. Executes any function calls in a loop
    4. Returns final text response with tool call records

    Args:
        user_id: Authenticated user's ID for tool execution (injected into all tool calls)
        history: Previous conversation messages [{"role": "user"|"assistant", "content": "..."}]
        new_message: Current user message
        db_session: Database session for tool execution

    Returns:
        AgentResponse with final text and list of executed tool calls
    """
    client = get_gemini_client()
    config = get_config()

    # T017: Validate input - empty message check
    if not new_message.strip():
        return AgentResponse(
            text="I didn't catch that. Could you say something?",
            tool_calls=[]
        )

    logger.info(f"Agent request started user_id={user_id} message={new_message[:50]}...")

    # Build contents from history
    contents = build_contents_from_history(history, config.max_history_messages)

    # Add new user message
    contents.append(types.Content(
        role="user",
        parts=[types.Part(text=new_message)]
    ))

    # Prepare configuration with system instruction and tools
    gen_config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        tools=[get_task_tools()],
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
    )

    # Tool execution tracking
    tool_calls_executed: list[ToolCallRecord] = []

    # T027-T030: Tool execution loop with max iterations
    for iteration in range(config.max_iterations):
        logger.debug(f"Gemini call iteration={iteration}")

        # Call Gemini API
        response = await client.aio.models.generate_content(
            model=config.model,
            contents=contents,
            config=gen_config
        )

        # T018, T019: Check for function calls
        if not response.function_calls:
            # No function calls - return final text response
            final_text = response.text or "I'm not sure how to respond to that."
            logger.info(
                f"Response generated text_length={len(final_text)} "
                f"tool_count={len(tool_calls_executed)}"
            )
            return AgentResponse(
                text=final_text,
                tool_calls=tool_calls_executed
            )

        # Process function calls
        function_parts = []
        for fc in response.function_calls:
            fn_name = fc.name
            fn_args = dict(fc.args) if fc.args else {}

            # T020: Security - Inject user_id into every tool call
            fn_args["user_id"] = user_id

            # T025: Log function call detection
            logger.info(f"Function call detected tool={fn_name} args={fn_args}")

            # T021: Execute tool via dispatch
            result = await execute_tool(fn_name, fn_args, db_session)

            # T026: Log tool execution result
            logger.info(f"Tool execution result tool={fn_name} status={result.get('status')}")

            # T022: Track execution
            tool_calls_executed.append(ToolCallRecord(
                name=fn_name,
                arguments=fn_args,
                result=result
            ))

            # T023: Build FunctionResponse for Gemini
            function_parts.append(types.Part(
                function_response=types.FunctionResponse(
                    name=fn_name,
                    response=result
                )
            ))

        # T024: Append model response and function results to contents
        contents.append(response.candidates[0].content)
        contents.append(types.Content(role="function", parts=function_parts))

    # T028, T029: Max iterations reached - return pause message
    logger.warning("Max tool iterations reached")
    return AgentResponse(
        text="I've been working on that but need to pause. Could you try again?",
        tool_calls=tool_calls_executed
    )


# =============================================================================
# Error Handling Wrapper (T034-T040)
# =============================================================================

async def run_gemini_agent_safe(
    user_id: str,
    history: list[dict],
    new_message: str,
    db_session: AsyncSession
) -> AgentResponse:
    """
    Safe wrapper for run_gemini_agent with comprehensive error handling.

    This is the PRIMARY INTERFACE for the chat endpoint. It catches all
    Gemini API errors and returns friendly user messages.

    Args:
        user_id: Authenticated user's ID
        history: Previous conversation messages
        new_message: Current user message
        db_session: Database session for tool execution

    Returns:
        AgentResponse - always returns a response, never raises
    """
    try:
        return await run_gemini_agent(user_id, history, new_message, db_session)

    except ResourceExhausted:
        # T035: Rate limit hit
        logger.warning("Gemini rate limit hit")
        return AgentResponse(
            text="I'm a bit busy right now. Please try again in a moment!",
            tool_calls=[]
        )

    except ServiceUnavailable:
        # T036: Server error
        logger.error("Gemini service unavailable")
        return AgentResponse(
            text="I'm having trouble connecting. Please try again shortly.",
            tool_calls=[]
        )

    except DeadlineExceeded:
        # T037: Timeout
        logger.error("Gemini request timeout")
        return AgentResponse(
            text="That took too long. Could you try a simpler request?",
            tool_calls=[]
        )

    except ValueError as e:
        # T038: Configuration errors (missing API key)
        logger.error(f"Configuration error: {e}")
        return AgentResponse(
            text="Something's not configured correctly. Please contact support.",
            tool_calls=[]
        )

    except Exception as e:
        # T039: Generic fallback
        logger.exception("Unexpected error in agent")
        return AgentResponse(
            text="Something went wrong on my end. Please try again.",
            tool_calls=[]
        )


# =============================================================================
# Module Exports (T012, T041, T042)
# =============================================================================

__all__ = [
    # Data classes
    "ToolCallRecord",
    "AgentResponse",
    "AgentConfig",
    # Main functions
    "run_gemini_agent_safe",
    "run_gemini_agent",
    # Utilities
    "build_contents_from_history",
    "estimate_tokens",
    "get_gemini_client",
    "get_config",
]
