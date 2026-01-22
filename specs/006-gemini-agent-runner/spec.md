# Feature Specification: Gemini Agent Integration & Runner (Chunk 5)

**Feature Branch**: `006-gemini-agent-runner`
**Created**: 2026-01-16
**Status**: Draft
**Input**: User description: "Chunk 5: Gemini Agent Integration & Runner - Define how to initialize Gemini model, declare tools (from Chunk 3), handle stateless per-request agent run, tool execution loop, and final response generation."

## Overview

This specification defines the Gemini AI agent integration layer that orchestrates AI-powered task management conversations. The agent is responsible for:

1. Initializing and configuring the Gemini model with API credentials
2. Constructing prompts from conversation history and system instructions
3. Processing user messages through the Gemini API with function calling
4. Executing tool calls and feeding results back to Gemini
5. Managing the multi-turn tool execution loop until a final text response is generated
6. Handling token limits and rate limit graceful degradation

The agent is stateless - it receives all required context (conversation history, user message) per request and produces a response without maintaining any in-memory state.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Simple Conversational Response (Priority: P1)

A user sends a greeting or general question that does not require any task operations. The agent processes the message through Gemini and returns a friendly conversational response without invoking any tools.

**Why this priority**: This is the baseline functionality - the agent must be able to generate text responses. If this fails, nothing else works.

**Independent Test**: Can be fully tested by sending a non-task message (e.g., "Hello!") and verifying a text response is returned with no tool_calls.

**Acceptance Scenarios**:

1. **Given** a user message "Hello, how are you?", **When** the agent processes it, **Then** Gemini returns a friendly text response and no function calls are made.
2. **Given** a user message "What can you help me with?", **When** the agent processes it, **Then** the response explains the available task management capabilities.
3. **Given** empty conversation history and a new user message, **When** the agent runs, **Then** only the system prompt and current message are sent to Gemini.

---

### User Story 2 - Single Tool Invocation (Priority: P1)

A user requests a task operation that requires exactly one tool call. The agent calls Gemini, receives a function call, executes it, feeds the result back, and returns the final natural language response.

**Why this priority**: Single tool invocation is the core AI-powered functionality that differentiates this from a static chat interface.

**Independent Test**: Can be fully tested by sending "Add a task: Buy milk" and verifying add_task tool is called, result is fed back, and final response confirms the creation.

**Acceptance Scenarios**:

1. **Given** a user message "Add a task to buy groceries", **When** the agent processes it, **Then** it calls the add_task tool, receives the result, and generates a confirmation message.
2. **Given** a user message "Show my tasks", **When** the agent processes it, **Then** it calls the list_tasks tool and formats the results in the response.
3. **Given** a tool execution that returns an error (task not found), **When** the result is fed back, **Then** the agent generates a friendly error message.

---

### User Story 3 - Multi-Turn Tool Execution (Priority: P1)

A user request requires the agent to call multiple tools in sequence (e.g., list tasks to find ID, then complete the task). The agent handles the iterative tool execution loop until Gemini returns a final text response.

**Why this priority**: Multi-turn execution enables the AI to handle complex, ambiguous requests intelligently - a key differentiator.

**Independent Test**: Can be fully tested by sending "Complete my groceries task" where the agent must first list_tasks to find the ID, then complete_task.

**Acceptance Scenarios**:

1. **Given** a user message "Complete the grocery shopping task", **When** the agent processes it, **Then** it first calls list_tasks to identify the task ID, then calls complete_task with that ID.
2. **Given** a sequence of tool calls exceeding 3 rounds, **When** processing continues, **Then** the agent enforces a maximum iteration limit and generates a response.
3. **Given** the model returns both text and a function call, **When** processing, **Then** the function call is executed before returning the text.

---

### User Story 4 - Conversation History Context (Priority: P2)

The agent receives conversation history and uses it to maintain context across multiple user messages within a session.

**Why this priority**: Context awareness enables natural multi-turn conversations but depends on basic message processing working first.

**Independent Test**: Can be tested by providing a history with "I added a task called Report" and then sending "Mark it as complete" - the agent should understand "it" refers to "Report".

**Acceptance Scenarios**:

1. **Given** conversation history containing "Added task: Weekly report", **When** user says "Delete it", **Then** the agent understands the reference and attempts to delete "Weekly report".
2. **Given** a conversation with 50+ messages, **When** processing a new message, **Then** the agent truncates/summarizes old messages to stay within token limits.
3. **Given** conversation history with both user and assistant messages, **When** constructing the prompt, **Then** messages are formatted with correct role attribution.

---

### User Story 5 - Rate Limit Graceful Degradation (Priority: P2)

When the Gemini API returns a rate limit error, the agent returns a friendly message asking the user to try again later.

**Why this priority**: Rate limit handling is important for user experience during peak usage but is not core functionality.

**Independent Test**: Can be tested by simulating a 429 response from Gemini and verifying the agent returns a graceful error message.

**Acceptance Scenarios**:

1. **Given** Gemini returns HTTP 429 (rate limited), **When** the agent catches this error, **Then** it returns a friendly message like "I'm a bit busy, please try again in a moment."
2. **Given** Gemini returns HTTP 500 (server error), **When** the agent catches this error, **Then** it returns a generic error message without exposing technical details.
3. **Given** an API timeout, **When** the timeout is detected, **Then** the agent returns a message indicating temporary unavailability.

---

### Edge Cases

- **Empty user message**: Agent should reject or ask for input rather than calling Gemini with empty content.
- **Tool returns malformed JSON**: Agent should handle parsing errors gracefully and inform the user.
- **Infinite tool loop**: Agent must enforce a maximum iteration count (e.g., 5) to prevent runaway processing.
- **Token limit exceeded**: If history + message + system prompt exceeds context window, oldest messages should be pruned.
- **Model returns no response**: Handle null/empty Gemini responses gracefully.
- **Concurrent requests**: Each request is independent; no shared state to cause race conditions.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST use the google-generativeai SDK to interact with Gemini API.
- **FR-002**: System MUST configure the SDK with the GEMINI_API_KEY environment variable on initialization.
- **FR-003**: System MUST use model "gemini-1.5-flash" or "gemini-2.5-flash" (configurable, default to gemini-1.5-flash).
- **FR-004**: System MUST define a system prompt that instructs Gemini to act as a friendly Todo assistant.
- **FR-005**: System MUST pass the 5 tool declarations (from Chunk 3/4) to every generate_content call.
- **FR-006**: System MUST accept user_id, conversation history (list of messages), and new user message as input to the agent runner.
- **FR-007**: System MUST construct Gemini contents array from conversation history with proper "user" and "model" role mapping.
- **FR-008**: System MUST prepend the system prompt to every request as initial context.
- **FR-009**: When Gemini returns function calls, System MUST execute each tool and collect results.
- **FR-010**: System MUST feed function results back to Gemini using the function response format.
- **FR-011**: System MUST continue the tool execution loop until Gemini returns a text-only response (no function calls).
- **FR-012**: System MUST enforce a maximum of 5 tool execution iterations per request.
- **FR-013**: System MUST return the final text response along with a list of all tool calls executed.
- **FR-014**: System MUST inject user_id into every tool call to ensure user isolation.
- **FR-015**: System MUST handle Gemini API errors (rate limits, server errors) gracefully.
- **FR-016**: System MUST log all tool invocations with arguments and results for debugging.
- **FR-017**: System MUST implement token counting/estimation to manage context window limits.
- **FR-018**: System MUST truncate conversation history when approaching the 100k token limit.

### Configuration Requirements

- **FR-019**: GEMINI_API_KEY environment variable MUST be required; agent initialization MUST fail if not set.
- **FR-020**: Model name MUST be configurable via GEMINI_MODEL environment variable (default: gemini-1.5-flash).
- **FR-021**: Maximum tool iterations MUST be configurable (default: 5).
- **FR-022**: Context history message limit MUST be configurable (default: 20 messages).

### Key Entities

- **GeminiAgent**: The main agent class/module that encapsulates model initialization, prompt construction, and response generation.
- **AgentRunner**: The stateless function that orchestrates a single request through the agent, handling the tool execution loop.
- **ToolRegistry**: A mapping of tool names to their execution functions for dynamic dispatch.
- **AgentResponse**: The structured output containing final text, tool calls executed, and any metadata.

---

## System Prompt *(mandatory)*

The system prompt establishes the AI's persona, capabilities, and behavioral guidelines:

```
You are a helpful and friendly Todo manager assistant. Your name is TaskBot.

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

The user_id will be provided automatically for all operations - you don't need to ask for it.
```

---

## Agent Initialization *(mandatory)*

### SDK Configuration

```python
import google.generativeai as genai
import os

def initialize_gemini() -> genai.GenerativeModel:
    """Initialize and return the configured Gemini model."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is required")

    genai.configure(api_key=api_key)

    model_name = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")

    return genai.GenerativeModel(
        model_name=model_name,
        system_instruction=SYSTEM_PROMPT
    )
```

### Tool Declarations Reference

Tools are declared using the format from Chunk 3/4 specification. The agent imports tool_declarations from the tools module:

```python
from tools.task_tools import TOOL_DECLARATIONS, execute_tool

# TOOL_DECLARATIONS = [add_task, list_tasks, complete_task, delete_task, update_task]
```

---

## Stateless Agent Runner *(mandatory)*

### Function Signature

```python
from typing import Optional
from dataclasses import dataclass

@dataclass
class ToolCallRecord:
    name: str
    arguments: dict
    result: dict

@dataclass
class AgentResponse:
    text: str
    tool_calls: list[ToolCallRecord]
    conversation_id: Optional[int] = None

async def run_gemini_agent(
    user_id: str,
    history: list[dict],  # [{"role": "user"|"assistant", "content": "..."}]
    new_message: str,
    db_session: AsyncSession
) -> AgentResponse:
    """
    Process a user message through the Gemini agent.

    Args:
        user_id: The authenticated user's ID for tool execution
        history: Previous conversation messages
        new_message: The current user message
        db_session: Database session for tool execution

    Returns:
        AgentResponse with final text and executed tool calls
    """
```

### Processing Flow Pseudocode

```python
async def run_gemini_agent(user_id, history, new_message, db_session):
    # 1. Initialize model (or use cached instance)
    model = get_gemini_model()

    # 2. Build contents array from history
    contents = build_contents_from_history(history)

    # 3. Add new user message
    contents.append({"role": "user", "parts": [new_message]})

    # 4. Prepare tool declarations
    tools = get_tool_declarations()

    # 5. Initialize tracking
    tool_calls_executed = []
    max_iterations = int(os.environ.get("MAX_TOOL_ITERATIONS", 5))

    # 6. Tool execution loop
    for iteration in range(max_iterations):
        # Call Gemini
        response = await model.generate_content_async(
            contents=contents,
            tools=tools
        )

        # Check for function calls
        if not has_function_calls(response):
            # No function calls - return final text
            return AgentResponse(
                text=extract_text(response),
                tool_calls=tool_calls_executed
            )

        # Execute each function call
        function_responses = []
        for fn_call in response.candidates[0].content.parts:
            if hasattr(fn_call, 'function_call'):
                fn_name = fn_call.function_call.name
                fn_args = dict(fn_call.function_call.args)

                # Inject user_id for security
                fn_args["user_id"] = user_id

                # Execute tool
                result = await execute_tool(fn_name, fn_args, db_session)

                # Track execution
                tool_calls_executed.append(ToolCallRecord(
                    name=fn_name,
                    arguments=fn_args,
                    result=result
                ))

                # Prepare function response
                function_responses.append({
                    "name": fn_name,
                    "response": result
                })

        # Add model response and function results to contents
        contents.append(response.candidates[0].content)
        contents.append({
            "role": "function",
            "parts": function_responses
        })

    # Max iterations reached
    return AgentResponse(
        text="I've been working on that but need to pause. Could you try again?",
        tool_calls=tool_calls_executed
    )
```

---

## Tool Execution Function *(mandatory)*

### Dispatcher Pattern

```python
from typing import Any

# Tool registry maps tool names to handler functions
TOOL_HANDLERS = {
    "add_task": handle_add_task,
    "list_tasks": handle_list_tasks,
    "complete_task": handle_complete_task,
    "delete_task": handle_delete_task,
    "update_task": handle_update_task,
}

async def execute_tool(
    tool_name: str,
    args: dict[str, Any],
    db_session: AsyncSession
) -> dict[str, Any]:
    """
    Execute a tool by name with given arguments.

    Args:
        tool_name: Name of the tool to execute
        args: Arguments for the tool (must include user_id)
        db_session: Database session for operations

    Returns:
        JSON-serializable result dictionary
    """
    handler = TOOL_HANDLERS.get(tool_name)

    if not handler:
        logger.error(f"Unknown tool requested: {tool_name}")
        return {"status": "error", "message": f"Unknown tool: {tool_name}"}

    try:
        logger.info(f"Executing tool: {tool_name} with args: {args}")
        result = await handler(db_session, **args)
        logger.info(f"Tool {tool_name} returned: {result}")
        return result
    except Exception as e:
        logger.exception(f"Tool execution failed: {tool_name}")
        return {"status": "error", "message": str(e)}
```

### Tool Handler Interface

Each tool handler follows this signature:

```python
async def handle_add_task(
    db_session: AsyncSession,
    user_id: str,
    title: str,
    description: Optional[str] = None
) -> dict[str, Any]:
    """Create a new task for the user."""
    # Implementation uses SQLModel operations
    ...
    return {"status": "created", "task_id": task.id, "title": task.title}
```

---

## Context Management *(mandatory)*

### History Formatting

```python
def build_contents_from_history(
    history: list[dict],
    max_messages: int = 20
) -> list[dict]:
    """
    Convert conversation history to Gemini contents format.

    Args:
        history: List of {"role": "user"|"assistant", "content": "..."}
        max_messages: Maximum messages to include (oldest are pruned)

    Returns:
        Gemini-compatible contents array
    """
    # Truncate to most recent messages
    recent_history = history[-max_messages:] if len(history) > max_messages else history

    contents = []
    for msg in recent_history:
        # Map assistant role to model role for Gemini
        role = "model" if msg["role"] == "assistant" else "user"
        contents.append({
            "role": role,
            "parts": [msg["content"]]
        })

    return contents
```

### Token Estimation (Simplified)

```python
def estimate_tokens(text: str) -> int:
    """Rough token estimation (4 chars per token average)."""
    return len(text) // 4

def should_truncate_history(
    history: list[dict],
    new_message: str,
    system_prompt: str,
    max_tokens: int = 90000  # Leave buffer below 100k limit
) -> bool:
    """Check if history needs truncation."""
    total = estimate_tokens(system_prompt) + estimate_tokens(new_message)
    for msg in history:
        total += estimate_tokens(msg["content"])
    return total > max_tokens
```

---

## Token / Rate Limit Handling *(mandatory)*

### Rate Limit Response

```python
from google.api_core.exceptions import ResourceExhausted, ServiceUnavailable

async def run_gemini_agent_safe(...) -> AgentResponse:
    """Wrapper with error handling."""
    try:
        return await run_gemini_agent(...)
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
    except Exception as e:
        logger.exception("Unexpected error in agent")
        return AgentResponse(
            text="Something went wrong on my end. Please try again.",
            tool_calls=[]
        )
```

### Free Tier Awareness

- Gemini free tier: ~5-15 requests per minute
- Keep context minimal to reduce processing time
- Avoid unnecessary API calls for simple greetings (but currently all messages go through Gemini)
- Log rate limit events for monitoring

---

## Logging & Observability *(mandatory)*

### Required Log Events

| Event | Level | Data |
| ----- | ----- | ---- |
| Agent request started | INFO | user_id, message_preview |
| Gemini API call | DEBUG | model, content_length, has_tools |
| Function call detected | INFO | tool_name, arguments |
| Tool execution result | INFO | tool_name, status |
| Agent response generated | INFO | text_length, tool_count |
| Rate limit hit | WARNING | - |
| API error | ERROR | error_type, message |

### Example Log Format

```
2026-01-16 10:30:45 INFO agent: Request started user_id=user-123 message="Add task..."
2026-01-16 10:30:46 INFO agent: Function call detected tool=add_task args={"title": "Buy milk"}
2026-01-16 10:30:46 INFO agent: Tool execution result tool=add_task status=created task_id=5
2026-01-16 10:30:47 INFO agent: Response generated text_length=45 tool_count=1
```

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Agent correctly initializes with GEMINI_API_KEY and fails fast if key is missing.
- **SC-002**: Simple conversational messages receive text responses with no tool calls.
- **SC-003**: Task operation requests trigger appropriate tool calls and return confirmation.
- **SC-004**: Multi-turn tool execution completes successfully for ambiguous requests (e.g., "complete my report task").
- **SC-005**: Tool execution loop terminates after max iterations without hanging.
- **SC-006**: Rate limit errors result in friendly user messages, not error stack traces.
- **SC-007**: All tool calls have user_id injected for security (100% coverage).
- **SC-008**: Conversation history is properly formatted with correct role mapping.
- **SC-009**: Agent processing completes in under 5 seconds excluding Gemini API latency.
- **SC-010**: All tool invocations are logged with arguments and results.

---

## Assumptions

- The google-generativeai SDK supports async operations via `generate_content_async`.
- Gemini models (1.5-flash, 2.5-flash) support function calling with the provided schema format.
- Tool handlers (from Chunk 3) return JSON-serializable dictionaries.
- Database sessions are provided by the FastAPI dependency injection system.
- The system prompt is included as system_instruction in GenerativeModel (not as first content).
- Function calling responses use the standard Gemini response structure with candidates[0].content.parts.

---

## Dependencies

- **Phase III Constitution**: Architectural principles (stateless, user isolation, rate limits).
- **Chunk 2 (Database Schema)**: AsyncSession type for tool execution.
- **Chunk 3/4 (Function Tools)**: TOOL_DECLARATIONS and tool handler implementations.
- **Chunk 4 (FastAPI Endpoint)**: Integration point that calls the agent runner.
- **google-generativeai SDK**: Core dependency for Gemini API integration.

---

## Out of Scope

- Streaming responses (future enhancement)
- Custom prompt templates or persona switching
- Caching of Gemini responses
- Retry logic for transient failures (graceful error only)
- Advanced token counting using tiktoken or similar
- Conversation summarization (simple truncation for MVP)
- Multi-model support beyond Gemini

---

## Implementation Reference Structure

```
backend/
├── services/
│   └── agent.py           # Main module for this spec
│       ├── SYSTEM_PROMPT   # Constant
│       ├── initialize_gemini()
│       ├── build_contents_from_history()
│       ├── execute_tool()
│       ├── run_gemini_agent()
│       └── run_gemini_agent_safe()  # Error handling wrapper
```

The agent module exports `run_gemini_agent_safe` as the primary interface for the chat endpoint.
