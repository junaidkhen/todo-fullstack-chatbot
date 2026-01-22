"""Chat API endpoint for AI-powered task management.

Implements POST /api/{user_id}/chat endpoint per spec:
- Receives user messages with optional conversation_id
- Validates user existence
- Manages conversation persistence
- Calls Gemini agent for AI processing
- Returns structured response with tool execution details

Follows Phase III constitution's stateless architecture.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from src.database import get_session
from src.schemas.chat import ChatRequest, ChatResponse, ToolCall, ErrorResponse
from src.dependencies import get_validated_user
from src.services.agent import ToolCallRecord, AgentResponse, run_gemini_agent_safe
from src.services.conversation import (
    get_or_create_conversation,
    fetch_history,
    store_user_message,
    store_assistant_response,
)
from src.config import get_config

logger = logging.getLogger(__name__)

router = APIRouter()


# =============================================================================
# Helper Functions (T017)
# =============================================================================

def tool_record_to_schema(record: ToolCallRecord) -> ToolCall:
    """Convert internal ToolCallRecord to API ToolCall schema."""
    return ToolCall(
        name=record.name,
        arguments=record.arguments,
        result=record.result
    )


def agent_to_chat_response(
    conversation_id: int,
    agent_response: AgentResponse
) -> ChatResponse:
    """Convert AgentResponse to ChatResponse schema.

    T018: Returns null for tool_calls if empty, not empty array.
    """
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


# =============================================================================
# Chat Endpoint (T010-T015)
# =============================================================================

@router.post(
    "/chat",
    response_model=ChatResponse,
    responses={
        200: {"model": ChatResponse, "description": "Successful response"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        401: {"model": ErrorResponse, "description": "User not found"},
        403: {"model": ErrorResponse, "description": "Access denied"},
        422: {"model": ErrorResponse, "description": "Validation error"},
        429: {"model": ErrorResponse, "description": "Rate limited"},
        500: {"model": ErrorResponse, "description": "Internal error"},
        503: {"model": ErrorResponse, "description": "Service unavailable"},
    },
    summary="Send a chat message",
    description="""
    Process a user message through the Gemini AI agent.

    Creates or continues a conversation, executes any tool calls,
    and returns the AI's natural language response.
    """,
)
async def send_chat_message(
    user_id: str,
    request: ChatRequest,
    session: AsyncSession = Depends(get_session),
    validated_user: str = Depends(get_validated_user),
) -> ChatResponse:
    """
    Process a chat message and return AI response.

    Args:
        user_id: Authenticated user's ID (from path)
        request: ChatRequest with message and optional conversation_id
        session: Database session
        validated_user: User ID validated by dependency

    Returns:
        ChatResponse with conversation_id, response text, and tool_calls

    Raises:
        HTTPException: For various error conditions (see responses above)
    """
    config = get_config()

    logger.info(
        f"Chat request received user_id={user_id} "
        f"conversation_id={request.conversation_id} "
        f"message_length={len(request.message)}"
    )

    # T011, T013: Get or create conversation
    conversation = await get_or_create_conversation(
        user_id=user_id,
        conversation_id=request.conversation_id,
        session=session
    )
    # Store conversation_id immediately to avoid lazy loading after commits
    conversation_id = conversation.id

    # T013: Store user message
    await store_user_message(
        conversation_id=conversation_id,
        user_id=user_id,
        content=request.message,
        session=session
    )

    # T023, T024: Fetch conversation history for context
    history = await fetch_history(
        conversation_id=conversation_id,
        user_id=user_id,
        limit=config.history_message_limit,
        session=session
    )

    # Remove the last message (the one we just stored) since we pass it separately
    if history and history[-1]["role"] == "user":
        history = history[:-1]

    # T011: Call Gemini agent (safe wrapper handles all errors)
    agent_response = await run_gemini_agent_safe(
        user_id=user_id,
        history=history,
        new_message=request.message,
        db_session=session
    )

    # T013: Store assistant response
    await store_assistant_response(
        conversation_id=conversation_id,
        user_id=user_id,
        content=agent_response.text,
        session=session
    )

    # T016, T017, T018: Convert to response schema
    response = agent_to_chat_response(conversation_id, agent_response)

    logger.info(
        f"Chat response generated conversation_id={conversation_id} "
        f"response_length={len(response.response)} "
        f"tool_count={len(response.tool_calls) if response.tool_calls else 0}"
    )

    return response
