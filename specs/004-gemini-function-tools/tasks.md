# Chunk 4 Tasks: Gemini Function Calling Tools Definition

**Feature Branch**: `004-gemini-function-tools`
**Input**: Design documents from `/specs/004-gemini-function-tools/`
**Constitution**: Phase III Constitution (`specs/phase3/constitution.md`)
**References**: Chunk 5 (FastAPI Chat Endpoint), Chunk 7 (Agent Behavior)
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, quickstart.md ✅

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/` for source code, `backend/tests/` for tests

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency management

- [x] T001 Add `google-genai>=1.0.0` to `backend/requirements.txt`
- [x] T002 [P] Add `GEMINI_API_KEY` documentation to `backend/.env.example`
- [x] T003 Create Gemini module init file `backend/src/gemini/__init__.py` with `get_task_tools` export

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core Gemini tool declaration infrastructure that MUST be complete before user story tool implementations

**⚠️ CRITICAL**: No user story tool implementations can begin until this phase is complete

- [x] T004 Create `backend/src/gemini/tools.py` with base structure and imports from `google.genai.types`
- [x] T005 [P] Define TypedDict classes for tool return types in `backend/src/services/task_tools.py` (TaskItem, AddTaskResult, ListTasksResult, CompleteTaskResult, DeleteTaskResult, UpdateTaskResult per data-model.md)
- [x] T006 Create tool dispatcher mapping dict in `backend/src/services/task_tools.py` for routing function calls to handlers

**Checkpoint**: Foundation ready - tool declarations can now be implemented for each user story

---

## Phase 3: User Story 1 - Add a New Task via Chat (Priority: P1) 🎯 MVP

**Goal**: Declare `add_task` tool that enables AI to create tasks for users

**Independent Test**: Verify tool declaration loads, has correct name, description, and parameter schema matching spec (FR-001, FR-002, FR-010)

**Reference (Chunk 7)**: Agent maps intents like "add task buy milk", "I need to remember to X", "put X on my list" to this tool

### Implementation for User Story 1

- [x] T007 [US1] Implement `add_task` FunctionDeclaration in `backend/src/gemini/tools.py` with parameters: user_id (string, required), title (string, required), description (string, optional)
- [x] T008 [US1] Implement async `add_task_handler(user_id: str, title: str, description: str | None)` in `backend/src/services/task_tools.py`
- [x] T009 [US1] Add user ownership validation and database task creation using Task model from `backend/src/models/task.py`
- [x] T010 [US1] Return JSON response: `{"status": "created", "task_id": N, "title": "..."}` on success, `{"status": "error", "message": "..."}` on failure

**Checkpoint**: add_task tool complete - can create tasks via chat

---

## Phase 4: User Story 2 - List Tasks via Chat (Priority: P1)

**Goal**: Declare `list_tasks` tool that enables AI to retrieve user's tasks with optional filtering

**Independent Test**: Verify tool declaration has status enum with values ["all", "pending", "completed"] (FR-009)

**Reference (Chunk 7)**: Agent maps intents like "show my tasks", "what's on my list?", "show pending tasks" to this tool

### Implementation for User Story 2

- [x] T011 [P] [US2] Implement `list_tasks` FunctionDeclaration in `backend/src/gemini/tools.py` with parameters: user_id (string, required), status (string enum ["all", "pending", "completed"], optional)
- [x] T012 [US2] Implement async `list_tasks_handler(user_id: str, status: str | None)` in `backend/src/services/task_tools.py`
- [x] T013 [US2] Add status filtering logic: query tasks WHERE user_id matches and apply status filter (all/pending/completed)
- [x] T014 [US2] Return JSON response: `{"status": "listed", "tasks": [...]}` with TaskItem array per data-model.md

**Checkpoint**: list_tasks tool complete - can view tasks via chat

---

## Phase 5: User Story 3 - Complete a Task via Chat (Priority: P2)

**Goal**: Declare `complete_task` tool that enables AI to mark tasks as done

**Independent Test**: Verify task_id parameter is typed as integer, not string (FR-012)

**Reference (Chunk 7)**: Agent maps intents like "mark task 3 done", "I finished X", "complete the grocery task" to this tool (may call list_tasks first for name-based resolution)

### Implementation for User Story 3

- [x] T015 [P] [US3] Implement `complete_task` FunctionDeclaration in `backend/src/gemini/tools.py` with parameters: user_id (string, required), task_id (integer, required)
- [x] T016 [US3] Implement async `complete_task_handler(user_id: str, task_id: int)` in `backend/src/services/task_tools.py`
- [x] T017 [US3] Add ownership validation: task must belong to user_id before marking complete
- [x] T018 [US3] Set task `completed=True` in database and return `{"status": "completed", "task_id": N, "title": "..."}`
- [x] T019 [US3] Return error JSON `{"status": "error", "message": "Task not found or does not belong to user"}` if validation fails

**Checkpoint**: complete_task tool complete - can mark tasks done via chat

---

## Phase 6: User Story 4 - Delete a Task via Chat (Priority: P2)

**Goal**: Declare `delete_task` tool that enables AI to remove tasks permanently

**Independent Test**: Verify tool has correct parameters and returns deleted status on success

**Reference (Chunk 7)**: Agent maps intents like "delete task 5", "remove the meeting task", "cancel my gym task" to this tool

### Implementation for User Story 4

- [x] T020 [P] [US4] Implement `delete_task` FunctionDeclaration in `backend/src/gemini/tools.py` with parameters: user_id (string, required), task_id (integer, required)
- [x] T021 [US4] Implement async `delete_task_handler(user_id: str, task_id: int)` in `backend/src/services/task_tools.py`
- [x] T022 [US4] Add ownership validation: task must belong to user_id before deletion
- [x] T023 [US4] Delete task from database and return `{"status": "deleted", "task_id": N, "title": "..."}`
- [x] T024 [US4] Return error JSON `{"status": "error", "message": "Task not found or does not belong to user"}` if validation fails

**Checkpoint**: delete_task tool complete - can remove tasks via chat

---

## Phase 7: User Story 5 - Update a Task via Chat (Priority: P3)

**Goal**: Declare `update_task` tool that enables AI to modify task title/description

**Independent Test**: Verify title and description are optional parameters (only task_id and user_id required) (FR-011)

**Reference (Chunk 7)**: Agent maps intents like "rename task 2 to X", "add description to task 1", "change the meeting task" to this tool

### Implementation for User Story 5

- [x] T025 [P] [US5] Implement `update_task` FunctionDeclaration in `backend/src/gemini/tools.py` with parameters: user_id (string, required), task_id (integer, required), title (string, optional), description (string, optional)
- [x] T026 [US5] Implement async `update_task_handler(user_id: str, task_id: int, title: str | None, description: str | None)` in `backend/src/services/task_tools.py`
- [x] T027 [US5] Validate at least one of title/description is provided; return error if neither given
- [x] T028 [US5] Add ownership validation and update only provided fields in database
- [x] T029 [US5] Return `{"status": "updated", "task_id": N, "title": "..."}` on success
- [x] T030 [US5] Return error JSON for validation failures or task not found

**Checkpoint**: update_task tool complete - all 5 tools declared and implemented

---

## Phase 8: Integration & Tool Assembly

**Purpose**: Assemble all declarations into types.Tool and create dispatcher

- [x] T031 Create `get_task_tools()` function in `backend/src/gemini/tools.py` that returns `types.Tool` with all 5 FunctionDeclarations bundled
- [x] T032 Implement `dispatch_tool(name: str, args: dict)` async function in `backend/src/services/task_tools.py` for routing function calls
- [x] T033 [P] Export `get_task_tools` from `backend/src/gemini/__init__.py`
- [x] T034 [P] Export handlers and dispatcher from `backend/src/services/__init__.py`

**Checkpoint**: Tool module ready for integration with chat endpoint (Chunk 5)

---

## Phase 9: Unit Tests & Validation

**Purpose**: Verify tool declarations conform to Gemini SDK and spec requirements

- [x] T035 Create `backend/tests/unit/test_gemini_tools.py` test file
- [x] T036 Test `get_task_tools()` returns valid `types.Tool` object with exactly 5 declarations (FR-001)
- [x] T037 [P] Test all 5 tools have `user_id` as required parameter (FR-002)
- [x] T038 [P] Test `add_task` parameters: user_id (required), title (required), description (optional)
- [x] T039 [P] Test `list_tasks` parameters: user_id (required), status enum ["all", "pending", "completed"] (FR-009)
- [x] T040 [P] Test `complete_task`, `delete_task`, `update_task` have integer `task_id` parameter (FR-012)
- [x] T041 Test `update_task` has optional title and description parameters (FR-011)

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and documentation

- [x] T042 [P] Verify all return types match data-model.md TypedDict definitions (FR-006, FR-007)
- [x] T043 [P] Ensure all error responses include `"status": "error"` and `"message"` field (FR-008)
- [x] T044 Run unit tests: `pytest backend/tests/unit/test_gemini_tools.py -v`
- [x] T045 Verify quickstart.md example works with real Gemini API key
- [x] T046 Validate SDK compatibility with `automatic_function_calling=disable` per plan.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - US1 (add_task) and US2 (list_tasks) can run in parallel (both P1)
  - US3 (complete_task) and US4 (delete_task) can run in parallel (both P2)
  - US5 (update_task) is P3 - can start after any other story
- **Integration (Phase 8)**: Depends on all user story tools being declared
- **Unit Tests (Phase 9)**: Can start after Phase 8 (tests final assembled tools)
- **Polish (Phase 10)**: Depends on Unit Tests completion

### User Story Dependencies

- **User Story 1 (P1) - add_task**: Can start after Foundational (Phase 2) - No cross-story dependencies
- **User Story 2 (P1) - list_tasks**: Can start after Foundational (Phase 2) - No cross-story dependencies
- **User Story 3 (P2) - complete_task**: Requires US1 for creating tasks to complete (logical dependency)
- **User Story 4 (P2) - delete_task**: Requires US1 for creating tasks to delete (logical dependency)
- **User Story 5 (P3) - update_task**: Requires US1 for creating tasks to update (logical dependency)

### Within Each User Story

1. FunctionDeclaration first
2. Async handler implementation second
3. Validation and error handling third
4. Return type verification last

### Parallel Opportunities

**Phase 2 (Foundational)**:
```bash
T005: TypedDict definitions (different file)
```

**User Stories (Phase 3-7)** - All tool declarations can be parallelized:
```bash
Developer A: US1 (T007-T010) + US3 (T015-T019)
Developer B: US2 (T011-T014) + US4 (T020-T024)
Developer C: US5 (T025-T030)
```

**Phase 9 (Unit Tests)** - All tests marked [P] can run in parallel:
```bash
T037, T038, T039, T040 - Test different tool schemas
```

---

## Parallel Example: User Stories 1 & 2

```bash
# After Phase 2 completes, launch US1 and US2 in parallel:
Task: "T007 [US1] Implement add_task FunctionDeclaration in backend/src/gemini/tools.py"
Task: "T011 [P] [US2] Implement list_tasks FunctionDeclaration in backend/src/gemini/tools.py"
# Note: These work on same file but different sections - coordinate commits
```

---

## Implementation Strategy

### MVP First (User Story 1 + 2)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational (T004-T006)
3. Complete Phase 3: User Story 1 - add_task (T007-T010)
4. Complete Phase 4: User Story 2 - list_tasks (T011-T014)
5. **STOP and VALIDATE**: Test add + list via quickstart.md example
6. Deploy/demo if ready - users can add and view tasks via chat

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add US1 (add_task) → Test → Partial MVP
3. Add US2 (list_tasks) → Test → Full MVP (add + list)
4. Add US3 (complete_task) → Test → Users can complete tasks
5. Add US4 (delete_task) → Test → Users can delete tasks
6. Add US5 (update_task) → Test → Full CRUD capability
7. Integration + Tests + Polish → Production ready

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T006)
2. Once Foundational is done:
   - Developer A: User Story 1 + 3 (add_task + complete_task)
   - Developer B: User Story 2 + 4 (list_tasks + delete_task)
   - Developer C: User Story 5 (update_task)
3. Integration phase: Combine and validate (T031-T034)
4. Testing: Run unit tests (T035-T041)

---

## Summary

| Metric | Count |
|--------|-------|
| Total Tasks | 46 |
| Setup Tasks (Phase 1) | 3 |
| Foundational Tasks (Phase 2) | 3 |
| US1 (add_task) Tasks | 4 |
| US2 (list_tasks) Tasks | 4 |
| US3 (complete_task) Tasks | 5 |
| US4 (delete_task) Tasks | 5 |
| US5 (update_task) Tasks | 6 |
| Integration Tasks (Phase 8) | 4 |
| Unit Test Tasks (Phase 9) | 7 |
| Polish Tasks (Phase 10) | 5 |
| Parallel Opportunities | 14 tasks marked [P] |

### Suggested MVP Scope

**Phase 1 + 2 + 3 + 4**: Setup → Foundational → User Story 1 (add_task) → User Story 2 (list_tasks)

This provides core capability for users to:
- Add tasks via natural language ("Add task buy groceries")
- List tasks via natural language ("Show my tasks", "What's on my list?")

### Integration Points

| Chunk | Integration Point | Tasks |
|-------|------------------|-------|
| Chunk 5 (FastAPI) | Import `get_task_tools()` for Gemini config | T031, T033 |
| Chunk 5 (FastAPI) | Call `dispatch_tool()` to execute function calls | T032, T034 |
| Chunk 7 (Agent Behavior) | Tool declarations match intent mapping table | All US implementations |

---

## Success Criteria Mapping (from spec.md)

| Spec Success Criteria | Tasks |
|----------------------|-------|
| SC-001: Tools conform to Gemini SDK schema | T004, T007, T011, T015, T020, T025, T031, T036 |
| SC-002: 100% user_id on all tools | T037 |
| SC-003: 95%+ intent identification | Covered by Chunk 7 (Agent Behavior) |
| SC-004: Error responses have status + message | T010, T014, T019, T024, T030, T043 |
| SC-005: Consistent JSON structure | T042 |
| SC-006: User isolation enforced | T009, T017, T022, T028 |
| SC-007: Ambiguous requests clarify | Covered by Chunk 7 (Agent Behavior) |
| SC-008: Non-task messages no tools | Covered by Chunk 7 (Agent Behavior) |

---

## Notes

- [P] tasks = different files or independent concerns, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story tool can be tested independently once declared
- All handlers MUST be async for non-blocking database operations (per Phase III Constitution)
- Use manual execution mode: `automatic_function_calling=disable` per plan.md
- Commit after each task or logical group
- Stop at any checkpoint to validate tool functionality

---

**Generated**: 2026-01-17 | **Spec Version**: 1.0.0 | **Plan Version**: 1.0.0 | **Constitution**: Phase III v1.0.0
