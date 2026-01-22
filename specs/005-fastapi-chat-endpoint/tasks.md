# Tasks: FastAPI Backend Structure & Chat Endpoint (Chunk 4)

**Input**: Design documents from `/specs/005-fastapi-chat-endpoint/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md
**Dependencies**: Chunk 2 (003-db-models-schema), Chunk 3 (004-gemini-function-tools), Chunk 5 (006-gemini-agent-runner), Chunk 7 (008-conversation-persistence)

**Tests**: Not explicitly requested - test tasks included only for critical integration points.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project dependencies and configuration

- [X] T001 Add google-generativeai>=0.8.0 and google-api-core>=2.0.0 to backend/requirements.txt
- [X] T002 [P] Create config module with environment variables in backend/src/config.py (GEMINI_API_KEY, GEMINI_MODEL, FRONTEND_ORIGIN, MAX_TOOL_ITERATIONS, HISTORY_MESSAGE_LIMIT)
- [X] T003 [P] Update backend/.env.example with new environment variables for Gemini and CORS configuration

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**Depends on**: Phase 1 completion + Chunk 2 models (Conversation, Message) existing

- [X] T004 Create Pydantic schemas in backend/src/schemas/chat.py (ChatRequest, ChatResponse, ToolCall, ErrorResponse) per data-model.md
- [X] T005 Create user validation dependency in backend/src/dependencies.py (get_validated_user function)
- [X] T006 [P] Create agent stub in backend/src/services/agent.py (ToolCallRecord, AgentResponse dataclasses, run_gemini_agent_safe returning echo response)
- [X] T007 [P] Create tool declarations stub in backend/src/tools/task_tools.py (TOOL_DECLARATIONS empty list, execute_tool returning error stub)
- [X] T008 Create conversation service in backend/src/services/conversation.py (get_or_create_conversation, fetch_history, store_user_message, store_assistant_response) per Chunk 7 spec
- [X] T009 Create schemas __init__.py export in backend/src/schemas/__init__.py

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Send a Chat Message (Priority: P1)

**Goal**: Authenticated user sends natural language message and receives AI response with conversation ID

**Independent Test**: POST to /api/{user_id}/chat with valid user_id and message returns 200 with conversation_id and response text

### Implementation for User Story 1

- [X] T010 [US1] Create chat router skeleton in backend/src/api/chat.py with POST endpoint at /chat
- [X] T011 [US1] Implement chat endpoint processing flow: validate user, resolve conversation, store user message, call agent stub, store response, return ChatResponse
- [X] T012 [US1] Wire user validation dependency (get_validated_user) into chat endpoint
- [X] T013 [US1] Integrate conversation service calls (get_or_create_conversation, store messages) in chat endpoint
- [X] T014 [US1] Add chat router to main.py with path prefix /api/{user_id}
- [X] T015 [US1] Update CORS middleware in main.py to use FRONTEND_ORIGIN from config

**Checkpoint**: User Story 1 complete - basic chat messaging works with stub agent

---

## Phase 4: User Story 2 - Receive Tool Execution Results (Priority: P1)

**Goal**: When AI performs task operations, tool execution details are included in response for transparency

**Independent Test**: Send "Add task: Buy milk" and verify response.tool_calls contains add_task with name, arguments, and result

### Implementation for User Story 2

- [X] T016 [US2] Extend chat endpoint to convert AgentResponse.tool_calls to ChatResponse.tool_calls using ToolCall schema
- [X] T017 [US2] Add tool_call conversion helper function in backend/src/api/chat.py (tool_record_to_schema, agent_to_chat_response)
- [X] T018 [US2] Ensure empty tool_calls returns null (not empty array) in response per spec

**Checkpoint**: User Story 2 complete - tool execution transparency implemented

---

## Phase 5: User Story 3 - Handle Unauthorized Access (Priority: P1)

**Goal**: Requests without proper authentication or invalid user_id are rejected with appropriate error responses

**Independent Test**: Send request with empty/invalid user_id and verify 400/401 response with ErrorResponse format

### Implementation for User Story 3

- [X] T019 [US3] Add HTTPException handling in get_validated_user for empty user_id (400 Bad Request)
- [X] T020 [US3] Add HTTPException handling in get_validated_user for non-existent user (401 Unauthorized)
- [X] T021 [US3] Ensure all error responses use ErrorResponse schema format (error, message, details)

**Checkpoint**: User Story 3 complete - unauthorized access properly blocked

---

## Phase 6: User Story 4 - Continue Existing Conversation (Priority: P2)

**Goal**: User returns to continue previous conversation; system loads history and maintains context

**Independent Test**: Send multiple messages with same conversation_id and verify context is maintained (agent receives history)

### Implementation for User Story 4

- [X] T022 [US4] Add conversation ownership validation in get_or_create_conversation (user cannot access another user's conversation)
- [X] T023 [US4] Implement fetch_history call in chat endpoint to retrieve recent messages before agent call
- [X] T024 [US4] Pass conversation history to agent stub in correct format (list of role/content dicts)
- [X] T025 [US4] Add 403 Forbidden response when user attempts to access another user's conversation in chat endpoint

**Checkpoint**: User Story 4 complete - conversation continuity works with ownership validation

---

## Phase 7: User Story 5 - Handle Service Errors Gracefully (Priority: P2)

**Goal**: External service failures (Gemini API, database) return user-friendly error messages without exposing internals

**Independent Test**: Simulate Gemini rate limit and verify 429 response with friendly message

### Implementation for User Story 5

- [X] T026 [US5] Add exception handler for ResourceExhausted (rate limit) in backend/main.py returning 429
- [X] T027 [US5] Add exception handler for ServiceUnavailable in backend/main.py returning 503
- [X] T028 [US5] Add generic exception handler in backend/main.py returning 500 with user-friendly message (no stack traces)
- [X] T029 [US5] Import google.api_core.exceptions in main.py for Gemini error types
- [X] T030 [US5] Add logging for all caught exceptions using Python logging module

**Checkpoint**: User Story 5 complete - graceful error handling implemented

---

## Phase 8: Edge Cases & Validation

**Purpose**: Handle edge cases from spec.md

- [X] T031 Add validation for empty/whitespace-only message in ChatRequest validator (return 400)
- [X] T032 Add validation for message exceeding 10,000 characters in ChatRequest (return 400)
- [X] T033 Add validation for invalid conversation_id format in ChatRequest (non-positive integer returns 400)
- [X] T034 Handle conversation_id not found by creating new conversation (graceful fallback in get_or_create_conversation)
- [X] T035 Add request body validation error handler in main.py for 422 Unprocessable Entity

**Checkpoint**: All edge cases handled per spec

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Final integration, logging, and verification

- [X] T036 [P] Add logging statements throughout chat endpoint for observability (request received, agent called, response sent)
- [X] T037 [P] Verify statelessness: ensure no request-level caching or in-memory state
- [X] T038 [P] Add response time logging (measure endpoint latency excluding Gemini API)
- [X] T039 Run manual integration test: verify chat endpoint works end-to-end with stub agent
- [X] T040 Update backend/.env.example with complete example values for all new config variables

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup + Chunk 2 models existing
- **User Story 1 (Phase 3)**: Depends on Foundational - core endpoint
- **User Story 2 (Phase 4)**: Depends on US1 - extends response
- **User Story 3 (Phase 5)**: Depends on Foundational - can parallel with US1/US2
- **User Story 4 (Phase 6)**: Depends on US1 - extends conversation handling
- **User Story 5 (Phase 7)**: Depends on US1 - adds error handlers
- **Edge Cases (Phase 8)**: Depends on Foundational - can parallel with US4/US5
- **Polish (Phase 9)**: Depends on all user stories complete

### External Dependencies

- **Chunk 2 (003-db-models-schema)**: Conversation and Message models MUST exist before Phase 2 T008
- **Chunk 3/4 (004-gemini-function-tools)**: Tool declarations stub (T007) will be replaced when Chunk 3/4 implements real tools
- **Chunk 5 (006-gemini-agent-runner)**: Agent stub (T006) will be replaced when Chunk 5 implements real Gemini integration
- **Chunk 7 (008-conversation-persistence)**: Conversation service (T008) implements the persistence spec

### Within Each User Story

1. Foundation tasks must complete first
2. Core implementation before extensions
3. Validation and error handling after happy path

### Parallel Opportunities

**Phase 2 (Foundational)**:
```
T004 (schemas) can run parallel with T006 (agent stub) and T007 (tools stub)
T005 (dependencies) and T008 (conversation service) depend on models
```

**Multi-User Story Parallel**:
```
After US1 complete, US2, US3, US4, US5 can proceed in parallel if staffed
Edge Cases (Phase 8) can run parallel with US4 and US5
```

---

## Parallel Example: Phase 2 Foundational

```bash
# Launch these tasks in parallel (no dependencies between them):
Task: T004 - Create Pydantic schemas in backend/src/schemas/chat.py
Task: T006 - Create agent stub in backend/src/services/agent.py
Task: T007 - Create tool declarations stub in backend/src/tools/task_tools.py
```

---

## Implementation Strategy

### MVP First (User Story 1 + 2 + 3 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1 (basic messaging)
4. Complete Phase 4: User Story 2 (tool transparency)
5. Complete Phase 5: User Story 3 (auth validation)
6. **STOP and VALIDATE**: Test basic chat flow with stub agent
7. Deploy/demo if ready

### Full Implementation

1. Complete MVP (Phases 1-5)
2. Add User Story 4 (conversation continuity)
3. Add User Story 5 (error handling)
4. Add Edge Cases (Phase 8)
5. Polish and logging (Phase 9)
6. Replace stubs when Chunk 3/5 are implemented

---

## Integration Points to Stub

These stubs enable Chunk 4 to be independently testable before dependent chunks are implemented:

### Agent Stub (replaced by Chunk 5)
```python
# backend/src/services/agent.py
async def run_gemini_agent_safe(user_id, history, new_message, db_session):
    return AgentResponse(text=f"Echo: {new_message}", tool_calls=[])
```

### Tools Stub (replaced by Chunk 3/4)
```python
# backend/src/tools/task_tools.py
TOOL_DECLARATIONS = []  # Populated by Chunk 3/4

async def execute_tool(tool_name, args, session):
    return {"status": "error", "message": "Tools not implemented"}
```

---

## Success Verification

| Criterion | Task | Verification |
|-----------|------|--------------|
| SC-001: <3s response | T039 | Manual test with stub |
| SC-002: Error responses | T019-T021, T026-T030 | Validate all error paths |
| SC-003: Message persistence | T011, T013 | Check DB after request |
| SC-004: Statelessness | T037 | Code review |
| SC-005: Auth blocking | T019-T021 | Test invalid users |
| SC-006: CORS | T015 | Browser/curl test |
| SC-007: Tool transparency | T016-T018 | Response schema check |
| SC-008: No stack traces | T028 | Error response check |

---

## Notes

- [P] tasks = different files, no dependencies on each other
- [Story] label maps task to specific user story for traceability
- Stubs enable independent testing before Chunks 3/5 are complete
- All error responses follow ErrorResponse schema
- Conversation service (T008) implements Chunk 7 spec interface
- Agent stub (T006) implements Chunk 5 spec interface
