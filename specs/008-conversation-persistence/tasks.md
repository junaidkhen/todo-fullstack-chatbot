# Tasks: Conversation Persistence Logic (Chunk 7)

**Input**: Design documents from `/specs/008-conversation-persistence/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/persistence-api.md
**Branch**: `008-conversation-persistence`

**Tests**: NOT explicitly requested in spec. No test tasks included unless implementation discovers critical needs.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `backend/tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Database model creation and project structure updates

- [x] T001 [P] Create MessageRole enum in backend/src/models/conversation.py
- [x] T002 Create Conversation model with user_id, timestamps, and messages relationship in backend/src/models/conversation.py
- [x] T003 Create Message model with conversation_id FK, role, content, tool_calls, created_at in backend/src/models/conversation.py
- [x] T004 Add composite index ix_messages_conversation_created on (conversation_id, created_at) in backend/src/models/conversation.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Database initialization and module setup that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No persistence function work can begin until this phase is complete

- [x] T005 Import Conversation and Message models in backend/src/database.py init_db function
- [x] T006 Verify SQLModel.metadata.create_all includes conversations and messages tables in backend/src/database.py
- [x] T007 Create persistence module skeleton with type imports in backend/src/persistence.py

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Get or Create Conversation (Priority: P1) 🎯 MVP

**Goal**: Retrieve an existing conversation or create a new one, enforcing user isolation

**Independent Test**: Call `get_or_create_conversation` with a user_id and no conversation_id, verify a new conversation is created, then call again with the returned conversation_id to verify the existing conversation is retrieved.

**Acceptance Criteria** (from spec):
1. If conversation_id is None → create new conversation for user_id
2. If conversation_id exists and belongs to user_id → return existing
3. If conversation_id exists but belongs to different user → create new (isolation enforced)
4. If conversation_id doesn't exist → create new (graceful handling)

### Implementation for User Story 1

- [x] T008 [US1] Implement get_or_create_conversation async function signature with session, user_id, conversation_id parameters in backend/src/persistence.py
- [x] T009 [US1] Add query logic to check if conversation_id exists and belongs to user_id in backend/src/persistence.py
- [x] T010 [US1] Add create new conversation logic when conversation_id is None or invalid in backend/src/persistence.py
- [x] T011 [US1] Add user isolation enforcement (return new conversation if ownership mismatch) in backend/src/persistence.py

**Checkpoint**: User Story 1 should be fully functional - conversations can be created and retrieved with user isolation

---

## Phase 4: User Story 2 - Fetch Conversation History (Priority: P1)

**Goal**: Fetch recent messages from a conversation for AI model context

**Independent Test**: Create a conversation with 40 messages, call `fetch_history(conversation_id, limit=30)`, verify exactly 30 messages are returned in chronological order (oldest to newest).

**Acceptance Criteria** (from spec):
1. If conversation has fewer than limit messages → return all in chronological order
2. If conversation has more than limit messages → return N most recent in chronological order
3. If conversation has no messages → return empty list
4. Messages returned as dictionaries with: role, content, created_at, tool_calls

### Implementation for User Story 2

- [x] T012 [US2] Implement fetch_history async function signature with session, conversation_id, user_id, limit parameters in backend/src/persistence.py
- [x] T013 [US2] Add query logic to select N most recent messages ordered by created_at DESC then reverse for chronological order in backend/src/persistence.py
- [x] T014 [US2] Add user isolation filter (user_id must match) in fetch_history in backend/src/persistence.py
- [x] T015 [US2] Implement message_to_dict helper to convert Message to Gemini-compatible format (role, content, created_at, tool_calls) in backend/src/persistence.py
- [x] T016 [US2] Handle edge case: return empty list for non-existent or unauthorized conversation_id in backend/src/persistence.py

**Checkpoint**: User Story 2 should be fully functional - conversation history can be retrieved with proper ordering and user isolation

---

## Phase 5: User Story 3 - Store User Message (Priority: P1)

**Goal**: Persist user messages so conversation history is maintained across requests

**Independent Test**: Call `store_user_message(conversation_id, "Hello")`, then fetch history and verify the message exists with role="user" and content="Hello".

**Acceptance Criteria** (from spec):
1. Creates Message record with role="user" and provided content
2. Message appears in fetch_history with role="user"
3. Empty content string is valid (for empty submit scenarios)

### Implementation for User Story 3

- [x] T017 [US3] Implement store_user_message async function signature with session, conversation_id, user_id, content parameters in backend/src/persistence.py
- [x] T018 [US3] Add conversation ownership validation (raises ValueError if invalid) in store_user_message in backend/src/persistence.py
- [x] T019 [US3] Create Message with role=MessageRole.USER, content, user_id, conversation_id in backend/src/persistence.py
- [x] T020 [US3] Add message to session and return created Message instance in backend/src/persistence.py

**Checkpoint**: User Story 3 should be fully functional - user messages can be stored with ownership validation

---

## Phase 6: User Story 4 - Store Assistant Response (Priority: P1)

**Goal**: Persist AI assistant responses with optional tool call metadata

**Independent Test**: Call `store_assistant_response(conversation_id, "Here are your tasks", [{"name": "list_tasks", "args": {}}])`, then fetch history and verify the response exists with role="assistant", content, and tool_calls metadata.

**Acceptance Criteria** (from spec):
1. Creates Message record with role="assistant" and provided content
2. Stores tool_calls as JSON metadata when provided
3. Message appears in fetch_history with role="assistant" and tool_calls accessible

### Implementation for User Story 4

- [x] T021 [US4] Implement store_assistant_response async function signature with session, conversation_id, user_id, content, tool_calls parameters in backend/src/persistence.py
- [x] T022 [US4] Add conversation ownership validation (raises ValueError if invalid) in store_assistant_response in backend/src/persistence.py
- [x] T023 [US4] Serialize tool_calls to JSON string using json.dumps when provided in backend/src/persistence.py
- [x] T024 [US4] Create Message with role=MessageRole.ASSISTANT, content, tool_calls JSON, user_id, conversation_id in backend/src/persistence.py
- [x] T025 [US4] Add message to session and return created Message instance in backend/src/persistence.py

**Checkpoint**: User Story 4 should be fully functional - assistant responses can be stored with tool call metadata

---

## Phase 7: User Story 5 - User Isolation in All Operations (Priority: P1)

**Goal**: Enforce user isolation across all persistence operations (security requirement)

**Independent Test**: Create conversations for user_a and user_b, then attempt cross-user access via all functions and verify isolation is maintained.

**Acceptance Criteria** (from spec):
1. user_b cannot fetch history for user_a's conversation
2. System validates ownership before storing messages
3. Every data access function includes user_id validation

### Implementation for User Story 5

- [x] T026 [US5] Audit get_or_create_conversation for user_id validation at all code paths in backend/src/persistence.py
- [x] T027 [US5] Audit fetch_history includes user_id filter in query in backend/src/persistence.py
- [x] T028 [US5] Audit store_user_message validates conversation.user_id == user_id in backend/src/persistence.py
- [x] T029 [US5] Audit store_assistant_response validates conversation.user_id == user_id in backend/src/persistence.py
- [x] T030 [US5] Add helper function _validate_conversation_ownership(session, conversation_id, user_id) in backend/src/persistence.py

**Checkpoint**: User Story 5 complete - all operations enforce user isolation

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T031 [P] Add module docstring and function docstrings per persistence-api.md contract in backend/src/persistence.py
- [x] T032 [P] Add __all__ exports for public API (get_or_create_conversation, fetch_history, store_user_message, store_assistant_response) in backend/src/persistence.py
- [x] T033 Export Conversation, Message, MessageRole from backend/src/models/__init__.py
- [ ] T034 Run quickstart.md validation scenarios manually to verify all functions work

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup (Phase 1) - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - US1 (Get/Create Conversation) → Can start immediately after Foundational
  - US2 (Fetch History) → Can start after Foundational (no US1 dependency)
  - US3 (Store User Message) → Can start after Foundational (no US1/US2 dependency)
  - US4 (Store Assistant Response) → Can start after Foundational (no prior story dependency)
  - US5 (User Isolation Audit) → Should start after US1-US4 complete (audits implementations)
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Get/Create Conversation - Independent, no dependencies on other stories
- **User Story 2 (P1)**: Fetch History - Independent, no dependencies on other stories
- **User Story 3 (P1)**: Store User Message - Independent, no dependencies on other stories
- **User Story 4 (P1)**: Store Assistant Response - Independent, no dependencies on other stories
- **User Story 5 (P1)**: User Isolation - Depends on US1-US4 being implemented (audit task)

### Within Each User Story

- Function signature before implementation logic
- Query logic before validation logic
- Core implementation before edge case handling
- Story complete before moving to next

### Parallel Opportunities

- T001 (MessageRole enum) can run in parallel with early Phase 1 tasks
- T008-T011 (US1), T012-T016 (US2), T017-T020 (US3), T021-T025 (US4) can run in parallel after Foundational
- T031 and T032 (Polish phase) can run in parallel

---

## Parallel Example: User Stories 1-4 After Foundational

```bash
# Once Foundational (Phase 2) completes, launch all user stories in parallel:
# Developer A: User Story 1 (T008-T011)
# Developer B: User Story 2 (T012-T016)
# Developer C: User Story 3 (T017-T020)
# Developer D: User Story 4 (T021-T025)

# Then User Story 5 (audit) after all implementations exist
```

---

## Implementation Strategy

### MVP First (User Stories 1-4)

1. Complete Phase 1: Setup (models)
2. Complete Phase 2: Foundational (database init)
3. Complete Phase 3-6: All core persistence functions in parallel
4. **STOP and VALIDATE**: Test each function independently
5. Complete Phase 7: User Isolation audit
6. Complete Phase 8: Polish

### Incremental Delivery

1. Complete Setup + Foundational → Models and database ready
2. Add US1: get_or_create_conversation → Test independently
3. Add US2: fetch_history → Test independently
4. Add US3: store_user_message → Test independently
5. Add US4: store_assistant_response → Test independently
6. Audit US5 → Verify isolation across all functions
7. Polish → Documentation and exports

---

## Summary

| Phase | Task Count | Stories Covered |
|-------|------------|-----------------|
| Phase 1: Setup | 4 | - |
| Phase 2: Foundational | 3 | - |
| Phase 3: US1 (Get/Create) | 4 | US1 |
| Phase 4: US2 (Fetch History) | 5 | US2 |
| Phase 5: US3 (Store User) | 4 | US3 |
| Phase 6: US4 (Store Assistant) | 5 | US4 |
| Phase 7: US5 (User Isolation) | 5 | US5 |
| Phase 8: Polish | 4 | - |
| **Total** | **34** | **5 User Stories** |

**MVP Scope**: User Stories 1-4 (core persistence functions)
**Full Scope**: All 5 user stories including isolation audit

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All functions are async per spec requirement
- No transaction commits in persistence functions (caller responsibility)
- Type hints required on all parameters and return values per Phase III Constitution
