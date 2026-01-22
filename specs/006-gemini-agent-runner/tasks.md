# Tasks: Gemini Agent Integration & Runner (Chunk 5)

**Input**: Design documents from `/specs/006-gemini-agent-runner/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/agent-response.json, quickstart.md
**Dependencies**: Chunk 3 (003-db-models-schema), Chunk 4 (004-gemini-function-tools), Chunk 7 (007-agent-behavior)

**Tests**: OPTIONAL - tests are NOT explicitly requested in the feature spec.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/`
- Agent module: `backend/src/services/agent.py`
- Tools module: `backend/src/gemini/tools.py` (from Chunk 4)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and SDK verification

- [X] T001 Verify google-genai package installed in backend/requirements.txt
- [X] T002 [P] Create backend/src/services/ directory structure with __init__.py
- [X] T003 [P] Verify GEMINI_API_KEY in backend/.env.example and document required env vars

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core agent infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Create backend/src/services/agent.py with module docstring and imports
- [X] T005 Define SYSTEM_PROMPT constant in backend/src/services/agent.py (from spec.md)
- [X] T006 [P] Define ToolCallRecord dataclass in backend/src/services/agent.py
- [X] T007 [P] Define AgentResponse dataclass in backend/src/services/agent.py
- [X] T008 [P] Define AgentConfig dataclass with from_env() classmethod in backend/src/services/agent.py
- [X] T009 Implement get_gemini_client() singleton in backend/src/services/agent.py
- [X] T010 Implement get_config() helper in backend/src/services/agent.py
- [X] T011 Import tool declarations from backend/src/gemini/tools.py (Chunk 4 dependency)
- [X] T012 Add module __all__ exports in backend/src/services/agent.py
- [X] T013 Configure logging in backend/src/services/agent.py

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Simple Conversational Response (Priority: P1) 🎯 MVP

**Goal**: Agent processes non-task messages and returns friendly text responses without invoking any tools

**Independent Test**: Send "Hello!" and verify text response with no tool_calls in result

### Implementation for User Story 1

- [X] T014 [US1] Implement build_contents_from_history() function in backend/src/services/agent.py
- [X] T015 [US1] Implement estimate_tokens() helper function in backend/src/services/agent.py
- [X] T016 [US1] Implement run_gemini_agent() basic structure with Gemini API call in backend/src/services/agent.py
- [X] T017 [US1] Add empty message validation in run_gemini_agent()
- [X] T018 [US1] Return AgentResponse with text when no function calls in response

**Checkpoint**: At this point, conversational messages like "Hello!" should get text responses without tool calls

---

## Phase 4: User Story 2 - Single Tool Invocation (Priority: P1)

**Goal**: Agent calls Gemini, receives a function call, executes it, feeds the result back, and returns the final response

**Independent Test**: Send "Add a task: Buy milk" and verify add_task tool is called with correct args

### Implementation for User Story 2

- [X] T019 [US2] Implement function call detection in run_gemini_agent() in backend/src/services/agent.py
- [X] T020 [US2] Implement user_id injection into function call arguments for security
- [X] T021 [US2] Call execute_tool() from Chunk 4 for each function call
- [X] T022 [US2] Create ToolCallRecord for each executed tool
- [X] T023 [US2] Build FunctionResponse objects to feed results back to Gemini
- [X] T024 [US2] Append model response and function results to contents for continuation
- [X] T025 [US2] Add logging for function call detection (INFO level) in backend/src/services/agent.py
- [X] T026 [US2] Add logging for tool execution results (INFO level) in backend/src/services/agent.py

**Checkpoint**: Single tool operations like "Add task X" or "Show my tasks" should work

---

## Phase 5: User Story 3 - Multi-Turn Tool Execution (Priority: P1)

**Goal**: Handle iterative tool execution loop until Gemini returns a final text response

**Independent Test**: Send "Complete my groceries task" and verify list_tasks then complete_task are called in sequence

### Implementation for User Story 3

- [X] T027 [US3] Implement tool execution loop (max_iterations) in run_gemini_agent()
- [X] T028 [US3] Enforce maximum iteration limit (default 5) from AgentConfig
- [X] T029 [US3] Return pause message when max iterations reached without final response
- [X] T030 [US3] Track and return all tool_calls_executed in AgentResponse

**Checkpoint**: Multi-step operations like "delete my meeting task" (requires list then delete) should work

---

## Phase 6: User Story 4 - Conversation History Context (Priority: P2)

**Goal**: Agent uses conversation history to maintain context across messages

**Independent Test**: Provide history with "I added Report task" then send "Mark it complete" - agent should understand "it"

### Implementation for User Story 4

- [X] T031 [US4] Add max_messages truncation in build_contents_from_history()
- [X] T032 [US4] Implement proper role mapping (assistant -> model) for Gemini contents
- [X] T033 [US4] Add should_truncate_history() helper for token management (optional, for future)

**Checkpoint**: Follow-up messages like "delete it" should resolve correctly from history

---

## Phase 7: User Story 5 - Rate Limit Graceful Degradation (Priority: P2)

**Goal**: Handle Gemini API errors gracefully with friendly user messages

**Independent Test**: Simulate 429 response and verify friendly error message is returned

### Implementation for User Story 5

- [X] T034 [US5] Create run_gemini_agent_safe() wrapper in backend/src/services/agent.py
- [X] T035 [US5] Handle ResourceExhausted exception (rate limit) with friendly message
- [X] T036 [US5] Handle ServiceUnavailable exception (server error) with friendly message
- [X] T037 [US5] Handle DeadlineExceeded exception (timeout) with friendly message
- [X] T038 [US5] Handle ValueError for configuration errors (missing API key)
- [X] T039 [US5] Handle generic Exception as fallback with friendly message
- [X] T040 [US5] Add logging for each error type (WARNING for rate limit, ERROR for others)

**Checkpoint**: API errors should never expose stack traces to users

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Finalization and integration verification

- [X] T041 [P] Update backend/src/services/__init__.py with agent exports
- [X] T042 Verify all module exports in __all__ list in backend/src/services/agent.py
- [X] T043 Run quickstart.md checklist validation
- [X] T044 Verify integration point with chat endpoint (Chunk 4/5 FastAPI integration)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - US1 (P1) must complete before US2, US3
  - US2 (P1) must complete before US3 (multi-turn builds on single tool)
  - US4, US5 (P2) can run after US1 completes
- **Polish (Phase 8)**: Depends on all user stories being complete

### External Dependencies

| Chunk | What This Spec Needs | How to Proceed |
|-------|---------------------|----------------|
| Chunk 3 (003-db-models-schema) | AsyncSession, Task model | Already exists |
| Chunk 4 (004-gemini-function-tools) | get_task_tools(), execute_tool() | Import from backend/src/gemini/tools.py |
| Chunk 7 (007-agent-behavior) | Extended system prompt | SYSTEM_PROMPT constant already includes base; Chunk 7 extends behavior rules |

### Within Each User Story

- Core implementation before integration
- Logging after basic functionality
- Story complete before moving to next priority

### Parallel Opportunities

- T002, T003 can run in parallel (Setup phase)
- T006, T007, T008 can run in parallel (dataclass definitions)
- After Foundational phase completes, US4 and US5 can run in parallel with each other (but after US1/US2/US3)

---

## Parallel Example: Foundational Phase

```bash
# Launch dataclass definitions together:
Task: "Define ToolCallRecord dataclass in backend/src/services/agent.py"
Task: "Define AgentResponse dataclass in backend/src/services/agent.py"
Task: "Define AgentConfig dataclass with from_env() classmethod in backend/src/services/agent.py"
```

---

## Implementation Strategy

### MVP First (User Stories 1-3 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (conversational responses)
4. **VALIDATE**: Test with "Hello!" - should get text response, no tools
5. Complete Phase 4: User Story 2 (single tool)
6. **VALIDATE**: Test with "Add task: Test" - should create task
7. Complete Phase 5: User Story 3 (multi-turn)
8. **VALIDATE**: Test with "Complete my Test task" - should work
9. **MVP COMPLETE** - Deploy/demo ready

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add US1 → Conversational AI works → Basic demo
3. Add US2 → Single tool operations work → Task creation demo
4. Add US3 → Complex operations work → Full agent demo (MVP!)
5. Add US4 → Context-aware conversations → Enhanced demo
6. Add US5 → Production-ready error handling → Production ready

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- The agent is **stateless** - all context comes from parameters per request
- **Security**: user_id MUST be injected into every tool call (T020 is critical)
- **Chunk 7 Integration**: The SYSTEM_PROMPT defined here is the base; Chunk 7's behavioral rules extend it

---

## Summary

| Metric | Value |
|--------|-------|
| Total Tasks | 44 |
| Setup Phase Tasks | 3 |
| Foundational Tasks | 10 |
| User Story 1 Tasks | 5 |
| User Story 2 Tasks | 8 |
| User Story 3 Tasks | 4 |
| User Story 4 Tasks | 3 |
| User Story 5 Tasks | 7 |
| Polish Tasks | 4 |
| Parallel Opportunities | 7 (T002-T003, T006-T008, T041) |
| MVP Scope | User Stories 1-3 (17 tasks after Foundational) |
