# Feature Specification: FastAPI Backend Structure & Chat Endpoint (Chunk-4)

**Feature Branch**: `005-fastapi-chat-endpoint`
**Created**: 2026-01-16
**Status**: Draft
**Input**: User description: "Chunk 4: FastAPI Backend Structure & Chat Endpoint - Define the FastAPI application skeleton, single stateless chat endpoint, dependencies, and request/response models"

## Overview

This specification defines the FastAPI backend application structure and the single stateless chat endpoint that serves as the primary interface between the frontend chat UI and the Gemini AI agent. The endpoint receives user messages, orchestrates AI processing with function calling, and returns natural language responses.

The architecture follows the Phase III constitution's stateless design principle - no in-memory state is maintained; all conversation context is persisted in the database.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Send a Chat Message (Priority: P1)

An authenticated user sends a natural language message through the chat interface. The system receives the message, processes it through the Gemini agent, and returns a conversational response.

**Why this priority**: This is the core functionality - without message sending and receiving, no other features work.

**Independent Test**: Can be fully tested by sending a POST request to the chat endpoint with a valid user ID and message, verifying a response is returned.

**Acceptance Scenarios**:

1. **Given** an authenticated user with ID "user-123", **When** they send a message "Add a task to buy groceries", **Then** the endpoint returns a JSON response with the AI's natural language reply and the conversation ID.
2. **Given** a user sending their first message (no conversation_id), **When** the message is processed, **Then** a new conversation is created and its ID is returned in the response.
3. **Given** a user with an existing conversation (conversation_id provided), **When** they send a follow-up message, **Then** the message is added to that conversation's history.

---

### User Story 2 - Receive Tool Execution Results (Priority: P1)

When the AI decides to perform a task operation (add, list, complete, delete, update), the tool is executed and the result is included in the response for transparency.

**Why this priority**: Users need visibility into what actions the AI performed on their behalf.

**Independent Test**: Can be tested by sending a task-related message and verifying the response includes tool_calls array with execution details.

**Acceptance Scenarios**:

1. **Given** a user message "Add task: Buy milk", **When** the AI calls the add_task tool, **Then** the response includes a tool_calls array showing the tool name and result.
2. **Given** a user message "Show my tasks", **When** the AI calls list_tasks, **Then** the response includes the tool_calls array with the retrieved tasks.
3. **Given** a conversational message with no task intent (e.g., "Hello"), **When** processed, **Then** the response has an empty or null tool_calls field.

---

### User Story 3 - Handle Unauthorized Access (Priority: P1)

When a request is made without proper authentication or with an invalid user ID, the system rejects it with an appropriate error response.

**Why this priority**: Security is non-negotiable; user isolation must be enforced at the API level.

**Independent Test**: Can be tested by sending requests with invalid/missing user IDs and verifying 401/403 responses.

**Acceptance Scenarios**:

1. **Given** a request with an empty user_id, **When** the endpoint processes it, **Then** it returns a 400 Bad Request with a descriptive error message.
2. **Given** a request with a user_id that doesn't exist, **When** the endpoint processes it, **Then** it returns a 401 Unauthorized error.
3. **Given** a request attempting to access another user's conversation, **When** the endpoint processes it, **Then** it returns a 403 Forbidden error.

---

### User Story 4 - Continue Existing Conversation (Priority: P2)

A user returns to continue a previous conversation. The system loads the conversation history and maintains context for the AI.

**Why this priority**: Context persistence is essential for natural conversation flow but depends on basic messaging working first.

**Independent Test**: Can be tested by sending multiple messages with the same conversation_id and verifying context is maintained.

**Acceptance Scenarios**:

1. **Given** a user with conversation_id 42 containing 3 previous messages, **When** they send a new message, **Then** the AI has access to the full conversation history for context.
2. **Given** a valid conversation_id, **When** the same conversation_id is returned in the response, **Then** the user can continue using it for subsequent messages.
3. **Given** a conversation_id that doesn't belong to the user, **When** they try to access it, **Then** the system rejects the request.

---

### User Story 5 - Handle Service Errors Gracefully (Priority: P2)

When external services (Gemini API, database) fail, the system returns user-friendly error messages without exposing internal details.

**Why this priority**: Robustness and good UX during failures are important but not blocking for core functionality.

**Independent Test**: Can be tested by simulating service failures and verifying graceful error responses.

**Acceptance Scenarios**:

1. **Given** the Gemini API is rate-limited, **When** a request is made, **Then** the endpoint returns a friendly message like "I'm a bit busy right now, please try again in a moment."
2. **Given** a database connection failure, **When** a request is made, **Then** the endpoint returns a 500 error with a user-friendly message.
3. **Given** any internal error, **When** it occurs, **Then** no stack traces or internal details are exposed to the user.

---

### Edge Cases

- **Empty message**: When user sends an empty or whitespace-only message, reject with 400 error.
- **Very long message**: When message exceeds reasonable length (e.g., 10,000 characters), reject with 400 error.
- **Invalid conversation_id format**: When conversation_id is not a valid integer, reject with 400 error.
- **Conversation not found**: When conversation_id doesn't exist, create a new conversation instead.
- **Concurrent requests**: Multiple simultaneous requests from same user should be handled safely without race conditions.
- **Malformed JSON body**: Invalid JSON in request body returns 422 Unprocessable Entity.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST expose a single chat endpoint at POST `/api/{user_id}/chat`.
- **FR-002**: The endpoint MUST accept a JSON body containing message (required) and conversation_id (optional).
- **FR-003**: The endpoint MUST return a JSON response containing conversation_id, response text, and optional tool_calls array.
- **FR-004**: System MUST validate that user_id exists and is authorized before processing.
- **FR-005**: System MUST create a new conversation if conversation_id is not provided or is invalid.
- **FR-006**: System MUST persist user messages to the conversation history before AI processing.
- **FR-007**: System MUST persist AI responses to the conversation history after processing.
- **FR-008**: System MUST integrate with the Gemini agent for AI processing (agent defined in Chunk 5).
- **FR-009**: System MUST pass tool definitions to Gemini (tools defined in Chunk 3/4).
- **FR-010**: System MUST execute tool calls returned by Gemini and feed results back.
- **FR-011**: System MUST return tool execution details in the response for transparency.
- **FR-012**: System MUST enforce CORS to allow requests from the frontend origin.
- **FR-013**: All database operations MUST be asynchronous and non-blocking.
- **FR-014**: System MUST NOT store any state in memory - all state must come from database.

### Error Handling Requirements

- **FR-015**: Invalid or missing user_id MUST return HTTP 400 with descriptive message.
- **FR-016**: Unauthorized access attempts MUST return HTTP 401.
- **FR-017**: Access to another user's resources MUST return HTTP 403.
- **FR-018**: Invalid request body MUST return HTTP 422 with validation errors.
- **FR-019**: Internal server errors MUST return HTTP 500 with user-friendly message (no stack traces).
- **FR-020**: Gemini API rate limits MUST return HTTP 429 with retry guidance.

### Key Entities

- **ChatRequest**: The incoming request body containing user message and optional conversation reference.
- **ChatResponse**: The outgoing response containing AI reply, conversation ID, and tool execution details.
- **ToolCall**: Record of a tool invocation including name, arguments, and result.
- **Conversation**: Database entity storing message history for a user session.
- **Message**: Individual message within a conversation (user or assistant role).

---

## Request & Response Contracts *(mandatory)*

### Request Schema: ChatRequest

| Field           | Type         | Required | Description                                    |
| --------------- | ------------ | -------- | ---------------------------------------------- |
| message         | string       | Yes      | The user's natural language message            |
| conversation_id | integer/null | No       | ID of existing conversation to continue        |

**Validation Rules**:
- message: Must be non-empty, max 10,000 characters
- conversation_id: If provided, must be a positive integer

### Response Schema: ChatResponse

| Field           | Type         | Description                                    |
| --------------- | ------------ | ---------------------------------------------- |
| conversation_id | integer      | ID of the conversation (new or existing)       |
| response        | string       | The AI's natural language response             |
| tool_calls      | array/null   | List of tools executed during processing       |

### ToolCall Schema

| Field     | Type   | Description                              |
| --------- | ------ | ---------------------------------------- |
| name      | string | Name of the tool (e.g., "add_task")      |
| arguments | object | Arguments passed to the tool             |
| result    | object | Result returned from tool execution      |

### Error Response Schema

| Field   | Type   | Description                          |
| ------- | ------ | ------------------------------------ |
| error   | string | Error type/code                      |
| message | string | Human-readable error description     |
| details | object | Optional additional error context    |

---

## Backend Folder Structure *(informational)*

The backend application organizes code into logical modules:

```
backend/
├── main.py              # Application entry point, CORS, lifespan
├── routers/
│   └── chat.py          # Chat endpoint router
├── dependencies.py      # Dependency injection (DB session, auth)
├── schemas.py           # Pydantic request/response models
├── models/              # SQLModel database models
│   ├── conversation.py  # Conversation and Message models
│   └── task.py          # Task model (from Phase II)
├── services/
│   ├── agent.py         # Gemini agent integration (Chunk 5)
│   └── conversation.py  # Conversation persistence logic
├── tools/               # Gemini function calling tools
│   └── task_tools.py    # 5 task tools (Chunk 3)
└── config.py            # Environment configuration
```

---

## API Behavior Flow *(mandatory)*

### Chat Endpoint Processing Flow

1. **Receive Request**: Accept POST to `/api/{user_id}/chat` with ChatRequest body
2. **Validate User**: Verify user_id is valid and authorized
3. **Resolve Conversation**: Load existing conversation or create new one
4. **Store User Message**: Persist the incoming message to conversation history
5. **Load Context**: Retrieve recent conversation messages for AI context
6. **Call Gemini Agent**: Send message + history + tools to Gemini
7. **Handle Function Calls**: If Gemini returns tool calls, execute them
8. **Feed Results Back**: Return tool results to Gemini for final response
9. **Get Final Response**: Receive AI's natural language response
10. **Store AI Response**: Persist assistant message to conversation history
11. **Return Response**: Send ChatResponse to client

### Statelessness Guarantee

- No request-level caching in memory
- No conversation state stored in application memory
- Every request fetches fresh state from database
- Server can restart without losing any user data

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Chat endpoint responds to valid requests in under 3 seconds (excluding Gemini API latency).
- **SC-002**: 100% of requests include proper error responses for invalid inputs.
- **SC-003**: User messages and AI responses are persisted correctly 100% of the time.
- **SC-004**: Server restart does not lose any conversation data or user context.
- **SC-005**: Unauthorized access attempts are blocked 100% of the time.
- **SC-006**: Frontend can successfully communicate with backend via CORS.
- **SC-007**: Tool execution results are returned in response for all tool-calling scenarios.
- **SC-008**: Error responses never expose internal stack traces or implementation details.

---

## Assumptions

- User authentication is handled by Better Auth and user_id is provided by the frontend after successful auth.
- The Gemini agent (Chunk 5) provides a function to process messages and return responses.
- The task tools (Chunk 3/4) are implemented as callable functions that return JSON results.
- Database schema (Chunk 2) includes conversations table with message history.
- The frontend origin for CORS is configurable via environment variable.
- Rate limit handling can return a graceful message without complex retry logic for MVP.

---

## Dependencies

- **Phase III Constitution**: Architectural principles and technology stack.
- **Chunk 2 (Database Schema)**: Conversation and Message models must exist.
- **Chunk 3 (Function Tools)**: Tool definitions for Gemini function calling.
- **Chunk 5 (Gemini Agent)**: Agent that processes messages with Gemini API.
- **Better Auth**: User authentication providing valid user_id values.

---

## Out of Scope

- WebSocket/streaming responses (future enhancement)
- File upload in chat messages
- Message editing or deletion
- Conversation archiving or export
- Rate limiting implementation (graceful error only)
- Health check endpoints
- Metrics/monitoring endpoints
- Admin endpoints
